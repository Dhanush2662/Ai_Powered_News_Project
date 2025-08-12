# Redis Caching Implementation

## Overview

This document describes the Redis caching implementation added to the Bias News Checker backend. The caching mechanism is designed to improve performance by storing frequently accessed data, reducing the number of API calls to external news services, and decreasing response times.

## Features

- **Configurable TTL**: Cache time-to-live is configurable via environment variables
- **Prefix-based Caching**: Different data types use different cache prefixes for better organization
- **Development Mode**: Uses FakeRedis for development/testing without requiring a Redis server
- **Production Mode**: Supports real Redis server for production environments
- **Cache Clearing**: Utilities for clearing specific cache prefixes or all cache

## Configuration

The following environment variables control the caching behavior:

```
# Caching Configuration
CACHE_TTL_SECONDS=600           # Default cache TTL in seconds (10 minutes)
USE_REAL_REDIS=False            # Whether to use real Redis or FakeRedis
REDIS_HOST=localhost            # Redis server host
REDIS_PORT=6379                 # Redis server port
REDIS_PASSWORD=                 # Redis server password (if required)
REDIS_DB=0                      # Redis database number
```

## Implementation Details

### Cache Decorator

The caching mechanism is implemented as a decorator that can be applied to any async function:

```python
@cache(prefix="news_api")
async def fetch_news_from_api(self, source_id: str, category: str = "general") -> List[dict]:
    # Function implementation
```

The decorator handles:
- Generating a unique cache key based on function name, prefix, and arguments
- Checking if data exists in cache
- Returning cached data if available
- Executing the function and caching the result if not in cache

### Cached Functions

The following functions in the NewsService class are now cached:

- `fetch_news_from_api` - Caches news from NewsAPI for specific sources
- `fetch_indian_news_from_gnews` - Caches Indian news from GNews API
- `fetch_indian_news_from_newsapi` - Caches Indian news from NewsAPI
- `fetch_indian_news_from_mediastack` - Caches Indian news from Mediastack API
- `fetch_indian_news_from_currents` - Caches Indian news from Currents API
- `get_enhanced_aggregated_news` - Caches aggregated news from all sources

## Testing

A test script is provided to verify the caching functionality:

```bash
python test_cache.py
```

This script demonstrates:
- Cache hit/miss behavior
- Performance improvement with caching
- Cache key generation
- Cache clearing

## Production Deployment

For production deployment:

1. Set `USE_REAL_REDIS=True` in your environment variables
2. Configure Redis connection parameters (host, port, password, etc.)
3. Adjust `CACHE_TTL_SECONDS` based on your data freshness requirements

## Troubleshooting

- If caching doesn't seem to be working, check that Redis is running (if `USE_REAL_REDIS=True`)
- Verify that the cache TTL is not set too low
- Check for errors in the Redis connection
- Use the `clear_cache()` function to reset the cache if needed