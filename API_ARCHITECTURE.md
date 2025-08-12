# Bias News Checker - API Architecture

## 🎯 Project Overview
A comprehensive news bias detection and fact-checking platform that helps users explore news from multiple perspectives.

## 📡 API Endpoints & Logic

### **1. News Feed APIs**
```python
# GET /news-feed
# Purpose: Get aggregated news articles from multiple sources
# Logic: 
# - Fetch from NewsAPI (real news)
# - Apply bias scoring to each article
# - Return formatted articles with bias indicators
```

### **2. Bias Analysis APIs**
```python
# POST /analyze-bias
# Purpose: Analyze political bias in news articles
# Logic:
# - Use OpenAI GPT-4 for advanced bias detection
# - TextBlob/NLTK for sentiment analysis
# - Custom bias detection algorithms
# - Return bias score, direction, biased words, neutral summary
```

### **3. Fact Checking APIs**
```python
# POST /fact-check
# Purpose: Verify claims and statements
# Logic:
# - Use OpenAI GPT-4 for fact verification
# - Google Custom Search API for source verification
# - Return verdict (true/false/misleading), evidence, sources
```

### **4. Coverage Comparison APIs**
```python
# POST /compare-coverage
# Purpose: Compare how different sources cover the same topic
# Logic:
# - Use NewsAPI to get articles from different sources
# - Analyze bias patterns across sources
# - Identify blindspots and missing perspectives
```

## 🔧 External APIs Required

### **1. OpenAI API (Primary AI)**
- **Purpose**: Bias analysis, fact checking, neutral summary generation
- **Endpoints Used**: 
  - `openai.ChatCompletion.create()` for GPT-4
- **Cost**: ~$0.03 per 1K tokens
- **Rate Limits**: 3 requests per minute (free tier)

### **2. NewsAPI (News Aggregation)**
- **Purpose**: Get real news articles from multiple sources
- **Endpoints Used**:
  - `/v2/everything` - Search all articles
  - `/v2/top-headlines` - Get top headlines
  - `/v2/sources` - Get available sources
- **Cost**: $449/month (Developer plan)
- **Rate Limits**: 1,000 requests/day

### **3. Google Custom Search API**
- **Purpose**: Fact verification and source checking
- **Endpoints Used**:
  - `/customsearch/v1` - Search for verification sources
- **Cost**: $5 per 1,000 queries
- **Rate Limits**: 10,000 queries/day

### **4. Google Generative AI (Gemini)**
- **Purpose**: Alternative AI for bias analysis
- **Endpoints Used**:
  - `google.generativeai.generate_content()`
- **Cost**: Free tier available
- **Rate Limits**: 15 requests/minute

## 🗄️ Database Schema

### **Tables:**
1. **news_sources** - Store source information and bias ratings
2. **articles** - Store article data and metadata
3. **bias_analyses** - Store bias analysis results
4. **fact_checks** - Store fact checking results
5. **coverage_comparisons** - Store coverage analysis results

## 🔄 API Workflow

### **News Feed Workflow:**
```
1. User requests news feed
2. Backend calls NewsAPI for articles
3. For each article:
   - Analyze bias using OpenAI
   - Store results in database
   - Return formatted response
```

### **Bias Analysis Workflow:**
```
1. User submits article URL/content
2. Backend extracts text content
3. Send to OpenAI for bias analysis
4. Process results and generate neutral summary
5. Return comprehensive analysis
```

### **Fact Check Workflow:**
```
1. User submits claim
2. Backend uses OpenAI to analyze claim
3. Use Google Custom Search to find supporting evidence
4. Cross-reference with multiple sources
5. Return verdict with evidence
```

## 💰 Cost Estimation

### **Monthly Costs:**
- **OpenAI API**: $50-100 (depending on usage)
- **NewsAPI**: $449 (Developer plan)
- **Google Custom Search**: $20-50 (depending on queries)
- **Total**: ~$520-600/month

### **Free Alternatives:**
- **NewsAPI**: Use free tier (100 requests/day)
- **OpenAI**: Use GPT-3.5-turbo instead of GPT-4
- **Google Custom Search**: Use free tier (100 queries/day)

## 🚀 Implementation Priority

### **Phase 1 (MVP - Current)**
- ✅ Mock APIs for testing
- ✅ Basic frontend functionality
- ✅ Simple bias detection logic

### **Phase 2 (Real APIs)**
- 🔄 Integrate NewsAPI for real news
- 🔄 Integrate OpenAI for bias analysis
- 🔄 Add database storage

### **Phase 3 (Advanced Features)**
- 🔄 Google Custom Search for fact checking
- 🔄 Advanced bias detection algorithms
- 🔄 Coverage comparison features

## 🔧 Environment Variables Needed

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# NewsAPI
NEWS_API_KEY=your-news-api-key

# Google APIs
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-custom-search-engine-id

# Database
DATABASE_URL=postgresql://user:pass@localhost/bias_news

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 📊 API Response Formats

### **News Feed Response:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "source": "Source Name",
      "url": "https://article-url.com",
      "bias_score": -0.3,
      "published_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 10
}
```

### **Bias Analysis Response:**
```json
{
  "bias_score": -0.3,
  "bias_direction": "left",
  "biased_words": ["liberal", "progressive"],
  "emotional_tone": "neutral",
  "confidence_score": 0.8,
  "neutral_summary": "Neutral summary...",
  "recommendations": ["Read multiple sources"]
}
```

### **Fact Check Response:**
```json
{
  "claim": "Original claim",
  "verdict": "true",
  "confidence_score": 0.9,
  "evidence": ["Evidence 1", "Evidence 2"],
  "sources": ["https://source1.com", "https://source2.com"],
  "explanation": "Detailed explanation..."
}
```

## 🎯 Next Steps

1. **Get API Keys**: Sign up for OpenAI, NewsAPI, and Google APIs
2. **Replace Mock APIs**: Integrate real APIs one by one
3. **Add Database**: Set up PostgreSQL for data storage
4. **Test & Deploy**: Test with real data and deploy

This architecture provides a scalable foundation for your Bias News Checker project!
