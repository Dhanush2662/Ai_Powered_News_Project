import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  CalendarIcon,
  GlobeAltIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { fetchNews } from '../api/fetchNews';
import { fetchFromAPI } from '../api/fetchNews';
import CountryFilter from '../components/CountryFilter';

interface Article {
  title: string;
  description: string;
  url: string;
  urlToImage?: string;
  source: {
    name: string;
    id?: string;
  };
  publishedAt: string;
  content?: string;
  author?: string;
}

interface CountryArticle {
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
}

const NewsFeed: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [countryArticles, setCountryArticles] = useState<CountryArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('technology');
  const [selectedCountry, setSelectedCountry] = useState('in');
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState<'topic' | 'country'>('topic');

  const topicsList = [
    'technology', 'politics', 'business', 'health', 'science', 
    'sports', 'entertainment', 'world', 'environment', 'education'
  ];

  useEffect(() => {
    if (viewMode === 'topic') {
      loadNews();
    } else {
      loadCountryNews();
    }
  }, [selectedTopic, selectedCountry, viewMode]);

  const loadNews = async () => {
    try {
      setLoading(true);
      const newsArticles = await fetchNews(selectedTopic);
      setArticles(newsArticles || []);
      if (newsArticles && newsArticles.length > 0) {
        toast.success(`Loaded ${newsArticles.length} articles about ${selectedTopic}`);
      } else {
        toast.error('No articles found for this topic');
      }
    } catch (error) {
      toast.error('Error fetching news');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCountryNews = async () => {
    try {
      setLoading(true);
      const response = await fetchFromAPI(`/api/news/country/${selectedCountry}`);
      if (response && response.articles) {
        setCountryArticles(response.articles);
        toast.success(`Loaded ${response.articles.length} articles from ${selectedCountry.toUpperCase()}`);
      } else {
        toast.error('No articles found for this country');
      }
    } catch (error) {
      toast.error('Error fetching country news');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    if (viewMode === 'topic') {
      await loadNews();
    } else {
      await loadCountryNews();
    }
    setRefreshing(false);
  };

  const filteredArticles = viewMode === 'topic' 
    ? articles.filter(article => {
        const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             article.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
      })
    : countryArticles.filter(article => {
        const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             article.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesSearch;
      });

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="loading-spinner"></div>
          <p className="text-gray-600">Loading news articles...</p>
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
          <p className="text-gray-600">Stay informed with real-time news from multiple sources</p>
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

      {/* View Mode Toggle */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setViewMode('topic')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'topic'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Topic-based News
        </button>
        <button
          onClick={() => setViewMode('country')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'country'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Country-based News
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
        {viewMode === 'topic' && (
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
        )}

        {/* Country Filter */}
        {viewMode === 'country' && (
          <CountryFilter 
            selectedCountry={selectedCountry} 
            onSelect={setSelectedCountry} 
          />
        )}
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.map((article, index) => (
          <div key={index} className="card hover:shadow-lg transition-all duration-200">
            {article.urlToImage && (
              <img
                src={article.urlToImage}
                alt={article.title}
                className="w-full h-48 object-cover rounded-t-lg"
              />
            )}
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {article.title}
              </h3>
              <p className="text-gray-600 mb-4 line-clamp-3">
                {viewMode === 'topic' ? article.description : article.description}
              </p>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{viewMode === 'topic' ? article.source.name : article.source}</span>
                <span className="flex items-center">
                  <CalendarIcon className="h-4 w-4 mr-1" />
                  {format(new Date(viewMode === 'topic' ? article.publishedAt : article.published_at), 'MMM dd, yyyy')}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <Link
                  to={`/bias-analysis?url=${encodeURIComponent(article.url)}`}
                  className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  Analyze Bias
                </Link>
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
            {searchTerm ? 'Try adjusting your search terms.' : 'Try selecting a different topic or country.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
