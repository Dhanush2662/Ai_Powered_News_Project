#!/usr/bin/env python3
"""
Comprehensive test for all news APIs including the newly integrated ones.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class NewsAPITester:
    def __init__(self):
        # Load all API keys
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        self.mediastack_key = os.getenv('MEDIASTACK_API_KEY')
        self.currents_api_key = os.getenv('CURRENTS_API_KEY')
        self.guardian_api_key = os.getenv('GUARDIAN_API_KEY')
        self.nytimes_api_key = os.getenv('NYTIMES_API_KEY')
        self.nytimes_api_key_2 = os.getenv('NYTIMES_API_KEY_2')
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.newsdata_io_key = os.getenv('NEWSDATAIO_KEY')
        self.worldnews_key = os.getenv('WORLDNEWS_KEY')
        
    async def test_newsapi(self):
        """Test NewsAPI"""
        if not self.news_api_key:
            return "❌ NewsAPI: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        'country': 'us',
                        'pageSize': 5,
                        'apiKey': self.news_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    return f"✅ NewsAPI: {len(articles)} articles"
                else:
                    return f"❌ NewsAPI: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ NewsAPI: {str(e)[:100]}"
    
    async def test_gnews(self):
        """Test GNews API"""
        if not self.gnews_api_key:
            return "❌ GNews: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://gnews.io/api/v4/top-headlines",
                    params={
                        'country': 'us',
                        'max': 5,
                        'apikey': self.gnews_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    return f"✅ GNews: {len(articles)} articles"
                else:
                    return f"❌ GNews: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ GNews: {str(e)[:100]}"
    
    async def test_mediastack(self):
        """Test Mediastack API"""
        if not self.mediastack_key:
            return "❌ Mediastack: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "http://api.mediastack.com/v1/news",
                    params={
                        'access_key': self.mediastack_key,
                        'countries': 'us',
                        'limit': 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    return f"✅ Mediastack: {len(articles)} articles"
                else:
                    return f"❌ Mediastack: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ Mediastack: {str(e)[:100]}"
    
    async def test_currents(self):
        """Test Currents API"""
        if not self.currents_api_key:
            return "❌ Currents: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.currentsapi.services/v1/latest-news",
                    params={
                        'apiKey': self.currents_api_key,
                        'country': 'US',
                        'page_size': 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('news', [])
                    return f"✅ Currents: {len(articles)} articles"
                else:
                    return f"❌ Currents: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ Currents: {str(e)[:100]}"
    
    async def test_guardian(self):
        """Test Guardian API"""
        if not self.guardian_api_key:
            return "❌ Guardian: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://content.guardianapis.com/search",
                    params={
                        'api-key': self.guardian_api_key,
                        'page-size': 5,
                        'show-fields': 'headline,byline,thumbnail,short-url'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('response', {}).get('results', [])
                    return f"✅ Guardian: {len(articles)} articles"
                else:
                    return f"❌ Guardian: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ Guardian: {str(e)[:100]}"
    
    async def test_nytimes(self):
        """Test NY Times API"""
        if not self.nytimes_api_key:
            return "❌ NY Times: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.nytimes.com/svc/topstories/v2/home.json",
                    params={'api-key': self.nytimes_api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('results', [])
                    return f"✅ NY Times: {len(articles)} articles"
                else:
                    return f"❌ NY Times: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ NY Times: {str(e)[:100]}"
    
    async def test_serpapi(self):
        """Test SerpAPI (Google News)"""
        if not self.serpapi_key:
            return "❌ SerpAPI: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://serpapi.com/search.json",
                    params={
                        'engine': 'google_news',
                        'q': 'news',
                        'gl': 'us',
                        'hl': 'en',
                        'num': 5,
                        'api_key': self.serpapi_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('news_results', [])
                    return f"✅ SerpAPI: {len(articles)} articles"
                else:
                    return f"❌ SerpAPI: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ SerpAPI: {str(e)[:100]}"
    
    async def test_newsdata_io(self):
        """Test NewsData.io API"""
        if not self.newsdata_io_key:
            return "❌ NewsData.io: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://newsdata.io/api/1/news",
                    params={
                        'apikey': self.newsdata_io_key,
                        'country': 'us',
                        'size': 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('results', [])
                    return f"✅ NewsData.io: {len(articles)} articles"
                else:
                    return f"❌ NewsData.io: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ NewsData.io: {str(e)[:100]}"
    
    async def test_worldnews(self):
        """Test WorldNews API"""
        if not self.worldnews_key:
            return "❌ WorldNews: No API key"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.worldnewsapi.com/search-news",
                    params={
                        'api-key': self.worldnews_key,
                        'text': 'news',
                        'number': 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('news', [])
                    return f"✅ WorldNews: {len(articles)} articles"
                else:
                    return f"❌ WorldNews: HTTP {response.status_code} - {response.text[:100]}"
                    
        except Exception as e:
            return f"❌ WorldNews: {str(e)[:100]}"
    
    async def test_backend_endpoints(self):
        """Test backend API endpoints"""
        results = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test Indian News Feed
                response = await client.get("http://localhost:8000/api/news/indian")
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ Indian News Feed: {len(data)} articles")
                else:
                    results.append(f"❌ Indian News Feed: HTTP {response.status_code}")
                
                # Test International News Feed
                response = await client.get("http://localhost:8000/api/news/international")
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ International News Feed: {len(data)} articles")
                else:
                    results.append(f"❌ International News Feed: HTTP {response.status_code}")
                
                # Test Country News for India
                response = await client.get("http://localhost:8000/api/news/country/in")
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ Country News (India): {len(data)} articles")
                else:
                    results.append(f"❌ Country News (India): HTTP {response.status_code}")
                
                # Test Country News for US
                response = await client.get("http://localhost:8000/api/news/country/us")
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ Country News (US): {len(data)} articles")
                else:
                    results.append(f"❌ Country News (US): HTTP {response.status_code}")
                    
        except Exception as e:
            results.append(f"❌ Backend endpoints: {str(e)[:100]}")
        
        return results
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("🔍 COMPREHENSIVE NEWS API TEST")
        print("="*60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test individual APIs
        print("📡 TESTING INDIVIDUAL APIs:")
        print("-" * 40)
        
        api_tests = [
            self.test_newsapi(),
            self.test_gnews(),
            self.test_mediastack(),
            self.test_currents(),
            self.test_guardian(),
            self.test_nytimes(),
            self.test_serpapi(),
            self.test_newsdata_io(),
            self.test_worldnews()
        ]
        
        api_results = await asyncio.gather(*api_tests, return_exceptions=True)
        
        for result in api_results:
            if isinstance(result, Exception):
                print(f"❌ API Test Error: {str(result)[:100]}")
            else:
                print(result)
        
        print()
        print("🔗 TESTING BACKEND ENDPOINTS:")
        print("-" * 40)
        
        # Test backend endpoints
        backend_results = await self.test_backend_endpoints()
        for result in backend_results:
            print(result)
        
        print()
        print("📊 SUMMARY:")
        print("-" * 40)
        
        # Count working APIs
        working_apis = sum(1 for result in api_results if isinstance(result, str) and result.startswith("✅"))
        total_apis = len(api_results)
        working_endpoints = sum(1 for result in backend_results if result.startswith("✅"))
        total_endpoints = len(backend_results)
        
        print(f"📡 Individual APIs: {working_apis}/{total_apis} working")
        print(f"🔗 Backend Endpoints: {working_endpoints}/{total_endpoints} working")
        
        if working_apis >= 3 and working_endpoints >= 2:
            print("\n🎉 NEWS FEED IS FULLY FUNCTIONAL! 🎉")
        elif working_apis >= 2:
            print("\n✅ News feed is functional with multiple sources")
        else:
            print("\n⚠️  News feed has limited functionality")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    tester = NewsAPITester()
    asyncio.run(tester.run_all_tests())