import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  ChartBarIcon,
  GlobeAltIcon,
  ArrowTrendingUpIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface CoverageComparisonResult {
  topic: string;
  sources: {
    name: string;
    bias_rating: string;
    articles: Array<{
      title: string;
      url: string;
      sentiment: string;
      keywords: string[];
    }>;
  }[];
  blindspots: string[];
  trending_topics: string[];
}

const CoverageComparison: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [eventName, setEventName] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [result, setResult] = useState<CoverageComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<string[]>([]);

  useEffect(() => {
    fetchAvailableSources();
    fetchTrendingTopics();
  }, []);

  const fetchAvailableSources = async () => {
    try {
      const response = await fetch('/api/news/sources');
      if (response.ok) {
        const data = await response.json();
        setAvailableSources(data.sources || []);
      }
    } catch (error) {
      console.error('Error fetching sources:', error);
    }
  };

  const fetchTrendingTopics = async () => {
    try {
      const response = await fetch('/api/coverage/trending');
      if (response.ok) {
        const data = await response.json();
        setTrendingTopics(data.trending_topics || []);
      }
    } catch (error) {
      console.error('Error fetching trending topics:', error);
    }
  };

  const handleTopicComparison = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic to compare');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/coverage/topic/${encodeURIComponent(topic.trim())}`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Coverage comparison completed');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Comparison failed');
      }
    } catch (error) {
      toast.error('Error performing comparison');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEventComparison = async () => {
    if (!eventName.trim()) {
      toast.error('Please enter an event name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/coverage/event/${encodeURIComponent(eventName.trim())}`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Event coverage analysis completed');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Analysis failed');
      }
    } catch (error) {
      toast.error('Error analyzing event coverage');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSourceComparison = async () => {
    if (selectedSources.length < 2) {
      toast.error('Please select at least 2 sources to compare');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/coverage/sources/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sources: selectedSources,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Source comparison completed');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Comparison failed');
      }
    } catch (error) {
      toast.error('Error comparing sources');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBiasColor = (biasRating: string) => {
    switch (biasRating.toLowerCase()) {
      case 'left':
        return 'bias-left';
      case 'right':
        return 'bias-right';
      default:
        return 'bias-center';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Coverage Comparison</h1>
        <p className="text-gray-600">Compare how different sources cover the same events and identify blindspots</p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="space-y-6">
          {/* Topic Comparison */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compare Topic Coverage</h3>
            <div className="flex gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Enter a topic (e.g., 'climate change', 'elections')"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={handleTopicComparison}
                disabled={loading || !topic.trim()}
                className="btn-primary flex items-center justify-center"
              >
                {loading ? (
                  <div className="loading-spinner mr-2"></div>
                ) : (
                  <ChartBarIcon className="h-5 w-5 mr-2" />
                )}
                Compare
              </button>
            </div>
          </div>

          {/* Event Comparison */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Analyze Event Coverage</h3>
            <div className="flex gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Enter an event name (e.g., '2024 Presidential Debate')"
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={handleEventComparison}
                disabled={loading || !eventName.trim()}
                className="btn-primary flex items-center justify-center"
              >
                {loading ? (
                  <div className="loading-spinner mr-2"></div>
                ) : (
                  <EyeIcon className="h-5 w-5 mr-2" />
                )}
                Analyze
              </button>
            </div>
          </div>

          {/* Source Comparison */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Compare Specific Sources</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {availableSources.map((source) => (
                  <label key={source} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedSources.includes(source)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSources([...selectedSources, source]);
                        } else {
                          setSelectedSources(selectedSources.filter(s => s !== source));
                        }
                      }}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">{source}</span>
                  </label>
                ))}
              </div>
              <button
                onClick={handleSourceComparison}
                disabled={loading || selectedSources.length < 2}
                className="btn-primary flex items-center justify-center"
              >
                {loading ? (
                  <div className="loading-spinner mr-2"></div>
                ) : (
                  <GlobeAltIcon className="h-5 w-5 mr-2" />
                )}
                Compare Sources
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Trending Topics */}
      {trendingTopics.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Trending Topics</h3>
          <div className="flex flex-wrap gap-2">
            {trendingTopics.map((topic, index) => (
              <button
                key={index}
                onClick={() => {
                  setTopic(topic);
                  handleTopicComparison();
                }}
                className="flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-sm transition-colors duration-200"
              >
                <TrendingUpIcon className="h-4 w-4" />
                <span>{topic}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Sources Comparison */}
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Coverage Analysis: {result.topic}
            </h3>
            
            <div className="space-y-6">
              {result.sources.map((source, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-medium text-gray-900">{source.name}</h4>
                    <span className={`bias-indicator ${getBiasColor(source.bias_rating)}`}>
                      {source.bias_rating}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    {source.articles.map((article, articleIndex) => (
                      <div key={articleIndex} className="bg-gray-50 p-3 rounded-lg">
                        <h5 className="font-medium text-gray-900 mb-2">{article.title}</h5>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Sentiment: {article.sentiment}</span>
                          <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-700"
                          >
                            Read Article
                          </a>
                        </div>
                        {article.keywords.length > 0 && (
                          <div className="mt-2">
                            <span className="text-xs text-gray-500">Keywords: </span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {article.keywords.map((keyword, keywordIndex) => (
                                <span
                                  key={keywordIndex}
                                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
                                >
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Blindspots */}
          {result.blindspots.length > 0 && (
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Identified Blindspots</h3>
              <div className="space-y-2">
                {result.blindspots.map((blindspot, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <EyeIcon className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">{blindspot}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <ChartBarIcon className="h-6 w-6 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">How to use this tool</h3>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>• Enter a topic to see how different sources cover it</li>
              <li>• Analyze specific events to understand coverage patterns</li>
              <li>• Compare selected news sources side by side</li>
              <li>• Identify blindspots - stories ignored by certain sources</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoverageComparison;
