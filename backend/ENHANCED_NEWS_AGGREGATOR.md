# Enhanced News Aggregator - India Priority

## 🎯 Overview

The Enhanced News Aggregator is a sophisticated news collection system that prioritizes India-focused news first, followed by news from countries with significant Indian populations. It aggregates news from multiple APIs and RSS feeds to provide comprehensive coverage.

## 🌟 Key Features

### 1. **India-First Priority System**
- India news gets highest priority (priority score: 1000+)
- Other countries ranked by Indian population significance
- Smart sorting by priority and recency

### 2. **Multi-API Integration**
- **NewsAPI**: Top headlines by country
- **GNews**: Global news with country filtering
- **Mediastack**: News aggregation service
- **Currents API**: Keyword-based news search
- **RSS Feeds**: Direct feeds from major Indian news sources

### 3. **Country Coverage**
- 🇮🇳 **India** (Priority 1) - Primary focus
- 🇺🇸 **USA** (Priority 2) - Large Indian-American population
- 🇦🇪 **UAE** (Priority 3) - Major Indian expat community
- 🇬🇧 **UK** (Priority 4) - Significant Indian-British population
- 🇨🇦 **Canada** (Priority 5) - Growing Indian-Canadian community
- 🇦🇺 **Australia** (Priority 6) - Indian-Australian population
- 🇸🇬 **Singapore** (Priority 7) - Indian-Singaporean community

### 4. **Smart Content Filtering**
- Indian keyword detection for relevance
- Duplicate article removal
- Content quality filtering
- Date-based sorting

### 5. **Robust Error Handling**
- Graceful API failure handling
- Automatic fallback to backup sources
- Parallel processing for speed
- Comprehensive logging

## 🚀 API Endpoints

### Main Endpoints

#### 1. **Prioritized Feed** - `/api/enhanced-news/prioritized-feed`
```http
GET /api/enhanced-news/prioritized-feed?limit=100&use_cache=true
```
**Description**: Main endpoint that returns India headlines first, followed by other countries.

**Parameters**:
- `limit` (int): Maximum articles to return (default: 100)
- `use_cache` (bool): Whether to use cached results (default: true)

**Response**:
```json
{
  "status": "success",
  "total_articles": 85,
  "articles": [...],
  "sections": {
    "india_headlines": 45,
    "other_countries": 40
  }
}
```

#### 2. **India Headlines** - `/api/enhanced-news/india-headlines`
```http
GET /api/enhanced-news/india-headlines?limit=50
```
**Description**: Get India-focused headlines only.

#### 3. **Countries with Indian Presence** - `/api/enhanced-news/countries-with-indian-presence`
```http
GET /api/enhanced-news/countries-with-indian-presence?limit_per_country=25&countries=us,ae,gb
```
**Description**: Get news from countries with significant Indian populations.

#### 4. **Specific Country** - `/api/enhanced-news/country/{country_code}`
```http
GET /api/enhanced-news/country/us?limit=50
```
**Description**: Get news for a specific country.

#### 5. **RSS Feeds** - `/api/enhanced-news/rss-feeds/{country_code}`
```http
GET /api/enhanced-news/rss-feeds/in
```
**Description**: Get RSS feeds for India or UK.

### Utility Endpoints

#### 6. **API Status** - `/api/enhanced-news/api-status`
```http
GET /api/enhanced-news/api-status
```
**Description**: Check configuration status of all APIs.

#### 7. **Test Aggregation** - `/api/enhanced-news/test-aggregation`
```http
GET /api/enhanced-news/test-aggregation
```
**Description**: Test endpoint to verify aggregation is working.

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```env
# News APIs
NEWS_API_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_key_here
MEDIASTACK_API_KEY=your_mediastack_key_here
CURRENTS_API_KEY=your_currents_key_here
```

### API Key Sources

