// API Configuration
const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
  // News Feed
  NEWS_FEED: `${API_BASE_URL}/news-feed`,
  
  // Bias Analysis
  ANALYZE_BIAS: `${API_BASE_URL}/analyze-bias`,
  
  // Fact Check
  FACT_CHECK: `${API_BASE_URL}/fact-check`,
  
  // Coverage Comparison
  COMPARE_COVERAGE: `${API_BASE_URL}/compare-coverage`,
  
  // Additional endpoints
  NEWS_SOURCES: `${API_BASE_URL}/news/sources`,
  TRENDING_TOPICS: `${API_BASE_URL}/coverage/trending`,
};

export default API_ENDPOINTS;
