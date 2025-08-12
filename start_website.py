#!/usr/bin/env python3
"""
Complete website startup script - runs both frontend and backend
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check and install required dependencies"""
    print("🔧 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import uvicorn
        print("✅ uvicorn is available")
    except ImportError:
        print("📦 Installing uvicorn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn", "fastapi"])
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js is available: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js first.")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm is available: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first.")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies"""
    print("📦 Installing frontend dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing npm packages...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        else:
            print("✅ Frontend dependencies already installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory and start server
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False
    
    return True

def start_frontend():
    """Start the frontend development server"""
    print("🚀 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Start React development server
        subprocess.run(["npm", "start"], cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False
    
    return True

def open_browser():
    """Open browser after a delay"""
    time.sleep(5)  # Wait for servers to start
    print("🌐 Opening website in browser...")
    webbrowser.open("http://localhost:3000")

def main():
    """Main function to start the complete website"""
    print("🎉 Starting Bias News Checker Website...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed")
        return
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("❌ Frontend setup failed")
        return
    
    print("\n✅ All dependencies ready!")
    print("\n🚀 Starting servers...")
    print("📝 Backend: http://localhost:8000")
    print("📝 Frontend: http://localhost:3000")
    print("🛑 Press Ctrl+C to stop all servers")
    print("=" * 50)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend in main thread
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Website stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
