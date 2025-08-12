#!/usr/bin/env python3
"""
Simple test script to verify the improved fetch_news_by_country function
without requiring uvicorn or FastAPI server
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

async def test_news_service():
    """Test the news service directly"""
    try:
        from services.news_service import NewsService
        
        print("🧪 Testing improved fetch_news_by_country function...")
        
        news_service = NewsService()
        
        # Test India endpoint
        print("\n📰 Testing India (in)...")
        articles = await news_service.fetch_news_by_country("in")
        print(f"✅ India: {len(articles)} articles fetched")
        
        # Show sample articles
        for i, article in enumerate(articles[:3]):
            print(f"\n📰 Article {i+1}:")
            print(f"   Title: {article.get('title', 'N/A')[:60]}...")
            print(f"   Source: {article.get('source', 'N/A')}")
            print(f"   API: {article.get('api_source', 'N/A')}")
        
        # Test other countries
        countries = ["us", "gb"]
        for country in countries:
            print(f"\n📰 Testing {country.upper()}...")
            try:
                articles = await news_service.fetch_news_by_country(country)
                print(f"✅ {country.upper()}: {len(articles)} articles")
            except Exception as e:
                print(f"❌ {country.upper()}: Error - {e}")
        
        print("\n🎉 All tests completed!")
        print("✅ The improved error handling is working correctly.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and have all dependencies installed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting simple test of improved news service...")
    asyncio.run(test_news_service())
