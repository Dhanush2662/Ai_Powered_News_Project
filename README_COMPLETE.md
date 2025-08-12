# Bias News Checker - Complete News Analysis Platform

A comprehensive news analysis platform that helps users explore news from multiple perspectives by detecting political bias, generating neutral summaries, identifying blindspots, and verifying news using AI tools and APIs.

## 🎯 Project Goal

To create a comprehensive website that shows users both sides of the news by detecting political bias, generating neutral summaries, identifying blindspots, and verifying news using AI tools and APIs.

## ✨ Complete Feature Set (8 Features)

### ✅ **1. Aggregating News from Different Channels**
- **Multi-API Integration**: Combines NewsAPI, GNews, MediaStack, and CurrentsAPI
- **Real-time Updates**: Fetches latest news from multiple sources
- **Source Diversity**: Includes both global and local news sources
- **Content Filtering**: Filter by topic, source, and date
- **API Endpoints**: `/api/news/feed`, `/api/news/sources`, `/api/news/search`

### ✅ **2. Detecting Political Bias**
- **AI-Powered Analysis**: Uses OpenAI GPT-4 for advanced bias detection
- **NLP Analysis**: TextBlob and NLTK for sentiment and bias scoring
- **Multi-factor Scoring**: Combines source bias, content analysis, and emotional indicators
- **Neutral Summaries**: Generates unbiased versions of articles
- **Blindspot Detection**: Identifies missing perspectives
- **API Endpoints**: `/api/bias/analyze`, `/api/bias/summarize`, `/api/bias/blindspots`

### ✅ **3. Truth/Trustworthiness Score**
- **Confidence Scoring**: Calculates reliability scores for claims
- **Multi-source Verification**: Cross-references with multiple sources
- **Evidence Collection**: Gathers supporting evidence for claims
- **Verdict Classification**: True, False, Misleading, or Unverified
- **API Endpoints**: `/api/fact-check/verify`, `/api/fact-check/verify-url`

### ✅ **4. Fact-Checking Service**
- **Google Custom Search Integration**: Searches for verification sources
- **AI Analysis**: Uses OpenAI for claim verification
- **Evidence Ranking**: Prioritizes high-quality sources
- **URL Content Extraction**: Analyzes content from URLs
- **Batch Processing**: Handles multiple claims simultaneously
- **API Endpoints**: `/api/fact-check/verify`, `/api/fact-check/verify-url`, `/api/fact-check/batch`

### ✅ **5. Comparing How Channels Report the Same News**
- **Multi-source Comparison**: Compares coverage across different outlets
- **Bias Pattern Analysis**: Identifies bias patterns across sources
- **Coverage Balance**: Analyzes left/center/right coverage distribution
- **Timeline Analysis**: Tracks how stories evolve over time
- **Keyword Analysis**: Identifies common themes and differences
- **API Endpoints**: `/api/coverage/compare`, `/api/coverage/topic`, `/api/coverage/event`

### ✅ **6. Sentiment Analysis**
- **Multi-method Analysis**: Combines TextBlob, custom algorithms, and AI
- **Emotional Intensity**: Measures emotional intensity and tone
- **Word-based Analysis**: Identifies positive/negative words and intensifiers
- **Timeline Analysis**: Tracks sentiment changes throughout text
- **Confidence Scoring**: Calculates analysis confidence
- **Batch Processing**: Analyzes multiple texts simultaneously
- **API Endpoints**: `/api/sentiment/analyze`, `/api/sentiment/analyze-batch`, `/api/sentiment/trending`

### ✅ **7. Fake News Detection**
- **Multi-method Detection**: Content analysis, source credibility, AI analysis, and fact-checking
- **Pattern Recognition**: Identifies suspicious language patterns
- **Source Verification**: Checks domain credibility and trust indicators
- **Red Flag Detection**: Identifies specific warning signs
- **Risk Assessment**: Low, Medium, High risk classification
- **Recommendations**: Provides actionable advice
- **API Endpoints**: `/api/fake-news/detect`, `/api/fake-news/detect-batch`, `/api/fake-news/high-risk`

### ✅ **8. User Feedback System**
- **Multi-type Feedback**: Ratings, comments, reports, and helpful votes
- **Community Features**: User ratings and comments on articles
- **Feedback Analytics**: Statistics and trends analysis
- **Popular Articles**: Identifies most-discussed content
- **Controversial Content**: Finds articles with mixed ratings
- **User History**: Tracks user feedback history
- **API Endpoints**: `/api/feedback/submit`, `/api/feedback/article/{id}`, `/api/feedback/popular`

## 🏗️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Services**: OpenAI GPT-4, Google Generative AI
- **APIs**: NewsAPI, GNews, MediaStack, CurrentsAPI, Google Custom Search
- **NLP**: TextBlob, NLTK, scikit-learn
- **Authentication**: JWT tokens with bcrypt

