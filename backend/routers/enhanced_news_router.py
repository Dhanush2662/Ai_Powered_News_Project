from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from services.enhanced_news_service import enhanced_news_service
from typing import Optional, List, Dict
import logging

router = APIRouter(prefix="/api/enhanced-news", tags=["Enhanced News"])
logger = logging.getLogger(__name__)

@router.get("/feed")
async def get_enhanced_news_feed(
    topic: Optional[str] = Query(None, description="Filter by topic (technology, business, politics, sports, health, science, entertainment, education)"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    limit: int = Query(50, ge=1, le=100, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    focus_indian: bool = Query(True, description="Focus on Indian news sources"),
    db: Session = Depends(get_db)
):
    """
    Get enhanced news feed with intelligent topic filtering, performance optimization,
    and comprehensive RSS feed coverage.
    
    Features:
    - 30+ RSS feeds from Indian and international sources
    - Intelligent topic classification using NLP keywords
    - Advanced duplicate removal
    - Asynchronous concurrent fetching
    - Performance monitoring and error handling
    - Relevance-based sorting
    """
    try:
        articles = await enhanced_news_service.get_enhanced_news_feed(
            db=db,
            topic=topic,
            source=source,
            limit=limit,
            offset=offset,
            focus_indian=focus_indian
        )
        
        return {
            "success": True,
            "articles": articles,
            "total": len(articles),
            "topic": topic,
            "focus_indian": focus_indian,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Enhanced news feed error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch enhanced news feed: {str(e)}")

@router.get("/performance")
async def get_performance_stats():
    """
    Get performance statistics for RSS feeds including:
    - Success rates
    - Average fetch times
    - Failed feeds
    - Feed reliability scores
    """
    try:
        stats = enhanced_news_service.get_performance_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Performance stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")

@router.post("/reset-failed-feeds")
async def reset_failed_feeds():
    """
    Reset the failed feeds list to retry previously failed feeds.
    """
    try:
        enhanced_news_service.reset_failed_feeds()
        return {
            "success": True,
            "message": "Failed feeds list has been reset"
        }
    except Exception as e:
        logger.error(f"Reset failed feeds error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset failed feeds: {str(e)}")

@router.get("/topics")
async def get_available_topics():
    """
    Get list of available topics with their keyword counts.
    """
    try:
        topics = {
            topic: len(keywords) 
            for topic, keywords in enhanced_news_service.topic_keywords.items()
        }
        
        return {
            "success": True,
            "topics": topics,
            "total_topics": len(topics)
        }
    except Exception as e:
        logger.error(f"Get topics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

@router.get("/feeds")
async def get_feed_info():
    """
    Get information about all configured RSS feeds.
    """
    try:
        feed_info = {
            category: [
                {
                    "name": feed["name"],
                    "source": feed["source"],
                    "category": feed["category"],
                    "reliability": feed["reliability"],
                    "status": "failed" if feed["name"] in enhanced_news_service.failed_feeds else "active"
                }
                for feed in feeds
            ]
            for category, feeds in enhanced_news_service.rss_feeds.items()
        }
        
        total_feeds = sum(len(feeds) for feeds in enhanced_news_service.rss_feeds.values())
        active_feeds = total_feeds - len(enhanced_news_service.failed_feeds)
        
        return {
            "success": True,
            "feeds": feed_info,
            "summary": {
                "total_feeds": total_feeds,
                "active_feeds": active_feeds,
                "failed_feeds": len(enhanced_news_service.failed_feeds),
                "success_rate": (active_feeds / total_feeds * 100) if total_feeds > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Get feed info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feed info: {str(e)}")

@router.get("/test/{topic}")
async def test_topic_filtering(
    topic: str,
    limit: int = Query(10, ge=1, le=50),
    focus_indian: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Test topic filtering accuracy for a specific topic.
    Returns articles with relevance scores and classification details.
    """
    try:
        articles = await enhanced_news_service.get_enhanced_news_feed(
            db=db,
            topic=topic,
            limit=limit,
            focus_indian=focus_indian
        )
        
        # Add classification details for testing
        test_results = []
        for article in articles:
            test_results.append({
                "title": article.get("title", ""),
                "classified_topic": article.get("topic", ""),
                "feed_category": article.get("feed_category", ""),
                "source": article.get("source_name", ""),
                "is_indian": article.get("is_indian", False),
                "reliability": article.get("feed_reliability", 0),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", "")
            })
        
        return {
            "success": True,
            "topic": topic,
            "total_articles": len(test_results),
            "focus_indian": focus_indian,
            "articles": test_results
        }
        
    except Exception as e:
        logger.error(f"Topic filtering test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test topic filtering: {str(e)}")