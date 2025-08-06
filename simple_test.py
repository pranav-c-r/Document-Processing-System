import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    # Test health check
    print("Testing health check...")
    try:
        response = requests.get(f"{base_url}/documents/health/")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test query endpoint
    print("\nTesting query endpoint...")
    try:
        data = {
            "question": "Does this policy cover knee surgery?",
            "document_type": "unknown"
        }
        response = requests.post(f"{base_url}/documents/query/", json=data)
        if response.status_code == 200:
            print("✅ Query test passed!")
            result = response.json()
            print(f"Answer: {result['answer'][:100]}...")
            print(f"Confidence: {result['confidence']}")
            print(f"Score: {result['score_details']['score']}")
        else:
            print(f"❌ Query test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Query test error: {e}")

if __name__ == "__main__":
    test_api() 