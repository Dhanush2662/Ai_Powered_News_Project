#!/usr/bin/env python3
"""
Test script for Enhanced News Aggregator
This script demonstrates the India-prioritized news aggregation functionality
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/enhanced-news"

async def test_api_status():
    """Test API configuration status"""
    print("🔍 Testing API Status...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api-status")
            if response.status_code == 200:
                data = response.json()
                print("✅ API Status Check Successful!")
                print(f"   Configured APIs: {data['total_configured_apis']}")
                print(f"   Supported Countries: {', '.join(data['api_status']['supported_countries'])}")
                print(f"   RSS Countries: {', '.join(data['api_status']['rss_countries'])}")
                return True
            else:
                print(f"❌ API Status Check Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API Status Check Error: {e}")
        return False

async def test_india_headlines():
    """Test India headlines endpoint"""
    print("\n📰 Testing India Headlines...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{BASE_URL}/india-headlines?limit=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ India Headlines: {data['total_articles']} articles")
                
                for i, article in enumerate(data['articles'][:3], 1):
                    print(f"   {i}. {article['title'][:80]}...")
                    print(f"      Source: {article['source']}")
                    print(f"      Published: {article.get('published_at', 'N/A')}")
                return True
            else:
                print(f"❌ India Headlines Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ India Headlines Error: {e}")
        return False

async def test_prioritized_feed():
    """Test the main prioritized news feed"""
    print("\n🎯 Testing Prioritized News Feed...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{BASE_URL}/prioritized-feed?limit=20&use_cache=false")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Prioritized Feed: {data['total_articles']} articles")
                print(f"   India Headlines: {data['sections']['india_headlines']}")
                print(f"   Other Countries: {data['sections']['other_countries']}")
                
                print("\n📋 Sample Articles:")
                for i, article in enumerate(data['articles'][:5], 1):
                    section = article.get('section', 'Unknown')
                    country = article.get('country_name', 'India' if 'India' in section else 'Unknown')
                    print(f"   {i}. [{section}] {article['title'][:60]}...")
                    print(f"      Country: {country} | Source: {article['source']}")
                
                return True
            else:
                print(f"❌ Prioritized Feed Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Prioritized Feed Error: {e}")
        return False

async def test_countries_with_indian_presence():
    """Test countries with Indian presence endpoint"""
    print("\n🌍 Testing Countries with Indian Presence...")
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.get(f"{BASE_URL}/countries-with-indian-presence?limit_per_country=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Countries with Indian Presence: {data['total_articles']} articles")
                
                for country_code, info in data['countries'].items():
                    print(f"   {info['name']}: {info['articles_count']} articles")
                
                return True
            else:
                print(f"❌ Countries with Indian Presence Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Countries with Indian Presence Error: {e}")
        return False

async def test_rss_feeds():
    """Test RSS feeds for India"""
    print("\n📡 Testing RSS Feeds (India)...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{BASE_URL}/rss-feeds/in")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ RSS Feeds (India): {data['total_articles']} articles")
                print(f"   Available Feeds: {', '.join(data['available_feeds'])}")
                
                for i, article in enumerate(data['articles'][:3], 1):
                    print(f"   {i}. {article['title'][:60]}...")
                    print(f"      Source: {article['source']}")
                
                return True
            else:
                print(f"❌ RSS Feeds Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ RSS Feeds Error: {e}")
        return False

async def test_aggregation():
    """Test the aggregation functionality"""
    print("\n🧪 Testing News Aggregation...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{BASE_URL}/test-aggregation")
            if response.status_code == 200:
                data = response.json()
                print("✅ Aggregation Test Successful!")
                print(f"   India Headlines: {data['test_results']['india_headlines_count']}")
                print(f"   Other Countries: {data['test_results']['other_countries_count']}")
                
                print("\n📝 Sample India Titles:")
                for i, title in enumerate(data['test_results']['sample_india_titles'], 1):
                    print(f"   {i}. {title}...")
                
                print("\n📝 Sample Other Countries Titles:")
                for i, title in enumerate(data['test_results']['sample_other_titles'], 1):
                    print(f"   {i}. {title}...")
                
                return True
            else:
                print(f"❌ Aggregation Test Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Aggregation Test Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Enhanced News Aggregator Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Status", test_api_status),
        ("India Headlines", test_india_headlines),
        ("Countries with Indian Presence", test_countries_with_indian_presence),
        ("RSS Feeds", test_rss_feeds),
        ("Aggregation Test", test_aggregation),
        ("Prioritized Feed", test_prioritized_feed),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Enhanced News Aggregator is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the API keys in your .env file.")
    
    print("\n📚 Available Endpoints:")
    print("   • GET /api/enhanced-news/prioritized-feed - Main prioritized feed")
    print("   • GET /api/enhanced-news/india-headlines - India-only headlines")
    print("   • GET /api/enhanced-news/countries-with-indian-presence - Other countries")
    print("   • GET /api/enhanced-news/country/{country_code} - Specific country")
    print("   • GET /api/enhanced-news/rss-feeds/{country_code} - RSS feeds")
    print("   • GET /api/enhanced-news/api-status - API configuration status")

if __name__ == "__main__":
    asyncio.run(main())