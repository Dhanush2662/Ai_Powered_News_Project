#!/usr/bin/env python3
"""
Simple backend startup script that doesn't require uvicorn to be installed globally
"""

import subprocess
import sys
import os

def install_uvicorn():
    """Install uvicorn if not available"""
    try:
        import uvicorn
        print("✅ uvicorn is already available")
        return True
    except ImportError:
        print("📦 Installing uvicorn...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn", "fastapi"])
            print("✅ uvicorn installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install uvicorn")
            return False

def start_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        
        print("🚀 Starting backend server...")
        print("📝 Test the India endpoint at: http://localhost:8000/api/news/country/in")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Change to backend directory
        os.chdir('backend')
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError:
        print("❌ uvicorn not available even after installation attempt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    print("🔧 Setting up backend environment...")
    
    if install_uvicorn():
        start_server()
    else:
        print("❌ Cannot start server without uvicorn")
        print("💡 Try running: python -m pip install uvicorn fastapi")
