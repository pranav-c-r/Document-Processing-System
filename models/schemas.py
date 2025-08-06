from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    filename: str
    document_id: str
    status: str
    message: str

class QueryRequest(BaseModel):
    question: str
    document_type: Optional[str] = "unknown"  # "known" or "unknown"

class ScoreDetails(BaseModel):
    document_type: str
    question_weight: float
    document_weight: float
    score: float

class QueryResponse(BaseModel):
    answer: str
    justification: str
    matched_clauses: List[str]
    score_details: ScoreDetails
    confidence: float

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    document_type: str
    upload_time: datetime
    chunk_count: int
    total_tokens: int

class EmbeddingRequest(BaseModel):
    document_id: str
    document_type: str = "unknown"

class EmbeddingResponse(BaseModel):
    document_id: str
    status: str
    chunks_processed: int
    vectors_stored: int
    message: str 