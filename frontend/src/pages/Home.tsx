import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  ShieldCheckIcon, 
  ChartBarIcon, 
  DocumentTextIcon,
  EyeIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import CountryFilter from '../components/CountryFilter';
import { fetchFromAPI } from '../api/fetchNews';

interface Article {
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
}

const Home: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState('in');
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchCountryNews = async (countryCode: string) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetchFromAPI(`/api/news/country/${countryCode}`);
      if (response && response.articles) {
        setArticles(response.articles);
      }
    } catch (err) {
      setError('Failed to fetch news. Please try again.');
      console.error('Error fetching country news:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCountryNews(selectedCountry);
  }, [selectedCountry]);

  const handleCountryChange = (countryCode: string) => {
    setSelectedCountry(countryCode);
  };

  const features = [
    {
      icon: MagnifyingGlassIcon,
      title: 'Bias Detection',
      description: 'Analyze news articles for political bias using advanced AI algorithms and NLP techniques.',
      href: '/bias-analysis'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Fact Checking',
      description: 'Verify claims and statements using multiple sources and AI-powered analysis.',
      href: '/fact-check'
    },
    {
      icon: ChartBarIcon,
      title: 'Coverage Comparison',
      description: 'Compare how different sources cover the same events and identify blindspots.',
      href: '/coverage-comparison'
    },
    {
      icon: DocumentTextIcon,
      title: 'Neutral Summaries',
      description: 'Generate balanced, neutral summaries that reduce bias and present multiple perspectives.',
      href: '/bias-analysis'
    },
    {
      icon: EyeIcon,
      title: 'Blindspot Detection',
      description: 'Identify stories that are ignored by certain political leanings or news sources.',
      href: '/coverage-comparison'
    },
    {
      icon: CheckCircleIcon,
      title: 'Multi-Source Verification',
      description: 'Cross-reference information across multiple reliable sources for accuracy.',
      href: '/fact-check'
    }
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-16 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-2xl">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Discover Truth in News
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-primary-100">
            Detect bias, verify facts, and explore multiple perspectives with AI-powered analysis
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/news"
              className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200"
            >
              Explore News
            </Link>
            <Link
              to="/bias-analysis"
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary-600 transition-colors duration-200"
            >
              Analyze Bias
            </Link>
          </div>
        </div>
      </section>

      {/* Country News Section */}
      <section className="bg-white rounded-2xl p-8 border border-gray-200">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Latest News by Country
          </h2>
          <p className="text-lg text-gray-600">
            Get the latest news from your selected country
          </p>
        </div>

        <CountryFilter 
          selectedCountry={selectedCountry} 
          onSelect={handleCountryChange} 
        />

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-2 text-gray-600">Loading news...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {!loading && !error && articles.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.slice(0, 6).map((article, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow">
                <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">
                  {article.title}
                </h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {article.description}
                </p>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>{article.source}</span>
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Read more →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && !error && articles.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-600">No news articles found for the selected country.</p>
          </div>
        )}
      </section>

      {/* Features Grid */}
      <section>
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our comprehensive toolkit helps you navigate the complex landscape of news media
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Link
              key={feature.title}
              to={feature.href}
              className="group block"
            >
              <div className="card hover:shadow-lg transition-all duration-200 group-hover:border-primary-300">
                <div className="flex items-center mb-4">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                  <h3 className="text-xl font-semibold text-gray-900 ml-3">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-gray-600 group-hover:text-gray-700">
                  {feature.description}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 rounded-2xl p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-gray-600">
            Our AI-powered system analyzes news from multiple angles
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">1</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Input News</h3>
            <p className="text-gray-600">
              Paste a news article URL or text content for analysis
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">2</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Our AI analyzes bias, verifies facts, and compares coverage
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600">3</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Results</h3>
            <p className="text-gray-600">
              Receive detailed reports with bias scores and neutral summaries
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center bg-white rounded-2xl p-8 border border-gray-200">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Start?
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          Begin your journey toward more informed news consumption
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/news"
            className="btn-primary"
          >
            Browse News Feed
          </Link>
          <Link
            to="/fact-check"
            className="bg-gray-100 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors duration-200"
          >
            Check a Fact
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
