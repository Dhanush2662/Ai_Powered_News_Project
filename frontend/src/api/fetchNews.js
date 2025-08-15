import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

// Updated to use enhanced backend API with Indian news prioritization
export const fetchNews = async (query = 'technology') => {
  try {
    const response = await fetchFromAPI(`/api/news/feed?topic=${encodeURIComponent(query)}&limit=50&focus_indian=true`);
    return response.articles || [];
  } catch (error) {
    console.error('Error fetching news:', error);
    return [];
  }
};

export const fetchFromAPI = async (endpoint, options = {}) => {
  try {
    const url = `${BACKEND_URL}${endpoint}`;
    console.log('Fetching from:', url);
    
    const response = await axios({
      method: options.method || 'GET',
      url: url,
      data: options.data,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      timeout: 15000, // 15 second timeout for aggregated news
    });
    
    console.log('API Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching from API:', error);
    console.error('Error details:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });
    throw error;
  }
};
