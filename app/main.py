from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from routers import document_router
import requests
import os
import uuid
from typing import List
from pydantic import BaseModel

app = FastAPI()
app.include_router(document_router.router)

# Security
security = HTTPBearer()

class HackRxRequest(BaseModel):
    documents: str  # URL to PDF
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = os.getenv("API_KEY", "your-secret-key")
    if credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

@app.get("/")
def home():
    return {"message": "Document Processing API is up!"}

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(request: HackRxRequest, token: str = Depends(verify_token)):
    """
    Accepts a JSON body with 'documents' (URL to PDF) and 'questions' (list of strings).
    Returns answers for each question in the required format.
    """
    # Generate unique session ID for this request to isolate documents
    session_id = f"hackrx_{uuid.uuid4().hex[:8]}"

# --- Webhook endpoint for Railway ---
from fastapi import Request

@app.post("/webhook")
async def railway_webhook(request: Request):
    data = await request.json()
    # You can add custom logic here
    return {"message": "Webhook received", "data": data}
    
    # Download PDF from URL
    try:
        response = requests.get(request.documents, timeout=30)
        response.raise_for_status()
        file_content = response.content
        filename = request.documents.split("/")[-1]
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        from utils.file_utils import FileUtils
        file_type = FileUtils.get_file_type_from_extension(file_extension)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get document: {str(e)}")

    # Process document
    try:
        from services.document_processor import DocumentProcessor
        from services.embedding_service import EmbeddingService
        from services.llm_service import LLMService
        doc_processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        llm_service = LLMService()
        result = doc_processor.process_document(file_content, filename, file_type)
        chunks = result["chunks"]
        document_id = result["document_id"]
        
        # Store embeddings with session isolation
        embedding_service.store_embeddings(
            chunks, 
            user_id="hackrx", 
            document_type="unknown",
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    # Answer each question
    answers = []
    for question in request.questions:
        try:
            # Search only within the current session to avoid cross-document contamination
            similar_chunks = embedding_service.search_similar(
                question, 
                user_id="hackrx", 
                top_k=3,
                session_id=session_id
            )
            context = [chunk["text"] for chunk in similar_chunks]
            llm_response = llm_service.generate_answer(question, context)
            answer = llm_response["answer"] if isinstance(llm_response, dict) and "answer" in llm_response else str(llm_response)
        except Exception as e:
            answer = f"Error: {str(e)}"
        answers.append(answer)
    
    # Clean up session vectors after processing
    try:
        embedding_service.delete_session_vectors(session_id, "hackrx")
    except Exception as e:
        print(f"Warning: Could not clean up session vectors: {e}")
    
    return HackRxResponse(answers=answers) 