# Bias News Checker

A comprehensive website that helps users explore news from multiple perspectives by detecting political bias, generating neutral summaries, identifying blindspots, and verifying news using AI tools and APIs.

## 🎯 Project Goal

To create a website that shows users both sides of the news by detecting political bias, generating neutral summaries, identifying blindspots, and verifying news using AI tools and APIs.

## ✨ Main Features

- **News Aggregation**: Shows headlines from multiple sources (NDTV, Republic TV, etc.)
- **Bias Detection**: Detects bias score for each news source
- **Blindspot Detection**: Alerts users when a story is ignored by one side
- **Neutral Summary**: Converts emotional or politically slanted articles into objective summaries
- **Fact-Checking Agent**: Verifies news via Google Search API
- **Coverage Comparison**: Shows how different outlets report the same event

## 🏗️ Tech Stack

- **Frontend**: React.js with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **APIs**: NewsAPI, Google Search API, OpenAI GPT-4, Gemini
- **OCR**: Tesseract for image/PDF text extraction

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `.env` files in both backend and frontend directories with your API keys.

## 📁 Project Structure

```
bias-news-checker/
├── backend/                 # FastAPI backend
├── frontend/               # React frontend
├── database/              # Database schemas and migrations
├── docs/                  # Documentation
└── README.md
```

## 🔧 API Endpoints

- `GET /api/news` - Get aggregated news
- `POST /api/analyze-bias` - Analyze article bias
- `POST /api/summarize` - Generate neutral summary
- `POST /api/fact-check` - Verify news authenticity
- `GET /api/coverage-comparison` - Compare coverage across sources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License
