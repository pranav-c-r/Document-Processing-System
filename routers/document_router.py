# app/routers/document_router.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from typing import List

# Import models
from models.schemas import (
    DocumentUploadResponse, 
    QueryRequest, 
    QueryResponse, 
    EmbeddingRequest, 
    EmbeddingResponse
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

@router.post("/upload/", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
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
        
        # Store document metadata
        document_store[result["document_id"]] = {
            "filename": result["filename"],
            "file_type": result["file_type"],
            "total_chunks": result["total_chunks"],
            "upload_time": result["upload_time"].isoformat(),
            "document_type": "unknown"  # Default to unknown
        }
        
        # Store document chunks
        document_chunks[result["document_id"]] = result["chunks"]
        
        return DocumentUploadResponse(
            filename=result["filename"],
            document_id=result["document_id"],
            status="success",
            message=f"Document processed successfully. {result['total_chunks']} chunks created."
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
        
        # Store embeddings in Pinecone
        result = embedding_service.store_embeddings(chunks, request.document_type)
        
        return EmbeddingResponse(
            document_id=request.document_id,
            status="success",
            chunks_processed=result["vectors_stored"],
            vectors_stored=result["vectors_stored"],
            message="Embeddings generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Query a document with a natural language question"""
    try:
        # Search for relevant chunks using embedding service
        search_results = embedding_service.search_similar(
            query=request.question,
            top_k=5,
            document_type=request.document_type
        )
        
        # Extract context from search results
        context_chunks = [result["text"] for result in search_results if result["text"]]
        
        # If no relevant chunks found, return a message
        if not context_chunks:
            return QueryResponse(
                answer="No relevant information found in the uploaded documents for your question.",
                justification="The search did not return any relevant document chunks for your query.",
                matched_clauses=[],
                score_details={
                    "document_type": request.document_type,
                    "question_weight": 2.0,
                    "document_weight": 2.0 if request.document_type == "unknown" else 0.5,
                    "score": 0.0
                },
                confidence=0.0
            )
        
        # Generate answer using LLM
        llm_response = llm_service.generate_answer(
            question=request.question,
            context_chunks=context_chunks,
            document_type=request.document_type
        )
        
        # Create response
        return QueryResponse(
            answer=llm_response["answer"],
            justification=llm_response["justification"],
            matched_clauses=llm_response["matched_clauses"],
            score_details=llm_response["score_details"],
            confidence=llm_response["confidence"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = []
        for doc_id, doc_info in document_store.items():
            documents.append({
                "document_id": doc_id,
                "filename": doc_info["filename"],
                "file_type": doc_info["file_type"],
                "total_chunks": doc_info["total_chunks"],
                "upload_time": doc_info["upload_time"],
                "document_type": doc_info["document_type"]
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
        
        # Delete from document store
        del document_store[document_id]
        
        # In a real system, you would also:
        # 1. Delete embeddings from Pinecone
        # 2. Delete chunks from storage
        # 3. Delete metadata from database
        
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
