import openai
import os
from typing import List, Dict, Any
import re

class BiasAnalysisService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "demo-key")
        if api_key and api_key != "demo-key":
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.use_openai = True
        else:
            self.openai_client = None
            self.use_openai = False
            print("⚠️  OpenAI API key not set. Using fallback analysis.")
        
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
            # Simple sentiment analysis
            sentiment_score = self._simple_sentiment(content)
            
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
                "bias_direction": "neutral",
                "biased_words": [],
                "emotional_tone": "neutral",
                "neutral_summary": content[:200] + "..." if len(content) > 200 else content,
                "confidence_score": 0.5,
                "recommendations": ["Unable to analyze"]
            }
    
    def _simple_sentiment(self, content: str) -> float:
        """Simple sentiment analysis without external libraries"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "positive", "success", "win"]
        negative_words = ["bad", "terrible", "awful", "horrible", "negative", "fail", "lose", "problem"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
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
        
        # Calculate final bias score (-1 to +1 scale)
        bias_score = base_score + sentiment_contribution + word_bias
        bias_score = max(-1.0, min(1.0, bias_score))
        
        return round(bias_score, 2)
    
    def _determine_emotional_tone(self, sentiment_score: float, bias_score: float) -> str:
        """Determine emotional tone based on sentiment and bias"""
        if abs(sentiment_score) > 0.3 or abs(bias_score) > 0.5:
            if sentiment_score > 0 or bias_score > 0:
                return "positive"
            else:
                return "negative"
        else:
            return "neutral"
    
    async def _generate_neutral_summary(self, content: str, source_bias_score: float) -> str:
        """Generate neutral summary using OpenAI or fallback"""
        if not self.use_openai or not self.openai_client:
            # Fallback summary generation
            return self._generate_fallback_summary(content)
        
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
            return self._generate_fallback_summary(content)
    
    def _generate_fallback_summary(self, content: str) -> str:
        """Generate a simple fallback summary without AI"""
        # Simple text processing to create a basic summary
        sentences = content.split('.')
        if len(sentences) > 3:
            summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = content[:300] + "..." if len(content) > 300 else content
        
        return f"Summary: {summary}"
    
    async def generate_neutral_summary(self, content: str, source_bias_score: float) -> Dict[str, Any]:
        """Generate neutral summary with bias reduction score"""
        try:
            # Generate neutral summary
            neutral_summary = await self._generate_neutral_summary(content, source_bias_score)
            
            return {
                "neutral_summary": neutral_summary,
                "bias_reduction_score": 0.3,
                "original_bias_score": 0.0,
                "neutral_bias_score": 0.0
            }
            
        except Exception as e:
            print(f"Error generating neutral summary: {str(e)}")
            return {
                "neutral_summary": content[:200] + "..." if len(content) > 200 else content,
                "bias_reduction_score": 0.0,
                "original_bias_score": 0.0,
                "neutral_bias_score": 0.0
            }
    
    async def detect_blindspots(self, db) -> List[Dict[str, Any]]:
        """Detect news stories that are only covered by one side of the media"""
        return [
            {
                "topic": "Sample Topic",
                "covered_by": "left",
                "missing_from": ["center", "right"],
                "articles": ["Sample Article 1", "Sample Article 2"]
            }
        ]
