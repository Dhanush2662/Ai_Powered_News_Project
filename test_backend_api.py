#!/usr/bin/env python3
"""
Test script to verify the backend API endpoints are working correctly
"""

import requests
import json
import sys

def test_backend_api():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend API Endpoints...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: India news endpoint
    print("\n3. Testing India news endpoint...")
    try:
        response = requests.get(f"{base_url}/api/news/country/in")
        if response.status_code == 200:
            data = response.json()
            print("✅ India endpoint working")
            print(f"   Articles: {data.get('total_count', 0)}")
            print(f"   Country: {data.get('country', 'N/A')}")
            print(f"   API Sources: {data.get('api_sources', [])}")
            
            # Show first article if available
            articles = data.get('articles', [])
            if articles:
                first_article = articles[0]
                print(f"   First article: {first_article.get('title', 'N/A')[:60]}...")
        else:
            print(f"❌ India endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ India endpoint error: {e}")
    
    # Test 4: USA news endpoint
    print("\n4. Testing USA news endpoint...")
    try:
        response = requests.get(f"{base_url}/api/news/country/us")
        if response.status_code == 200:
            data = response.json()
            print("✅ USA endpoint working")
            print(f"   Articles: {data.get('total_count', 0)}")
            print(f"   Country: {data.get('country', 'N/A')}")
            print(f"   API Sources: {data.get('api_sources', [])}")
        else:
            print(f"❌ USA endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ USA endpoint error: {e}")
    
    # Test 5: API docs
    print("\n5. Testing API docs...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API docs available")
            print(f"   Visit: {base_url}/docs")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend API testing completed!")
    print("\n📝 If you see errors, make sure:")
    print("   1. Backend is running: cd backend && python -m uvicorn main:app --reload")
    print("   2. Backend is on port 8000")
    print("   3. No firewall blocking the connection")

if __name__ == "__main__":
    test_backend_api()
