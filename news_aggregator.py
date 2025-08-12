#!/usr/bin/env python3
"""
News Aggregator Script
Integrates 4 free news APIs: GNews, NewsAPI, Mediastack, and Currents API
Fetches news from multiple sources and highlights Indian news
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from collections import defaultdict

class NewsAggregator:
    def __init__(self):
        # API Keys
        self.gnews_api_key = "7a76b55cdf89577b0ababe91756acb67"
        self.newsapi_key = "5eaaaccf09ae4096b235a28fd7ff5367"
        self.mediastack_key = "f2b8d11753198f4cd7b985b7476757dc"
        self.currents_api_key = "WbFru5nT9aggF2qnjp90YNBSVy7HwXzjDxhzR44l2LSzewGW"
        
        # API Endpoints
        self.gnews_endpoint = "https://gnews.io/api/v4/top-headlines"
        self.newsapi_endpoint = "https://newsapi.org/v2/top-headlines"
        self.mediastack_endpoint = "http://api.mediastack.com/v1/news"
        self.currents_endpoint = "https://api.currentsapi.services/v1/latest-news"
        
        # Countries for Mediastack
        self.countries = ["us", "in", "gb", "ca", "au", "de", "fr", "jp", "br", "mx", "ru", "cn", "kr", "sg", "ae", "sa", "za", "ng", "ke", "eg"]
        
        self.all_news = []
        self.duplicate_titles = set()

    def fetch_gnews(self) -> List[Dict[str, Any]]:
        """Fetch news from GNews API"""
        news_items = []
        
        try:
            # Global news
            params = {
                'token': self.gnews_api_key,
                'lang': 'en',
                'max': 50
            }
            response = requests.get(self.gnews_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"GNews - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'gnews',
                        'is_indian': False
                    })
            
            # Indian news specifically
            params['country'] = 'in'
            response = requests.get(self.gnews_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"GNews India - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'gnews',
                        'is_indian': True
                    })
                    
        except Exception as e:
            print(f"Error fetching from GNews: {e}")
        
        return news_items

    def fetch_newsapi(self) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        news_items = []
        
        try:
            # Global news
            params = {
                'apiKey': self.newsapi_key,
                'language': 'en',
                'pageSize': 50
            }
            response = requests.get(self.newsapi_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'newsapi',
                        'is_indian': False
                    })
            
            # Indian news specifically
            params['country'] = 'in'
            response = requests.get(self.newsapi_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"NewsAPI India - {article.get('source', {}).get('name', 'Unknown')}",
                        'publishedAt': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'api_source': 'newsapi',
                        'is_indian': True
                    })
                    
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
        
        return news_items

    def fetch_mediastack(self) -> List[Dict[str, Any]]:
        """Fetch news from Mediastack API"""
        news_items = []
        
        try:
            # Global news with multiple countries
            countries_str = ','.join(self.countries)
            params = {
                'access_key': self.mediastack_key,
                'countries': countries_str,
                'languages': 'en',
                'limit': 50
            }
            response = requests.get(self.mediastack_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('data', []):
                    is_indian = article.get('country') == 'in' or 'india' in article.get('title', '').lower()
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"Mediastack - {article.get('source', 'Unknown')}",
                        'publishedAt': article.get('published_at', ''),
                        'url': article.get('url', ''),
                        'api_source': 'mediastack',
                        'is_indian': is_indian
                    })
            
            # Indian news with keywords
            params['keywords'] = 'india'
            response = requests.get(self.mediastack_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('data', []):
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"Mediastack India - {article.get('source', 'Unknown')}",
                        'publishedAt': article.get('published_at', ''),
                        'url': article.get('url', ''),
                        'api_source': 'mediastack',
                        'is_indian': True
                    })
                    
        except Exception as e:
            print(f"Error fetching from Mediastack: {e}")
        
        return news_items

    def fetch_currents(self) -> List[Dict[str, Any]]:
        """Fetch news from Currents API"""
        news_items = []
        
        try:
            params = {
                'apiKey': self.currents_api_key,
                'language': 'en',
                'limit': 50
            }
            response = requests.get(self.currents_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('news', []):
                    is_indian = article.get('country') == 'IN' or 'india' in article.get('title', '').lower()
                    news_items.append({
                        'title': article.get('title', ''),
                        'source': f"Currents - {article.get('domain', 'Unknown')}",
                        'publishedAt': article.get('published', ''),
                        'url': article.get('url', ''),
                        'api_source': 'currents',
                        'is_indian': is_indian
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

    def sort_by_date(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort news by publishedAt date (descending)"""
        def parse_date(date_str):
            try:
                # Handle different date formats
                for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                return datetime.now()
            except:
                return datetime.now()
        
        return sorted(news_list, key=lambda x: parse_date(x.get('publishedAt', '')), reverse=True)

    def aggregate_news(self) -> List[Dict[str, Any]]:
        """Aggregate news from all APIs"""
        print("🔄 Fetching news from all APIs...")
        
        # Fetch from all APIs
        gnews_news = self.fetch_gnews()
        print(f"✅ GNews: {len(gnews_news)} articles")
        
        newsapi_news = self.fetch_newsapi()
        print(f"✅ NewsAPI: {len(newsapi_news)} articles")
        
        mediastack_news = self.fetch_mediastack()
        print(f"✅ Mediastack: {len(mediastack_news)} articles")
        
        currents_news = self.fetch_currents()
        print(f"✅ Currents API: {len(currents_news)} articles")
        
        # Combine all news
        all_news = gnews_news + newsapi_news + mediastack_news + currents_news
        print(f"📊 Total articles fetched: {len(all_news)}")
        
        # Remove duplicates
        unique_news = self.remove_duplicates(all_news)
        print(f"🔄 After removing duplicates: {len(unique_news)} articles")
        
        # Sort by date
        sorted_news = self.sort_by_date(unique_news)
        
        return sorted_news

    def print_headlines(self, news_list: List[Dict[str, Any]]):
        """Print headlines grouped by source with Indian news highlighted"""
        print("\n" + "="*80)
        print("📰 NEWS HEADLINES BY SOURCE")
        print("="*80)
        
        # Group by API source
        grouped_news = defaultdict(list)
        for item in news_list:
            api_source = item.get('api_source', 'unknown')
            grouped_news[api_source].append(item)
        
        # Print each group
        for api_source, articles in grouped_news.items():
            print(f"\n🔸 {api_source.upper()} NEWS:")
            print("-" * 50)
            
            for i, article in enumerate(articles[:20], 1):  # Show top 20 per source
                title = article.get('title', '')
                is_indian = article.get('is_indian', False)
                
                if is_indian:
                    print(f"🇮🇳 {i:2d}. {title}")
                else:
                    print(f"   {i:2d}. {title}")
        
        # Summary
        indian_count = sum(1 for item in news_list if item.get('is_indian', False))
        total_count = len(news_list)
        
        print("\n" + "="*80)
        print(f"📈 SUMMARY:")
        print(f"   Total headlines: {total_count}")
        print(f"   Indian headlines: {indian_count} (🇮🇳)")
        print(f"   International headlines: {total_count - indian_count}")
        print("="*80)

def main():
    """Main function to run the news aggregator"""
    print("🚀 Starting News Aggregator...")
    print("Integrating: GNews, NewsAPI, Mediastack, and Currents API")
    
    aggregator = NewsAggregator()
    
    # Aggregate news
    news_list = aggregator.aggregate_news()
    
    # Print headlines
    aggregator.print_headlines(news_list)
    
    # Save to JSON file
    with open('aggregated_news.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 News data saved to 'aggregated_news.json'")
    print("✅ News aggregation completed!")

if __name__ == "__main__":
    main()
