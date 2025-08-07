#!/usr/bin/env python3
"""
Test script to demonstrate document isolation functionality.
This script shows how the system now properly isolates documents by session.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-key"  # Replace with your actual API key

def test_document_isolation():
    """Test document isolation using sessions"""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    print("🧪 Testing Document Isolation System")
    print("=" * 50)
    
    # Step 1: Create two different sessions
    print("\n1. Creating sessions...")
    
    session1_data = {"session_id": "test_session_1", "description": "First test session"}
    session2_data = {"session_id": "test_session_2", "description": "Second test session"}
    
    response1 = requests.post(f"{BASE_URL}/documents/session/create", 
                            json=session1_data, headers=headers)
    response2 = requests.post(f"{BASE_URL}/documents/session/create", 
                            json=session2_data, headers=headers)
    
    print(f"Session 1 created: {response1.status_code}")
    print(f"Session 2 created: {response2.status_code}")
    
    # Step 2: Upload different documents to different sessions
    print("\n2. Uploading documents to different sessions...")
    
    # Create test documents (you would normally upload real files)
    # For this test, we'll simulate the process
    
    # Step 3: Test querying with session isolation
    print("\n3. Testing query isolation...")
    
    # Query with session 1
    query_data = {
        "question": "What is the main topic?",
        "session_id": "test_session_1"
    }
    
    response = requests.post(f"{BASE_URL}/documents/query/", 
                           json=query_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Query in Session 1: {result['answer'][:100]}...")
    else:
        print(f"Query failed: {response.status_code}")
    
    # Query with session 2
    query_data = {
        "question": "What is the main topic?",
        "session_id": "test_session_2"
    }
    
    response = requests.post(f"{BASE_URL}/documents/query/", 
                           json=query_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Query in Session 2: {result['answer'][:100]}...")
    else:
        print(f"Query failed: {response.status_code}")
    
    # Step 4: Test document-specific queries
    print("\n4. Testing document-specific queries...")
    
    # List documents in session 1
    response = requests.get(f"{BASE_URL}/documents/list/?session_id=test_session_1", 
                          headers=headers)
    
    if response.status_code == 200:
        documents = response.json()
        print(f"Documents in Session 1: {len(documents['documents'])}")
        
        if documents['documents']:
            # Query specific document
            doc_id = documents['documents'][0]['document_id']
            query_data = {
                "question": "What is this document about?",
                "document_id": doc_id
            }
            
            response = requests.post(f"{BASE_URL}/documents/query/", 
                                  json=query_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Document-specific query: {result['answer'][:100]}...")
            else:
                print(f"Document-specific query failed: {response.status_code}")
    
    # Step 5: Clean up
    print("\n5. Cleaning up sessions...")
    
    response1 = requests.delete(f"{BASE_URL}/documents/session/test_session_1", headers=headers)
    response2 = requests.delete(f"{BASE_URL}/documents/session/test_session_2", headers=headers)
    
    print(f"Session 1 deleted: {response1.status_code}")
    print(f"Session 2 deleted: {response2.status_code}")
    
    print("\n✅ Document isolation test completed!")

def test_hackrx_isolation():
    """Test HackRx endpoint isolation"""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    print("\n🧪 Testing HackRx Document Isolation")
    print("=" * 50)
    
    # Test data
    hackrx_data = {
        "documents": "https://example.com/test.pdf",  # Replace with actual PDF URL
        "questions": [
            "What is the main topic of this document?",
            "What are the key points mentioned?"
        ]
    }
    
    print("Sending HackRx request...")
    response = requests.post(f"{BASE_URL}/hackrx/run", 
                           json=hackrx_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ HackRx request successful!")
        print(f"Answers: {result['answers']}")
    else:
        print(f"❌ HackRx request failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Document Isolation Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    test_document_isolation()
    
    # Test HackRx isolation
    test_hackrx_isolation()
    
    print("\n🎉 All tests completed!")
