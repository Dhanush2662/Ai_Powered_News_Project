import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bias_news.db")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-demo-key-for-testing")
    
    # Google
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
    
    # Existing News APIs
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
    MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY", "")
    CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")
    
    # New News APIs (only adding missing ones)
    NEWSAPI_ADDITIONAL_KEY = os.getenv("NEWSAPI_ADDITIONAL_KEY", "")
    NEWSDATA_IO_KEY = os.getenv("NEWSDATAIO_KEY", "")
    WORLDNEWS_API_KEY = os.getenv("WORLDNEWS_KEY", "")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    
    # Additional Premium APIs
    GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY", "")
    NYTIMES_API_KEY = os.getenv("NYTIMES_API_KEY", "")
    NYTIMES_API_KEY_2 = os.getenv("NYTIMES_API_KEY_2", "")
    
    # Cache
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 600))
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
