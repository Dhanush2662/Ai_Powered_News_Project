import openai
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import Article, NewsSource
from textblob import TextBlob
import re
import json

class BiasAnalysisService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Bias indicators
        self.bias_indicators = {
            "emotional_words": [
                "shocking", "outrageous", "disgusting", "amazing", "incredible",
                "terrible", "wonderful", "horrible", "fantastic", "appalling"
            ],
            "political_terms": [
                "liberal", "conservative", "progressive", "traditional",
                "radical", "moderate", "extreme", "mainstream"
            ],
            "loaded_language": [
                "clearly", "obviously", "undoubtedly", "certainly",
                "naturally", "of course", "everyone knows"
            ]
        }
    
    async def analyze_article_bias(self, content: str, source_bias_score: float) -> Dict[str, Any]:
        """Analyze bias in an article using AI and NLP"""
        try:
            # Basic NLP analysis
            blob = TextBlob(content)
            
            # Sentiment analysis
            sentiment_score = blob.sentiment.polarity
            
            # Detect biased words
            biased_words = self._detect_biased_words(content)
            
            # Calculate bias score based on multiple factors
            bias_score = self._calculate_bias_score(content, sentiment_score, source_bias_score, biased_words)
            
            # Determine emotional tone
            emotional_tone = self._determine_emotional_tone(sentiment_score, bias_score)
            
            # Generate neutral summary using AI
            neutral_summary = await self._generate_neutral_summary(content, source_bias_score)
            
            return {
                "bias_score": bias_score,
                "bias_direction": "left" if bias_score < -0.3 else "right" if bias_score > 0.3 else "neutral",
                "biased_words": biased_words,
                "emotional_tone": emotional_tone,
                "confidence_score": 0.8,
                "neutral_summary": neutral_summary,
                "recommendations": [
                    "Consider reading from multiple sources",
                    "Look for factual reporting",
                    "Check for balanced perspectives"
                ]
            }
            
        except Exception as e:
            print(f"Error analyzing article bias: {str(e)}")
            return {
                "bias_score": 0.0,
                "emotional_tone": "neutral",
                "biased_words": [],
                "neutral_summary": content[:200] + "..." if len(content) > 200 else content,
                "sentiment_score": 0.0
            }
    
    def _detect_biased_words(self, content: str) -> List[str]:
        """Detect biased words in content"""
        content_lower = content.lower()
        detected_words = []
        
        for category, words in self.bias_indicators.items():
            for word in words:
                if word.lower() in content_lower:
                    detected_words.append(word)
        
        return list(set(detected_words))
    
    def _calculate_bias_score(self, content: str, sentiment_score: float, source_bias_score: float, biased_words: List[str]) -> float:
        """Calculate overall bias score"""
        # Base score from source bias
        base_score = source_bias_score * 0.3
        
        # Sentiment contribution
        sentiment_contribution = sentiment_score * 0.2
        
        # Biased words contribution
        word_bias = len(biased_words) * 0.1
        if len(biased_words) > 5:
            word_bias = 0.5  # Cap at 0.5
        
        # Content length normalization
        content_length_factor = min(len(content) / 1000, 1.0)
        
        # Calculate final bias score (-5 to +5 scale)
        bias_score = base_score + sentiment_contribution + word_bias
        bias_score = max(-5.0, min(5.0, bias_score))
        
        return round(bias_score, 2)
    
    def _determine_emotional_tone(self, sentiment_score: float, bias_score: float) -> str:
        """Determine emotional tone based on sentiment and bias"""
        if abs(sentiment_score) > 0.3 or abs(bias_score) > 2.0:
            if sentiment_score > 0 or bias_score > 0:
                return "positive"
            else:
                return "negative"
        else:
            return "neutral"
    
    async def _generate_neutral_summary(self, content: str, source_bias_score: float) -> str:
        """Generate neutral summary using OpenAI"""
        try:
            prompt = f"""
            Please provide a neutral, objective summary of the following news content. 
            Remove any emotional language, bias, or subjective opinions. 
            Focus on facts and present information in a balanced way.
            
            Content: {content[:1000]}
            
            Neutral Summary:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a neutral news summarizer. Provide objective, factual summaries without bias or emotional language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating neutral summary: {str(e)}")
            # Fallback to simple summary
            return content[:200] + "..." if len(content) > 200 else content
    
    async def generate_neutral_summary(self, content: str, source_bias_score: float) -> Dict[str, Any]:
        """Generate neutral summary with bias reduction score"""
        try:
            # Analyze original content
            original_analysis = await self.analyze_article_bias(content, source_bias_score)
            
            # Generate neutral summary
            neutral_summary = await self._generate_neutral_summary(content, source_bias_score)
            
            # Analyze neutral summary
            neutral_analysis = await self.analyze_article_bias(neutral_summary, 0.0)
            
            # Calculate bias reduction
            bias_reduction = abs(original_analysis["bias_score"]) - abs(neutral_analysis["bias_score"])
            bias_reduction_score = max(0, bias_reduction)
            
            return {
                "neutral_summary": neutral_summary,
                "bias_reduction_score": round(bias_reduction_score, 2),
                "original_bias_score": original_analysis["bias_score"],
                "neutral_bias_score": neutral_analysis["bias_score"]
            }
            
        except Exception as e:
            print(f"Error generating neutral summary: {str(e)}")
            return {
                "neutral_summary": content[:200] + "..." if len(content) > 200 else content,
                "bias_reduction_score": 0.0,
                "original_bias_score": 0.0,
                "neutral_bias_score": 0.0
            }
    
    async def detect_blindspots(self, db: Session) -> List[Dict[str, Any]]:
        """Detect news stories that are only covered by one side of the media"""
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            # Get recent articles (last 7 days)
            recent_date = datetime.now() - timedelta(days=7)
            
            # Get articles by political leaning
            left_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "left",
                Article.published_at >= recent_date
            ).all()
            
            center_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "center",
                Article.published_at >= recent_date
            ).all()
            
            right_articles = db.query(Article).join(NewsSource).filter(
                NewsSource.political_lean == "right",
                Article.published_at >= recent_date
            ).all()
            
            # Extract topics from each group
            left_topics = set(article.topic for article in left_articles if article.topic)
            center_topics = set(article.topic for article in center_articles if article.topic)
            right_topics = set(article.topic for article in right_articles if article.topic)
            
            # Find blindspots
            blindspots = []
            
            # Topics only covered by left
            left_only = left_topics - center_topics - right_topics
            for topic in left_only:
                blindspots.append({
                    "topic": topic,
                    "covered_by": "left",
                    "missing_from": ["center", "right"],
                    "articles": [a.title for a in left_articles if a.topic == topic][:3]
                })
            
            # Topics only covered by right
            right_only = right_topics - center_topics - left_topics
            for topic in right_only:
                blindspots.append({
                    "topic": topic,
                    "covered_by": "right",
                    "missing_from": ["center", "left"],
                    "articles": [a.title for a in right_articles if a.topic == topic][:3]
                })
            
            # Topics only covered by center
            center_only = center_topics - left_topics - right_topics
            for topic in center_only:
                blindspots.append({
                    "topic": topic,
                    "covered_by": "center",
                    "missing_from": ["left", "right"],
                    "articles": [a.title for a in center_articles if a.topic == topic][:3]
                })
            
            return blindspots
            
        except Exception as e:
            print(f"Error detecting blindspots: {str(e)}")
            return []
