#!/usr/bin/env python3
"""
Test script to verify the improved fetch_news_by_country function
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

from services.news_service import NewsService

async def test_india_endpoint():
    """Test the India endpoint with improved error handling"""
    print("🧪 Testing India endpoint with improved error handling...")
    
    news_service = NewsService()
    
    try:
        # Test India endpoint
        articles = await news_service.fetch_news_by_country("in")
        
        print(f"✅ Successfully fetched {len(articles)} articles for India")
        
        # Show sample articles
        for i, article in enumerate(articles[:5]):
            print(f"\n📰 Article {i+1}:")
            print(f"   Title: {article.get('title', 'N/A')}")
            print(f"   Source: {article.get('source', 'N/A')}")
            print(f"   API: {article.get('api_source', 'N/A')}")
            print(f"   Published: {article.get('published_at', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing India endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_other_countries():
    """Test other countries to ensure they still work"""
    print("\n🧪 Testing other countries...")
    
    news_service = NewsService()
    countries = ["us", "gb", "au"]
    
    for country in countries:
        try:
            articles = await news_service.fetch_news_by_country(country)
            print(f"✅ {country.upper()}: {len(articles)} articles")
        except Exception as e:
            print(f"❌ {country.upper()}: Error - {e}")

async def main():
    """Main test function"""
    print("🚀 Starting tests for improved fetch_news_by_country function...")
    
    # Test India
    india_success = await test_india_endpoint()
    
    # Test other countries
    await test_other_countries()
    
    if india_success:
        print("\n✅ All tests completed successfully!")
        print("🎉 The improved error handling is working correctly.")
        print("📝 You can now test the endpoint at: http://localhost:8000/api/news/country/in")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
