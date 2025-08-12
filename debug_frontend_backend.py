#!/usr/bin/env python3
"""
Debug script to identify frontend-backend communication issues
"""

import requests
import json
import time

def test_backend_directly():
    """Test backend endpoints directly"""
    print("🔍 Testing Backend Directly...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test India endpoint
    print("\n📰 Testing India endpoint directly...")
    try:
        response = requests.get(f"{base_url}/api/news/country/in", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend working!")
            print(f"Total articles: {data.get('total_count', 0)}")
            print(f"API sources: {data.get('api_sources', [])}")
            
            articles = data.get('articles', [])
            if articles:
                print(f"First article: {articles[0].get('title', 'N/A')[:50]}...")
            else:
                print("⚠️ No articles returned")
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"Error text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Backend not running or not accessible")
        print("💡 Make sure backend is running: cd backend && python -m uvicorn main:app --reload")
    except requests.exceptions.Timeout:
        print("❌ Timeout error - Backend taking too long to respond")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_frontend_api_call():
    """Simulate the frontend API call"""
    print("\n🌐 Testing Frontend API Call Simulation...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/news/country/in"
    
    print(f"Making request to: {base_url}{endpoint}")
    
    try:
        response = requests.get(
            f"{base_url}{endpoint}",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            print(f"Response structure: {list(data.keys())}")
            print(f"Articles count: {len(data.get('articles', []))}")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ API call error: {e}")

def check_ports():
    """Check if ports are in use"""
    print("\n🔌 Checking Port Status...")
    print("=" * 50)
    
    import socket
    
    ports = [8000, 3000]
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"✅ Port {port} is in use (likely our service)")
        else:
            print(f"❌ Port {port} is not in use")
        sock.close()

def main():
    """Main debugging function"""
    print("🐛 Frontend-Backend Debugging Tool")
    print("=" * 50)
    
    # Check ports
    check_ports()
    
    # Test backend directly
    test_backend_directly()
    
    # Test frontend API call simulation
    test_frontend_api_call()
    
    print("\n" + "=" * 50)
    print("🎯 Debugging Summary:")
    print("1. If backend tests fail: Backend not running or has errors")
    print("2. If frontend simulation fails: Network/CORS issues")
    print("3. If both work: Frontend code issue")
    print("\n💡 Next steps:")
    print("   - Start backend: cd backend && python -m uvicorn main:app --reload")
    print("   - Start frontend: cd frontend && npm start")
    print("   - Check browser console for errors")

if __name__ == "__main__":
    main()
