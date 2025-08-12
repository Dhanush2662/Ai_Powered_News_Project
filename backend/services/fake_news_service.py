import openai
import os
from typing import Dict, List, Any
import re
import json
import httpx
from urllib.parse import urlparse
from datetime import datetime, timedelta

class FakeNewsDetectionService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Fake news indicators
        self.suspicious_patterns = [
            r'\b(clickbait|shocking|you won\'t believe|amazing|incredible)\b',
            r'\b(conspiracy|cover-up|secret|hidden truth)\b',
            r'\b(urgent|breaking|exclusive|just in)\b',
            r'\b(100%|guaranteed|proven|scientific breakthrough)\b',
            r'\b(they don\'t want you to know|mainstream media won\'t tell you)\b'
        ]
        
        # Credible news sources (whitelist)
        self.credible_sources = [
            'reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'pbs.org',
            'theguardian.com', 'nytimes.com', 'washingtonpost.com',
            'wsj.com', 'bloomberg.com', 'cnn.com', 'foxnews.com',
            'abcnews.go.com', 'cbsnews.com', 'nbcnews.com'
        ]
        
        # Suspicious domains
        self.suspicious_domains = [
            'fake-news', 'conspiracy', 'truth-bomb', 'real-news',
            'alternative-news', 'underground-news'
        ]
    
    async def detect_fake_news(self, content: str, url: str = None, source: str = None) -> Dict[str, Any]:
        """Comprehensive fake news detection"""
        try:
            # Multiple detection methods
            content_analysis = self._analyze_content_patterns(content)
            source_credibility = self._check_source_credibility(url, source)
            ai_analysis = await self._ai_fake_news_analysis(content, url, source)
            fact_checking = await self._basic_fact_checking(content)
            
            # Combine all analyses
            overall_score = self._calculate_fake_news_score(
                content_analysis, source_credibility, ai_analysis, fact_checking
            )
            
            return {
                "fake_news_score": overall_score,
                "risk_level": self._get_risk_level(overall_score),
                "confidence_score": self._calculate_confidence(
                    content_analysis, source_credibility, ai_analysis, fact_checking
                ),
                "detection_methods": {
                    "content_analysis": content_analysis,
                    "source_credibility": source_credibility,
                    "ai_analysis": ai_analysis,
                    "fact_checking": fact_checking
                },
                "red_flags": self._identify_red_flags(content, url, source),
                "recommendations": self._generate_recommendations(overall_score),
                "verdict": self._get_verdict(overall_score)
            }
            
        except Exception as e:
            print(f"Error in fake news detection: {str(e)}")
            return {
                "fake_news_score": 0.5,
                "risk_level": "medium",
                "confidence_score": 0.0,
                "detection_methods": {},
                "red_flags": [],
                "recommendations": ["Unable to analyze content"],
                "verdict": "unverified"
            }
    
    def _analyze_content_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze content for suspicious patterns"""
        content_lower = content.lower()
        
        # Check for suspicious patterns
        pattern_matches = []
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                pattern_matches.extend(matches)
        
        # Check for excessive punctuation
        exclamation_count = content.count('!')
        question_count = content.count('?')
        caps_count = sum(1 for c in content if c.isupper())
        
        # Calculate suspiciousness score
        pattern_score = len(pattern_matches) * 0.1
        punctuation_score = (exclamation_count * 0.05) + (question_count * 0.02)
        caps_score = (caps_count / len(content)) * 0.3 if content else 0
        
        total_score = min(pattern_score + punctuation_score + caps_score, 1.0)
        
        return {
            "suspicious_patterns": pattern_matches,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "caps_ratio": round(caps_count / len(content), 3) if content else 0,
            "suspiciousness_score": round(total_score, 3)
        }
    
    def _check_source_credibility(self, url: str, source: str) -> Dict[str, Any]:
        """Check source credibility"""
        credibility_score = 0.5  # Default neutral score
        
        if url:
            domain = urlparse(url).netloc.lower()
            
            # Check if domain is in credible sources
            if any(credible in domain for credible in self.credible_sources):
                credibility_score = 0.9
            elif any(suspicious in domain for suspicious in self.suspicious_domains):
                credibility_score = 0.1
            else:
                # Check domain age and other factors
                credibility_score = self._assess_domain_credibility(domain)
        
        if source:
            # Check source name for suspicious keywords
            source_lower = source.lower()
            if any(suspicious in source_lower for suspicious in self.suspicious_domains):
                credibility_score = min(credibility_score, 0.3)
        
        return {
            "credibility_score": round(credibility_score, 3),
            "source_type": self._classify_source_type(url, source),
            "domain_analysis": self._analyze_domain(url) if url else {},
            "trust_indicators": self._identify_trust_indicators(url, source)
        }
    
    def _assess_domain_credibility(self, domain: str) -> float:
        """Assess domain credibility based on various factors"""
        # Simple heuristic - can be enhanced with domain age checking
        if len(domain) < 10:
            return 0.3  # Short domains are suspicious
        elif domain.count('.') > 2:
            return 0.4  # Too many subdomains
        else:
            return 0.6  # Neutral
    
    def _classify_source_type(self, url: str, source: str) -> str:
        """Classify the type of news source"""
        if not url and not source:
            return "unknown"
        
        text = (url or source).lower()
        
        if any(credible in text for credible in self.credible_sources):
            return "established_media"
        elif any(suspicious in text for suspicious in self.suspicious_domains):
            return "suspicious_source"
        elif "blog" in text or "wordpress" in text:
            return "blog"
        elif "social" in text or "facebook" in text or "twitter" in text:
            return "social_media"
        else:
            return "unknown"
    
    def _analyze_domain(self, url: str) -> Dict[str, Any]:
        """Analyze domain characteristics"""
        if not url:
            return {}
        
        domain = urlparse(url).netloc
        return {
            "domain": domain,
            "domain_length": len(domain),
            "subdomain_count": domain.count('.'),
            "has_https": url.startswith('https'),
            "is_shortened": len(domain) < 15
        }
    
    def _identify_trust_indicators(self, url: str, source: str) -> List[str]:
        """Identify trust indicators"""
        indicators = []
        
        if url and url.startswith('https'):
            indicators.append("https_secure")
        
        if source and any(credible in source.lower() for credible in self.credible_sources):
            indicators.append("established_source")
        
        if url and any(credible in url.lower() for credible in self.credible_sources):
            indicators.append("reputable_domain")
        
        return indicators
    
    async def _ai_fake_news_analysis(self, content: str, url: str, source: str) -> Dict[str, Any]:
        """Use AI to analyze fake news indicators"""
        try:
            prompt = f"""
            Analyze the following news content for fake news indicators:
            
            Content: {content[:1000]}
            URL: {url or 'Not provided'}
            Source: {source or 'Not provided'}
            
            Return a JSON object with:
            - fake_news_probability (0-1)
            - suspicious_indicators (list of suspicious elements)
            - credibility_issues (list of credibility problems)
            - recommendation (string)
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fake news detection expert. Analyze content for suspicious patterns, credibility issues, and fake news indicators."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {
                    "fake_news_probability": 0.5,
                    "suspicious_indicators": [],
                    "credibility_issues": [],
                    "recommendation": "Unable to analyze with AI"
                }
        except Exception as e:
            print(f"AI fake news analysis error: {str(e)}")
            return {
                "fake_news_probability": 0.5,
                "suspicious_indicators": [],
                "credibility_issues": [],
                "recommendation": "AI analysis failed"
            }
    
    async def _basic_fact_checking(self, content: str) -> Dict[str, Any]:
        """Basic fact checking using keyword analysis"""
        # Extract potential claims
        claims = self._extract_potential_claims(content)
        
        # Check for unverifiable statements
        unverifiable_count = sum(1 for claim in claims if self._is_unverifiable(claim))
        
        fact_check_score = 1.0 - (unverifiable_count / len(claims)) if claims else 0.5
        
        return {
            "fact_check_score": round(fact_check_score, 3),
            "potential_claims": claims[:5],  # Top 5 claims
            "unverifiable_claims": [claim for claim in claims if self._is_unverifiable(claim)][:3],
            "verifiable_claims": [claim for claim in claims if not self._is_unverifiable(claim)][:3]
        }
    
    def _extract_potential_claims(self, content: str) -> List[str]:
        """Extract potential factual claims from content"""
        sentences = re.split(r'[.!?]+', content)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only substantial sentences
                # Look for factual statements
                if any(keyword in sentence.lower() for keyword in [
                    'study shows', 'research indicates', 'scientists say',
                    'according to', 'reports show', 'data reveals',
                    'statistics show', 'experts say', 'officials confirm'
                ]):
                    claims.append(sentence)
        
        return claims
    
    def _is_unverifiable(self, claim: str) -> bool:
        """Check if a claim is likely unverifiable"""
        unverifiable_indicators = [
            'anonymous sources', 'insiders say', 'rumors suggest',
            'some people say', 'it is believed', 'allegedly',
            'supposedly', 'reportedly', 'according to sources'
        ]
        
        return any(indicator in claim.lower() for indicator in unverifiable_indicators)
    
    def _calculate_fake_news_score(self, content_analysis: Dict, source_credibility: Dict, 
                                 ai_analysis: Dict, fact_checking: Dict) -> float:
        """Calculate overall fake news score"""
        # Weighted combination of all analyses
        content_score = content_analysis.get("suspiciousness_score", 0.5)
        source_score = 1.0 - source_credibility.get("credibility_score", 0.5)  # Invert credibility
        ai_score = ai_analysis.get("fake_news_probability", 0.5)
        fact_score = 1.0 - fact_checking.get("fact_check_score", 0.5)  # Invert fact check
        
        # Weighted average
        overall_score = (
            content_score * 0.25 +
            source_score * 0.25 +
            ai_score * 0.3 +
            fact_score * 0.2
        )
        
        return round(overall_score, 3)
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score > 0.7:
            return "high"
        elif score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, content_analysis: Dict, source_credibility: Dict,
                            ai_analysis: Dict, fact_checking: Dict) -> float:
        """Calculate confidence in fake news detection"""
        # Higher confidence if all methods agree
        scores = [
            content_analysis.get("suspiciousness_score", 0.5),
            1.0 - source_credibility.get("credibility_score", 0.5),
            ai_analysis.get("fake_news_probability", 0.5),
            1.0 - fact_checking.get("fact_check_score", 0.5)
        ]
        
        # Calculate variance
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Lower variance = higher confidence
        confidence = max(0.3, 1.0 - variance)
        
        return round(confidence, 3)
    
    def _identify_red_flags(self, content: str, url: str, source: str) -> List[str]:
        """Identify specific red flags"""
        red_flags = []
        
        # Content red flags
        if content.count('!') > 5:
            red_flags.append("Excessive exclamation marks")
        
        if any(pattern in content.lower() for pattern in self.suspicious_patterns):
            red_flags.append("Suspicious language patterns")
        
        # Source red flags
        if url and any(suspicious in url.lower() for suspicious in self.suspicious_domains):
            red_flags.append("Suspicious domain")
        
        if source and len(source) < 5:
            red_flags.append("Unclear source")
        
        return red_flags
    
    def _generate_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on fake news score"""
        recommendations = []
        
        if score > 0.7:
            recommendations.extend([
                "Exercise extreme caution with this content",
                "Verify claims with multiple reliable sources",
                "Check if the source is known for spreading misinformation"
            ])
        elif score > 0.4:
            recommendations.extend([
                "Verify important claims with additional sources",
                "Check the credibility of the source",
                "Look for corroborating evidence"
            ])
        else:
            recommendations.extend([
                "Content appears relatively trustworthy",
                "Still verify important claims with multiple sources"
            ])
        
        return recommendations
    
    def _get_verdict(self, score: float) -> str:
        """Get final verdict"""
        if score > 0.7:
            return "likely_fake"
        elif score > 0.4:
            return "suspicious"
        else:
            return "likely_real"
    
    async def batch_detect_fake_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect fake news for multiple articles"""
        results = []
        
        for article in articles:
            content = article.get("content", "")
            url = article.get("url", "")
            source = article.get("source", "")
            
            detection = await self.detect_fake_news(content, url, source)
            results.append({
                "article_id": article.get("id"),
                "title": article.get("title"),
                "detection_result": detection
            })
        
        return results
