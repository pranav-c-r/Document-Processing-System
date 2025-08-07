# app/routers/document_router.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import uuid
from dotenv import load_dotenv
from typing import List

# Import models
from models.schemas import (
    DocumentUploadResponse, 
    QueryRequest, 
    QueryResponse, 
    EmbeddingRequest, 
    EmbeddingResponse,
    SessionRequest,
    SessionResponse
)

# Import services
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from services.scoring_service import ScoringService

# Import utils
from utils.file_utils import FileUtils

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

# Initialize services
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()
llm_service = LLMService()
scoring_service = ScoringService()

# In-memory storage for document metadata (in production, use a database)
document_store = {}
# In-memory storage for document chunks (in production, use a database)
document_chunks = {}
# In-memory storage for sessions (in production, use a database)
sessions = {}

@router.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """Create a new session for document isolation"""
    try:
        sessions[request.session_id] = {
            "description": request.description,
            "created_at": str(uuid.uuid4()),
            "documents": []
        }
        return SessionResponse(
            session_id=request.session_id,
            status="success",
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its documents"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete session documents from vector store
        embedding_service.delete_session_vectors(session_id, "default_user")
        
        # Delete session metadata
        del sessions[session_id]
        
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), session_id: str = None):
    """Upload and process a document (PDF, DOCX, or email)"""
    try:
        # Validate file
        file_extension = FileUtils.validate_file(file)
        file_type = FileUtils.get_file_type_from_extension(file_extension)
        
        # Read file content
        file_content = await FileUtils.read_file_content(file)
        
        # Process document
        result = document_processor.process_document(
            file_content=file_content,
            filename=file.filename,
            file_type=file_type
        )
        
        # Store document metadata with session info and detected document type
        document_store[result["document_id"]] = {
            "filename": result["filename"],
            "file_type": result["file_type"],
            "document_type": result["document_type"],  # Use detected document type
            "total_chunks": result["total_chunks"],
            "upload_time": result["upload_time"].isoformat(),
            "session_id": session_id
        }
        
        # Store document chunks
        document_chunks[result["document_id"]] = result["chunks"]
        
        # Add document to session if session_id provided
        if session_id and session_id in sessions:
            sessions[session_id]["documents"].append(result["document_id"])
        
        return DocumentUploadResponse(
            filename=result["filename"],
            document_id=result["document_id"],
            status="success",
            message=f"Document processed successfully. {result['total_chunks']} chunks created. Detected type: {result['document_type']}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed/", response_model=EmbeddingResponse)
async def embed_document(request: EmbeddingRequest):
    """Generate embeddings for a processed document"""
    try:
        # Get document metadata
        if request.document_id not in document_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get document chunks
        if request.document_id not in document_chunks:
            raise HTTPException(status_code=404, detail="Document chunks not found")
        
        chunks = document_chunks[request.document_id]
        document_info = document_store[request.document_id]
        
        # Use detected document type if not specified
        document_type = request.document_type if request.document_type != "unknown" else document_info["document_type"]
        
        # Store embeddings in Pinecone with session isolation
        result = embedding_service.store_embeddings(
            chunks, 
            user_id="default_user", 
            document_type=document_type,
            session_id=request.session_id
        )
        
        return EmbeddingResponse(
            document_id=request.document_id,
            status="success",
            chunks_processed=result["vectors_stored"],
            vectors_stored=result["vectors_stored"],
            message=f"Embeddings generated successfully for document type: {document_type}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Query a document with a natural language question"""
    try:
        # Determine search parameters
        search_params = {
            "query": request.question,
            "user_id": "default_user",
            "top_k": 5
        }
        
        # If specific document_id is provided, search only within that document
        if request.document_id:
            search_params["document_id"] = request.document_id
            # Get document type from stored metadata
            if request.document_id in document_store:
                document_type = document_store[request.document_id]["document_type"]
            else:
                document_type = "unknown"
        # If session_id is provided, search only within that session
        elif request.session_id:
            search_params["session_id"] = request.session_id
            document_type = request.document_type
        else:
            # Search across all documents, use provided document type or "unknown"
            document_type = request.document_type
        
        # Only add document_type filter if it's not "unknown" to avoid over-filtering
        if document_type and document_type != "unknown":
            search_params["document_type"] = document_type
        
        # Search for relevant chunks using embedding service
        search_results = embedding_service.search_similar(**search_params)
        
        # Extract context from search results
        context_chunks = [result["text"] for result in search_results if result["text"]]
        
        # If no relevant chunks found, return a message
        if not context_chunks:
            return QueryResponse(
                answer="No relevant information found in the specified document(s) for your question.",
                justification="The search did not return any relevant document chunks for your query.",
                matched_clauses=[],
                score_details={
                    "document_type": document_type,
                    "question_weight": 2.0,
                    "document_weight": 2.0 if document_type == "unknown" else 0.5,
                    "score": 0.0
                },
                confidence=0.0,
                document_id=request.document_id
            )
        
        # Generate answer using LLM
        llm_response = llm_service.generate_answer(
            question=request.question,
            context_chunks=context_chunks,
            document_type=document_type
        )
        
        # Create response
        return QueryResponse(
            answer=llm_response["answer"],
            justification=llm_response["justification"],
            matched_clauses=llm_response["matched_clauses"],
            score_details=llm_response["score_details"],
            confidence=llm_response["confidence"],
            document_id=request.document_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/")
async def list_documents(session_id: str = None):
    """List all uploaded documents, optionally filtered by session"""
    try:
        documents = []
        for doc_id, doc_info in document_store.items():
            # Filter by session if provided
            if session_id and doc_info.get("session_id") != session_id:
                continue
                
            documents.append({
                "document_id": doc_id,
                "filename": doc_info["filename"],
                "file_type": doc_info["file_type"],
                "total_chunks": doc_info["total_chunks"],
                "upload_time": doc_info["upload_time"],
                "document_type": doc_info["document_type"],
                "session_id": doc_info.get("session_id")
            })
        
        return {"documents": documents, "total": len(documents)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}/")
async def delete_document(document_id: str):
    """Delete a document and its embeddings"""
    try:
        if document_id not in document_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get session_id for proper vector deletion
        session_id = document_store[document_id].get("session_id")
        
        # Delete from document store
        del document_store[document_id]
        
        # Delete embeddings from Pinecone
        embedding_service.delete_document_vectors(
            document_id, 
            "default_user", 
            session_id
        )
        
        # Delete chunks from memory
        if document_id in document_chunks:
            del document_chunks[document_id]
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "document_processor": "available",
            "embedding_service": "available" if embedding_service.index else "unavailable",
            "llm_service": "available"
        }
    }
