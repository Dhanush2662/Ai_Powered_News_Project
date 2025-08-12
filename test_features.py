#!/usr/bin/env python3
"""
Test script to verify all Bias News Checker features are working
"""

import asyncio
import httpx
import json

# Test data
TEST_ARTICLE = """
The BJP government today announced a comprehensive economic policy that promises to boost GDP growth by 8% over the next five years. 
Finance Minister Nirmala Sitharaman stated that this policy will create millions of jobs and transform India into a $5 trillion economy. 
Opposition parties have criticized the policy as "anti-poor" and "pro-corporate," claiming it will benefit only the wealthy elite while ignoring the common man's struggles.
"""

TEST_CLAIM = "NASA confirms 3 days of darkness in December 2024"

async def test_bias_analysis():
    """Test bias analysis feature"""
    print("🧪 Testing Bias Analysis...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/bias/analyze",
                json={"content": TEST_ARTICLE}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bias Analysis: SUCCESS")
                print(f"   Bias Score: {result.get('bias_score', 'N/A')}")
                print(f"   Direction: {result.get('bias_direction', 'N/A')}")
                print(f"   Emotional Tone: {result.get('emotional_tone', 'N/A')}")
                return True
            else:
                print(f"❌ Bias Analysis: FAILED - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Bias Analysis: ERROR - {str(e)}")
            return False

async def test_fact_check():
    """Test fact checking feature"""
    print("🧪 Testing Fact Check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/fact-check/verify",
                json={"claim": TEST_CLAIM}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Fact Check: SUCCESS")
                print(f"   Verdict: {result.get('verdict', 'N/A')}")
                print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
                return True
            else:
                print(f"❌ Fact Check: FAILED - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Fact Check: ERROR - {str(e)}")
            return False

async def test_news_feed():
    """Test news feed feature"""
    print("🧪 Testing News Feed...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/news/")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ News Feed: SUCCESS")
                print(f"   Articles: {len(result.get('articles', []))}")
                return True
            else:
                print(f"❌ News Feed: FAILED - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ News Feed: ERROR - {str(e)}")
            return False

async def test_coverage_comparison():
    """Test coverage comparison feature"""
    print("🧪 Testing Coverage Comparison...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/coverage/trending")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Coverage Comparison: SUCCESS")
                print(f"   Trending Topics: {len(result.get('topics', []))}")
                return True
            else:
                print(f"❌ Coverage Comparison: FAILED - {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Coverage Comparison: ERROR - {str(e)}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting Bias News Checker Feature Tests...")
    print("=" * 50)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    await asyncio.sleep(3)
    
    results = []
    
    # Test all features
    results.append(await test_news_feed())
    results.append(await test_bias_analysis())
    results.append(await test_fact_check())
    results.append(await test_coverage_comparison())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"✅ Working Features: {sum(results)}/{len(results)}")
    print(f"❌ Failed Features: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 ALL FEATURES ARE WORKING!")
    else:
        print("⚠️  Some features need attention")
    
    print("\n🌐 Frontend should be available at: http://localhost:3000")
    print("🔧 Backend API available at: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())
