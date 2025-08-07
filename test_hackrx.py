import requests
import json

def test_hackrx_endpoint():
    url = "http://127.0.0.1:8000/hackrx/run"
    
    # Test data
    payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is this document about?",
            "What are the main topics covered?",
            "What is the purpose of this document?"
        ]
    }
    
    headers = {
        "Authorization": "Bearer your-secret-key",
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing /hackrx/run endpoint...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Answers: {json.dumps(result, indent=2)}")
        else:
            print("❌ ERROR!")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_hackrx_endpoint() 