import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  CalendarIcon,
  GlobeAltIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { fetchFromAPI } from '../api/fetchNews';

interface Article {
  id?: number;
  title: string;
  content: string;
  url: string;
  published_at?: string;
  topic?: string;
  summary?: string;
  source_name: string;
  source_bias_score?: number;
  is_indian?: boolean;
  api_source?: string;
  urlToImage?: string;
}

const NewsFeed: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('technology');
  const [refreshing, setRefreshing] = useState(false);

  const topicsList = [
    'technology', 'politics', 'business', 'health', 'science', 
    'sports', 'entertainment', 'world', 'environment', 'education'
  ];

  useEffect(() => {
    loadNews();
  }, [selectedTopic]);

  const loadNews = async () => {
    try {
      setLoading(true);
      // Use enhanced news feed endpoint with Indian news prioritization
      const response = await fetchFromAPI(`/api/news/feed?topic=${encodeURIComponent(selectedTopic)}&limit=50&focus_indian=true`);
      
      if (response && response.articles) {
        setArticles(response.articles);
        toast.success(`Loaded ${response.articles.length} articles about ${selectedTopic} (${response.indian_count} Indian, ${response.international_count} International)`);
      } else {
        toast.error('No articles found for this topic');
      }
    } catch (error) {
      toast.error('Error fetching news'); // This is the error you're seeing
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadNews();
    setRefreshing(false);
  };

  const filteredArticles = articles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         article.content.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="loading-spinner"></div>
          <p className="text-gray-600">Loading news articles from multiple sources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">News Feed</h1>
          <p className="text-gray-600">Stay informed with real-time news from multiple sources (Indian news prioritized)</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-primary flex items-center space-x-2"
        >
          <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh News'}</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Topic Filter */}
        <div className="flex items-center space-x-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {topicsList.map((topic) => (
              <option key={topic} value={topic}>
                {topic.charAt(0).toUpperCase() + topic.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.map((article, index) => (
          <div key={index} className={`card hover:shadow-lg transition-all duration-200 ${
            article.is_indian ? 'border-l-4 border-l-orange-500' : ''
          }`}>
            {article.urlToImage && (
              <img
                src={article.urlToImage}
                alt={article.title}
                className="w-full h-48 object-cover rounded-t-lg"
              />
            )}
            <div className="p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                  {article.title}
                </h3>
                {article.is_indian && (
                  <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                    🇮🇳 Indian
                  </span>
                )}
              </div>
              <p className="text-gray-600 mb-4 line-clamp-3">
                {article.content}
              </p>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{article.source_name}</span>
                <span className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  {article.published_at ? format(new Date(article.published_at), 'MMM dd, yyyy') : 'Recent'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">
                  Source: {article.api_source || 'API'}
                </span>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  Read More →
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredArticles.length === 0 && (
        <div className="text-center py-12">
          <GlobeAltIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
          <p className="text-gray-600">
            {searchTerm ? 'Try adjusting your search terms.' : 'Try selecting a different topic.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
