from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Article, NewsSource, CoverageComparison
from services.coverage_service import CoverageComparisonService
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter()

class CoverageComparisonResponse(BaseModel):
    id: int
    topic: str
    left_articles: List[dict]
    center_articles: List[dict]
    right_articles: List[dict]
    comparison_date: datetime
    
    class Config:
        from_attributes = True

class ArticleComparison(BaseModel):
    id: int
    title: str
    content: str
    source_name: str
    source_bias_score: float
    published_at: Optional[datetime]

@router.get("/topic/{topic}", response_model=CoverageComparisonResponse)
async def compare_coverage_by_topic(
    topic: str,
    db: Session = Depends(get_db)
):
    """Compare how different outlets cover the same topic"""
    try:
        coverage_service = CoverageComparisonService()
        
        # Get articles from different political leanings
        left_articles = db.query(Article).join(NewsSource).filter(
            NewsSource.political_lean == "left",
            Article.topic.ilike(f"%{topic}%")
        ).limit(5).all()
        
        center_articles = db.query(Article).join(NewsSource).filter(
            NewsSource.political_lean == "center",
            Article.topic.ilike(f"%{topic}%")
        ).limit(5).all()
        
        right_articles = db.query(Article).join(NewsSource).filter(
            NewsSource.political_lean == "right",
            Article.topic.ilike(f"%{topic}%")
        ).limit(5).all()
        
        # Convert to response format
        left_data = [
            {
                "id": article.id,
                "title": article.title,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "source_name": article.source.name,
                "source_bias_score": article.source.bias_score,
                "published_at": article.published_at
            }
            for article in left_articles
        ]
        
        center_data = [
            {
                "id": article.id,
                "title": article.title,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "source_name": article.source.name,
                "source_bias_score": article.source.bias_score,
                "published_at": article.published_at
            }
            for article in center_articles
        ]
        
        right_data = [
            {
                "id": article.id,
                "title": article.title,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "source_name": article.source.name,
                "source_bias_score": article.source.bias_score,
                "published_at": article.published_at
            }
            for article in right_articles
        ]
        
        return CoverageComparisonResponse(
            id=1,  # Placeholder
            topic=topic,
            left_articles=left_data,
            center_articles=center_data,
            right_articles=right_data,
            comparison_date=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing coverage: {str(e)}")

@router.get("/event/{event_name}")
async def compare_event_coverage(
    event_name: str,
    db: Session = Depends(get_db)
):
    """Compare coverage of a specific event across different outlets"""
    try:
        coverage_service = CoverageComparisonService()
        
        # Search for articles about the specific event
        articles = db.query(Article).join(NewsSource).filter(
            Article.title.ilike(f"%{event_name}%") | 
            Article.content.ilike(f"%{event_name}%")
        ).all()
        
        # Group by political leaning
        left_articles = [a for a in articles if a.source.political_lean == "left"]
        center_articles = [a for a in articles if a.source.political_lean == "center"]
        right_articles = [a for a in articles if a.source.political_lean == "right"]
        
        return {
            "event": event_name,
            "left_coverage": [
                {
                    "title": article.title,
                    "source": article.source.name,
                    "bias_score": article.source.bias_score,
                    "summary": article.content[:200] + "..." if len(article.content) > 200 else article.content
                }
                for article in left_articles[:3]
            ],
            "center_coverage": [
                {
                    "title": article.title,
                    "source": article.source.name,
                    "bias_score": article.source.bias_score,
                    "summary": article.content[:200] + "..." if len(article.content) > 200 else article.content
                }
                for article in center_articles[:3]
            ],
            "right_coverage": [
                {
                    "title": article.title,
                    "source": article.source.name,
                    "bias_score": article.source.bias_score,
                    "summary": article.content[:200] + "..." if len(article.content) > 200 else article.content
                }
                for article in right_articles[:3]
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing event coverage: {str(e)}")

@router.get("/sources/compare")
async def compare_sources(
    source1: str = Query(..., description="First source name"),
    source2: str = Query(..., description="Second source name"),
    db: Session = Depends(get_db)
):
    """Compare two specific news sources"""
    try:
        source1_data = db.query(NewsSource).filter(NewsSource.name.ilike(f"%{source1}%")).first()
        source2_data = db.query(NewsSource).filter(NewsSource.name.ilike(f"%{source2}%")).first()
        
        if not source1_data or not source2_data:
            raise HTTPException(status_code=404, detail="One or both sources not found")
        
        # Get recent articles from both sources
        source1_articles = db.query(Article).filter(Article.source_id == source1_data.id).limit(5).all()
        source2_articles = db.query(Article).filter(Article.source_id == source2_data.id).limit(5).all()
        
        return {
            "source1": {
                "name": source1_data.name,
                "bias_score": source1_data.bias_score,
                "political_lean": source1_data.political_lean,
                "articles": [
                    {
                        "title": article.title,
                        "topic": article.topic,
                        "published_at": article.published_at
                    }
                    for article in source1_articles
                ]
            },
            "source2": {
                "name": source2_data.name,
                "bias_score": source2_data.bias_score,
                "political_lean": source2_data.political_lean,
                "articles": [
                    {
                        "title": article.title,
                        "topic": article.topic,
                        "published_at": article.published_at
                    }
                    for article in source2_articles
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing sources: {str(e)}")

@router.get("/trending")
async def get_trending_topics(db: Session = Depends(get_db)):
    """Get trending topics that are being covered by multiple outlets"""
    try:
        # Get topics that appear in multiple sources
        from sqlalchemy import func
        
        trending_topics = db.query(
            Article.topic,
            func.count(Article.id).label('article_count'),
            func.count(func.distinct(Article.source_id)).label('source_count')
        ).filter(
            Article.topic.isnot(None)
        ).group_by(Article.topic).having(
            func.count(func.distinct(Article.source_id)) > 1
        ).order_by(func.count(Article.id).desc()).limit(10).all()
        
        return {
            "trending_topics": [
                {
                    "topic": topic,
                    "article_count": article_count,
                    "source_count": source_count
                }
                for topic, article_count, source_count in trending_topics
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending topics: {str(e)}")
