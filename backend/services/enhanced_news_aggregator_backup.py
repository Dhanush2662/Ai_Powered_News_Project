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
from dotenv import load_dotenv  # Add this line

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
        
        # Enhanced RSS feeds for India and UK
        self.rss_feeds = {
            "in": [
                # Existing feeds
                {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV"},
                {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "source": "Times of India"},
                {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "source": "The Hindu"},
                {"name": "Indian Express", "url": "https://indianexpress.com/section/india/feed/", "source": "Indian Express"},
                {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms", "source": "Economic Times"},
                {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "source": "Hindustan Times"},
                
                # NEW MAJOR NEWS OUTLETS
                {"name": "India Today", "url": "https://www.indiatoday.in/rss/1206514", "source": "India Today"},
                {"name": "Firstpost", "url": "https://www.firstpost.com/rss/india.xml", "source": "Firstpost"},
                {"name": "Business Standard", "url": "https://www.business-standard.com/rss/home_page_top_stories.rss", "source": "Business Standard"},
                {"name": "National Herald", "url": "https://www.nationalheraldindia.com/rss.xml", "source": "National Herald"},
                {"name": "Zee Business", "url": "https://www.zeebiz.com/rss/india-news.xml", "source": "Zee Business"},
                
                # SPECIALIZED NEWS PLATFORMS
                {"name": "Scroll.in", "url": "https://scroll.in/feeds/all.rss", "source": "Scroll.in"},
                {"name": "ThePrint", "url": "https://theprint.in/feed/", "source": "ThePrint"},
                {"name": "The Quint", "url": "https://www.thequint.com/rss", "source": "The Quint"},
                {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml", "source": "Moneycontrol"},
                {"name": "ETTelecom", "url": "https://telecom.economictimes.indiatimes.com/rss/topstories", "source": "ETTelecom"},
                {"name": "Trak.in", "url": "https://trak.in/feed/", "source": "Trak.in"},
                {"name": "TechCircle", "url": "https://www.techcircle.in/rss", "source": "TechCircle"},
                {"name": "Inc42", "url": "https://inc42.com/feed/", "source": "Inc42"},
                {"name": "YourStory", "url": "https://yourstory.com/feed", "source": "YourStory"},
                
                # GOVERNMENT SOURCES
                {"name": "PIB India", "url": "https://pib.gov.in/rss/lreleng.xml", "source": "PIB India"},
                {"name": "StartupIndia", "url": "https://www.startupindia.gov.in/rss.xml", "source": "StartupIndia"},
                
                # TECHNOLOGY
                {"name": "Digital Inspiration", "url": "https://www.labnol.org/feed/", "source": "Digital Inspiration"},
                {"name": "Gadgets 360", "url": "https://gadgets.ndtv.com/rss/news", "source": "Gadgets 360"},
                {"name": "TechGYD", "url": "https://techgyd.com/feed/", "source": "TechGYD"},
                
                # FINANCIAL NEWS
                {"name": "Mint", "url": "https://www.livemint.com/rss/news", "source": "Mint"},
                {"name": "ET Now", "url": "https://www.etnow.in/rss", "source": "ET Now"},
                {"name": "NSE", "url": "https://www.nseindia.com/rss/press_releases.xml", "source": "NSE"},
                
                # SPORTS
                {"name": "NDTV Sports", "url": "https://sports.ndtv.com/rss/news", "source": "NDTV Sports"},
                {"name": "TOI Sports", "url": "https://timesofindia.indiatimes.com/rss/sports/rssfeedstopstories.cms", "source": "TOI Sports"},
                {"name": "Sportstar", "url": "https://sportstar.thehindu.com/rss/", "source": "Sportstar"},
                {"name": "myKhel", "url": "https://www.mykhel.com/rss/cricket/feed.xml", "source": "myKhel"}
            ],
            "gb": [
                {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "source": "BBC News"},
                {"name": "The Guardian", "url": "https://www.theguardian.com/uk/rss", "source": "The Guardian"},
                {"name": "Reuters UK", "url": "https://feeds.reuters.com/reuters/UKdomesticNews", "source": "Reuters UK"}
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

    async def fetch_prioritized_news(self, limit_per_country: int = 50) -> Dict[str, List[dict]]:
        """
        Fetch news with India prioritized first, followed by other countries with Indian populations
        """
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
        """Fetch news for a specific country from all available APIs"""
        all_articles = []
        
        # Create tasks for parallel execution
        tasks = []
        
        # NewsAPI
        if self.news_api_key:
            tasks.append(self.fetch_newsapi_by_country(country_code))
        
        # GNews
        if self.gnews_api_key:
            tasks.append(self.fetch_gnews_by_country(country_code))
        
        # Mediastack
        if self.mediastack_key:
            tasks.append(self.fetch_mediastack_by_country(country_code))
        
        # Currents API
        if self.currents_api_key:
            tasks.append(self.fetch_currents_by_country(country_code))
        
        # RSS feeds (for India and UK)
        if country_code in self.rss_feeds:
            tasks.append(self.fetch_rss_feeds(country_code))
        
        # Execute all tasks in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"❌ Task {i} failed: {result}")
                else:
                    all_articles.extend(result)
        
        except Exception as e:
            print(f"❌ Error in parallel execution: {e}")
        
        # Remove duplicates and sort
        unique_articles = self.remove_duplicates(all_articles)
        sorted_articles = sorted(unique_articles, key=lambda x: x.get("published_at", ""), reverse=True)
        
        return sorted_articles[:limit]

    async def fetch_newsapi_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from NewsAPI"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'apiKey': self.news_api_key,
                    'country': country_code,
                    'language': 'en',
                    'pageSize': 50
                }
                
                response = await client.get('https://newsapi.org/v2/top-headlines', params=params)
                
                # Check for API errors
                if response.status_code != 200:
                    print(f"❌ NewsAPI HTTP {response.status_code}: {response.text}")
                    return articles
                    
                data = response.json()
                
                # Check for API-specific errors
                if data.get('status') == 'error':
                    print(f"❌ NewsAPI Error: {data.get('message', 'Unknown error')}")
                    return articles
                
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
                
        except Exception as e:
            print(f"❌ NewsAPI failed for {country_code}: {e}")
            print(f"   API Key present: {bool(self.news_api_key)}")
        
        return articles

    async def fetch_gnews_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from GNews API"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'apikey': self.gnews_api_key,
                    'country': country_code,
                    'lang': 'en',
                    'max': 50
                }
                
                response = await client.get('https://gnews.io/api/v4/top-headlines', params=params)
                response.raise_for_status()
                
                data = response.json()
                for article in data.get('articles', []):
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
                
        except Exception as e:
            print(f"❌ GNews failed for {country_code}: {e}")
        
        return articles

    async def fetch_mediastack_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from Mediastack API"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'access_key': self.mediastack_key,
                    'countries': country_code,
                    'languages': 'en',
                    'limit': 50
                }
                
                response = await client.get('http://api.mediastack.com/v1/news', params=params)
                response.raise_for_status()
                
                data = response.json()
                for article in data.get('data', []):
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
                
        except Exception as e:
            print(f"❌ Mediastack failed for {country_code}: {e}")
        
        return articles

    async def fetch_currents_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from Currents API using keywords"""
        articles = []
        try:
            country_info = self.priority_countries.get(country_code, {})
            keywords = country_info.get("keywords", [country_code.upper()])
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for keyword in keywords[:3]:  # Use top 3 keywords
                    try:
                        params = {
                            'apiKey': self.currents_api_key,
                            'language': 'en',
                            'keywords': keyword,
                            'page_size': 20
                        }
                        
                        response = await client.get('https://api.currentsapi.services/v1/search', params=params)
                        response.raise_for_status()
                        
                        data = response.json()
                        for article in data.get('news', []):
                            articles.append({
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'url': article.get('url', ''),
                                'published_at': article.get('published', ''),
                                'source': f"Currents - {article.get('domain', 'Unknown')}",
                                'api_source': 'currents',
                                'image_url': article.get('image', ''),
                                'content': article.get('description', '')
                            })
                    except Exception as e:
                        print(f"❌ Currents keyword '{keyword}' failed: {e}")
                        continue
                        
                print(f"✅ Currents {country_code}: {len(articles)} articles")
                
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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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
            
            if not compatible_apis:
                return {
                    "success": False,
                    "error": f"No APIs support country code '{country_code}'. Please try a different country.",
                    "articles": []
                }
            
            # Fetch news
            articles = await self.fetch_country_news(country_code, limit)
            
            return {
                "success": True,
                "country_code": country_code,
                "country_name": self.priority_countries.get(country_code, {}).get("name", country_code.upper()),
                "compatible_apis": compatible_apis,
                "articles_count": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {e}")
            return {
                "success": False,
                "error": f"Internal error while fetching news for '{country_input}': {str(e)}",
                "articles": []
            }

    def _validate_api_keys(self):
        """Validate and log available API keys"""
        available_apis = []
        
        if self.news_api_key:
            available_apis.append('NewsAPI')
        if self.gnews_api_key:
            available_apis.append('GNews')
        if self.mediastack_key:
            available_apis.append('Mediastack')
        if self.currents_api_key:
            available_apis.append('Currents')
        
        if available_apis:
            logging.info(f"✅ Available APIs: {', '.join(available_apis)}")
        else:
            logging.warning("⚠️ No API keys found! News fetching will fail.")

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
        """
        Get merged news feed with India headlines first, followed by other countries
        """
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
            article["section"] = "Other Countries with Indian Presence"
            # Priority score based on country priority and recency
            try:
                date_score = datetime.fromisoformat(article.get("published_at", "").replace("Z", "+00:00")).timestamp()
            except:
                date_score = 0
            
            article["priority_score"] = (10 - article.get("priority", 5)) * 100 + date_score / 1000000
            merged_feed.append(article)
        
        # Sort by priority score (highest first)
        merged_feed.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return merged_feed[:limit]

    @cache(prefix="enhanced_news_feed", ttl=600)  # Cache for 10 minutes
    async def get_cached_prioritized_feed(self, limit: int = 100) -> List[dict]:
        """Get cached version of prioritized news feed"""
        return await self.get_merged_prioritized_feed(limit)

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns standardized country code or None if invalid
        """
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
        """
        Fetch country news with enhanced validation and error handling
        """
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