#!/usr/bin/env python3
"""
Startup script for the Document Processing System
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting Document Processing System...")
    print("=" * 50)
    
    # Check if required environment variables are set
    required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        print("The application will start but some features may not work properly.")
    
    print("\n📋 Server Configuration:")
    print(f"   - Host: 127.0.0.1")
    print(f"   - Port: 8000")
    print(f"   - API Documentation: http://127.0.0.1:8000/docs")
    print(f"   - Health Check: http://127.0.0.1:8000/documents/health/")
    
    print("\n🎯 Document Isolation Features:")
    print("   ✅ Session-based document isolation")
    print("   ✅ Document-specific queries")
    print("   ✅ Automatic vector cleanup")
    print("   ✅ Cross-document contamination prevention")
    
    print("\n" + "=" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
