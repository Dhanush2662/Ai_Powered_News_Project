import axios from 'axios';

const API_KEY = '5eaaaccf09ae4096b235a28fd7ff5367';
const BASE_URL = 'https://newsapi.org/v2/everything';
const BACKEND_URL = 'http://localhost:8000'; // Our backend API

export const fetchNews = async (query = 'technology') => {
  try {
    const response = await axios.get(BASE_URL, {
      params: {
        q: query,
        sortBy: 'publishedAt',
        language: 'en',
        apiKey: API_KEY,
      },
    });
    return response.data.articles;
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
      timeout: 10000, // 10 second timeout
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
