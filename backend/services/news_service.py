import httpx
import os
import traceback
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Article, NewsSource
from datetime import datetime, timedelta
import json
import feedparser
from dateutil import parser
from utils.cache import cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_API_KEY")
        self.currents_api_key = os.getenv("CURRENTS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        
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
            "mediastack": ["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "er", "es", "et", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"],
            "currents": []  # Currents API uses keywords, not country codes
        }

        # Enhanced news sources with more Indian sources
        self.sources = {
            # Indian News Sources
            "ndtv": {"name": "NDTV", "bias_score": -2.5, "political_lean": "left", "country": "in"},
            "republic-tv": {"name": "Republic TV", "bias_score": 3.5, "political_lean": "right", "country": "in"},
            "the-hindu": {"name": "The Hindu", "bias_score": -1.0, "political_lean": "center", "country": "in"},
            "times-of-india": {"name": "Times of India", "bias_score": 0.5, "political_lean": "center", "country": "in"},
            "hindustan-times": {"name": "Hindustan Times", "bias_score": -0.5, "political_lean": "center", "country": "in"},
            "indian-express": {"name": "Indian Express", "bias_score": -1.5, "political_lean": "left", "country": "in"},
            "zeenews": {"name": "Zee News", "bias_score": 2.0, "political_lean": "right", "country": "in"},
            "economictimes": {"name": "Economic Times", "bias_score": 0.0, "political_lean": "center", "country": "in"},
            "livemint": {"name": "LiveMint", "bias_score": -0.5, "political_lean": "center", "country": "in"},
            "business-standard": {"name": "Business Standard", "bias_score": 0.0, "political_lean": "center", "country": "in"},
            "moneycontrol": {"name": "MoneyControl", "bias_score": 0.0, "political_lean": "center", "country": "in"},
            "firstpost": {"name": "Firstpost", "bias_score": 1.0, "political_lean": "right", "country": "in"},
            "news18": {"name": "News18", "bias_score": 1.5, "political_lean": "right", "country": "in"},
            "cnbctv18": {"name": "CNBC TV18", "bias_score": 0.0, "political_lean": "center", "country": "in"},
            "financialexpress": {"name": "Financial Express", "bias_score": 0.0, "political_lean": "center", "country": "in"},
            
            # International Sources
            "cnn": {"name": "CNN", "bias_score": -2.0, "political_lean": "left", "country": "us"},
            "fox-news": {"name": "Fox News", "bias_score": 4.0, "political_lean": "right", "country": "us"},
            "bbc-news": {"name": "BBC News", "bias_score": -0.5, "political_lean": "center", "country": "gb"},
            "reuters": {"name": "Reuters", "bias_score": 0.0, "political_lean": "center", "country": "gb"},
            "ap": {"name": "Associated Press", "bias_score": 0.0, "political_lean": "center", "country": "us"}
        }
        
        # Indian keywords for better coverage
        self.indian_keywords = [
            "India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
            "Modi", "BJP", "Congress", "Rahul Gandhi", "Amit Shah",
            "RBI", "Reserve Bank", "Sensex", "Nifty", "BSE", "NSE",
            "Indian economy", "Indian government", "Indian politics",
            "Indian cricket", "IPL", "BCCI", "Indian sports",
            "Indian technology", "Indian startups", "Indian business"
        ]
        
        # Country to keywords mapping
        self.country_keywords = {
            "in": ["India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"],
            "us": ["USA", "United States", "America", "American", "Washington", "New York", "Los Angeles"],
            "gb": ["UK", "United Kingdom", "Britain", "British", "London", "England"],
            "au": ["Australia", "Australian", "Sydney", "Melbourne", "Canberra"],
            "ca": ["Canada", "Canadian", "Toronto", "Vancouver", "Ottawa"],
            "de": ["Germany", "German", "Berlin", "Munich", "Frankfurt"],
            "fr": ["France", "French", "Paris", "Lyon", "Marseille"],
            "jp": ["Japan", "Japanese", "Tokyo", "Osaka", "Kyoto"]
        }
        
        # RSS feeds for India
        self.india_rss_feeds = [
            {
                "name": "NDTV",
                "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
                "source": "NDTV"
            },
            {
                "name": "Republic TV", 
                "url": "https://www.republicworld.com/rss/latest-news.xml",
                "source": "Republic TV"
            },
            {
                "name": "Times Now",
                "url": "https://www.timesnownews.com/rssfeeds/-2128936835.cms",
                "source": "Times Now"
            },
            {
                "name": "The Hindu",
                "url": "https://www.thehindu.com/news/national/feeder/default.rss",
                "source": "The Hindu"
            }
        ]

    @cache(prefix="news_api")
    async def fetch_news_from_api(self, source_id: str, category: str = "general") -> List[dict]:
        """Fetch news from NewsAPI for a specific source"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/everything"
                params = {
                    "sources": source_id,
                    "apiKey": self.news_api_key,
                    "pageSize": 20,
                    "sortBy": "publishedAt"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("articles", [])
                
        except Exception as e:
            print(f"Error fetching news from {source_id}: {str(e)}")
            return []

    @cache(prefix="gnews_api")
    async def fetch_indian_news_from_gnews(self) -> List[dict]:
        """Fetch Indian news from GNews API"""
        try:
            async with httpx.AsyncClient() as client:
                # Country-specific Indian news
                params = {
                    'token': self.gnews_api_key,
                    'country': 'in',
                    'lang': 'en',
                    'max': 50
                }
                response = await client.get('https://gnews.io/api/v4/top-headlines', params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = []
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'content': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source_name': f"GNews - {article.get('source', {}).get('name', 'Unknown')}",
                        'is_indian': True,
                        'api_source': 'gnews'
                    })
                return articles
                
        except Exception as e:
            print(f"Error fetching from GNews: {str(e)}")
            return []

    @cache(prefix="newsapi_indian")
    async def fetch_indian_news_from_newsapi(self) -> List[dict]:
        """Fetch Indian news from NewsAPI"""
        try:
            async with httpx.AsyncClient() as client:
                # Country-specific Indian news
                params = {
                    'apiKey': self.news_api_key,
                    'country': 'in',
                    'language': 'en',
                    'pageSize': 50
                }
                response = await client.get('https://newsapi.org/v2/top-headlines', params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = []
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'content': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source_name': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                        'is_indian': True,
                        'api_source': 'newsapi'
                    })
                return articles
                
        except Exception as e:
            print(f"Error fetching from NewsAPI: {str(e)}")
            return []

    @cache(prefix="mediastack_api")
    async def fetch_indian_news_from_mediastack(self) -> List[dict]:
        """Fetch Indian news from Mediastack API"""
        try:
            async with httpx.AsyncClient() as client:
                # Indian country + keywords
                params = {
                    'access_key': self.mediastack_key,
                    'countries': 'in',
                    'languages': 'en',
                    'limit': 50
                }
                response = await client.get('http://api.mediastack.com/v1/news', params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = []
                for article in data.get('data', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'content': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('published_at', ''),
                        'source_name': f"Mediastack - {article.get('source', 'Unknown')}",
                        'is_indian': True,
                        'api_source': 'mediastack'
                    })
                return articles
                
        except Exception as e:
            print(f"Error fetching from Mediastack: {str(e)}")
            return []

    @cache(prefix="currents_api")
    async def fetch_indian_news_from_currents(self) -> List[dict]:
        """Fetch Indian news from Currents API"""
        try:
            async with httpx.AsyncClient() as client:
                # Global news filtered for Indian content
                params = {
                    'apiKey': self.currents_api_key,
                    'language': 'en',
                    'limit': 100
                }
                response = await client.get('https://api.currentsapi.services/v1/latest-news', params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = []
                for article in data.get('news', []):
                    # Check if it's Indian news
                    is_indian = (
                        article.get('country') == 'IN' or 
                        'india' in article.get('title', '').lower() or
                        'indian' in article.get('title', '').lower() or
                        any(keyword.lower() in article.get('title', '').lower() for keyword in self.indian_keywords)
                    )
                    
                    if is_indian:
                        articles.append({
                            'title': article.get('title', ''),
                            'content': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('published', ''),
                            'source_name': f"Currents - {article.get('domain', 'Unknown')}",
                            'is_indian': True,
                            'api_source': 'currents'
                        })
                return articles
                
        except Exception as e:
            print(f"Error fetching from Currents API: {str(e)}")
            return []

    @cache(prefix="aggregated_news")
    async def get_enhanced_aggregated_news(
        self, 
        db: Session, 
        topic: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        focus_indian: bool = True
    ) -> List[dict]:
        """Get enhanced aggregated news with focus on Indian news"""
        try:
            all_articles = []
            
            # Fetch from all APIs
            if focus_indian:
                gnews_articles = await self.fetch_indian_news_from_gnews()
                newsapi_articles = await self.fetch_indian_news_from_newsapi()
                mediastack_articles = await self.fetch_indian_news_from_mediastack()
                currents_articles = await self.fetch_indian_news_from_currents()
                
                all_articles = gnews_articles + newsapi_articles + mediastack_articles + currents_articles
            else:
                # Get from database for non-Indian news
                query = db.query(Article).join(NewsSource)
                if topic:
                    query = query.filter(Article.topic.ilike(f"%{topic}%"))
                if source:
                    query = query.filter(NewsSource.name.ilike(f"%{source}%"))
                
                articles = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
                
                for article in articles:
                    all_articles.append({
                        "id": article.id,
                        "title": article.title,
                        "content": article.content,
                        "url": article.url,
                        "published_at": article.published_at,
                        "topic": article.topic,
                        "summary": article.summary,
                        "source_name": article.source.name,
                        "source_bias_score": article.source.bias_score,
                        "is_indian": article.source.country == "in"
                    })
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_articles = []
            for article in all_articles:
                title = article.get('title', '').strip().lower()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_articles.append(article)
            
            # Sort by date (newest first)
            unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            
            # Apply pagination
            return unique_articles[offset:offset + limit]
            
        except Exception as e:
            print(f"Error getting enhanced aggregated news: {str(e)}")
            return []
    
    async def update_news_sources(self, db: Session):
        """Update news sources in database"""
        try:
            for source_id, source_data in self.sources.items():
                # Check if source exists
                existing_source = db.query(NewsSource).filter(NewsSource.name == source_data["name"]).first()
                
                if not existing_source:
                    # Create new source
                    new_source = NewsSource(
                        name=source_data["name"],
                        url=f"https://{source_id}.com",
                        bias_score=source_data["bias_score"],
                        political_lean=source_data["political_lean"],
                        country=source_data["country"]
                    )
                    db.add(new_source)
                else:
                    # Update existing source
                    existing_source.bias_score = source_data["bias_score"]
                    existing_source.political_lean = source_data["political_lean"]
                
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error updating news sources: {str(e)}")
            db.rollback()
            return False
    
    async def fetch_and_store_articles(self, db: Session, source_id: str):
        """Fetch articles from API and store in database"""
        try:
            # Get source from database
            source = db.query(NewsSource).filter(NewsSource.name == self.sources[source_id]["name"]).first()
            if not source:
                print(f"Source {source_id} not found in database")
                return False
            
            # Fetch articles from API
            articles_data = await self.fetch_news_from_api(source_id)
            
            for article_data in articles_data:
                # Check if article already exists
                existing_article = db.query(Article).filter(
                    Article.url == article_data.get("url")
                ).first()
                
                if not existing_article:
                    # Create new article
                    new_article = Article(
                        title=article_data.get("title", ""),
                        content=article_data.get("content", ""),
                        url=article_data.get("url", ""),
                        published_at=datetime.fromisoformat(article_data.get("publishedAt", "").replace("Z", "+00:00")),
                        source_id=source.id,
                        topic=self._extract_topic(article_data.get("title", "")),
                        summary=article_data.get("description", "")
                    )
                    db.add(new_article)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error fetching and storing articles: {str(e)}")
            db.rollback()
            return False
    
    def _extract_topic(self, title: str) -> str:
        """Extract topic from article title"""
        # Simple topic extraction - can be enhanced with NLP
        common_topics = [
            "politics", "economy", "technology", "sports", "entertainment",
            "health", "education", "environment", "crime", "international"
        ]
        
        title_lower = title.lower()
        for topic in common_topics:
            if topic in title_lower:
                return topic
        
        return "general"
    
    async def get_trending_topics(self, db: Session) -> List[str]:
        """Get trending topics from recent articles"""
        try:
            from sqlalchemy import func
            
            # Get topics from recent articles
            recent_date = datetime.now() - timedelta(days=7)
            trending_topics = db.query(
                Article.topic,
                func.count(Article.id).label('count')
            ).filter(
                Article.published_at >= recent_date,
                Article.topic.isnot(None)
            ).group_by(Article.topic).order_by(func.count(Article.id).desc()).limit(10).all()
            
            return [topic for topic, count in trending_topics]
            
        except Exception as e:
            print(f"Error getting trending topics: {str(e)}")
            return []

    def validate_and_normalize_country_code(self, country_input: str) -> Optional[str]:
        """
        Validate and normalize country code input
        Returns normalized ISO country code or None if invalid
        """
        if not country_input:
            logger.warning("Empty country input provided")
            return None
        
        # Normalize input: lowercase and strip whitespace
        normalized_input = country_input.lower().strip()
        
        # Check if it's in our mapping
        if normalized_input in self.country_code_mapping:
            normalized_code = self.country_code_mapping[normalized_input]
            logger.info(f"Country code normalized: '{country_input}' -> '{normalized_code}'")
            return normalized_code
        
        logger.warning(f"Unsupported country: '{country_input}'. Supported countries: {list(set(self.country_code_mapping.values()))}")
        return None

    def get_compatible_apis_for_country(self, country_code: str) -> List[str]:
        """
        Get list of APIs that support the given country code
        """
        compatible_apis = []
        
        for api_name, supported_countries in self.api_compatibility.items():
            if country_code in supported_countries:
                compatible_apis.append(api_name)
        
        # Currents API uses keywords, so it's always available
        compatible_apis.append("currents")
        
        logger.info(f"Compatible APIs for {country_code}: {compatible_apis}")
        return compatible_apis

    async def fetch_news_by_country(self, country_input: str) -> List[dict]:
        """Fetch news for specific country with enhanced validation and error handling"""
        try:
            # Validate and normalize country code
            country_code = self.validate_and_normalize_country_code(country_input)
            
            if not country_code:
                logger.error(f"Invalid country code: {country_input}")
                return []
            
            # Get compatible APIs
            compatible_apis = self.get_compatible_apis_for_country(country_code)
            
            if not compatible_apis:
                logger.error(f"No APIs support country code: {country_code}")
                return []
            
            logger.info(f"Fetching news for {country_code} using APIs: {compatible_apis}")
            
            results = []

            # NEWS API
            if "newsapi" in compatible_apis and self.news_api_key:
                try:
                    newsapi_articles = await self.fetch_newsapi_by_country(country_code)
                    logger.info(f"✅ NewsAPI {country_code}: {len(newsapi_articles)} articles")
                    results.extend(newsapi_articles)
                except Exception as e:
                    logger.error(f"❌ NewsAPI failed for {country_code}: {e}")

            # GNEWS API
            if "gnews" in compatible_apis and self.gnews_api_key:
                try:
                    gnews_articles = await self.fetch_gnews_by_country(country_code)
                    logger.info(f"✅ GNews {country_code}: {len(gnews_articles)} articles")
                    results.extend(gnews_articles)
                except Exception as e:
                    logger.error(f"❌ GNews failed for {country_code}: {e}")

            # MEDIASTACK API
            if "mediastack" in compatible_apis and self.mediastack_key:
                try:
                    mediastack_articles = await self.fetch_mediastack_by_country(country_code)
                    logger.info(f"✅ Mediastack {country_code}: {len(mediastack_articles)} articles")
                    results.extend(mediastack_articles)
                except Exception as e:
                    logger.error(f"❌ Mediastack failed for {country_code}: {e}")

            # CURRENTS API (always available with keywords)
            if self.currents_api_key:
                try:
                    currents_articles = await self.fetch_currents_by_country(country_code)
                    logger.info(f"✅ Currents {country_code}: {len(currents_articles)} articles")
                    results.extend(currents_articles)
                except Exception as e:
                    logger.error(f"❌ Currents failed for {country_code}: {e}")

            # RSS feeds (only for India)
            if country_code.lower() == "in":
                try:
                    rss_articles = await self.fetch_india_rss_feeds()
                    logger.info(f"✅ RSS Feeds: {len(rss_articles)} articles")
                    results.extend(rss_articles)
                except Exception as e:
                    logger.error(f"❌ RSS failed: {e}")

            # Remove duplicates by title
            seen_titles = set()
            unique_results = []
            for article in results:
                title = article.get("title", "").strip().lower()
                if title and title not in seen_titles:
                    unique_results.append(article)
                    seen_titles.add(title)

            # Sort by published date (descending)
            unique_results.sort(key=lambda x: x.get("published_at", ""), reverse=True)

            logger.info(f"🔄 Final results for {country_code}: {len(unique_results)} unique articles")
            return unique_results[:100]  # Limit to 100 articles
            
        except Exception as e:
            logger.error(f"Error fetching country news for '{country_input}': {str(e)}")
            logger.error(traceback.format_exc())
            return []

    async def fetch_gnews_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from GNews API for specific country"""
        articles = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Country-specific news
                params = {
                    'token': self.gnews_api_key,
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
                        'api_source': 'gnews'
                    })
                    
        except Exception as e:
            print(f"Error fetching from GNews for {country_code}: {str(e)}")
        
        return articles

    async def fetch_newsapi_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from NewsAPI for specific country"""
        articles = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Country-specific news
                params = {
                    'apiKey': self.news_api_key,
                    'country': country_code,
                    'language': 'en',
                    'pageSize': 50
                }
                response = await client.get('https://newsapi.org/v2/top-headlines', params=params)
                response.raise_for_status()
                
                data = response.json()
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                        'api_source': 'newsapi'
                    })
                    
        except Exception as e:
            print(f"Error fetching from NewsAPI for {country_code}: {str(e)}")
        
        return articles

    async def fetch_mediastack_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from Mediastack API for specific country"""
        articles = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Country-specific news
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
                        'api_source': 'mediastack'
                    })
                    
        except Exception as e:
            print(f"Error fetching from Mediastack for {country_code}: {str(e)}")
        
        return articles

    async def fetch_currents_by_country(self, country_code: str) -> List[dict]:
        """Fetch news from Currents API using country keywords"""
        articles = []
        
        try:
            # Special handling for India - use keywords instead of country
            if country_code.lower() == "in":
                keywords = ["India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]
            else:
                # Get keywords for other countries
                keywords = self.country_keywords.get(country_code, [country_code.upper()])
            
            async with httpx.AsyncClient() as client:
                for keyword in keywords[:3]:  # Use top 3 keywords
                    params = {
                        'apiKey': self.currents_api_key,
                        'language': 'en',
                        'keywords': keyword,
                        'page_size': 20
                    }
                    # Use the search endpoint instead of latest-news
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
                            'api_source': 'currents'
                        })
                        
        except Exception as e:
            print(f"Error fetching from Currents API for {country_code}: {str(e)}")
            traceback.print_exc()
        
        return articles

    async def fetch_india_rss_feeds(self) -> List[dict]:
        """Fetch news from Indian RSS feeds"""
        articles = []
        
        try:
            for feed in self.india_rss_feeds:
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
                            'api_source': 'rss'
                        })
                        
                except Exception as e:
                    print(f"❌ Error fetching RSS feed {feed['name']}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching RSS feeds: {str(e)}")
        
        return articles

    def remove_duplicates_by_url(self, articles: List[dict]) -> List[dict]:
        """Remove duplicate articles based on URL"""
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            url = article.get('url', '').strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
