from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv
import os
from typing import Optional

from routers import news, fact_check, enhanced_news_router
from database.database import engine
from database import models
from utils.cache import clear_cache

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News Platform API",
    description="API for news feed, fact-checking, consensus scoring, and translation",
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

# Include only required routers
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(fact_check.router, prefix="/api/fact-check", tags=["fact-check"])
app.include_router(enhanced_news_router.router, tags=["enhanced-news"])

@app.get("/")
async def root():
    return {"message": "News Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/cache/clear")
async def clear_cache_endpoint(prefix: Optional[str] = Query(None, description="Cache prefix to clear. If not provided, all cache will be cleared.")):
    clear_cache(prefix)
    return {"message": f"Cache cleared successfully{f' for prefix: {prefix}' if prefix else ''}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
