import asyncio
from datetime import datetime, timedelta
from database.database import SessionLocal
from database.models import Article, NewsSource
from sqlalchemy.orm import Session

def populate_sample_news():
    """Populate database with sample news articles"""
    db = SessionLocal()
    
    # Sample news articles
    sample_articles = [
        {
            "title": "India's Tech Sector Shows Strong Growth in Q4 2024",
            "content": "India's technology sector demonstrated remarkable resilience and growth in the fourth quarter of 2024, with major IT companies reporting strong earnings and increased demand for digital services.",
            "url": "https://example.com/india-tech-growth",
            "source_name": "Tech India Today",
            "published_at": datetime.now() - timedelta(hours=2),
            "is_indian": True,
            "bias_score": 0.2,
            "category": "technology"
        },
        {
            "title": "Indian Startups Raise Record $12 Billion in Funding This Year",
            "content": "Indian startups have raised a record $12 billion in funding this year, marking a significant milestone for the country's entrepreneurial ecosystem and innovation landscape.",
            "url": "https://example.com/startup-funding",
            "source_name": "Startup India News",
            "published_at": datetime.now() - timedelta(hours=4),
            "is_indian": True,
            "bias_score": 0.1,
            "category": "business"
        },
        {
            "title": "New AI Research Center Opens in Bangalore",
            "content": "A new artificial intelligence research center has opened in Bangalore, focusing on developing AI solutions for healthcare, agriculture, and education sectors in India.",
            "url": "https://example.com/ai-research-bangalore",
            "source_name": "AI India Weekly",
            "published_at": datetime.now() - timedelta(hours=6),
            "is_indian": True,
            "bias_score": 0.0,
            "category": "technology"
        },
        {
            "title": "Digital India Initiative Reaches 500 Million Users",
            "content": "The Digital India initiative has successfully reached 500 million users, marking a significant achievement in the country's digital transformation journey.",
            "url": "https://example.com/digital-india-milestone",
            "source_name": "Digital India Today",
            "published_at": datetime.now() - timedelta(hours=8),
            "is_indian": True,
            "bias_score": 0.15,
            "category": "technology"
        },
        {
            "title": "Indian Space Program Launches New Satellite",
            "content": "ISRO successfully launched a new communication satellite, enhancing India's space capabilities and strengthening the country's position in the global space industry.",
            "url": "https://example.com/isro-satellite-launch",
            "source_name": "Space India News",
            "published_at": datetime.now() - timedelta(hours=10),
            "is_indian": True,
            "bias_score": 0.05,
            "category": "science"
        },
        {
            "title": "Global Technology Trends for 2024",
            "content": "Experts predict major technology trends for 2024, including advances in artificial intelligence, quantum computing, and sustainable technology solutions.",
            "url": "https://example.com/global-tech-trends",
            "source_name": "Global Tech Review",
            "published_at": datetime.now() - timedelta(hours=12),
            "is_indian": False,
            "bias_score": 0.0,
            "category": "technology"
        },
        {
            "title": "Renewable Energy Adoption Accelerates Worldwide",
            "content": "Global adoption of renewable energy sources continues to accelerate, with solar and wind power leading the transition to sustainable energy solutions.",
            "url": "https://example.com/renewable-energy-global",
            "source_name": "Green Energy Today",
            "published_at": datetime.now() - timedelta(hours=14),
            "is_indian": False,
            "bias_score": 0.1,
            "category": "environment"
        },
        {
            "title": "Indian Fintech Companies Expand Globally",
            "content": "Several Indian fintech companies are expanding their operations globally, bringing innovative financial solutions to international markets.",
            "url": "https://example.com/indian-fintech-global",
            "source_name": "Fintech India",
            "published_at": datetime.now() - timedelta(hours=16),
            "is_indian": True,
            "bias_score": 0.2,
            "category": "business"
        }
    ]
    
    try:
        # Clear existing articles
        db.query(Article).delete()
        
        # Create a default news source if it doesn't exist
        default_source = db.query(NewsSource).filter_by(name="Sample News").first()
        if not default_source:
            default_source = NewsSource(
                name="Sample News",
                url="https://example.com",
                bias_score=0.0,
                political_lean="center",
                country="IN"
            )
            db.add(default_source)
            db.commit()
            db.refresh(default_source)
        
        # Add sample articles
        for article_data in sample_articles:
            # Remove fields that don't exist in Article model
            article_data_clean = {
                "title": article_data["title"],
                "content": article_data["content"],
                "url": article_data["url"],
                "published_at": article_data["published_at"],
                "topic": article_data["category"],
                "source_id": default_source.id
            }
            article = Article(**article_data_clean)
            db.add(article)
        
        db.commit()
        print(f"✅ Successfully added {len(sample_articles)} sample news articles to the database")
        
        # Verify articles were added
        count = db.query(Article).count()
        print(f"📊 Total articles in database: {count}")
        
        # Show some articles
        articles = db.query(Article).limit(3).all()
        print("\n📰 Sample articles:")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article.title}")
            print(f"   Source: {article.source.name if article.source else 'Unknown'}")
            print(f"   Topic: {article.topic}")
            print()
            
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_sample_news()