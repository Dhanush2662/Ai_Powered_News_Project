import asyncio
from services.news_service import NewsService
from database.database import SessionLocal

async def test_news_fetch():
    db = SessionLocal()
    service = NewsService()
    
    print("🔄 Fetching news articles...")
    articles = await service.get_enhanced_aggregated_news(db, topic='technology', limit=10)
    
    print(f"✅ Fetched {len(articles)} articles")
    
    for i, article in enumerate(articles[:5]):
        print(f"{i+1}. {article.get('title', 'No title')}")
        print(f"   Source: {article.get('source_name', 'Unknown')}")
        print(f"   Indian: {article.get('is_indian', False)}")
        print()
    
    db.close()
    return len(articles)

if __name__ == "__main__":
    result = asyncio.run(test_news_fetch())
    print(f"Total articles fetched: {result}")