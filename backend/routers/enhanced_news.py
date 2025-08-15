from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from services.enhanced_news_aggregator import EnhancedNewsAggregator
import traceback

router = APIRouter()
news_aggregator = EnhancedNewsAggregator()

@router.get("/prioritized-feed")
async def get_prioritized_news_feed(
    limit: int = Query(100, description="Maximum number of articles to return"),
    use_cache: bool = Query(True, description="Whether to use cached results")
):
    """
    Get prioritized news feed with India headlines first, followed by other countries with Indian populations
    """
    try:
        if use_cache:
            articles = await news_aggregator.get_cached_prioritized_feed(limit)
        else:
            articles = await news_aggregator.get_merged_prioritized_feed(limit)
        
        return {
            "status": "success",
            "total_articles": len(articles),
            "articles": articles,
            "sections": {
                "india_headlines": len([a for a in articles if a.get("section") == "India Headlines"]),
                "other_countries": len([a for a in articles if a.get("section") == "Other Countries with Indian Presence"])
            }
        }
    except Exception as e:
        print(f"❌ Error in prioritized feed: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch prioritized news: {str(e)}")

@router.get("/india-headlines")
async def get_india_headlines(
    limit: int = Query(50, description="Maximum number of articles to return")
):
    """
    Get India-focused headlines only
    """
    try:
        india_news = await news_aggregator.fetch_country_news("in", limit)
        
        return {
            "status": "success",
            "country": "India",
            "total_articles": len(india_news),
            "articles": india_news
        }
    except Exception as e:
        print(f"❌ Error fetching India headlines: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch India headlines: {str(e)}")

@router.get("/countries-with-indian-presence")
async def get_countries_with_indian_presence(
    limit_per_country: int = Query(25, description="Maximum articles per country"),
    countries: Optional[str] = Query(None, description="Comma-separated country codes (us,ae,gb,ca,au,sg)")
):
    """
    Get news from countries with significant Indian populations
    """
    try:
        # Default countries or parse from query
        if countries:
            country_codes = [c.strip().lower() for c in countries.split(",")]
        else:
            country_codes = ["us", "ae", "gb", "ca", "au", "sg"]
        
        all_articles = []
        country_results = {}
        
        for country_code in country_codes:
            if country_code in news_aggregator.priority_countries:
                country_news = await news_aggregator.fetch_country_news(country_code, limit_per_country)
                country_info = news_aggregator.priority_countries[country_code]
                
                # Add metadata to articles
                for article in country_news:
                    article["country"] = country_code
                    article["country_name"] = country_info["name"]
                    article["priority"] = country_info["priority"]
                
                all_articles.extend(country_news)
                country_results[country_code] = {
                    "name": country_info["name"],
                    "articles_count": len(country_news)
                }
        
        # Sort by priority and date
        all_articles.sort(key=lambda x: (x.get("priority", 999), x.get("published_at", "")), reverse=True)
        
        return {
            "status": "success",
            "total_articles": len(all_articles),
            "countries": country_results,
            "articles": all_articles
        }
    except Exception as e:
        print(f"❌ Error fetching countries with Indian presence: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch news from countries: {str(e)}")

# Remove this entire endpoint (lines 107-129):
# @router.get("/country/{country_code}")
# async def get_country_news(...):
#     ...

# Keep only these 5 core endpoints:
# 1. /prioritized-feed (News Aggregation with Indian prioritization)
# 2. /india-headlines (Basic news aggregation)
# 3. /countries-with-indian-presence (Consensus Score - basic)
# 4. /api-status (System status)
# 5. /test-aggregation (Trending News)

# Remove the /country/{country_code} endpoint completely
# Remove the /rss-feeds/{country_code} endpoint
# Remove the /debug/{country_code} endpoint

# Keep only these core endpoints:
# 1. /prioritized-feed (News Aggregation with Indian prioritization)
# 2. /india-headlines (Basic news aggregation)
# 3. /countries-with-indian-presence (Basic consensus via country coverage)
# 4. /api-status (System status)
# 5. /test-aggregation (Testing)

@router.get("/rss-feeds/{country_code}")
async def get_rss_feeds(
    country_code: str
):
    """
    Get RSS feeds for a specific country (India and UK supported)
    """
    try:
        country_code = country_code.lower()
        
        if country_code not in news_aggregator.rss_feeds:
            raise HTTPException(status_code=400, detail=f"RSS feeds not available for country '{country_code}'")
        
        rss_articles = await news_aggregator.fetch_rss_feeds(country_code)
        
        return {
            "status": "success",
            "country_code": country_code,
            "total_articles": len(rss_articles),
            "available_feeds": [feed["name"] for feed in news_aggregator.rss_feeds[country_code]],
            "articles": rss_articles
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching RSS feeds for {country_code}: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch RSS feeds for {country_code}: {str(e)}")

@router.get("/api-status")
async def get_api_status():
    """
    Check the status of all configured APIs
    """
    try:
        status = {
            "newsapi": bool(news_aggregator.news_api_key),
            "gnews": bool(news_aggregator.gnews_api_key),
            "mediastack": bool(news_aggregator.mediastack_key),
            "currents": bool(news_aggregator.currents_api_key),
            "supported_countries": list(news_aggregator.priority_countries.keys()),
            "rss_countries": list(news_aggregator.rss_feeds.keys())
        }
        
        return {
            "status": "success",
            "api_status": status,
            "total_configured_apis": sum(1 for v in [status["newsapi"], status["gnews"], status["mediastack"], status["currents"]] if v)
        }
    except Exception as e:
        print(f"❌ Error checking API status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check API status: {str(e)}")

@router.get("/test-aggregation")
async def test_news_aggregation():
    """
    Test endpoint to verify the news aggregation is working
    """
    try:
        # Test with a small sample
        test_results = await news_aggregator.fetch_prioritized_news(limit_per_country=5)
        
        return {
            "status": "success",
            "test_results": {
                "india_headlines_count": len(test_results["india_headlines"]),
                "other_countries_count": len(test_results["other_countries"]),
                "sample_india_titles": [article.get("title", "")[:100] for article in test_results["india_headlines"][:3]],
                "sample_other_titles": [article.get("title", "")[:100] for article in test_results["other_countries"][:3]]
            },
            "api_status": {
                "newsapi_configured": bool(news_aggregator.news_api_key),
                "gnews_configured": bool(news_aggregator.gnews_api_key),
                "mediastack_configured": bool(news_aggregator.mediastack_key),
                "currents_configured": bool(news_aggregator.currents_api_key)
            }
        }
    except Exception as e:
        print(f"❌ Error in test aggregation: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Test aggregation failed: {str(e)}")

@router.get("/debug/{country_code}")
async def debug_country_news(country_code: str):
    """Debug endpoint to test individual APIs"""
    debug_info = {
        "country_code": country_code,
        "api_keys_status": {
            "newsapi": bool(news_aggregator.news_api_key),
            "gnews": bool(news_aggregator.gnews_api_key),
            "mediastack": bool(news_aggregator.mediastack_key),
            "currents": bool(news_aggregator.currents_api_key)
        },
        "api_results": {}
    }
    
    # Test each API individually
    try:
        if news_aggregator.news_api_key:
            newsapi_result = await news_aggregator.fetch_newsapi_by_country(country_code)
            debug_info["api_results"]["newsapi"] = len(newsapi_result)
        
        if news_aggregator.gnews_api_key:
            gnews_result = await news_aggregator.fetch_gnews_by_country(country_code)
            debug_info["api_results"]["gnews"] = len(gnews_result)
            
    except Exception as e:
        debug_info["error"] = str(e)
    
    return debug_info