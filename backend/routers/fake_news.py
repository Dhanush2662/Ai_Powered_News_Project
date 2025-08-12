from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from database.database import get_db
from services.fake_news_service import FakeNewsDetectionService
from database.models import FakeNewsDetection, Article
import json

router = APIRouter()
fake_news_service = FakeNewsDetectionService()

class FakeNewsDetectionRequest(BaseModel):
    content: str
    url: str = None
    source: str = None
    article_id: int = None

class BatchFakeNewsRequest(BaseModel):
    articles: List[Dict[str, Any]]

@router.post("/detect")
async def detect_fake_news(
    request: FakeNewsDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect fake news in content"""
    try:
        # Perform fake news detection
        detection = await fake_news_service.detect_fake_news(
            request.content, 
            request.url, 
            request.source
        )
        
        # Store in database if article_id is provided
        if request.article_id:
            # Check if article exists
            article = db.query(Article).filter(Article.id == request.article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Store detection
            fake_news_record = FakeNewsDetection(
                article_id=request.article_id,
                fake_news_score=detection["fake_news_score"],
                risk_level=detection["risk_level"],
                confidence_score=detection["confidence_score"],
                verdict=detection["verdict"],
                red_flags=json.dumps(detection["red_flags"])
            )
            
            db.add(fake_news_record)
            db.commit()
        
        return {
            "success": True,
            "detection": detection
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting fake news: {str(e)}")

@router.post("/detect-batch")
async def detect_batch_fake_news(
    request: BatchFakeNewsRequest,
    db: Session = Depends(get_db)
):
    """Detect fake news for multiple articles"""
    try:
        detection_results = await fake_news_service.batch_detect_fake_news(request.articles)
        
        return {
            "success": True,
            "detections": detection_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting batch fake news: {str(e)}")

@router.get("/article/{article_id}")
async def get_article_fake_news_detection(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get fake news detection for a specific article"""
    try:
        # Check if article exists
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get stored fake news detection
        detection_record = db.query(FakeNewsDetection).filter(
            FakeNewsDetection.article_id == article_id
        ).order_by(FakeNewsDetection.detection_date.desc()).first()
        
        if not detection_record:
            # Perform detection if not stored
            detection = await fake_news_service.detect_fake_news(
                article.content,
                article.url,
                article.source.name if article.source else None
            )
            
            # Store the detection
            detection_record = FakeNewsDetection(
                article_id=article_id,
                fake_news_score=detection["fake_news_score"],
                risk_level=detection["risk_level"],
                confidence_score=detection["confidence_score"],
                verdict=detection["verdict"],
                red_flags=json.dumps(detection["red_flags"])
            )
            
            db.add(detection_record)
            db.commit()
            
            return {
                "success": True,
                "detection": detection,
                "article": {
                    "id": article.id,
                    "title": article.title,
                    "source": article.source.name if article.source else None
                }
            }
        
        # Return stored detection
        return {
            "success": True,
            "detection": {
                "fake_news_score": detection_record.fake_news_score,
                "risk_level": detection_record.risk_level,
                "confidence_score": detection_record.confidence_score,
                "verdict": detection_record.verdict,
                "red_flags": json.loads(detection_record.red_flags),
                "detection_date": detection_record.detection_date.isoformat()
            },
            "article": {
                "id": article.id,
                "title": article.title,
                "source": article.source.name if article.source else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting article fake news detection: {str(e)}")

@router.get("/high-risk")
async def get_high_risk_articles(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get articles with high fake news risk"""
    try:
        # Get high risk detections
        high_risk_detections = db.query(FakeNewsDetection).join(Article).filter(
            FakeNewsDetection.risk_level == "high"
        ).order_by(FakeNewsDetection.fake_news_score.desc()).limit(limit).all()
        
        return {
            "success": True,
            "high_risk_articles": [
                {
                    "article_id": detection.article_id,
                    "article_title": detection.article.title,
                    "source": detection.article.source.name if detection.article.source else None,
                    "fake_news_score": detection.fake_news_score,
                    "risk_level": detection.risk_level,
                    "verdict": detection.verdict,
                    "red_flags": json.loads(detection.red_flags),
                    "detection_date": detection.detection_date.isoformat()
                }
                for detection in high_risk_detections
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting high risk articles: {str(e)}")

@router.get("/statistics")
async def get_fake_news_statistics(
    db: Session = Depends(get_db)
):
    """Get fake news detection statistics"""
    try:
        # Get all detections
        all_detections = db.query(FakeNewsDetection).all()
        
        # Calculate statistics
        total_detections = len(all_detections)
        high_risk_count = len([d for d in all_detections if d.risk_level == "high"])
        medium_risk_count = len([d for d in all_detections if d.risk_level == "medium"])
        low_risk_count = len([d for d in all_detections if d.risk_level == "low"])
        
        likely_fake_count = len([d for d in all_detections if d.verdict == "likely_fake"])
        suspicious_count = len([d for d in all_detections if d.verdict == "suspicious"])
        likely_real_count = len([d for d in all_detections if d.verdict == "likely_real"])
        
        avg_fake_news_score = sum(d.fake_news_score for d in all_detections) / total_detections if total_detections > 0 else 0
        avg_confidence = sum(d.confidence_score for d in all_detections) / total_detections if total_detections > 0 else 0
        
        return {
            "success": True,
            "statistics": {
                "total_detections": total_detections,
                "risk_level_distribution": {
                    "high": high_risk_count,
                    "medium": medium_risk_count,
                    "low": low_risk_count
                },
                "verdict_distribution": {
                    "likely_fake": likely_fake_count,
                    "suspicious": suspicious_count,
                    "likely_real": likely_real_count
                },
                "average_fake_news_score": round(avg_fake_news_score, 3),
                "average_confidence": round(avg_confidence, 3)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fake news statistics: {str(e)}")

@router.get("/trends")
async def get_fake_news_trends(
    db: Session = Depends(get_db),
    days: int = 7
):
    """Get fake news detection trends over time"""
    try:
        from datetime import datetime, timedelta
        
        # Get detections from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_detections = db.query(FakeNewsDetection).filter(
            FakeNewsDetection.detection_date >= cutoff_date
        ).order_by(FakeNewsDetection.detection_date.desc()).all()
        
        # Group by date
        daily_stats = {}
        for detection in recent_detections:
            date_str = detection.detection_date.strftime("%Y-%m-%d")
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    "count": 0,
                    "high_risk": 0,
                    "avg_score": 0.0,
                    "scores": []
                }
            
            daily_stats[date_str]["count"] += 1
            daily_stats[date_str]["scores"].append(detection.fake_news_score)
            if detection.risk_level == "high":
                daily_stats[date_str]["high_risk"] += 1
        
        # Calculate averages
        for date_str, stats in daily_stats.items():
            if stats["scores"]:
                stats["avg_score"] = round(sum(stats["scores"]) / len(stats["scores"]), 3)
            del stats["scores"]  # Remove raw scores from response
        
        return {
            "success": True,
            "trends": {
                "period_days": days,
                "total_detections": len(recent_detections),
                "daily_statistics": daily_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fake news trends: {str(e)}")

@router.get("/source-analysis")
async def analyze_source_fake_news_patterns(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Analyze fake news patterns by source"""
    try:
        # Get detections grouped by source
        source_detections = {}
        
        detections = db.query(FakeNewsDetection).join(Article).join(
            Article.source
        ).order_by(FakeNewsDetection.detection_date.desc()).limit(1000).all()
        
        for detection in detections:
            source_name = detection.article.source.name
            if source_name not in source_detections:
                source_detections[source_name] = {
                    "detections": [],
                    "count": 0,
                    "bias_score": detection.article.source.bias_score
                }
            
            source_detections[source_name]["detections"].append(detection.fake_news_score)
            source_detections[source_name]["count"] += 1
        
        # Calculate statistics for each source
        source_analysis = []
        for source_name, data in source_detections.items():
            if data["count"] >= 3:  # Only include sources with at least 3 detections
                avg_score = sum(data["detections"]) / len(data["detections"])
                high_risk_count = len([score for score in data["detections"] if score > 0.7])
                
                source_analysis.append({
                    "source_name": source_name,
                    "average_fake_news_score": round(avg_score, 3),
                    "detection_count": data["count"],
                    "high_risk_percentage": round((high_risk_count / data["count"]) * 100, 1),
                    "bias_score": data["bias_score"],
                    "risk_level": "high" if avg_score > 0.7 else "medium" if avg_score > 0.4 else "low"
                })
        
        # Sort by average fake news score (highest first)
        source_analysis.sort(key=lambda x: x["average_fake_news_score"], reverse=True)
        
        return {
            "success": True,
            "source_analysis": source_analysis[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing source fake news patterns: {str(e)}")