### **Frontend**
- **Framework**: React.js with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **UI Components**: Custom components with responsive design

### **Infrastructure**
- **Database**: PostgreSQL
- **Caching**: Redis (optional)
- **File Storage**: Local storage with OCR support
- **Deployment**: Docker-ready

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- API Keys (OpenAI, NewsAPI, Google)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Start the server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# The database will be created automatically when you start the backend
# Or manually run:
python -c "from database.database import engine; from database import models; models.Base.metadata.create_all(bind=engine)"
```

## 📁 Project Structure

```
bias-news-checker/
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   ├── database/           # Database models and connection
│   └── main.py            # FastAPI application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # React page components
│   │   ├── components/    # Reusable components
│   │   └── api/          # API client functions
│   └── package.json
├── news_aggregator.py      # Multi-API news aggregator
├── test_all_features.py   # Comprehensive test suite
└── README_COMPLETE.md     # This file
```

## 🔧 API Endpoints

### News Aggregation
- `GET /api/news/feed` - Get aggregated news feed
- `GET /api/news/sources` - Get available news sources
- `GET /api/news/search` - Search news by topic/keyword

### Bias Analysis
- `POST /api/bias/analyze` - Analyze article bias
- `POST /api/bias/summarize` - Generate neutral summary
- `GET /api/bias/blindspots` - Detect missing perspectives

### Fact Checking
- `POST /api/fact-check/verify` - Verify a claim
- `POST /api/fact-check/verify-url` - Verify content from URL
- `POST /api/fact-check/batch` - Verify multiple claims

### Coverage Comparison
- `GET /api/coverage/compare` - Compare coverage by topic
- `GET /api/coverage/topic/{topic}` - Get topic coverage
- `GET /api/coverage/event/{event}` - Compare event coverage

### Sentiment Analysis
- `POST /api/sentiment/analyze` - Analyze text sentiment
- `POST /api/sentiment/analyze-batch` - Analyze multiple texts
- `GET /api/sentiment/trending` - Get sentiment trends

### Fake News Detection
- `POST /api/fake-news/detect` - Detect fake news in content
- `POST /api/fake-news/detect-batch` - Detect fake news in multiple articles
- `GET /api/fake-news/high-risk` - Get high-risk articles

### User Feedback
- `POST /api/feedback/submit` - Submit user feedback
- `GET /api/feedback/article/{id}` - Get article feedback
- `GET /api/feedback/popular` - Get popular articles
- `POST /api/feedback/vote-helpful` - Vote comment as helpful

## 🧪 Testing

### Run Comprehensive Tests
```bash
python test_all_features.py
```

This will test all 8 features and generate a detailed report.

### Individual Feature Tests
```bash
# Test news aggregation
curl http://localhost:8000/api/news/feed

# Test bias analysis
curl -X POST http://localhost:8000/api/bias/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Test article content"}'

# Test sentiment analysis
curl -X POST http://localhost:8000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a positive article."}'

# Test fake news detection
curl -X POST http://localhost:8000/api/fake-news/detect \
  -H "Content-Type: application/json" \
  -d '{"content": "BREAKING: You won\'t believe this SHOCKING news!"}'
```

## 💰 Cost Estimation

### Monthly API Costs (Estimated)
- **OpenAI API**: $50-100 (depending on usage)
- **NewsAPI**: $449 (Developer plan) or free tier
- **Google Custom Search**: $20-50 (depending on queries)
- **Other APIs**: $20-50
- **Total**: ~$540-650/month (or free tier alternatives)

### Free Tier Alternatives
- Use free API tiers where available
- Implement caching to reduce API calls
- Use GPT-3.5-turbo instead of GPT-4 for cost savings

## 🔒 Security Features

- **CORS Protection**: Configured for frontend domains
- **Input Validation**: Pydantic models for all endpoints
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Data Sanitization**: Input sanitization and validation

## 📊 Performance Features

- **Database Indexing**: Optimized database queries
- **Caching**: Redis caching for frequently accessed data
- **Async Processing**: Non-blocking API calls
- **Batch Processing**: Efficient handling of multiple requests
- **Pagination**: Large dataset handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs` when running the server
- Review the test results for troubleshooting

## 🎉 Success Metrics

All 8 required features have been successfully implemented and tested:

✅ **Feature 1**: News Aggregation - Working with 4 APIs  
✅ **Feature 2**: Bias Detection - AI-powered analysis  
✅ **Feature 3**: Truth/Trustworthiness - Confidence scoring  
✅ **Feature 4**: Fact-Checking - Multi-source verification  
✅ **Feature 5**: Coverage Comparison - Cross-source analysis  
✅ **Feature 6**: Sentiment Analysis - Multi-method analysis  
✅ **Feature 7**: Fake News Detection - Comprehensive detection  
✅ **Feature 8**: User Feedback - Community features  

The platform is now production-ready with all requested features fully functional!
