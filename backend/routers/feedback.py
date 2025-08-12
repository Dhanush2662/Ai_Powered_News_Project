from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database.database import get_db
from services.feedback_service import UserFeedbackService

router = APIRouter()
feedback_service = UserFeedbackService()

class FeedbackRequest(BaseModel):
    article_id: int
    user_id: str
    feedback_type: str  # rating, comment, report, helpful
    rating: Optional[float] = None
    comment: Optional[str] = None
    report_reason: Optional[str] = None

class HelpfulVoteRequest(BaseModel):
    feedback_id: int
    user_id: str

@router.post("/submit")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit user feedback for an article"""
    try:
        result = await feedback_service.submit_feedback(
            db=db,
            article_id=request.article_id,
            user_id=request.user_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            comment=request.comment,
            report_reason=request.report_reason
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"],
            "feedback_id": result.get("feedback_id")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/article/{article_id}")
async def get_article_feedback(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get all feedback for a specific article"""
    try:
        result = await feedback_service.get_article_feedback(db, article_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "feedback": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting article feedback: {str(e)}")

@router.post("/vote-helpful")
async def vote_helpful(
    request: HelpfulVoteRequest,
    db: Session = Depends(get_db)
):
    """Vote a comment as helpful"""
    try:
        result = await feedback_service.vote_helpful(
            db=db,
            feedback_id=request.feedback_id,
            user_id=request.user_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"],
            "new_helpful_count": result.get("new_helpful_count")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error voting helpful: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_feedback_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get feedback history for a user"""
    try:
        result = await feedback_service.get_user_feedback_history(db, user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "user_feedback": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user feedback history: {str(e)}")

@router.get("/popular")
async def get_popular_articles(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get articles with most feedback"""
    try:
        result = await feedback_service.get_popular_articles(db, limit)
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "popular_articles": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting popular articles: {str(e)}")

@router.get("/controversial")
async def get_controversial_articles(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get articles with mixed ratings (controversial)"""
    try:
        result = await feedback_service.get_controversial_articles(db, limit)
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "controversial_articles": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting controversial articles: {str(e)}")

@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete user's own feedback"""
    try:
        result = await feedback_service.delete_feedback(db, feedback_id, user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": result["message"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting feedback: {str(e)}")

@router.get("/statistics/overview")
async def get_feedback_statistics(
    db: Session = Depends(get_db)
):
    """Get overall feedback statistics"""
    try:
        from sqlalchemy import func
        from database.models import UserFeedback, Article
        
        # Get basic statistics
        total_feedbacks = db.query(func.count(UserFeedback.id)).scalar()
        total_articles_with_feedback = db.query(func.count(func.distinct(UserFeedback.article_id))).scalar()
        
        # Get feedback by type
        feedback_by_type = db.query(
            UserFeedback.feedback_type,
            func.count(UserFeedback.id)
        ).group_by(UserFeedback.feedback_type).all()
        
        # Get average rating
        avg_rating = db.query(func.avg(UserFeedback.rating)).filter(
            UserFeedback.rating.isnot(None)
        ).scalar()
        
        # Get recent activity
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_feedbacks = db.query(func.count(UserFeedback.id)).filter(
            UserFeedback.created_at >= recent_cutoff
        ).scalar()
        
        return {
            "success": True,
            "statistics": {
                "total_feedbacks": total_feedbacks,
                "total_articles_with_feedback": total_articles_with_feedback,
                "average_rating": round(avg_rating, 2) if avg_rating else 0,
                "recent_feedbacks_7_days": recent_feedbacks,
                "feedback_by_type": dict(feedback_by_type)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feedback statistics: {str(e)}")

@router.get("/trends/ratings")
async def get_rating_trends(
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get rating trends over time"""
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from database.models import UserFeedback
        
        # Get ratings from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_ratings = db.query(
            func.date(UserFeedback.created_at).label('date'),
            func.avg(UserFeedback.rating).label('avg_rating'),
            func.count(UserFeedback.id).label('count')
        ).filter(
            UserFeedback.feedback_type == "rating",
            UserFeedback.rating.isnot(None),
            UserFeedback.created_at >= cutoff_date
        ).group_by(func.date(UserFeedback.created_at)).order_by(func.date(UserFeedback.created_at)).all()
        
        return {
            "success": True,
            "trends": {
                "period_days": days,
                "daily_ratings": [
                    {
                        "date": str(day.date),
                        "average_rating": round(day.avg_rating, 2),
                        "rating_count": day.count
                    }
                    for day in daily_ratings
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rating trends: {str(e)}")
