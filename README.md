# Document Processing System

A FastAPI-based document processing system that supports PDF, DOCX, and email files with advanced vector search capabilities, document isolation, and automatic document type detection.

## 🚀 Features

- **Multi-format Support**: Process PDF, DOCX, and email files
- **Vector Search**: Advanced semantic search using Pinecone and Google's embedding model
- **Document Isolation**: Session-based and document-specific isolation to prevent cross-contamination
- **Automatic Document Type Detection**: Intelligently detects document types from content and filename
- **LLM Integration**: Powered by Google's Generative AI for intelligent responses
- **Session Management**: Create isolated sessions for different document sets
- **Real-time Processing**: Fast document processing and querying

## 🔧 Document Isolation Solution

The system now properly isolates documents to prevent the issue where previously uploaded documents were being included in searches. This is achieved through:

### 1. Session-Based Isolation
- Create isolated sessions for different document sets
- Each session maintains its own vector space
- Queries are scoped to specific sessions

### 2. Document-Specific Queries
- Query specific documents by document_id
- Search only within the specified document
- No cross-document contamination

### 3. Automatic Cleanup
- HackRx endpoint automatically cleans up session vectors
- Prevents vector store pollution
- Maintains system performance

## 🎯 Automatic Document Type Detection

The system now automatically detects document types from content and filename patterns:

### Supported Document Types:
- **Policy Wordings**: Insurance policies, coverage documents
- **Legal Documents**: Contracts, agreements, legal clauses
- **Financial Documents**: Reports, statements, financial data
- **Technical Documents**: Specifications, manuals, technical content
- **Medical Documents**: Medical records, health information
- **Unknown**: General documents without specific patterns

### Detection Features:
- **Content Analysis**: Analyzes document text for domain-specific keywords
- **Filename Patterns**: Uses filename patterns for initial classification
- **Confidence Scoring**: Only classifies when confident (3+ keyword matches)
- **Specialized Processing**: Each document type gets specialized LLM prompts

## 📋 API Endpoints

### Session Management
- `POST /documents/session/create` - Create a new session
- `DELETE /documents/session/{session_id}` - Delete a session and all its documents

### Document Processing
- `POST /documents/upload/` - Upload and process a document (auto-detects type)
- `POST /documents/embed/` - Generate embeddings for a document
- `GET /documents/list/` - List all documents (optionally filtered by session)
- `DELETE /documents/{document_id}/` - Delete a specific document

### Querying
- `POST /documents/query/` - Query documents with natural language
- `POST /hackrx/run` - Process documents from URL and answer questions

## 🔍 Query Options

### Session-Based Querying
```json
{
  "question": "What is the main topic?",
  "session_id": "my_session_123"
}
```

### Document-Specific Querying
```json
{
  "question": "What is this document about?",
  "document_id": "doc_123"
}
```

### Traditional Querying (All User Documents)
```json
{
  "question": "What is the main topic?",
  "document_type": "Policy Wordings"
}
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Document-Processing-System
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=document-embeddings
PINECONE_REGION=us-west-2
PINECONE_CLOUD=aws
API_KEY=your_secret_key
```

4. Run the application:
```bash
python start_server.py
```

## 📖 Usage Examples

### 1. Upload Document (Auto-Detects Type)
```python
import requests

# Upload document - type will be auto-detected
files = {"file": open("insurance_policy.pdf", "rb")}
response = requests.post("http://localhost:8000/documents/upload/", files=files)
result = response.json()
print(f"Detected type: {result['message']}")  # Shows detected document type
```

### 2. Create Session and Upload Documents
```python
# Create session
session_data = {"session_id": "my_project", "description": "Project documents"}
response = requests.post("http://localhost:8000/documents/session/create", json=session_data)

# Upload document to session
files = {"file": open("document.pdf", "rb")}
data = {"session_id": "my_project"}
response = requests.post("http://localhost:8000/documents/upload/", files=files, data=data)
```

### 3. Query Documents in Session
```python
# Query within session
query_data = {
    "question": "What are the key points?",
    "session_id": "my_session"
}
response = requests.post("http://localhost:8000/documents/query/", json=query_data)
```

### 4. Query Specific Document
```python
# Query specific document
query_data = {
    "question": "What is this document about?",
    "document_id": "doc_123"
}
response = requests.post("http://localhost:8000/documents/query/", json=query_data)
```

## 🧪 Testing

### Test Document Type Detection:
```bash
python test_document_type_detection.py
```

### Test Document Isolation:
```bash
python test_document_isolation.py
```

## 🔒 Security

- API key authentication for all endpoints
- Session-based access control
- Document isolation prevents data leakage

## 📊 Performance

- Efficient vector storage with Pinecone
- Session-based cleanup prevents vector store pollution
- Optimized chunking for better search results
- Automatic document type detection reduces manual classification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions, please open an issue on GitHub. 