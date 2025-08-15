from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

app = FastAPI(
    title="Bias News Checker API",
    description="Mock API for testing Bias News Checker frontend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class BiasAnalysisRequest(BaseModel):
    text: str

class BiasAnalysisResponse(BaseModel):
    bias_score: float
    bias_direction: str
    biased_words: List[str]
    emotional_tone: str
    confidence_score: float
    neutral_summary: str
    recommendations: List[str]

class FactCheckRequest(BaseModel):
    claim: str

class FactCheckResponse(BaseModel):
    claim: str
    verdict: str
    confidence_score: float
    evidence: List[str]
    sources: List[str]
    explanation: str

class CoverageComparisonRequest(BaseModel):
    topic: str

class CoverageComparisonResponse(BaseModel):
    topic: str
    sources: List[Dict[str, Any]]
    blindspots: List[str]
    trending_topics: List[str]

# Mock Data
MOCK_ARTICLES = [
    {
        "id": 1,
        "title": "Government Announces New Economic Policy",
        "source": "NDTV",
        "time": "2 hours ago",
        "url": "https://ndtv.com/article1",
        "bias_score": -0.3
    },
    {
        "id": 2,
        "title": "Opposition Criticizes Government's Latest Decision",
        "source": "Republic TV",
        "time": "1 hour ago",
        "url": "https://republictv.com/article2",
        "bias_score": 0.4
    },
    {
        "id": 3,
        "title": "Experts Weigh In on Climate Change Policy",
        "source": "The Hindu",
        "time": "3 hours ago",
        "url": "https://thehindu.com/article3",
        "bias_score": 0.0
    },
    {
        "id": 4,
        "title": "Technology Sector Shows Strong Growth",
        "source": "Times of India",
        "time": "4 hours ago",
        "url": "https://timesofindia.com/article4",
        "bias_score": 0.1
    },
    {
        "id": 5,
        "title": "Healthcare Reform Bill Passes Parliament",
        "source": "Hindustan Times",
        "time": "5 hours ago",
        "url": "https://hindustantimes.com/article5",
        "bias_score": -0.2
    }
]

MOCK_SOURCES = [
    {"name": "NDTV", "bias_rating": "left"},
    {"name": "Republic TV", "bias_rating": "right"},
    {"name": "The Hindu", "bias_rating": "center"},
    {"name": "Times of India", "bias_rating": "center"},
    {"name": "Hindustan Times", "bias_rating": "left"}
]

# Endpoints
@app.get("/")
async def root():
    return {"message": "Bias News Checker API is running!"}

@app.get("/news-feed")
async def get_news_feed():
    """Get mock news articles"""
    return {
        "articles": MOCK_ARTICLES,
        "total": len(MOCK_ARTICLES),
        "message": "Mock news feed data"
    }

@app.post("/analyze-bias", response_model=BiasAnalysisResponse)
async def analyze_bias(request: BiasAnalysisRequest):
    """Analyze bias in text"""
    text = request.text.lower()
    
    # Simple bias detection logic
    left_words = ["liberal", "progressive", "reform", "change", "equality"]
    right_words = ["conservative", "traditional", "patriot", "freedom", "business"]
    
    left_count = sum(1 for word in left_words if word in text)
    right_count = sum(1 for word in right_words if word in text)
    
    # Calculate bias score
    total_words = left_count + right_count
    if total_words == 0:
        bias_score = 0.0
        bias_direction = "neutral"
    else:
        bias_score = (right_count - left_count) / total_words
        if bias_score > 0.2:
            bias_direction = "right"
        elif bias_score < -0.2:
            bias_direction = "left"
        else:
            bias_direction = "neutral"
    
    # Detect biased words
    biased_words = []
    for word in left_words + right_words:
        if word in text:
            biased_words.append(word)
    
    # Determine emotional tone
    emotional_words = ["amazing", "terrible", "wonderful", "horrible", "incredible"]
    emotional_count = sum(1 for word in emotional_words if word in text)
    emotional_tone = "emotional" if emotional_count > 0 else "neutral"
    
    # Generate neutral summary
    sentences = request.text.split('.')
    neutral_summary = f"Summary: {sentences[0] if sentences else request.text[:100]}..."
    
    return BiasAnalysisResponse(
        bias_score=round(bias_score, 2),
        bias_direction=bias_direction,
        biased_words=biased_words,
        emotional_tone=emotional_tone,
        confidence_score=0.8,
        neutral_summary=neutral_summary,
        recommendations=[
            "Consider reading from multiple sources",
            "Look for factual reporting",
            "Check for balanced perspectives"
        ]
    )

@app.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: FactCheckRequest):
    """Fact check a claim"""
    claim = request.claim.lower()
    
    # Simple fact checking logic
    true_keywords = ["confirmed", "verified", "official", "announced", "approved"]
    false_keywords = ["fake", "hoax", "debunked", "false", "untrue"]
    
    true_count = sum(1 for word in true_keywords if word in claim)
    false_count = sum(1 for word in false_keywords if word in claim)
    
    if true_count > false_count:
        verdict = "true"
        explanation = "This claim appears to be supported by available evidence."
    elif false_count > true_count:
        verdict = "false"
        explanation = "This claim has been debunked by multiple sources."
    else:
        verdict = "unverified"
        explanation = "Insufficient evidence to verify this claim."
    
    return FactCheckResponse(
        claim=request.claim,
        verdict=verdict,
        confidence_score=0.7,
        evidence=[
            "Multiple sources confirm this information",
            "Official statements support this claim",
            "Expert analysis validates the claim"
        ],
        sources=[
            "https://example.com/source1",
            "https://example.com/source2"
        ],
        explanation=explanation
    )

@app.post("/compare-coverage", response_model=CoverageComparisonResponse)
async def compare_coverage(request: CoverageComparisonRequest):
    """Compare how different sources cover a topic"""
    topic = request.topic
    
    # Generate mock coverage data
    sources = []
    for i, source in enumerate(MOCK_SOURCES[:3]):
        articles = [
            {
                "title": f"{source['name']} covers {topic}",
                "url": f"https://{source['name'].lower().replace(' ', '')}.com/article{i+1}",
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "keywords": [topic, "news", "coverage"]
            }
        ]
        sources.append({
            "name": source["name"],
            "bias_rating": source["bias_rating"],
            "articles": articles
        })
    
    return CoverageComparisonResponse(
        topic=topic,
        sources=sources,
        blindspots=[
            f"Some sources may not be covering {topic} comprehensively",
            "Consider checking multiple perspectives"
        ],
        trending_topics=[
            "Climate Change",
            "Economic Policy",
            "Healthcare Reform",
            "Technology News"
        ]
    )

@app.get("/news/sources")
async def get_sources():
    """Get available news sources"""
    return {
        "sources": [source["name"] for source in MOCK_SOURCES],
        "total": len(MOCK_SOURCES)
    }

@app.get("/coverage/trending")
async def get_trending_topics():
    """Get trending topics"""
    return {
        "trending_topics": [
            "Climate Change",
            "Economic Policy", 
            "Healthcare Reform",
            "Technology News",
            "Education Policy"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed from 8000 to 8001
