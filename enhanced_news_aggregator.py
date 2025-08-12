#!/usr/bin/env python3
"""
Enhanced News Aggregator - Focus on Indian News
Gets more Indian news from multiple sources and APIs
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from collections import defaultdict

class EnhancedNewsAggregator:
    def __init__(self):
        # API Keys
        self.gnews_api_key = "7a76b55cdf89577b0ababe91756acb67"
        self.newsapi_key = "5eaaaccf09ae4096b235a28fd7ff5367"
        self.mediastack_key = "f2b8d11753198f4cd7b985b7476757dc"
        self.currents_api_key = "WbFru5nT9aggF2qnjp90YNBSVy7HwXzjDxhzR44l2LSzewGW"
        
        # Indian News Sources
        self.indian_sources = [
            "timesofindia.indiatimes.com",
            "indianexpress.com", 
            "thehindu.com",
            "hindustantimes.com",
            "ndtv.com",
            "zeenews.india.com",
            "economictimes.indiatimes.com",
            "livemint.com",
            "business-standard.com",
            "moneycontrol.com",
            "firstpost.com",
            "news18.com",
            "cnbctv18.com",
            "financialexpress.com"
        ]
        
        # Indian Keywords for Better Coverage
        self.indian_keywords = [
            "India", "Indian", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
            "Modi", "BJP", "Congress", "Rahul Gandhi", "Amit Shah",
            "RBI", "Reserve Bank", "Sensex", "Nifty", "BSE", "NSE",
            "Indian economy", "Indian government", "Indian politics",
            "Indian cricket", "IPL", "BCCI", "Indian sports",
            "Indian technology", "Indian startups", "Indian business"
        ]

    def fetch_gnews_indian_news(self) -> List[Dict[str, Any]]:
        """Fetch Indian news from GNews with multiple approaches"""
        news_items = []
        
        try:
            # Approach 1: Country-specific Indian news
            params = {
                'token': self.gnews_api_key,
                'country': 'in',
                'lang': 'en',
                'max': 50
            }
            response = requests.get('https://gnews.io/api/v4/top-headlines', params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"GNews India - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'gnews',
                        'is_indian': True,
                        'priority': 'high'
                    })
            
            # Approach 2: Search for Indian keywords
            for keyword in self.indian_keywords[:5]:  # Use top 5 keywords
                params = {
                    'token': self.gnews_api_key,
                    'q': keyword,
                    'lang': 'en',
                    'max': 20
                }
                response = requests.get('https://gnews.io/api/v4/search', params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        news_items.append({
                            'title': article.get('title', ''),
                            'source': f"GNews Search - {article.get('source', {}).get('name', 'Unknown')}",
                            'publishedAt': article.get('publishedAt', ''),
                            'url': article.get('url', ''),
                            'api_source': 'gnews',
                            'is_indian': True,
                            'priority': 'medium'
                        })
                        
        except Exception as e:
            print(f"Error fetching from GNews: {e}")
        
        return news_items

    def fetch_newsapi_indian_news(self) -> List[Dict[str, Any]]:
        """Fetch Indian news from NewsAPI with multiple approaches"""
        news_items = []
        
        try:
            # Approach 1: Country-specific Indian news
            params = {
                'apiKey': self.newsapi_key,
                'country': 'in',
                'language': 'en',
                'pageSize': 50
            }
            response = requests.get('https://newsapi.org/v2/top-headlines', params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"NewsAPI India - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'newsapi',
                        'is_indian': True,
                        'priority': 'high'
                    })
            
            # Approach 2: Search for Indian topics
            indian_topics = ['India', 'Indian politics', 'Indian economy', 'Delhi', 'Mumbai']
            for topic in indian_topics:
                params = {
                    'apiKey': self.newsapi_key,
                    'q': topic,
                    'language': 'en',
                    'pageSize': 20
                }
                response = requests.get('https://newsapi.org/v2/everything', params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        news_items.append({
                            'title': article.get('title', ''),
                            'source': f"NewsAPI Search - {article.get('source', {}).get('name', 'Unknown')}",
                            'publishedAt': article.get('publishedAt', ''),
                            'url': article.get('url', ''),
                            'api_source': 'newsapi',
                            'is_indian': True,
                            'priority': 'medium'
                        })
                        
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
        
        return news_items

    def fetch_mediastack_indian_news(self) -> List[Dict[str, Any]]:
        """Fetch Indian news from Mediastack with enhanced Indian focus"""
        news_items = []
        
        try:
            # Approach 1: Indian country + keywords
            params = {
                'access_key': self.mediastack_key,
                'countries': 'in',
                'languages': 'en',
                'limit': 50
            }
            response = requests.get('http://api.mediastack.com/v1/news', params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('data', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"Mediastack India - {article.get('source', 'Unknown')}",
                        'publishedAt': article.get('published_at', ''),
                        'url': article.get('url', ''),
                        'api_source': 'mediastack',
                        'is_indian': True,
                        'priority': 'high'
                    })
            
            # Approach 2: Indian keywords
            for keyword in self.indian_keywords[:5]:
                params = {
                    'access_key': self.mediastack_key,
                    'keywords': keyword,
                    'languages': 'en',
                    'limit': 20
                }
                response = requests.get('http://api.mediastack.com/v1/news', params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('data', []):
                        news_items.append({
                            'title': article.get('title', ''),
                            'source': f"Mediastack Search - {article.get('source', 'Unknown')}",
                            'publishedAt': article.get('published_at', ''),
                            'url': article.get('url', ''),
                            'api_source': 'mediastack',
                            'is_indian': True,
                            'priority': 'medium'
                        })
                        
        except Exception as e:
            print(f"Error fetching from Mediastack: {e}")
        
        return news_items

    def fetch_currents_indian_news(self) -> List[Dict[str, Any]]:
        """Fetch Indian news from Currents API"""
        news_items = []
        
        try:
            # Approach 1: Global news filtered for Indian content
            params = {
                'apiKey': self.currents_api_key,
                'language': 'en',
                'limit': 100
            }
            response = requests.get('https://api.currentsapi.services/v1/latest-news', params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('news', []):
                    # Check if it's Indian news
                    is_indian = (
                        article.get('country') == 'IN' or 
                        'india' in article.get('title', '').lower() or
                        'indian' in article.get('title', '').lower() or
                        any(keyword.lower() in article.get('title', '').lower() for keyword in self.indian_keywords)
                    )
                    
                    if is_indian:
                        news_items.append({
                            'title': article.get('title', ''),
                            'source': f"Currents India - {article.get('domain', 'Unknown')}",
                            'publishedAt': article.get('published', ''),
                            'url': article.get('url', ''),
                            'api_source': 'currents',
                            'is_indian': True,
                            'priority': 'high'
                        })
                        
        except Exception as e:
            print(f"Error fetching from Currents API: {e}")
        
        return news_items

    def remove_duplicates(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news items based on title"""
        unique_news = []
        seen_titles = set()
        
        for item in news_list:
            title = item.get('title', '').strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)
        
        return unique_news

    def sort_by_priority_and_date(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort news by priority (Indian first) and date"""
        def parse_date(date_str):
            try:
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                return datetime.now()
            except:
                return datetime.now()
        
        # Sort by priority first (high > medium > low), then by date
        return sorted(news_list, 
                     key=lambda x: (x.get('priority', 'low') != 'high', 
                                  parse_date(x.get('publishedAt', ''))), 
                     reverse=True)

    def aggregate_indian_news(self) -> List[Dict[str, Any]]:
        """Aggregate Indian news from all APIs"""
        print("🔄 Fetching Indian news from all APIs...")
        
        # Fetch from all APIs
        gnews_news = self.fetch_gnews_indian_news()
        print(f"✅ GNews India: {len(gnews_news)} articles")
        
        newsapi_news = self.fetch_newsapi_indian_news()
        print(f"✅ NewsAPI India: {len(newsapi_news)} articles")
        
        mediastack_news = self.fetch_mediastack_indian_news()
        print(f"✅ Mediastack India: {len(mediastack_news)} articles")
        
        currents_news = self.fetch_currents_indian_news()
        print(f"✅ Currents India: {len(currents_news)} articles")
        
        # Combine all news
        all_news = gnews_news + newsapi_news + mediastack_news + currents_news
        print(f"📊 Total Indian articles fetched: {len(all_news)}")
        
        # Remove duplicates
        unique_news = self.remove_duplicates(all_news)
        print(f"🔄 After removing duplicates: {len(unique_news)} articles")
        
        # Sort by priority and date
        sorted_news = self.sort_by_priority_and_date(unique_news)
        
        return sorted_news

    def print_indian_headlines(self, news_list: List[Dict[str, Any]]):
        """Print Indian headlines grouped by source"""
        print("\n" + "="*80)
        print("🇮🇳 INDIAN NEWS HEADLINES BY SOURCE")
        print("="*80)
        
        # Group by API source
        grouped_news = defaultdict(list)
        for item in news_list:
            api_source = item.get('api_source', 'unknown')
            grouped_news[api_source].append(item)
        
        # Print each group
        for api_source, articles in grouped_news.items():
            print(f"\n🔸 {api_source.upper()} INDIAN NEWS:")
            print("-" * 50)
            
            for i, article in enumerate(articles[:15], 1):  # Show top 15 per source
                title = article.get('title', '')
                priority = article.get('priority', 'low')
                priority_icon = "🔥" if priority == 'high' else "⭐"
                
                print(f"{priority_icon} {i:2d}. {title}")
        
        # Summary
        high_priority = sum(1 for item in news_list if item.get('priority') == 'high')
        total_count = len(news_list)
        
        print("\n" + "="*80)
        print(f"📈 INDIAN NEWS SUMMARY:")
        print(f"   Total Indian headlines: {total_count}")
        print(f"   High priority headlines: {high_priority} (🔥)")
        print(f"   Medium priority headlines: {total_count - high_priority} (⭐)")
        print("="*80)

def main():
    """Main function to run the enhanced Indian news aggregator"""
    print("🚀 Starting Enhanced Indian News Aggregator...")
    print("Focusing on Indian news from multiple sources")
    
    aggregator = EnhancedNewsAggregator()
    
    # Aggregate Indian news
    news_list = aggregator.aggregate_indian_news()
    
    # Print headlines
    aggregator.print_indian_headlines(news_list)
    
    # Save to JSON file
    with open('indian_news.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Indian news data saved to 'indian_news.json'")
    print("✅ Enhanced Indian news aggregation completed!")

if __name__ == "__main__":
    main()
