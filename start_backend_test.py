#!/usr/bin/env python3
"""
Simple script to start the backend server for testing
"""

import uvicorn
import os
import sys

# Add backend to path
sys.path.append('backend')

if __name__ == "__main__":
    print("🚀 Starting backend server for testing...")
    print("📝 Test the India endpoint at: http://localhost:8000/api/news/country/in")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
