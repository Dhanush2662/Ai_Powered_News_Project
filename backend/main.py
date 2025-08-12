from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv
import os
from typing import Optional

from routers import news, bias_analysis, fact_check, coverage_comparison, sentiment_analysis, fake_news, feedback, enhanced_news
from database.database import engine
from database import models
from utils.cache import clear_cache

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bias News Checker API",
    description="API for detecting news bias, generating neutral summaries, and fact-checking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(enhanced_news.router, prefix="/api/enhanced-news", tags=["enhanced-news-aggregator"])
app.include_router(bias_analysis.router, prefix="/api/bias", tags=["bias-analysis"])
app.include_router(fact_check.router, prefix="/api/fact-check", tags=["fact-check"])
app.include_router(coverage_comparison.router, prefix="/api/coverage", tags=["coverage"])
app.include_router(sentiment_analysis.router, prefix="/api/sentiment", tags=["sentiment-analysis"])
app.include_router(fake_news.router, prefix="/api/fake-news", tags=["fake-news-detection"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["user-feedback"])

@app.get("/")
async def root():
    return {"message": "Bias News Checker API", "version": "1.0.0", "demo": "Visit /demo for Enhanced News Aggregator demo"}

@app.get("/demo")
async def demo():
    """Redirect to the enhanced news demo page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/enhanced_news_demo.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/cache/clear")
async def clear_cache_endpoint(prefix: Optional[str] = Query(None, description="Cache prefix to clear. If not provided, all cache will be cleared.")):
    """Clear cache with the given prefix or all cache if no prefix is provided"""
    deleted = clear_cache(prefix)
    return {"status": "success", "message": f"Cleared {deleted} cache entries", "prefix": prefix or "all"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
