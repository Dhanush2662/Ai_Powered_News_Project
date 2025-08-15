import httpx
import os
import traceback
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import feedparser
from dateutil import parser
from utils.cache import cache
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNewsAggregator:
    def __init__(self):
        # Load environment variables first
        load_dotenv()
        
        # Initialize API keys
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        self.mediastack_key = os.getenv('MEDIASTACK_API_KEY')
        self.currents_api_key = os.getenv('CURRENTS_API_KEY')
        
        # Validate API keys
        self._validate_api_keys()
        
        # Country code mapping for validation and normalization
        self.country_code_mapping = {
            # Standard ISO codes
            "in": "in", "india": "in", "ind": "in",
            "us": "us", "usa": "us", "united states": "us", "america": "us",
            "gb": "gb", "uk": "gb", "united kingdom": "gb", "britain": "gb",
            "ca": "ca", "canada": "ca",
            "au": "au", "australia": "au",
            "ae": "ae", "uae": "ae", "united arab emirates": "ae",
            "sg": "sg", "singapore": "sg",
            "de": "de", "germany": "de", "deutschland": "de",
            "fr": "fr", "france": "fr",
            "jp": "jp", "japan": "jp",
            "cn": "cn", "china": "cn",
            "br": "br", "brazil": "br",
            "mx": "mx", "mexico": "mx",
            "it": "it", "italy": "it",
            "es": "es", "spain": "es",
            "ru": "ru", "russia": "ru",
            "kr": "kr", "south korea": "kr",
            "za": "za", "south africa": "za",
            "ng": "ng", "nigeria": "ng",
            "eg": "eg", "egypt": "eg",
            "ar": "ar", "argentina": "ar",
            "cl": "cl", "chile": "cl",
            "co": "co", "colombia": "co",
            "pe": "pe", "peru": "pe",
            "th": "th", "thailand": "th",
            "id": "id", "indonesia": "id",
            "my": "my", "malaysia": "my",
            "ph": "ph", "philippines": "ph",
            "vn": "vn", "vietnam": "vn",
            "bd": "bd", "bangladesh": "bd",
            "pk": "pk", "pakistan": "pk",
            "lk": "lk", "sri lanka": "lk",
            "np": "np", "nepal": "np",
            "mm": "mm", "myanmar": "mm"
        }
        
        # API compatibility matrix
        self.api_compatibility = {
            "newsapi": ["ae", "ar", "at", "au", "be", "bg", "br", "ca", "ch", "cn", "co", "cu", "cz", "de", "eg", "fr", "gb", "gr", "hk", "hu", "id", "ie", "il", "in", "it", "jp", "kr", "lt", "lv", "ma", "mx", "my", "ng", "nl", "no", "nz", "ph", "pl", "pt", "ro", "rs", "ru", "sa", "se", "sg", "si", "sk", "th", "tr", "tw", "ua", "us", "ve", "za"],
            "gnews": ["au", "br", "ca", "cn", "eg", "fr", "de", "gr", "hk", "in", "ie", "il", "it", "jp", "nl", "no", "pk", "pe", "ph", "pt", "ro", "ru", "sg", "es", "se", "ch", "tw", "ua", "gb", "us"],
            "mediastack": ["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "er", "es", "et", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"]
        }
        
        # Priority countries with Indian populations
        self.priority_countries = {
            "in": {"name": "India", "priority": 1, "keywords": ["India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Modi", "BJP", "Congress"]},
            "us": {"name": "USA", "priority": 2, "keywords": ["USA", "United States", "America", "American", "Indian American", "H1B", "Silicon Valley"]},
            "ae": {"name": "UAE", "priority": 3, "keywords": ["UAE", "Dubai", "Abu Dhabi", "Emirates", "Indian expat", "NRI"]},
            "gb": {"name": "UK", "priority": 4, "keywords": ["UK", "United Kingdom", "Britain", "British", "London", "Indian British"]},
            "ca": {"name": "Canada", "priority": 5, "keywords": ["Canada", "Canadian", "Toronto", "Vancouver", "Indian Canadian"]},
            "au": {"name": "Australia", "priority": 6, "keywords": ["Australia", "Australian", "Sydney", "Melbourne", "Indian Australian"]},
            "sg": {"name": "Singapore", "priority": 7, "keywords": ["Singapore", "Singaporean", "Indian Singaporean"]}
        }
        
        # Enhanced RSS feeds for India and International
        self.rss_feeds = {
            "in": [
                # National feeds
                {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV"},
                {"name": "Republic World", "url": "https://www.republicworld.com/rss/latest-news.xml", "source": "Republic World"},
                {"name": "Times Now", "url": "https://www.timesnownews.com/rssfeeds/-2128936835.cms", "source": "Times Now"},
                {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "source": "The Hindu"},
                {"name": "Inshorts", "url": "https://inshorts.deta.dev/news", "source": "Inshorts"},
                {"name": "News18", "url": "https://www.news18.com/rss/", "source": "News18"},
                {"name": "Business Standard", "url": "https://www.business-standard.com/rss", "source": "Business Standard"},
                {"name": "Firstpost", "url": "https://www.firstpost.com/rss/", "source": "Firstpost"},
                {"name": "India Today", "url": "https://indiatoday.in/rss/1206578", "source": "India Today"},
                {"name": "Indian Express", "url": "https://indianexpress.com/feed", "source": "Indian Express"},
                {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms", "source": "Economic Times"},
                {"name": "Live Mint", "url": "https://www.livemint.com/rss/news", "source": "Live Mint"},
                {"name": "Zee News", "url": "http://zeenews.india.com/rss/india-national-news.xml", "source": "Zee News"},
                {"name": "National Herald", "url": "https://www.nationalheraldindia.com/rss", "source": "National Herald"},
                {"name": "Daily Excelsior", "url": "https://dailyexcelsior.com/feed", "source": "Daily Excelsior"},
                {"name": "Telangana Today", "url": "https://telanganatoday.com/feed", "source": "Telangana Today"},
                {"name": "Odisha Barta", "url": "https://odishabarta.com/feed", "source": "Odisha Barta"},
                {"name": "Times of Bengal", "url": "https://thetimesofbengal.com/feed", "source": "Times of Bengal"},
                {"name": "ABCR News", "url": "https://abcrnews.com/feed", "source": "ABCR News"},
                {"name": "Headlines of Today", "url": "https://headlinesoftoday.com/feed", "source": "Headlines of Today"},
                {"name": "CrowdWisdom360", "url": "https://crowdwisdom.live/feed", "source": "CrowdWisdom360"},
                {"name": "News Today Net", "url": "https://newstodaynet.com/feed", "source": "News Today Net"},
                
                # Major additional national feeds
                {"name": "Hindustan Times Top", "url": "https://www.hindustantimes.com/feeds/rss/top-news/rssfeed.xml", "source": "Hindustan Times"},
                {"name": "Hindustan Times Latest", "url": "https://www.hindustantimes.com/feeds/rss/latest/rssfeed.xml", "source": "Hindustan Times"},
                {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rss.cms", "source": "Times of India"},
                
                # Regional/city feeds
                {"name": "Agra News", "url": "https://agranews.com/feed", "source": "Agra News"},
                {"name": "North Lines", "url": "https://thenorthlines.com/feed", "source": "North Lines"},
                {"name": "Chandigarh City News", "url": "https://feeds.feedburner.com/ChandigarhCityNews", "source": "Chandigarh City News"},
                {"name": "Chandigarh Metro", "url": "https://chandigarhmetro.com/feed", "source": "Chandigarh Metro"},
                {"name": "ABC Live", "url": "https://cms.abclive.in/home/rss/1/30", "source": "ABC Live"},
                {"name": "QT Images", "url": "https://prod-qt-images.s3.amazonaws.com/feed.xml", "source": "QT Images"},
                {"name": "India's News", "url": "https://feeds.indiasnews.net/rss/701", "source": "India's News"},
                {"name": "Yo Vizag", "url": "https://yovizag.com/feed", "source": "Yo Vizag"},
                {"name": "Kashmir News", "url": "https://kashmirnews.in/feed", "source": "Kashmir News"},
                {"name": "Star of Mysore", "url": "https://starofmysore.com/feed", "source": "Star of Mysore"},
                {"name": "Assam Tribune", "url": "https://assamtribune.com/feed", "source": "Assam Tribune"},
                {"name": "Daily Times India", "url": "https://dailytimesindia.com/feed", "source": "Daily Times India"},
                {"name": "Live Nagpur", "url": "https://thelivenagpur.com/feed", "source": "Live Nagpur"},
                {"name": "Andhra Wishesh", "url": "https://andhrawishesh.com/feed", "source": "Andhra Wishesh"},
                {"name": "Sangai Express", "url": "https://thesangaiexpress.com/feed", "source": "Sangai Express"}
            ],
            "international": [
                # International RSS Feeds
                {"name": "BBC World News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC"},
                {"name": "CNN Top Stories", "url": "http://rss.cnn.com/rss/edition.rss", "source": "CNN"},
                {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "source": "Al Jazeera"},
                {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews", "source": "Reuters"},
                {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss", "source": "The Guardian"},
                {"name": "NASA Breaking News", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "source": "NASA"},
                {"name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "source": "New York Times"},
                {"name": "France24", "url": "https://www.france24.com/en/rss", "source": "France24"},
                {"name": "Deutsche Welle", "url": "http://rss.dw.com/rdf/rss-en-al", "source": "Deutsche Welle"}
            ]
        }
        
        # Indian-specific news sources and keywords
        self.indian_keywords = [
            "India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad",
            "Modi", "BJP", "Congress", "Rahul Gandhi", "Amit Shah", "Parliament", "Lok Sabha", "Rajya Sabha",
            "RBI", "Reserve Bank", "Sensex", "Nifty", "BSE", "NSE", "Rupee", "Indian economy",
            "IPL", "BCCI", "Indian cricket", "Bollywood", "Indian cinema",
            "IIT", "IIM", "ISRO", "Indian Space", "Make in India", "Digital India",
            "Kashmir", "Punjab", "Tamil Nadu", "Kerala", "West Bengal", "Maharashtra", "Gujarat"
        ]

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append("NewsAPI")
        if self.gnews_api_key:
            available_apis.append("GNews")
        if self.mediastack_key:
            available_apis.append("Mediastack")
        if self.currents_api_key:
            available_apis.append("Currents")
        
        if available_apis:
            print(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            print("⚠️ Warning: No API keys found. Only RSS feeds will be available.")
        
        return len(available_apis) > 0

    async def fetch_prioritized_news(self, limit_per_country: int = 50) -> Dict[str, List[dict]]:
        """Fetch news with India prioritized first, followed by other countries with Indian populations"""
        results = {
            "india_headlines": [],
            "other_countries": []
        }
        
        print("🚀 Starting Enhanced News Aggregation...")
        
        # Fetch India news first (highest priority)
        print("\n📍 Fetching India Headlines...")
        india_news = await self.fetch_country_news("in", limit_per_country)
        results["india_headlines"] = india_news
        print(f"✅ India: {len(india_news)} articles collected")
        
        # Fetch news from other priority countries
        print("\n🌍 Fetching News from Countries with Indian Populations...")
        other_countries_news = []
        
        for country_code, country_info in self.priority_countries.items():
            if country_code != "in":  # Skip India as it's already processed
                print(f"\n📍 Fetching {country_info['name']} news...")
                country_news = await self.fetch_country_news(country_code, limit_per_country // 2)
                
                # Add country metadata to each article
                for article in country_news:
                    article["country"] = country_code
                    article["country_name"] = country_info["name"]
                    article["priority"] = country_info["priority"]
                
                other_countries_news.extend(country_news)
                print(f"✅ {country_info['name']}: {len(country_news)} articles")
        
        # Sort other countries news by priority and date
        other_countries_news.sort(key=lambda x: (x.get("priority", 999), x.get("published_at", "")), reverse=True)
        results["other_countries"] = other_countries_news
        
        print(f"\n🎯 Final Results:")
        print(f"   India Headlines: {len(results['india_headlines'])} articles")
        print(f"   Other Countries: {len(results['other_countries'])} articles")
        print(f"   Total: {len(results['india_headlines']) + len(results['other_countries'])} articles")
        
        return results

    async def fetch_country_news(self, country_code: str, limit: int = 50) -> List[dict]:
        """Fetch news for a specific country using multiple APIs and RSS feeds"""
        all_articles = []
        
        # Fetch from RSS feeds first (most reliable)
        rss_articles = await self.fetch_rss_feeds(country_code)
        all_articles.extend(rss_articles)
        
        # Fetch from APIs if available
        if self.news_api_key:
            newsapi_articles = await self.fetch_newsapi(country_code)
            all_articles.extend(newsapi_articles)
        
        if self.gnews_api_key:
            gnews_articles = await self.fetch_gnews(country_code)
            all_articles.extend(gnews_articles)
        
        if self.mediastack_key:
            mediastack_articles = await self.fetch_mediastack(country_code)
            all_articles.extend(mediastack_articles)
        
        if self.currents_api_key:
            currents_articles = await self.fetch_currents(country_code)
            all_articles.extend(currents_articles)
        
        # Remove duplicates and filter
        unique_articles = self.remove_duplicates(all_articles)
        
        # Sort by published date (newest first)
        unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return unique_articles[:limit]

    async def fetch_newsapi(self, country_code: str) -> List[dict]:
        """Fetch news from NewsAPI"""
        articles = []
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?country={country_code}&apiKey={self.news_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                
                if data.get('status') == 'ok':
                    for article in data.get('articles', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', ''),
                            'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                            'api_source': 'newsapi',
                            'image_url': article.get('urlToImage', ''),
                            'content': article.get('content', '')
                        })
                    
                    print(f"✅ NewsAPI {country_code}: {len(articles)} articles")
                else:
                    print(f"❌ NewsAPI failed for {country_code}: {data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ NewsAPI failed for {country_code}: {e}")
        
        return articles

    async def fetch_gnews(self, country_code: str) -> List[dict]:
        """Fetch news from GNews API"""
        articles = []
        
        try:
            url = f"https://gnews.io/api/v4/top-headlines?country={country_code}&token={self.gnews_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                
                if 'articles' in data:
                    for article in data['articles']:
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', ''),
                            'source': f"GNews - {article.get('source', {}).get('name', 'Unknown')}",
                            'api_source': 'gnews',
                            'image_url': article.get('image', ''),
                            'content': article.get('content', '')
                        })
                    
                    print(f"✅ GNews {country_code}: {len(articles)} articles")
                else:
                    print(f"❌ GNews failed for {country_code}: {data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ GNews failed for {country_code}: {e}")
        
        return articles

    async def fetch_mediastack(self, country_code: str) -> List[dict]:
        """Fetch news from Mediastack API"""
        articles = []
        
        try:
            url = f"http://api.mediastack.com/v1/news?access_key={self.mediastack_key}&countries={country_code}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                
                if 'data' in data:
                    for article in data['data']:
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', ''),
                            'source': f"Mediastack - {article.get('source', 'Unknown')}",
                            'api_source': 'mediastack',
                            'image_url': article.get('image', ''),
                            'content': article.get('description', '')
                        })
                    
                    print(f"✅ Mediastack {country_code}: {len(articles)} articles")
                else:
                    print(f"❌ Mediastack failed for {country_code}: {data.get('error', {}).get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Mediastack failed for {country_code}: {e}")
        
        return articles

    async def fetch_currents(self, country_code: str) -> List[dict]:
        """Fetch news from Currents API"""
        articles = []
        
        try:
            url = f"https://api.currentsapi.services/v1/latest-news?country={country_code}&apiKey={self.currents_api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()
                
                if data.get('status') == 'ok':
                    for article in data.get('news', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('published', ''),
                            'source': f"Currents - {article.get('author', 'Unknown')}",
                            'api_source': 'currents',
                            'image_url': article.get('image', ''),
                            'content': article.get('description', '')
                        })
                    
                    print(f"✅ Currents {country_code}: {len(articles)} articles")
                else:
                    print(f"❌ Currents failed for {country_code}: {data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Currents failed for {country_code}: {e}")
        
        return articles

    async def fetch_rss_feeds(self, country_code: str) -> List[dict]:
        """Fetch news from RSS feeds"""
        articles = []
        feeds = self.rss_feeds.get(country_code, [])
        
        try:
            for feed in feeds:
                try:
                    # Parse RSS feed
                    feed_data = feedparser.parse(feed['url'])
                    
                    for entry in feed_data.entries[:10]:  # Get top 10 from each feed
                        # Parse date
                        published_at = ""
                        try:
                            if hasattr(entry, 'published'):
                                published_at = parser.parse(entry.published).isoformat()
                            elif hasattr(entry, 'updated'):
                                published_at = parser.parse(entry.updated).isoformat()
                            else:
                                published_at = datetime.now().isoformat()
                        except:
                            published_at = datetime.now().isoformat()
                        
                        articles.append({
                            'title': entry.title,
                            'description': getattr(entry, 'summary', ''),
                            'url': entry.link,
                            'published_at': published_at,
                            'source': f"RSS - {feed['source']}",
                            'api_source': 'rss',
                            'image_url': '',
                            'content': getattr(entry, 'summary', '')
                        })
                        
                except Exception as e:
                    print(f"❌ RSS feed {feed['name']} failed: {e}")
                    continue
                    
            print(f"✅ RSS {country_code}: {len(articles)} articles")
                    
        except Exception as e:
            print(f"❌ RSS feeds failed for {country_code}: {e}")
        
        return articles

    def remove_duplicates(self, articles: List[dict]) -> List[dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').strip().lower()
            # Create a simplified title for comparison
            simplified_title = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()
            
            if simplified_title and simplified_title not in seen_titles:
                seen_titles.add(simplified_title)
                unique_articles.append(article)
        
        return unique_articles

    def filter_indian_relevant_news(self, articles: List[dict]) -> List[dict]:
        """Filter articles that are relevant to Indian interests"""
        relevant_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # Check if article contains Indian keywords
            is_relevant = any(keyword.lower() in content for keyword in self.indian_keywords)
            
            if is_relevant:
                article['indian_relevance'] = True
                relevant_articles.append(article)
        
        return relevant_articles

    async def get_merged_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get merged news feed with India headlines first, followed by other countries"""
        prioritized_news = await self.fetch_prioritized_news()
        
        # Merge India headlines and other countries news
        merged_feed = []
        
        # Add India headlines first
        india_headlines = prioritized_news["india_headlines"]
        for article in india_headlines:
            article["section"] = "India Headlines"
            article["priority_score"] = 1000  # Highest priority
            merged_feed.append(article)
        
        # Add other countries news
        other_countries = prioritized_news["other_countries"]
        for article in other_countries:
            article["section"] = f"{article.get('country_name', 'International')} News"
            article["priority_score"] = 500 + (10 - article.get('priority', 10))  # Lower priority
            merged_feed.append(article)
        
        # Sort by priority score and date
        merged_feed.sort(key=lambda x: (x.get("priority_score", 0), x.get("published_at", "")), reverse=True)
        
        return merged_feed[:limit]

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """Validate and normalize country code input. Returns standardized country code or None if invalid"""
        if not country_input:
            return None
            
        # Normalize input
        normalized_input = country_input.lower().strip()
        
        # Check if it's in our mapping
        if normalized_input in self.country_code_mapping:
            return self.country_code_mapping[normalized_input]
        
        # If not found, return None
        return None

    async def fetch_country_news_with_validation(self, country_input: str, limit: int = 50) -> Dict[str, any]:
        """Fetch country news with enhanced validation and error handling"""
        try:
            # Validate and normalize country code
            country_code = self.validate_and_normalize_country_code(country_input)
            
            if not country_code:
                return {
                    "success": False,
                    "error": f"Invalid country code: '{country_input}'. Supported countries: {list(self.country_code_mapping.keys())[:10]}...",
                    "articles": []
                }
            
            # Check API compatibility
            compatible_apis = []
            for api_name, supported_countries in self.api_compatibility.items():
                if country_code in supported_countries:
                    compatible_apis.append(api_name)
            
            if not compatible_apis and country_code not in self.rss_feeds:
                return {
                    "success": False,
                    "error": f"No news sources available for country: {country_code}",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "articles": articles,
                "total_articles": len(articles),
                "compatible_apis": compatible_apis
            }
            
        except Exception as e:
            logger.error(f"Error fetching news for {country_input}: {str(e)}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "articles": []
            }