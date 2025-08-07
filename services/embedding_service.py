import os
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
from langchain.schema import Document

class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.google_api_available = True
        else:
            self.google_api_available = False

        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX", "document-embeddings")
        pinecone_region = os.getenv("PINECONE_REGION", "us-west-2")
        pinecone_cloud = os.getenv("PINECONE_CLOUD", "aws")

        if pinecone_api_key:
            try:
                self.pc = Pinecone(api_key=pinecone_api_key)
                if pinecone_index_name not in self.pc.list_indexes().names():
                    self.pc.create_index(
                        name=pinecone_index_name,
                        dimension=768,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud=pinecone_cloud,
                            region=pinecone_region
                        )
                    )
                self.index = self.pc.Index(pinecone_index_name)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Pinecone: {e}")
                self.index = None
        else:
            self.index = None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.google_api_available:
            return [[0.1] * 768 for _ in texts]
        try:
            model = genai.get_model('embedding-001')
            embeddings = []
            for text in texts:
                result = model.embed_content(text)
                embeddings.append(result['embedding'])
            return embeddings
        except Exception as e:
            return [[0.1] * 768 for _ in texts]

    def store_embeddings(self, documents: List[Document], user_id: str, document_type: str = "unknown", session_id: str = None) -> Dict[str, Any]:
        """
        Store embeddings with user_id and session_id metadata for proper document isolation.
        """
        if not self.index:
            raise Exception("Pinecone index not initialized")
        try:
            texts = [doc.page_content for doc in documents]
            embeddings = self.get_embeddings(texts)
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector_id = f"{user_id}_{doc.metadata['document_id']}_{doc.metadata['chunk_id']}"
                metadata = {
                    'user_id': user_id,
                    'document_id': doc.metadata['document_id'],
                    'chunk_id': doc.metadata['chunk_id'],
                    'text': doc.page_content,
                    'document_type': document_type,
                    'filename': doc.metadata.get('filename', '')
                }
                
                # Add session_id if provided for better isolation
                if session_id:
                    metadata['session_id'] = session_id
                    vector_id = f"{session_id}_{doc.metadata['document_id']}_{doc.metadata['chunk_id']}"
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            self.index.upsert(vectors=vectors)
            return {
                "vectors_stored": len(vectors),
                "document_id": documents[0].metadata["document_id"],
                "document_type": document_type,
                "session_id": session_id
            }
        except Exception as e:
            raise Exception(f"Error storing embeddings: {str(e)}")

    def search_similar(self, query: str, user_id: str, top_k: int = 5, document_type: str = None, 
                      document_id: str = None, session_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors with proper document isolation.
        - If document_id is provided, only search within that specific document
        - If session_id is provided, only search within that session
        - Otherwise, search within the user's documents
        """
        if not self.index:
            raise Exception("Pinecone index not initialized")
        try:
            query_embedding = self.get_embeddings([query])[0]
            
            # Build filter query based on provided parameters
            filter_query = {"user_id": {"$eq": user_id}}
            
            if document_id:
                # Search only within specific document
                filter_query["document_id"] = {"$eq": document_id}
            elif session_id:
                # Search only within specific session
                filter_query["session_id"] = {"$eq": session_id}
            
            if document_type:
                filter_query["document_type"] = {"$eq": document_type}
            
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_query
            )
            results = []
            for match in search_results.matches:
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get('text', ''),
                    "document_id": match.metadata.get('document_id', ''),
                    "chunk_id": match.metadata.get('chunk_id', ''),
                    "document_type": match.metadata.get('document_type', 'unknown'),
                    "session_id": match.metadata.get('session_id', '')
                })
            return results
        except Exception as e:
            raise Exception(f"Error searching embeddings: {str(e)}")

    def delete_document_vectors(self, document_id: str, user_id: str, session_id: str = None) -> bool:
        """
        Delete vectors for a specific document and user.
        """
        if not self.index:
            return False
        try:
            filter_query = {
                "document_id": {"$eq": document_id},
                "user_id": {"$eq": user_id}
            }
            
            if session_id:
                filter_query["session_id"] = {"$eq": session_id}
            
            results = self.index.query(
                vector=[0.1] * 768,
                top_k=10000,
                include_metadata=True,
                filter=filter_query
            )
            if results.matches:
                vector_ids = [match.id for match in results.matches]
                self.index.delete(ids=vector_ids)
            return True
        except Exception as e:
            return False

    def delete_session_vectors(self, session_id: str, user_id: str) -> bool:
        """
        Delete all vectors for a specific session and user.
        """
        if not self.index:
            return False
        try:
            results = self.index.query(
                vector=[0.1] * 768,
                top_k=10000,
                include_metadata=True,
                filter={
                    "session_id": {"$eq": session_id},
                    "user_id": {"$eq": user_id}
                }
            )
            if results.matches:
                vector_ids = [match.id for match in results.matches]
                self.index.delete(ids=vector_ids)
            return True
        except Exception as e:
            return False
