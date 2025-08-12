from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.models import UserFeedback, Article
from datetime import datetime
import json

class UserFeedbackService:
    def __init__(self):
        pass
    
    async def submit_feedback(
        self, 
        db: Session, 
        article_id: int, 
        user_id: str, 
        feedback_type: str,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        report_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit user feedback for an article"""
        try:
            # Validate article exists
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                return {"error": "Article not found"}
            
            # Validate feedback type
            valid_types = ["rating", "comment", "report", "helpful"]
            if feedback_type not in valid_types:
                return {"error": "Invalid feedback type"}
            
            # Validate rating if provided
            if rating is not None and (rating < 1 or rating > 5):
                return {"error": "Rating must be between 1 and 5"}
            
            # Check if user already submitted this type of feedback
            existing_feedback = db.query(UserFeedback).filter(
                UserFeedback.article_id == article_id,
                UserFeedback.user_id == user_id,
                UserFeedback.feedback_type == feedback_type
            ).first()
            
            if existing_feedback:
                # Update existing feedback
                if rating is not None:
                    existing_feedback.rating = rating
                if comment is not None:
                    existing_feedback.comment = comment
                if report_reason is not None:
                    existing_feedback.report_reason = report_reason
                
                db.commit()
                return {
                    "message": "Feedback updated successfully",
                    "feedback_id": existing_feedback.id
                }
            else:
                # Create new feedback
                new_feedback = UserFeedback(
                    article_id=article_id,
                    user_id=user_id,
                    feedback_type=feedback_type,
                    rating=rating,
                    comment=comment,
                    report_reason=report_reason
                )
                
                db.add(new_feedback)
                db.commit()
                db.refresh(new_feedback)
                
                return {
                    "message": "Feedback submitted successfully",
                    "feedback_id": new_feedback.id
                }
                
        except Exception as e:
            db.rollback()
            return {"error": f"Error submitting feedback: {str(e)}"}
    
    async def get_article_feedback(self, db: Session, article_id: int) -> Dict[str, Any]:
        """Get all feedback for a specific article"""
        try:
            feedbacks = db.query(UserFeedback).filter(
                UserFeedback.article_id == article_id
            ).all()
            
            # Calculate statistics
            ratings = [f.rating for f in feedbacks if f.rating is not None]
            comments = [f for f in feedbacks if f.comment]
            reports = [f for f in feedbacks if f.feedback_type == "report"]
            helpful_votes = [f for f in feedbacks if f.feedback_type == "helpful"]
            
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            total_ratings = len(ratings)
            total_comments = len(comments)
            total_reports = len(reports)
            total_helpful_votes = len(helpful_votes)
            
            return {
                "article_id": article_id,
                "statistics": {
                    "average_rating": round(avg_rating, 2),
                    "total_ratings": total_ratings,
                    "total_comments": total_comments,
                    "total_reports": total_reports,
                    "total_helpful_votes": total_helpful_votes
                },
                "ratings_distribution": self._calculate_ratings_distribution(ratings),
                "recent_comments": [
                    {
                        "id": c.id,
                        "comment": c.comment,
                        "user_id": c.user_id,
                        "created_at": c.created_at.isoformat(),
                        "helpful_votes": c.helpful_votes
                    }
                    for c in sorted(comments, key=lambda x: x.created_at, reverse=True)[:10]
                ],
                "report_reasons": [
                    {
                        "reason": r.report_reason,
                        "user_id": r.user_id,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in reports
                ]
            }
            
        except Exception as e:
            return {"error": f"Error getting feedback: {str(e)}"}
    
    def _calculate_ratings_distribution(self, ratings: List[float]) -> Dict[str, int]:
        """Calculate distribution of ratings"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for rating in ratings:
            rating_int = int(rating)
            if rating_int in distribution:
                distribution[rating_int] += 1
        
        return distribution
    
    async def vote_helpful(self, db: Session, feedback_id: int, user_id: str) -> Dict[str, Any]:
        """Vote a comment as helpful"""
        try:
            feedback = db.query(UserFeedback).filter(
                UserFeedback.id == feedback_id,
                UserFeedback.feedback_type == "comment"
            ).first()
            
            if not feedback:
                return {"error": "Comment not found"}
            
            # Check if user already voted helpful
            existing_vote = db.query(UserFeedback).filter(
                UserFeedback.article_id == feedback.article_id,
                UserFeedback.user_id == user_id,
                UserFeedback.feedback_type == "helpful"
            ).first()
            
            if existing_vote:
                return {"error": "User already voted helpful"}
            
            # Create helpful vote
            helpful_vote = UserFeedback(
                article_id=feedback.article_id,
                user_id=user_id,
                feedback_type="helpful"
            )
            
            db.add(helpful_vote)
            feedback.helpful_votes += 1
            db.commit()
            
            return {
                "message": "Vote recorded successfully",
                "new_helpful_count": feedback.helpful_votes
            }
            
        except Exception as e:
            db.rollback()
            return {"error": f"Error voting helpful: {str(e)}"}
    
    async def get_user_feedback_history(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get feedback history for a user"""
        try:
            feedbacks = db.query(UserFeedback).filter(
                UserFeedback.user_id == user_id
            ).order_by(UserFeedback.created_at.desc()).all()
            
            return {
                "user_id": user_id,
                "total_feedbacks": len(feedbacks),
                "feedback_by_type": self._group_feedback_by_type(feedbacks),
                "recent_feedbacks": [
                    {
                        "id": f.id,
                        "article_id": f.article_id,
                        "feedback_type": f.feedback_type,
                        "rating": f.rating,
                        "comment": f.comment,
                        "created_at": f.created_at.isoformat()
                    }
                    for f in feedbacks[:20]  # Last 20 feedbacks
                ]
            }
            
        except Exception as e:
            return {"error": f"Error getting user feedback history: {str(e)}"}
    
    def _group_feedback_by_type(self, feedbacks: List[UserFeedback]) -> Dict[str, int]:
        """Group feedback by type"""
        grouped = {}
        for feedback in feedbacks:
            feedback_type = feedback.feedback_type
            grouped[feedback_type] = grouped.get(feedback_type, 0) + 1
        return grouped
    
    async def get_popular_articles(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get articles with most feedback"""
        try:
            # Get articles with feedback counts
            articles_with_feedback = db.query(
                Article.id,
                Article.title,
                Article.url,
                Article.published_at
            ).join(UserFeedback).group_by(Article.id).order_by(
                db.func.count(UserFeedback.id).desc()
            ).limit(limit).all()
            
            result = []
            for article in articles_with_feedback:
                feedback_stats = await self.get_article_feedback(db, article.id)
                result.append({
                    "id": article.id,
                    "title": article.title,
                    "url": article.url,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "feedback_stats": feedback_stats.get("statistics", {})
                })
            
            return result
            
        except Exception as e:
            return {"error": f"Error getting popular articles: {str(e)}"}
    
    async def get_controversial_articles(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get articles with mixed ratings (controversial)"""
        try:
            # Get articles with rating variance
            articles_with_ratings = db.query(
                Article.id,
                Article.title,
                Article.url,
                Article.published_at
            ).join(UserFeedback).filter(
                UserFeedback.feedback_type == "rating",
                UserFeedback.rating.isnot(None)
            ).group_by(Article.id).having(
                db.func.count(UserFeedback.id) >= 3  # At least 3 ratings
            ).all()
            
            result = []
            for article in articles_with_ratings:
                feedback_stats = await self.get_article_feedback(db, article.id)
                ratings = [f.rating for f in db.query(UserFeedback).filter(
                    UserFeedback.article_id == article.id,
                    UserFeedback.feedback_type == "rating",
                    UserFeedback.rating.isnot(None)
                ).all()]
                
                if len(ratings) >= 3:
                    # Calculate variance
                    avg_rating = sum(ratings) / len(ratings)
                    variance = sum((r - avg_rating) ** 2 for r in ratings) / len(ratings)
                    
                    result.append({
                        "id": article.id,
                        "title": article.title,
                        "url": article.url,
                        "published_at": article.published_at.isoformat() if article.published_at else None,
                        "average_rating": round(avg_rating, 2),
                        "rating_variance": round(variance, 3),
                        "total_ratings": len(ratings)
                    })
            
            # Sort by variance (highest first)
            result.sort(key=lambda x: x["rating_variance"], reverse=True)
            return result[:limit]
            
        except Exception as e:
            return {"error": f"Error getting controversial articles: {str(e)}"}
    
    async def delete_feedback(self, db: Session, feedback_id: int, user_id: str) -> Dict[str, Any]:
        """Delete user's own feedback"""
        try:
            feedback = db.query(UserFeedback).filter(
                UserFeedback.id == feedback_id,
                UserFeedback.user_id == user_id
            ).first()
            
            if not feedback:
                return {"error": "Feedback not found or not owned by user"}
            
            db.delete(feedback)
            db.commit()
            
            return {"message": "Feedback deleted successfully"}
            
        except Exception as e:
            db.rollback()
            return {"error": f"Error deleting feedback: {str(e)}"}
