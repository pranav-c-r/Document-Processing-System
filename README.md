# LLM-Powered Intelligent Query-Retrieval System

A FastAPI-based document processing system that can handle PDFs, DOCX files, and emails, with intelligent query capabilities using Google's Gemini AI and Pinecone vector database.

## 🚀 Features

- **Document Processing**: Support for PDF, DOCX, and email files
- **Intelligent Chunking**: Advanced text splitting with LangChain
- **Semantic Search**: Vector embeddings with Google's embedding model
- **LLM Integration**: Google Gemini for intelligent question answering
- **Structured Output**: JSON responses with scoring and justification
- **Scoring System**: Weighted scoring based on document type and question complexity

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **LLM**: Google Gemini (gemini-1.5-pro)
- **Embeddings**: Google's embedding-001 model
- **Vector Database**: Pinecone
- **Document Processing**: PyPDF, python-docx, LangChain
- **Text Splitting**: LangChain RecursiveCharacterTextSplitter

## 📋 Prerequisites

1. Python 3.8+
2. Google API Key (for Gemini)
3. Pinecone API Key (for vector storage)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd Document-Processing-System
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=document-processing-index
```

### 3. Run the Application

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Upload Document
```http
POST /documents/upload/
Content-Type: multipart/form-data
```

**Request**: Upload a file (PDF, DOCX, or email)

**Response**:
```json
{
  "filename": "insurance_policy.pdf",
  "document_id": "uuid-here",
  "status": "success",
  "message": "Document processed successfully. 15 chunks created."
}
```

#### 2. Generate Embeddings
```http
POST /documents/embed/
Content-Type: application/json
```

**Request**:
```json
{
  "document_id": "uuid-here",
  "document_type": "unknown"
}
```

**Response**:
```json
{
  "document_id": "uuid-here",
  "status": "success",
  "chunks_processed": 15,
  "vectors_stored": 15,
  "message": "Embeddings generated successfully"
}
```

#### 3. Query Document
```http
POST /documents/query/
Content-Type: application/json
```

**Request**:
```json
{
  "question": "Does this policy cover knee surgery, and what are the conditions?",
  "document_type": "unknown"
}
```

**Response**:
```json
{
  "answer": "Yes, the policy covers knee surgery under the following conditions...",
  "justification": "As per Section 3.2 of the policy document, knee surgery is covered...",
  "matched_clauses": [
    "Section 3.2 Surgical Procedures",
    "Coverage for orthopedic surgeries"
  ],
  "score_details": {
    "document_type": "unknown",
    "question_weight": 2.0,
    "document_weight": 2.0,
    "score": 4.0
  },
  "confidence": 0.85
}
```

#### 4. List Documents
```http
GET /documents/list/
```

**Response**:
```json
{
  "documents": [
    {
      "document_id": "uuid-here",
      "filename": "insurance_policy.pdf",
      "file_type": "pdf",
      "total_chunks": 15,
      "upload_time": "2024-01-15T10:30:00",
      "document_type": "unknown"
    }
  ],
  "total": 1
}
```

#### 5. Delete Document
```http
DELETE /documents/{document_id}/
```

#### 6. Health Check
```http
GET /documents/health/
```

## 🎯 Scoring System

### Document Weights
- **Known Documents**: 0.5 (publicly available documents)
- **Unknown Documents**: 2.0 (private/unseen documents)

### Question Weights
- **Complex Questions**: 2.0 (analyze, compare, explain)
- **Simple Questions**: 1.5 (does, is, are, can, will)
- **Basic Questions**: 1.0 (default)

### Score Calculation
```
Score = Question Weight × Document Weight
```

### Example Scoring
| Question | Document Type | Question Weight | Document Weight | Score |
|----------|---------------|-----------------|-----------------|-------|
| "Does this policy cover knee surgery?" | Unknown | 1.5 | 2.0 | 3.0 |
| "Analyze the coverage limitations" | Unknown | 2.0 | 2.0 | 4.0 |
| "What is the premium amount?" | Known | 1.0 | 0.5 | 0.5 |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google API key for Gemini | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | `document-processing-index` |

### Document Processing Settings

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Max File Size**: 10MB
- **Supported Formats**: PDF, DOCX, DOC, EML

## 🧪 Testing

### Using curl

1. **Upload a document**:
```bash
curl -X POST "http://localhost:8000/documents/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_document.pdf"
```

2. **Query the document**:
```bash
curl -X POST "http://localhost:8000/documents/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the coverage limits?",
    "document_type": "unknown"
  }'
```

### Using Python requests

```python
import requests

# Upload document
with open('sample_document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/documents/upload/',
        files={'file': f}
    )
    print(response.json())

# Query document
response = requests.post(
    'http://localhost:8000/documents/query/',
    json={
        'question': 'What are the coverage limits?',
        'document_type': 'unknown'
    }
)
print(response.json())
```

## 📁 Project Structure

```
Document-Processing-System/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── routers/
│   │   └── document_router.py # API endpoints
│   ├── services/
│   │   ├── document_processor.py  # Document processing
│   │   ├── embedding_service.py   # Embedding generation
│   │   ├── llm_service.py        # LLM integration
│   │   └── scoring_service.py    # Scoring logic
│   └── utils/
│       └── file_utils.py      # File handling utilities
├── requirements.txt
├── .env
└── README.md
```

## 🔄 Workflow

1. **Document Upload**: User uploads PDF/DOCX/email
2. **Text Extraction**: Document is parsed and text is extracted
3. **Chunking**: Text is split into manageable chunks
4. **Embedding**: Chunks are converted to vectors using Google's embedding model
5. **Storage**: Vectors are stored in Pinecone with metadata
6. **Query Processing**: User asks a question
7. **Semantic Search**: Relevant chunks are retrieved using vector similarity
8. **LLM Answering**: Gemini generates structured answer with justification
9. **Scoring**: System calculates score based on document and question weights

## 🚨 Error Handling

The system includes comprehensive error handling for:
- Invalid file types
- File size limits
- API key issues
- Network connectivity problems
- LLM response parsing errors

## 🔒 Security Considerations

- File size limits (10MB max)
- File type validation
- Sanitized filenames
- Environment variable protection
- Input validation

## 📈 Performance Optimization

- Asynchronous processing
- Efficient text chunking
- Vector similarity search
- Caching of embeddings
- Batch processing capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the health check endpoint
3. Check environment variables
4. Verify API keys are valid

---

**Note**: This is a hackathon project. For production use, consider adding:
- Database persistence
- User authentication
- Rate limiting
- Comprehensive logging
- Unit tests
- CI/CD pipeline 