1. **NewsAPI**: [https://newsapi.org/](https://newsapi.org/)
   - Free tier: 1,000 requests/day
   - Supports country filtering

2. **GNews**: [https://gnews.io/](https://gnews.io/)
   - Free tier: 100 requests/day
   - Good for international coverage

3. **Mediastack**: [https://mediastack.com/](https://mediastack.com/)
   - Free tier: 500 requests/month
   - Reliable news aggregation

4. **Currents API**: [https://currentsapi.services/](https://currentsapi.services/)
   - Free tier: 600 requests/day
   - Keyword-based search

## 📊 Data Structure

### Article Object
```json
{
  "title": "Article headline",
  "description": "Article summary",
  "url": "https://example.com/article",
  "published_at": "2024-01-15T10:30:00Z",
  "source": "NewsAPI - Times of India",
  "api_source": "newsapi",
  "image_url": "https://example.com/image.jpg",
  "content": "Article content preview",
  "country": "in",
  "country_name": "India",
  "priority": 1,
  "section": "India Headlines",
  "priority_score": 1000.123456,
  "indian_relevance": true
}
```

## 🎨 Frontend Demo

Access the interactive demo at: `http://localhost:8000/demo`

### Demo Features
- **Prioritized Feed**: Shows India news first, then other countries
- **India Headlines**: India-only news
- **Other Countries**: News from countries with Indian populations
- **RSS Feeds**: Direct RSS feed integration
- **API Status**: Configuration checker
- **Responsive Design**: Works on mobile and desktop

## 🔄 Caching

The system includes intelligent caching:
- **Cache Duration**: 10 minutes for prioritized feed
- **Cache Keys**: Unique per endpoint and parameters
- **Cache Clearing**: Available via `/api/cache/clear`

## 🚦 Usage Examples

### JavaScript/Frontend Integration

```javascript
// Get prioritized news feed
async function getPrioritizedNews() {
  const response = await fetch('/api/enhanced-news/prioritized-feed?limit=50');
  const data = await response.json();
  
  if (data.status === 'success') {
    console.log(`Total articles: ${data.total_articles}`);
    console.log(`India headlines: ${data.sections.india_headlines}`);
    console.log(`Other countries: ${data.sections.other_countries}`);
    
    // Process articles
    data.articles.forEach(article => {
      console.log(`${article.section}: ${article.title}`);
    });
  }
}

// Get India-only headlines
async function getIndiaNews() {
  const response = await fetch('/api/enhanced-news/india-headlines?limit=30');
  const data = await response.json();
  return data.articles;
}

// Get news from specific country
async function getCountryNews(countryCode) {
  const response = await fetch(`/api/enhanced-news/country/${countryCode}?limit=25`);
  const data = await response.json();
  return data.articles;
}
```

### Python Integration

```python
import httpx
import asyncio

async def get_prioritized_news():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'http://localhost:8000/api/enhanced-news/prioritized-feed',
            params={'limit': 50, 'use_cache': False}
        )
        return response.json()

# Usage
news_data = asyncio.run(get_prioritized_news())
print(f"Total articles: {news_data['total_articles']}")
```

## 🔍 Testing

Run the test suite:

```bash
cd backend
python test_enhanced_news.py
```

### Test Coverage
- ✅ API Status Check
- ✅ India Headlines
- ✅ Countries with Indian Presence
- ✅ RSS Feeds
- ✅ Aggregation Test
- ✅ Prioritized Feed

## 🛠️ Technical Implementation

### Architecture
```
Enhanced News Aggregator
├── services/enhanced_news_aggregator.py  # Core aggregation logic
├── routers/enhanced_news.py              # API endpoints
├── static/enhanced_news_demo.html        # Frontend demo
└── test_enhanced_news.py                 # Test suite
```

### Key Classes
- **EnhancedNewsAggregator**: Main aggregation service
- **Priority System**: Country-based priority scoring
- **Multi-API Handler**: Parallel API processing
- **RSS Parser**: RSS feed integration
- **Cache Manager**: Intelligent caching system

### Performance Features
- **Parallel Processing**: All APIs called simultaneously
- **Smart Caching**: 10-minute cache with prefix-based clearing
- **Error Recovery**: Graceful handling of API failures
- **Duplicate Removal**: Title-based deduplication
- **Priority Sorting**: India-first, then by country priority and date

## 🎯 Benefits

1. **India-Centric**: Prioritizes Indian news and interests
2. **Comprehensive**: Multiple APIs and RSS feeds
3. **Reliable**: Robust error handling and fallbacks
4. **Fast**: Parallel processing and intelligent caching
5. **Scalable**: Easy to add new countries or APIs
6. **User-Friendly**: Clean API design and demo interface

## 🔮 Future Enhancements

- **AI-Powered Relevance**: Use AI to score Indian relevance
- **Real-time Updates**: WebSocket support for live updates
- **Personalization**: User preference-based filtering
- **Analytics**: Usage tracking and popular topics
- **Mobile App**: Native mobile application
- **Social Integration**: Social media news sources

## 📞 Support

For issues or questions:
1. Check the test suite: `python test_enhanced_news.py`
2. Verify API status: `GET /api/enhanced-news/api-status`
3. Check server logs for detailed error information
4. Ensure all API keys are properly configured in `.env`

---

**🎉 Your Enhanced News Aggregator is ready to deliver India-prioritized news from around the world!**