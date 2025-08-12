#!/usr/bin/env python3
"""
Test script for Bias News Checker Backend
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all backend endpoints"""
    print("🧪 Testing Bias News Checker Backend...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: News feed
    print("\n2. Testing news feed...")
    try:
        response = requests.get(f"{BASE_URL}/news-feed")
        if response.status_code == 200:
            data = response.json()
            print("✅ News feed working")
            print(f"   Articles: {len(data.get('articles', []))}")
        else:
            print(f"❌ News feed failed: {response.status_code}")
    except Exception as e:
        print(f"❌ News feed error: {e}")
    
    # Test 3: Bias analysis
    print("\n3. Testing bias analysis...")
    try:
        test_text = "This is a liberal progressive article about reform and change."
        response = requests.post(
            f"{BASE_URL}/analyze-bias",
            json={"text": test_text}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Bias analysis working")
            print(f"   Bias score: {data.get('bias_score')}")
            print(f"   Direction: {data.get('bias_direction')}")
        else:
            print(f"❌ Bias analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bias analysis error: {e}")
    
    # Test 4: Fact check
    print("\n4. Testing fact check...")
    try:
        test_claim = "The government announced a new policy that was confirmed by officials."
        response = requests.post(
            f"{BASE_URL}/fact-check",
            json={"claim": test_claim}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Fact check working")
            print(f"   Verdict: {data.get('verdict')}")
            print(f"   Confidence: {data.get('confidence_score')}")
        else:
            print(f"❌ Fact check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Fact check error: {e}")
    
    # Test 5: Coverage comparison
    print("\n5. Testing coverage comparison...")
    try:
        test_topic = "Climate Change"
        response = requests.post(
            f"{BASE_URL}/compare-coverage",
            json={"topic": test_topic}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Coverage comparison working")
            print(f"   Sources: {len(data.get('sources', []))}")
        else:
            print(f"❌ Coverage comparison failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Coverage comparison error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")

if __name__ == "__main__":
    test_endpoints()
