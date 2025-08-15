import openai
import os
from typing import List, Dict, Any
from collections import Counter
import asyncio
from datetime import datetime, timedelta

class ConsensusScoreService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def calculate_consensus_score(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate consensus score based on article similarity and agreement"""
        if len(articles) < 2:
            return {
                "consensus_score": 0.0,
                "agreement_level": "insufficient_data",
                "similar_articles": [],
                "conflicting_viewpoints": []
            }
        
        # Group similar articles
        similar_groups = await self._group_similar_articles(articles)
        
        # Calculate consensus based on agreement
        consensus_score = self._calculate_score(similar_groups)
        
        return {
            "consensus_score": consensus_score,
            "agreement_level": self._get_agreement_level(consensus_score),
            "similar_articles": similar_groups,
            "total_articles_analyzed": len(articles)
        }
    
    async def _group_similar_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group articles by similarity using AI"""
        groups = []
        
        for i, article in enumerate(articles):
            # Simple grouping by keywords and title similarity
            title_words = set(article.get('title', '').lower().split())
            
            # Find similar articles
            similar = []
            for j, other_article in enumerate(articles):
                if i != j:
                    other_words = set(other_article.get('title', '').lower().split())
                    similarity = len(title_words.intersection(other_words)) / len(title_words.union(other_words))
                    
                    if similarity > 0.3:  # 30% similarity threshold
                        similar.append({
                            "title": other_article.get('title'),
                            "source": other_article.get('source'),
                            "similarity": round(similarity, 2)
                        })
            
            if similar:
                groups.append({
                    "main_article": article.get('title'),
                    "similar_articles": similar,
                    "group_size": len(similar) + 1
                })
        
        return groups
    
    def _calculate_score(self, similar_groups: List[Dict[str, Any]]) -> float:
        """Calculate consensus score from 0.0 to 1.0"""
        if not similar_groups:
            return 0.0
        
        # Higher score for more articles covering similar topics
        total_articles = sum(group['group_size'] for group in similar_groups)
        largest_group = max(group['group_size'] for group in similar_groups)
        
        # Consensus score based on largest agreement group
        consensus_score = (largest_group / total_articles) if total_articles > 0 else 0.0
        
        return round(min(consensus_score, 1.0), 2)
    
    def _get_agreement_level(self, score: float) -> str:
        """Convert numeric score to agreement level"""
        if score >= 0.8:
            return "high_consensus"
        elif score >= 0.6:
            return "moderate_consensus"
        elif score >= 0.4:
            return "low_consensus"
        else:
            return "no_consensus"