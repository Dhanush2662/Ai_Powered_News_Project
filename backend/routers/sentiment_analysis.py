from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from database.database import get_db
from services.sentiment_service import SentimentAnalysisService
from database.models import SentimentAnalysis, Article
import json

router = APIRouter()
sentiment_service = SentimentAnalysisService()

class SentimentAnalysisRequest(BaseModel):
    content: str
    article_id: int = None

class BatchSentimentRequest(BaseModel):
    texts: List[str]

@router.post("/analyze")
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze sentiment of text content"""
    try:
        # Perform sentiment analysis
        analysis = await sentiment_service.analyze_sentiment(request.content)
        
        # Store in database if article_id is provided
        if request.article_id:
            # Check if article exists
            article = db.query(Article).filter(Article.id == request.article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Store analysis
            sentiment_record = SentimentAnalysis(
                article_id=request.article_id,
                overall_sentiment=analysis["overall_sentiment"],
                sentiment_label=analysis["sentiment_label"],
                confidence_score=analysis["confidence_score"],
                detailed_analysis=json.dumps(analysis["detailed_analysis"])
            )
            
            db.add(sentiment_record)
            db.commit()
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.post("/analyze-batch")
async def analyze_batch_sentiment(
    request: BatchSentimentRequest,
    db: Session = Depends(get_db)
):
    """Analyze sentiment of multiple texts"""
    try:
        analysis = await sentiment_service.analyze_multiple_texts(request.texts)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing batch sentiment: {str(e)}")

@router.get("/article/{article_id}")
async def get_article_sentiment(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for a specific article"""
    try:
        # Check if article exists
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get stored sentiment analysis
        sentiment_record = db.query(SentimentAnalysis).filter(
            SentimentAnalysis.article_id == article_id
        ).order_by(SentimentAnalysis.analysis_date.desc()).first()
        
        if not sentiment_record:
            # Perform analysis if not stored
            analysis = await sentiment_service.analyze_sentiment(article.content)
            
            # Store the analysis
            sentiment_record = SentimentAnalysis(
                article_id=article_id,
                overall_sentiment=analysis["overall_sentiment"],
                sentiment_label=analysis["sentiment_label"],
                confidence_score=analysis["confidence_score"],
                detailed_analysis=json.dumps(analysis["detailed_analysis"])
            )
            
            db.add(sentiment_record)
            db.commit()
            
            return {
                "success": True,
                "analysis": analysis,
                "article": {
                    "id": article.id,
                    "title": article.title,
                    "source": article.source.name if article.source else None
                }
            }
        
        # Return stored analysis
        return {
            "success": True,
            "analysis": {
                "overall_sentiment": sentiment_record.overall_sentiment,
                "sentiment_label": sentiment_record.sentiment_label,
                "confidence_score": sentiment_record.confidence_score,
                "detailed_analysis": json.loads(sentiment_record.detailed_analysis),
                "analysis_date": sentiment_record.analysis_date.isoformat()
            },
            "article": {
                "id": article.id,
                "title": article.title,
                "source": article.source.name if article.source else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting article sentiment: {str(e)}")

@router.get("/trending")
async def get_sentiment_trends(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get sentiment trends across articles"""
    try:
        # Get recent sentiment analyses
        recent_analyses = db.query(SentimentAnalysis).join(Article).order_by(
            SentimentAnalysis.analysis_date.desc()
        ).limit(limit).all()
        
        # Calculate trends
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_sentiment = 0.0
        
        for analysis in recent_analyses:
            sentiment_counts[analysis.sentiment_label] += 1
            total_sentiment += analysis.overall_sentiment
        
        avg_sentiment = total_sentiment / len(recent_analyses) if recent_analyses else 0
        
        return {
            "success": True,
            "trends": {
                "average_sentiment": round(avg_sentiment, 3),
                "sentiment_distribution": sentiment_counts,
                "total_articles_analyzed": len(recent_analyses)
            },
            "recent_analyses": [
                {
                    "article_id": analysis.article_id,
                    "article_title": analysis.article.title,
                    "sentiment_label": analysis.sentiment_label,
                    "overall_sentiment": analysis.overall_sentiment,
                    "confidence_score": analysis.confidence_score,
                    "analysis_date": analysis.analysis_date.isoformat()
                }
                for analysis in recent_analyses
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sentiment trends: {str(e)}")

@router.get("/compare-sources")
async def compare_source_sentiment(
    db: Session = Depends(get_db),
    limit: int = 5
):
    """Compare sentiment across different news sources"""
    try:
        # Get sentiment analyses grouped by source
        source_sentiments = {}
        
        analyses = db.query(SentimentAnalysis).join(Article).join(
            Article.source
        ).order_by(SentimentAnalysis.analysis_date.desc()).limit(100).all()
        
        for analysis in analyses:
            source_name = analysis.article.source.name
            if source_name not in source_sentiments:
                source_sentiments[source_name] = {
                    "sentiments": [],
                    "count": 0,
                    "bias_score": analysis.article.source.bias_score
                }
            
            source_sentiments[source_name]["sentiments"].append(analysis.overall_sentiment)
            source_sentiments[source_name]["count"] += 1
        
        # Calculate averages for each source
        comparison = []
        for source_name, data in source_sentiments.items():
            if data["count"] >= 3:  # Only include sources with at least 3 articles
                avg_sentiment = sum(data["sentiments"]) / len(data["sentiments"])
                comparison.append({
                    "source_name": source_name,
                    "average_sentiment": round(avg_sentiment, 3),
                    "article_count": data["count"],
                    "bias_score": data["bias_score"],
                    "sentiment_label": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
                })
        
        # Sort by average sentiment
        comparison.sort(key=lambda x: x["average_sentiment"], reverse=True)
        
        return {
            "success": True,
            "comparison": comparison[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing source sentiment: {str(e)}")
