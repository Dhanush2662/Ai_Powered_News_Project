#!/usr/bin/env python3
"""
Startup script for Bias News Checker Backend
"""

import os
import sys
import subprocess

def set_environment():
    """Set environment variables for the backend"""
    # Set default environment variables
    os.environ.setdefault("OPENAI_API_KEY", "demo-key")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./bias_news.db")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("DEBUG", "True")
    
    print("🔧 Environment variables set:")
    print(f"   Database: {os.environ.get('DATABASE_URL')}")
    print(f"   OpenAI: {'Set' if os.environ.get('OPENAI_API_KEY') != 'demo-key' else 'Using fallback'}")
    print(f"   Host: {os.environ.get('HOST')}:{os.environ.get('PORT')}")

def start_backend():
    """Start the FastAPI backend"""
    try:
        print("🚀 Starting Bias News Checker Backend...")
        print("=" * 50)
        
        # Change to backend directory
        os.chdir("backend")
        
        # Set environment
        set_environment()
        
        # Start the server
        subprocess.run([sys.executable, "main.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    start_backend()
