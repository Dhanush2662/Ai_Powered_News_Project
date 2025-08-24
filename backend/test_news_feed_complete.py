import asyncio
import httpx
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import sys

# Load environment variables
load_dotenv()

class NewsFeedTester:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_API_KEY")
        self.currents_api_key = os.getenv("CURRENTS_API_KEY")
        
        print("=" * 80)
        print("🚀 NEWS FEED COMPLETE FUNCTIONALITY TEST")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 NewsAPI Key: {self.news_api_key[:10]}...{self.news_api_key[-5:] if self.news_api_key else 'NOT FOUND'}")
        print(f"🔑 GNews Key: {self.gnews_api_key[:10]}...{self.gnews_api_key[-5:] if self.gnews_api_key else 'NOT FOUND'}")
        print(f"🔑 Mediastack Key: {self.mediastack_key[:10]}...{self.mediastack_key[-5:] if self.mediastack_key else 'NOT FOUND'}")
        print(f"🔑 Currents Key: {self.currents_api_key[:10]}...{self.currents_api_key[-5:] if self.currents_api_key else 'NOT FOUND'}")
        print("=" * 80)

    async def test_newsapi_detailed(self):
        """Test NewsAPI with detailed output"""
        print("\n📰 Testing NewsAPI...")
        if not self.news_api_key:
            print("❌ NewsAPI key not found")
            return False, []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test multiple endpoints
                endpoints = [
                    {
                        'name': 'US Top Headlines',
                        'url': 'https://newsapi.org/v2/top-headlines',
                        'params': {'apiKey': self.news_api_key, 'country': 'us', 'pageSize': 10}
                    },
                    {
                        'name': 'India Top Headlines', 
                        'url': 'https://newsapi.org/v2/top-headlines',
                        'params': {'apiKey': self.news_api_key, 'country': 'in', 'pageSize': 10}
                    },
                    {
                        'name': 'Technology News',
                        'url': 'https://newsapi.org/v2/top-headlines',
                        'params': {'apiKey': self.news_api_key, 'category': 'technology', 'pageSize': 10}
                    }
                ]
                
                all_articles = []
                for endpoint in endpoints:
                    try:
                        response = await client.get(endpoint['url'], params=endpoint['params'])
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'ok':
                                articles = data.get('articles', [])
                                print(f"   ✅ {endpoint['name']}: {len(articles)} articles")
                                if articles:
                                    print(f"      Sample: {articles[0].get('title', 'No title')[:60]}...")
                                all_articles.extend(articles)
                            else:
                                print(f"   ❌ {endpoint['name']}: {data.get('message', 'Unknown error')}")
                        else:
                            print(f"   ❌ {endpoint['name']}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {endpoint['name']}: {str(e)[:50]}...")
                
                success = len(all_articles) > 0
                print(f"📊 NewsAPI Total: {len(all_articles)} articles retrieved")
                return success, all_articles[:5]  # Return first 5 for display
                    
        except Exception as e:
            print(f"❌ NewsAPI: Critical Error - {str(e)}")
            return False, []

    async def test_gnews_detailed(self):
        """Test GNews API with detailed output"""
        print("\n🌍 Testing GNews...")
        if not self.gnews_api_key:
            print("❌ GNews key not found")
            return False, []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                endpoints = [
                    {
                        'name': 'US Headlines',
                        'params': {'apikey': self.gnews_api_key, 'country': 'us', 'max': 10, 'lang': 'en'}
                    },
                    {
                        'name': 'India Headlines',
                        'params': {'apikey': self.gnews_api_key, 'country': 'in', 'max': 10, 'lang': 'en'}
                    },
                    {
                        'name': 'Technology News',
                        'params': {'apikey': self.gnews_api_key, 'category': 'technology', 'max': 10, 'lang': 'en'}
                    }
                ]
                
                all_articles = []
                for endpoint in endpoints:
                    try:
                        response = await client.get('https://gnews.io/api/v4/top-headlines', params=endpoint['params'])
                        if response.status_code == 200:
                            data = response.json()
                            articles = data.get('articles', [])
                            print(f"   ✅ {endpoint['name']}: {len(articles)} articles")
                            if articles:
                                print(f"      Sample: {articles[0].get('title', 'No title')[:60]}...")
                            all_articles.extend(articles)
                        else:
                            print(f"   ❌ {endpoint['name']}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {endpoint['name']}: {str(e)[:50]}...")
                
                success = len(all_articles) > 0
                print(f"📊 GNews Total: {len(all_articles)} articles retrieved")
                return success, all_articles[:5]
                    
        except Exception as e:
            print(f"❌ GNews: Critical Error - {str(e)}")
            return False, []

    async def test_mediastack_detailed(self):
        """Test Mediastack API with detailed output"""
        print("\n📺 Testing Mediastack...")
        if not self.mediastack_key:
            print("❌ Mediastack key not found")
            return False, []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                endpoints = [
                    {
                        'name': 'US News',
                        'params': {'access_key': self.mediastack_key, 'countries': 'us', 'limit': 10}
                    },
                    {
                        'name': 'India News',
                        'params': {'access_key': self.mediastack_key, 'countries': 'in', 'limit': 10}
                    },
                    {
                        'name': 'Technology Category',
                        'params': {'access_key': self.mediastack_key, 'categories': 'technology', 'limit': 10}
                    }
                ]
                
                all_articles = []
                for endpoint in endpoints:
                    try:
                        response = await client.get('http://api.mediastack.com/v1/news', params=endpoint['params'])
                        if response.status_code == 200:
                            data = response.json()
                            articles = data.get('data', [])
                            print(f"   ✅ {endpoint['name']}: {len(articles)} articles")
                            if articles:
                                print(f"      Sample: {articles[0].get('title', 'No title')[:60]}...")
                            all_articles.extend(articles)
                        else:
                            print(f"   ❌ {endpoint['name']}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {endpoint['name']}: {str(e)[:50]}...")
                
                success = len(all_articles) > 0
                print(f"📊 Mediastack Total: {len(all_articles)} articles retrieved")
                return success, all_articles[:5]
                    
        except Exception as e:
            print(f"❌ Mediastack: Critical Error - {str(e)}")
            return False, []

    async def test_currents_detailed(self):
        """Test Currents API with detailed output"""
        print("\n⚡ Testing Currents...")
        if not self.currents_api_key:
            print("❌ Currents key not found")
            return False, []
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {'Authorization': self.currents_api_key}
                endpoints = [
                    {
                        'name': 'US Latest News',
                        'params': {'country': 'us', 'page_size': 10}
                    },
                    {
                        'name': 'India Latest News',
                        'params': {'country': 'in', 'page_size': 10}
                    },
                    {
                        'name': 'Technology Category',
                        'params': {'category': 'technology', 'page_size': 10}
                    }
                ]
                
                all_articles = []
                for endpoint in endpoints:
                    try:
                        response = await client.get('https://api.currentsapi.services/v1/latest-news', 
                                                  headers=headers, params=endpoint['params'])
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'ok':
                                articles = data.get('news', [])
                                print(f"   ✅ {endpoint['name']}: {len(articles)} articles")
                                if articles:
                                    print(f"      Sample: {articles[0].get('title', 'No title')[:60]}...")
                                all_articles.extend(articles)
                            else:
                                print(f"   ❌ {endpoint['name']}: {data.get('message', 'Unknown error')}")
                        else:
                            print(f"   ❌ {endpoint['name']}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {endpoint['name']}: {str(e)[:50]}...")
                
                success = len(all_articles) > 0
                print(f"📊 Currents Total: {len(all_articles)} articles retrieved")
                return success, all_articles[:5]
                    
        except Exception as e:
            print(f"❌ Currents: Critical Error - {str(e)}")
            return False, []

    async def test_backend_api_endpoints(self):
        """Test the actual backend API endpoints"""
        print("\n🔗 Testing Backend API Endpoints...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                base_url = "http://localhost:8000"
                
                endpoints = [
                    {
                        'name': 'Indian News Feed',
                        'url': f'{base_url}/api/news/feed?topic=technology&limit=10&focus_indian=true'
                    },
                    {
                        'name': 'International News Feed',
                        'url': f'{base_url}/api/news/feed?topic=technology&limit=10&focus_indian=false'
                    },
                    {
                        'name': 'Country News (India)',
                        'url': f'{base_url}/api/news/country/in'
                    },
                    {
                        'name': 'Country News (US)',
                        'url': f'{base_url}/api/news/country/us'
                    }
                ]
                
                backend_working = True
                for endpoint in endpoints:
                    try:
                        response = await client.get(endpoint['url'])
                        if response.status_code == 200:
                            data = response.json()
                            articles = data.get('articles', [])
                            total_count = data.get('total_count', 0)
                            print(f"   ✅ {endpoint['name']}: {len(articles)} articles (total: {total_count})")
                            if articles:
                                print(f"      Sample: {articles[0].get('title', 'No title')[:60]}...")
                        else:
                            print(f"   ❌ {endpoint['name']}: HTTP {response.status_code}")
                            backend_working = False
                    except Exception as e:
                        print(f"   ❌ {endpoint['name']}: {str(e)[:50]}...")
                        backend_working = False
                
                return backend_working
                
        except Exception as e:
            print(f"❌ Backend API Test: Critical Error - {str(e)}")
            return False

    async def run_complete_test(self):
        """Run complete news feed functionality test"""
        print(f"\n🚀 Starting Complete News Feed Test at {datetime.now().strftime('%H:%M:%S')}")
        
        # Test individual APIs
        newsapi_success, newsapi_articles = await self.test_newsapi_detailed()
        gnews_success, gnews_articles = await self.test_gnews_detailed()
        mediastack_success, mediastack_articles = await self.test_mediastack_detailed()
        currents_success, currents_articles = await self.test_currents_detailed()
        
        # Test backend endpoints
        backend_success = await self.test_backend_api_endpoints()
        
        # Calculate results
        api_results = {
            'NewsAPI': newsapi_success,
            'GNews': gnews_success,
            'Mediastack': mediastack_success,
            'Currents': currents_success
        }
        
        working_apis = [name for name, success in api_results.items() if success]
        failed_apis = [name for name, success in api_results.items() if not success]
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print("📊 COMPLETE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        print("\n🔌 API CONNECTIVITY:")
        for api_name, success in api_results.items():
            status = "✅ WORKING" if success else "❌ FAILED"
            print(f"   {api_name:<12}: {status}")
        
        print(f"\n🌐 BACKEND API: {'✅ WORKING' if backend_success else '❌ FAILED'}")
        
        print("\n📈 STATISTICS:")
        print(f"   Working APIs: {len(working_apis)}/4 ({', '.join(working_apis) if working_apis else 'None'})")
        print(f"   Failed APIs: {len(failed_apis)}/4 ({', '.join(failed_apis) if failed_apis else 'None'})")
        print(f"   Backend Status: {'Operational' if backend_success else 'Failed'}")
        
        # Overall assessment
        print("\n" + "=" * 80)
        if len(working_apis) >= 2 and backend_success:
            print("🎉 SUCCESS: News Feed is FULLY FUNCTIONAL!")
            print("   ✅ Multiple APIs are working")
            print("   ✅ Backend endpoints are responding")
            print("   ✅ Users can access news from multiple sources")
            overall_success = True
        elif len(working_apis) >= 1 and backend_success:
            print("⚠️ PARTIAL SUCCESS: News Feed is WORKING but with limited sources")
            print(f"   ✅ {len(working_apis)} API(s) working: {', '.join(working_apis)}")
            print("   ✅ Backend endpoints are responding")
            print("   ⚠️ Consider fixing failed APIs for better coverage")
            overall_success = True
        elif backend_success:
            print("⚠️ LIMITED FUNCTIONALITY: Backend working but APIs failing")
            print("   ✅ Backend endpoints are responding")
            print("   ❌ External APIs are not providing fresh content")
            print("   📝 News feed will show cached/database content only")
            overall_success = False
        else:
            print("❌ CRITICAL FAILURE: News Feed is NOT WORKING")
            print("   ❌ Backend endpoints are failing")
            print("   ❌ Users cannot access news feed")
            print("   🚨 IMMEDIATE ACTION REQUIRED")
            overall_success = False
        
        print("=" * 80)
        
        # Sample articles display
        if working_apis:
            print("\n📰 SAMPLE ARTICLES RETRIEVED:")
            all_samples = []
            if newsapi_success and newsapi_articles:
                all_samples.extend([("NewsAPI", article) for article in newsapi_articles[:2]])
            if gnews_success and gnews_articles:
                all_samples.extend([("GNews", article) for article in gnews_articles[:2]])
            
            for i, (source, article) in enumerate(all_samples[:3], 1):
                title = article.get('title', 'No title')
                print(f"   {i}. [{source}] {title[:70]}...")
        
        return overall_success, api_results, backend_success

if __name__ == "__main__":
    print("🔥 CRITICAL NEWS FEED FUNCTIONALITY TEST")
    print("This test will verify that your news feed works completely!\n")
    
    tester = NewsFeedTester()
    success, api_results, backend_status = asyncio.run(tester.run_complete_test())
    
    # Exit with appropriate code
    if success:
        print("\n✅ TEST PASSED: News Feed is working!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: News Feed needs attention!")
        sys.exit(1)