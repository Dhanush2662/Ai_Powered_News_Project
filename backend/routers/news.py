from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Article, NewsSource
from services.news_service import NewsService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ArticleResponse(BaseModel):
    id: Optional[int]
    title: str
    content: str
    url: str
    published_at: Optional[datetime]
    topic: Optional[str]
    summary: Optional[str]
    source_name: str
    source_bias_score: Optional[float]
    is_indian: Optional[bool] = False
    api_source: Optional[str] = None
    
    class Config:
        from_attributes = True

class NewsResponse(BaseModel):
    articles: List[ArticleResponse]
    total_count: int
    topics: List[str]

class EnhancedNewsResponse(BaseModel):
    articles: List[ArticleResponse]
    total_count: int
    indian_count: int
    international_count: int
    api_sources: List[str]

class CountryNewsResponse(BaseModel):
    country: str
    articles: List[ArticleResponse]
    total_count: int
    api_sources: List[str]

@router.get("/", response_model=NewsResponse)
async def get_news(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(20, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip"),
    db: Session = Depends(get_db)
):
    """Get aggregated news articles with optional filtering"""
    try:
        news_service = NewsService()
        articles = await news_service.get_aggregated_news(db, topic, source, limit, offset)
        
        # Get unique topics for filtering
        topics = db.query(Article.topic).distinct().all()
        topics = [topic[0] for topic in topics if topic[0]]
        
        return NewsResponse(
            articles=articles,
            total_count=len(articles),
            topics=topics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/feed", response_model=EnhancedNewsResponse)
async def get_enhanced_news_feed(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip"),
    focus_indian: bool = Query(True, description="Focus on Indian news"),
    db: Session = Depends(get_db)
):
    """Get enhanced news feed with focus on Indian news from multiple APIs"""
    try:
        news_service = NewsService()
        articles = await news_service.get_enhanced_aggregated_news(
            db, topic, source, limit, offset, focus_indian
        )
        
        # Calculate statistics
        indian_count = sum(1 for article in articles if article.get('is_indian', False))
        international_count = len(articles) - indian_count
        api_sources = list(set(article.get('api_source', 'unknown') for article in articles if article.get('api_source')))
        
        return EnhancedNewsResponse(
            articles=articles,
            total_count=len(articles),
            indian_count=indian_count,
            international_count=international_count,
            api_sources=api_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching enhanced news: {str(e)}")

@router.get("/country/{country_code}", response_model=CountryNewsResponse)
async def get_country_news(
    country_code: str,
    limit: int = Query(100, description="Number of articles to return"),
    db: Session = Depends(get_db)
):
    """Get news for specific country from all APIs and RSS feeds"""
    try:
        news_service = NewsService()
        articles = await news_service.fetch_news_by_country(country_code)
        
        # Limit articles
        limited_articles = articles[:limit]
        
        # Get unique API sources
        api_sources = list(set(article.get('api_source', 'unknown') for article in limited_articles if article.get('api_source')))
        
        return CountryNewsResponse(
            country=country_code,
            articles=limited_articles,
            total_count=len(limited_articles),
            api_sources=api_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news for {country_code}: {str(e)}")

@router.get("/indian", response_model=EnhancedNewsResponse)
async def get_indian_news(
    limit: int = Query(50, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip"),
    db: Session = Depends(get_db)
):
    """Get Indian news specifically from all APIs"""
    try:
        news_service = NewsService()
        articles = await news_service.get_enhanced_aggregated_news(
            db, None, None, limit, offset, focus_indian=True
        )
        
        # Filter only Indian articles
        indian_articles = [article for article in articles if article.get('is_indian', False)]
        
        # Calculate statistics
        api_sources = list(set(article.get('api_source', 'unknown') for article in indian_articles if article.get('api_source')))
        
        return EnhancedNewsResponse(
            articles=indian_articles,
            total_count=len(indian_articles),
            indian_count=len(indian_articles),
            international_count=0,
            api_sources=api_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Indian news: {str(e)}")

@router.get("/topics")
async def get_topics(db: Session = Depends(get_db)):
    """Get all available topics"""
    topics = db.query(Article.topic).distinct().all()
    return {"topics": [topic[0] for topic in topics if topic[0]]}

@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Get all news sources with their bias scores"""
    sources = db.query(NewsSource).all()
    return {
        "sources": [
            {
                "id": source.id,
                "name": source.name,
                "bias_score": source.bias_score,
                "political_lean": source.political_lean,
                "country": source.country
            }
            for source in sources
        ]
    }

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        url=article.url,
        published_at=article.published_at,
        topic=article.topic,
        summary=article.summary,
        source_name=article.source.name,
        source_bias_score=article.source.bias_score
    )
