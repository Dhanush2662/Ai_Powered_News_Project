from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import Article, NewsSource
from datetime import datetime, timedelta
import json

class CoverageComparisonService:
    def __init__(self):
        pass
    
    async def compare_coverage_by_topic(self, db: Session, topic: str) -> Dict[str, Any]:
        """Compare how different outlets cover the same topic"""
        try:
            # Get articles from different political leanings
            left_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "left",
                Article.topic.ilike(f"%{topic}%")
            ).order_by(Article.published_at.desc()).limit(5).all()
            
            center_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "center",
                Article.topic.ilike(f"%{topic}%")
            ).order_by(Article.published_at.desc()).limit(5).all()
            
            right_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "right",
                Article.topic.ilike(f"%{topic}%")
            ).order_by(Article.published_at.desc()).limit(5).all()
            
            return {
                "topic": topic,
                "left_coverage": self._format_articles(left_articles),
                "center_coverage": self._format_articles(center_articles),
                "right_coverage": self._format_articles(right_articles),
                "comparison_metrics": self._calculate_comparison_metrics(left_articles, center_articles, right_articles)
            }
            
        except Exception as e:
            print(f"Error comparing coverage by topic: {str(e)}")
            return {}
    
    def _format_articles(self, articles: List[Article]) -> List[Dict[str, Any]]:
        """Format articles for response"""
        return [
            {
                "id": article.id,
                "title": article.title,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "source_name": article.source.name,
                "source_bias_score": article.source.bias_score,
                "published_at": article.published_at,
                "url": article.url
            }
            for article in articles
        ]
    
    def _calculate_comparison_metrics(self, left_articles: List[Article], center_articles: List[Article], right_articles: List[Article]) -> Dict[str, Any]:
        """Calculate metrics for coverage comparison"""
        try:
            # Calculate average bias scores
            left_bias_avg = sum(a.source.bias_score for a in left_articles) / len(left_articles) if left_articles else 0
            center_bias_avg = sum(a.source.bias_score for a in center_articles) / len(center_articles) if center_articles else 0
            right_bias_avg = sum(a.source.bias_score for a in right_articles) / len(right_articles) if right_articles else 0
            
            # Calculate coverage balance
            total_articles = len(left_articles) + len(center_articles) + len(right_articles)
            coverage_balance = {
                "left_percentage": (len(left_articles) / total_articles * 100) if total_articles > 0 else 0,
                "center_percentage": (len(center_articles) / total_articles * 100) if total_articles > 0 else 0,
                "right_percentage": (len(right_articles) / total_articles * 100) if total_articles > 0 else 0
            }
            
            return {
                "average_bias_scores": {
                    "left": round(left_bias_avg, 2),
                    "center": round(center_bias_avg, 2),
                    "right": round(right_bias_avg, 2)
                },
                "coverage_balance": coverage_balance,
                "total_articles": total_articles
            }
            
        except Exception as e:
            print(f"Error calculating comparison metrics: {str(e)}")
            return {}
    
    async def compare_event_coverage(self, db: Session, event_name: str) -> Dict[str, Any]:
        """Compare coverage of a specific event across different outlets"""
        try:
            # Search for articles about the specific event
            articles = db.query(Article).join(NewsSource).filter(
                Article.title.ilike(f"%{event_name}%") | 
                Article.content.ilike(f"%{event_name}%")
            ).order_by(Article.published_at.desc()).all()
            
            # Group by political leaning
            left_articles = [a for a in articles if a.source.political_lean == "left"]
            center_articles = [a for a in articles if a.source.political_lean == "center"]
            right_articles = [a for a in articles if a.source.political_lean == "right"]
            
            # Analyze coverage patterns
            coverage_analysis = self._analyze_event_coverage(left_articles, center_articles, right_articles)
            
            return {
                "event": event_name,
                "left_coverage": self._format_articles(left_articles[:3]),
                "center_coverage": self._format_articles(center_articles[:3]),
                "right_coverage": self._format_articles(right_articles[:3]),
                "coverage_analysis": coverage_analysis
            }
            
        except Exception as e:
            print(f"Error comparing event coverage: {str(e)}")
            return {}
    
    def _analyze_event_coverage(self, left_articles: List[Article], center_articles: List[Article], right_articles: List[Article]) -> Dict[str, Any]:
        """Analyze patterns in event coverage"""
        try:
            # Extract common themes and keywords
            all_articles = left_articles + center_articles + right_articles
            
            # Simple keyword analysis
            keywords = self._extract_common_keywords([a.title + " " + a.content for a in all_articles])
            
            # Sentiment analysis (basic)
            left_sentiment = self._calculate_sentiment([a.content for a in left_articles])
            center_sentiment = self._calculate_sentiment([a.content for a in center_articles])
            right_sentiment = self._calculate_sentiment([a.content for a in right_articles])
            
            return {
                "common_keywords": keywords[:10],
                "sentiment_analysis": {
                    "left": left_sentiment,
                    "center": center_sentiment,
                    "right": right_sentiment
                },
                "coverage_timeline": self._create_coverage_timeline(all_articles)
            }
            
        except Exception as e:
            print(f"Error analyzing event coverage: {str(e)}")
            return {}
    
    def _extract_common_keywords(self, texts: List[str]) -> List[str]:
        """Extract common keywords from texts"""
        try:
            import re
            from collections import Counter
            
            # Simple keyword extraction
            all_words = []
            for text in texts:
                words = re.findall(r'\b\w+\b', text.lower())
                # Filter out common stop words
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
                words = [w for w in words if w not in stop_words and len(w) > 3]
                all_words.extend(words)
            
            # Count and return most common
            word_counts = Counter(all_words)
            return [word for word, count in word_counts.most_common(20)]
            
        except Exception as e:
            print(f"Error extracting keywords: {str(e)}")
            return []
    
    def _calculate_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """Calculate sentiment scores for texts"""
        try:
            from textblob import TextBlob
            
            if not texts:
                return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
            
            total_sentiment = 0.0
            for text in texts:
                blob = TextBlob(text)
                total_sentiment += blob.sentiment.polarity
            
            avg_sentiment = total_sentiment / len(texts)
            
            if avg_sentiment > 0.1:
                sentiment = "positive"
            elif avg_sentiment < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "score": round(avg_sentiment, 3)
            }
            
        except Exception as e:
            print(f"Error calculating sentiment: {str(e)}")
            return {"sentiment": "neutral", "score": 0.0}
    
    def _create_coverage_timeline(self, articles: List[Article]) -> List[Dict[str, Any]]:
        """Create timeline of coverage"""
        try:
            # Group articles by date
            timeline = {}
            for article in articles:
                date_key = article.published_at.strftime("%Y-%m-%d") if article.published_at else "unknown"
                if date_key not in timeline:
                    timeline[date_key] = []
                timeline[date_key].append({
                    "title": article.title,
                    "source": article.source.name,
                    "political_lean": article.source.political_lean
                })
            
            # Convert to sorted list
            timeline_list = [
                {
                    "date": date,
                    "articles": articles
                }
                for date, articles in sorted(timeline.items(), reverse=True)
            ]
            
            return timeline_list[:10]  # Return last 10 days
            
        except Exception as e:
            print(f"Error creating coverage timeline: {str(e)}")
            return []
    
    async def get_trending_topics(self, db: Session) -> List[Dict[str, Any]]:
        """Get trending topics that are being covered by multiple outlets"""
        try:
            from sqlalchemy import func
            
            # Get topics from recent articles (last 7 days)
            recent_date = datetime.now() - timedelta(days=7)
            
            trending_topics = db.query(
                Article.topic,
                func.count(Article.id).label('article_count'),
                func.count(func.distinct(Article.source_id)).label('source_count')
            ).filter(
                Article.published_at >= recent_date,
                Article.topic.isnot(None)
            ).group_by(Article.topic).having(
                func.count(func.distinct(Article.source_id)) > 1
            ).order_by(func.count(Article.id).desc()).limit(10).all()
            
            return [
                {
                    "topic": topic,
                    "article_count": article_count,
                    "source_count": source_count,
                    "coverage_intensity": round(article_count / source_count, 2) if source_count > 0 else 0
                }
                for topic, article_count, source_count in trending_topics
            ]
            
        except Exception as e:
            print(f"Error getting trending topics: {str(e)}")
            return []
