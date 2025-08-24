import asyncio
import httpx
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class APIKeyTester:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_API_KEY")
        self.currents_api_key = os.getenv("CURRENTS_API_KEY")
        
        print("=" * 60)
        print("🔑 API KEY TESTER")
        print("=" * 60)
        print(f"NewsAPI Key: {self.news_api_key[:10]}...{self.news_api_key[-5:] if self.news_api_key else 'NOT FOUND'}")
        print(f"GNews Key: {self.gnews_api_key[:10]}...{self.gnews_api_key[-5:] if self.gnews_api_key else 'NOT FOUND'}")
        print(f"Mediastack Key: {self.mediastack_key[:10]}...{self.mediastack_key[-5:] if self.mediastack_key else 'NOT FOUND'}")
        print(f"Currents Key: {self.currents_api_key[:10]}...{self.currents_api_key[-5:] if self.currents_api_key else 'NOT FOUND'}")
        print("=" * 60)

    async def test_newsapi(self):
        """Test NewsAPI"""
        print("\n🔍 Testing NewsAPI...")
        if not self.news_api_key:
            print("❌ NewsAPI key not found")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'apiKey': self.news_api_key,
                    'country': 'us',
                    'pageSize': 5
                }
                response = await client.get('https://newsapi.org/v2/top-headlines', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok':
                        articles = data.get('articles', [])
                        print(f"✅ NewsAPI: SUCCESS - Retrieved {len(articles)} articles")
                        if articles:
                            print(f"   Sample: {articles[0].get('title', 'No title')[:50]}...")
                        return True
                    else:
                        print(f"❌ NewsAPI: API Error - {data.get('message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ NewsAPI: HTTP {response.status_code} - {response.text[:100]}")
                    return False
                    
        except Exception as e:
            print(f"❌ NewsAPI: Exception - {str(e)}")
            return False

    async def test_gnews(self):
        """Test GNews API"""
        print("\n🔍 Testing GNews...")
        if not self.gnews_api_key:
            print("❌ GNews key not found")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'apikey': self.gnews_api_key,
                    'country': 'us',
                    'max': 5,
                    'lang': 'en'
                }
                response = await client.get('https://gnews.io/api/v4/top-headlines', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    print(f"✅ GNews: SUCCESS - Retrieved {len(articles)} articles")
                    if articles:
                        print(f"   Sample: {articles[0].get('title', 'No title')[:50]}...")
                    return True
                else:
                    print(f"❌ GNews: HTTP {response.status_code} - {response.text[:100]}")
                    return False
                    
        except Exception as e:
            print(f"❌ GNews: Exception - {str(e)}")
            return False

    async def test_mediastack(self):
        """Test Mediastack API"""
        print("\n🔍 Testing Mediastack...")
        if not self.mediastack_key:
            print("❌ Mediastack key not found")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'access_key': self.mediastack_key,
                    'countries': 'us',
                    'limit': 5
                }
                response = await client.get('http://api.mediastack.com/v1/news', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    print(f"✅ Mediastack: SUCCESS - Retrieved {len(articles)} articles")
                    if articles:
                        print(f"   Sample: {articles[0].get('title', 'No title')[:50]}...")
                    return True
                else:
                    print(f"❌ Mediastack: HTTP {response.status_code} - {response.text[:100]}")
                    return False
                    
        except Exception as e:
            print(f"❌ Mediastack: Exception - {str(e)}")
            return False

    async def test_currents(self):
        """Test Currents API"""
        print("\n🔍 Testing Currents...")
        if not self.currents_api_key:
            print("❌ Currents key not found")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    'Authorization': self.currents_api_key
                }
                params = {
                    'country': 'us',
                    'page_size': 5
                }
                response = await client.get('https://api.currentsapi.services/v1/latest-news', 
                                          headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok':
                        articles = data.get('news', [])
                        print(f"✅ Currents: SUCCESS - Retrieved {len(articles)} articles")
                        if articles:
                            print(f"   Sample: {articles[0].get('title', 'No title')[:50]}...")
                        return True
                    else:
                        print(f"❌ Currents: API Error - {data.get('message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Currents: HTTP {response.status_code} - {response.text[:100]}")
                    return False
                    
        except Exception as e:
            print(f"❌ Currents: Exception - {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all API tests"""
        print(f"\n🚀 Starting API tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'newsapi': await self.test_newsapi(),
            'gnews': await self.test_gnews(),
            'mediastack': await self.test_mediastack(),
            'currents': await self.test_currents()
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        working_apis = []
        failed_apis = []
        
        for api_name, success in results.items():
            status = "✅ WORKING" if success else "❌ FAILED"
            print(f"{api_name.upper():<12}: {status}")
            if success:
                working_apis.append(api_name)
            else:
                failed_apis.append(api_name)
        
        print("=" * 60)
        print(f"✅ Working APIs: {len(working_apis)}/4 ({', '.join(working_apis) if working_apis else 'None'})")
        print(f"❌ Failed APIs: {len(failed_apis)}/4 ({', '.join(failed_apis) if failed_apis else 'None'})")
        
        if working_apis:
            print(f"\n🎉 SUCCESS: {len(working_apis)} API(s) are working and can retrieve news!")
        else:
            print(f"\n⚠️ WARNING: No APIs are working. Please check your API keys.")
        
        return results

if __name__ == "__main__":
    tester = APIKeyTester()
    asyncio.run(tester.run_all_tests())