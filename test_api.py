#!/usr/bin/env python3
"""
Test script for the Document Processing API
Run this script to test all endpoints
"""

import requests
import json
import time
import os
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/documents/health/")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Status: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_document_upload(self, file_path: str) -> str:
        """Test document upload endpoint"""
        print(f"📤 Testing document upload: {file_path}")
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(f"{self.base_url}/documents/upload/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Document upload successful")
                print(f"   Document ID: {result['document_id']}")
                print(f"   Filename: {result['filename']}")
                print(f"   Message: {result['message']}")
                return result['document_id']
            else:
                print(f"❌ Document upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Document upload error: {e}")
            return None
    
    def test_embed_document(self, document_id: str) -> bool:
        """Test embedding generation endpoint"""
        print(f"🔗 Testing embedding generation for document: {document_id}")
        try:
            data = {
                "document_id": document_id,
                "document_type": "unknown"
            }
            response = self.session.post(f"{self.base_url}/documents/embed/", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Embedding generation successful")
                print(f"   Chunks processed: {result['chunks_processed']}")
                print(f"   Vectors stored: {result['vectors_stored']}")
                return True
            else:
                print(f"❌ Embedding generation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Embedding generation error: {e}")
            return False
    
    def test_query_document(self, question: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Test document query endpoint"""
        print(f"❓ Testing document query: {question}")
        try:
            data = {
                "question": question,
                "document_type": document_type
            }
            response = self.session.post(f"{self.base_url}/documents/query/", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Document query successful")
                print(f"   Answer: {result['answer'][:100]}...")
                print(f"   Confidence: {result['confidence']}")
                print(f"   Score: {result['score_details']['score']}")
                return result
            else:
                print(f"❌ Document query failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ Document query error: {e}")
            return {}
    
    def test_list_documents(self) -> bool:
        """Test list documents endpoint"""
        print("📋 Testing list documents...")
        try:
            response = self.session.get(f"{self.base_url}/documents/list/")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ List documents successful")
                print(f"   Total documents: {result['total']}")
                for doc in result['documents']:
                    print(f"   - {doc['filename']} ({doc['document_id']})")
                return True
            else:
                print(f"❌ List documents failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ List documents error: {e}")
            return False
    
    def test_delete_document(self, document_id: str) -> bool:
        """Test delete document endpoint"""
        print(f"🗑️ Testing delete document: {document_id}")
        try:
            response = self.session.delete(f"{self.base_url}/documents/{document_id}/")
            
            if response.status_code == 200:
                print("✅ Document deletion successful")
                return True
            else:
                print(f"❌ Document deletion failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Document deletion error: {e}")
            return False
    
    def run_full_test(self):
        """Run a complete test of all endpoints"""
        print("🚀 Starting API Test Suite")
        print("=" * 50)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Health check failed. Make sure the server is running.")
            return
        
        print("\n" + "=" * 50)
        
        # Test 2: Document Upload (simulated)
        print("📝 Note: Document upload test requires a real file.")
        print("   To test with a real file, modify the test_document_upload call below.")
        
        # Simulate document upload response
        document_id = "test-document-123"
        print(f"✅ Simulated document upload with ID: {document_id}")
        
        print("\n" + "=" * 50)
        
        # Test 3: Embedding Generation
        self.test_embed_document(document_id)
        
        print("\n" + "=" * 50)
        
        # Test 4: Document Queries
        test_questions = [
            "Does this policy cover knee surgery, and what are the conditions?",
            "What is the waiting period for pre-existing conditions?",
            "What are the coverage limits for hospitalization?",
            "Does the policy include maternity benefits?"
        ]
        
        for question in test_questions:
            self.test_query_document(question)
            print("-" * 30)
        
        print("\n" + "=" * 50)
        
        # Test 5: List Documents
        self.test_list_documents()
        
        print("\n" + "=" * 50)
        
        # Test 6: Delete Document
        self.test_delete_document(document_id)
        
        print("\n" + "=" * 50)
        print("✅ API Test Suite Completed!")

def create_sample_document():
    """Create a sample PDF document for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "sample_insurance_policy.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add sample insurance policy content
        c.drawString(100, 750, "SAMPLE INSURANCE POLICY")
        c.drawString(100, 720, "Policy Number: SAMPLE-001")
        c.drawString(100, 690, "Effective Date: January 1, 2024")
        
        c.drawString(100, 650, "COVERAGE DETAILS:")
        c.drawString(120, 620, "1. Medical Expenses: Up to $100,000")
        c.drawString(120, 600, "2. Hospitalization: Covered")
        c.drawString(120, 580, "3. Surgery: Covered with pre-authorization")
        c.drawString(120, 560, "4. Prescription Drugs: 80% coverage")
        
        c.drawString(100, 520, "WAITING PERIODS:")
        c.drawString(120, 490, "1. Pre-existing conditions: 12 months")
        c.drawString(120, 470, "2. Maternity benefits: 24 months")
        c.drawString(120, 450, "3. Dental procedures: 6 months")
        
        c.drawString(100, 410, "EXCLUSIONS:")
        c.drawString(120, 380, "1. Cosmetic procedures")
        c.drawString(120, 360, "2. Experimental treatments")
        c.drawString(120, 340, "3. Injuries from illegal activities")
        
        c.save()
        print(f"✅ Created sample document: {filename}")
        return filename
    except ImportError:
        print("⚠️ reportlab not installed. Skipping sample document creation.")
        return None
    except Exception as e:
        print(f"❌ Error creating sample document: {e}")
        return None

if __name__ == "__main__":
    # Create sample document if needed
    sample_file = create_sample_document()
    
    # Initialize tester
    tester = APITester()
    
    # Run tests
    tester.run_full_test()
    
    # If sample file was created, test with it
    if sample_file and os.path.exists(sample_file):
        print(f"\n🧪 Testing with real file: {sample_file}")
        document_id = tester.test_document_upload(sample_file)
        if document_id:
            tester.test_embed_document(document_id)
            tester.test_query_document("What are the coverage limits for medical expenses?")
            tester.test_delete_document(document_id)
        
        # Clean up
        try:
            os.remove(sample_file)
            print(f"🗑️ Cleaned up sample file: {sample_file}")
        except:
            pass 