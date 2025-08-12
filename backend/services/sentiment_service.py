import openai
import os
from typing import Dict, List, Any
from textblob import TextBlob
import re
import json

class SentimentAnalysisService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Sentiment indicators
        self.positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "positive", "success", "win", "victory", "hope", "progress",
            "improve", "better", "strong", "powerful", "confident"
        ]
        
        self.negative_words = [
            "bad", "terrible", "awful", "horrible", "disaster", "failure",
            "negative", "loss", "defeat", "fear", "danger", "threat",
            "worse", "weak", "powerless", "hopeless", "despair"
        ]
        
        self.emotional_intensifiers = [
            "very", "extremely", "incredibly", "absolutely", "completely",
            "totally", "utterly", "entirely", "thoroughly"
        ]
    
    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Comprehensive sentiment analysis using multiple methods"""
        try:
            # Basic TextBlob analysis
            blob = TextBlob(content)
            textblob_sentiment = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Custom word-based analysis
            word_sentiment = self._analyze_word_sentiment(content)
            
            # Emotional intensity analysis
            emotional_intensity = self._analyze_emotional_intensity(content)
            
            # AI-powered sentiment analysis
            ai_sentiment = await self._ai_sentiment_analysis(content)
            
            # Combine all analyses
            overall_sentiment = self._combine_sentiment_scores(
                textblob_sentiment, word_sentiment, ai_sentiment
            )
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_label": self._get_sentiment_label(overall_sentiment),
                "confidence_score": self._calculate_confidence(
                    textblob_sentiment, word_sentiment, ai_sentiment
                ),
                "detailed_analysis": {
                    "textblob": {
                        "polarity": round(textblob_sentiment, 3),
                        "subjectivity": round(textblob_subjectivity, 3)
                    },
                    "word_based": word_sentiment,
                    "emotional_intensity": emotional_intensity,
                    "ai_analysis": ai_sentiment
                },
                "emotional_indicators": {
                    "positive_words": word_sentiment["positive_words"],
                    "negative_words": word_sentiment["negative_words"],
                    "intensifiers": emotional_intensity["intensifiers"]
                },
                "sentiment_timeline": self._extract_sentiment_timeline(content)
            }
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {
                "overall_sentiment": 0.0,
                "sentiment_label": "neutral",
                "confidence_score": 0.0,
                "detailed_analysis": {},
                "emotional_indicators": {},
                "sentiment_timeline": []
            }
    
    def _analyze_word_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment based on positive/negative word counting"""
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return {
                "score": 0.0,
                "positive_words": [],
                "negative_words": [],
                "positive_ratio": 0.0,
                "negative_ratio": 0.0
            }
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        # Calculate score (-1 to 1)
        score = (positive_ratio - negative_ratio) * 2
        
        return {
            "score": round(score, 3),
            "positive_words": [word for word in words if word in self.positive_words],
            "negative_words": [word for word in words if word in self.negative_words],
            "positive_ratio": round(positive_ratio, 3),
            "negative_ratio": round(negative_ratio, 3)
        }
    
    def _analyze_emotional_intensity(self, content: str) -> Dict[str, Any]:
        """Analyze emotional intensity and intensifiers"""
        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)
        
        intensifier_count = sum(1 for word in words if word in self.emotional_intensifiers)
        exclamation_count = content.count('!')
        question_count = content.count('?')
        
        # Calculate intensity score
        intensity_score = (intensifier_count * 0.1) + (exclamation_count * 0.05) + (question_count * 0.02)
        intensity_score = min(intensity_score, 1.0)  # Cap at 1.0
        
        return {
            "intensity_score": round(intensity_score, 3),
            "intensifiers": [word for word in words if word in self.emotional_intensifiers],
            "exclamation_count": exclamation_count,
            "question_count": question_count
        }
    
    async def _ai_sentiment_analysis(self, content: str) -> Dict[str, Any]:
        """Use AI for advanced sentiment analysis"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the following text. Return a JSON object with: sentiment_score (-1 to 1), primary_emotion, emotional_intensity (low/medium/high), and key_emotional_phrases."
                    },
                    {
                        "role": "user",
                        "content": content[:1000]  # Limit to first 1000 chars
                    }
                ],
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {
                    "sentiment_score": 0.0,
                    "primary_emotion": "neutral",
                    "emotional_intensity": "low",
                    "key_emotional_phrases": []
                }
        except Exception as e:
            print(f"AI sentiment analysis error: {str(e)}")
            return {
                "sentiment_score": 0.0,
                "primary_emotion": "neutral",
                "emotional_intensity": "low",
                "key_emotional_phrases": []
            }
    
    def _combine_sentiment_scores(self, textblob: float, word_based: Dict, ai_analysis: Dict) -> float:
        """Combine multiple sentiment scores into overall score"""
        word_score = word_based.get("score", 0.0)
        ai_score = ai_analysis.get("sentiment_score", 0.0)
        
        # Weighted average
        combined_score = (textblob * 0.4) + (word_score * 0.3) + (ai_score * 0.3)
        
        return round(combined_score, 3)
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_confidence(self, textblob: float, word_based: Dict, ai_analysis: Dict) -> float:
        """Calculate confidence in sentiment analysis"""
        # Higher confidence if all methods agree
        scores = [textblob, word_based.get("score", 0.0), ai_analysis.get("sentiment_score", 0.0)]
        
        # Calculate variance
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Lower variance = higher confidence
        confidence = max(0.5, 1.0 - variance)
        
        return round(confidence, 3)
    
    def _extract_sentiment_timeline(self, content: str) -> List[Dict[str, Any]]:
        """Extract sentiment changes throughout the text"""
        sentences = re.split(r'[.!?]+', content)
        timeline = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                blob = TextBlob(sentence.strip())
                timeline.append({
                    "sentence_index": i,
                    "sentence": sentence.strip()[:100] + "..." if len(sentence.strip()) > 100 else sentence.strip(),
                    "sentiment": round(blob.sentiment.polarity, 3),
                    "subjectivity": round(blob.sentiment.subjectivity, 3)
                })
        
        return timeline[:10]  # Limit to first 10 sentences
    
    async def analyze_multiple_texts(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze sentiment across multiple texts"""
        results = []
        overall_sentiment = 0.0
        
        for text in texts:
            analysis = await self.analyze_sentiment(text)
            results.append(analysis)
            overall_sentiment += analysis["overall_sentiment"]
        
        if results:
            overall_sentiment /= len(results)
        
        return {
            "overall_sentiment": round(overall_sentiment, 3),
            "sentiment_label": self._get_sentiment_label(overall_sentiment),
            "individual_analyses": results,
            "sentiment_distribution": self._calculate_sentiment_distribution(results)
        }
    
    def _calculate_sentiment_distribution(self, analyses: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of sentiment labels"""
        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        
        for analysis in analyses:
            label = analysis.get("sentiment_label", "neutral")
            distribution[label] += 1
        
        return distribution
