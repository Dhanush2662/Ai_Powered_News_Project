import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { fetchFromAPI } from '../api/fetchNews';

interface FakeNewsDetection {
  fake_news_score: number;
  risk_level: string;
  confidence_score: number;
  verdict: string;
  red_flags: string[];
  recommendations: string[];
  detection_methods: any;
}

const FakeNewsDetection: React.FC = () => {
  const [content, setContent] = useState('');
  const [url, setUrl] = useState('');
  const [source, setSource] = useState('');
  const [detection, setDetection] = useState<FakeNewsDetection | null>(null);
  const [loading, setLoading] = useState(false);

  const detectFakeNews = async () => {
    if (!content.trim()) {
      toast.error('Please enter some content to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchFromAPI('/fake-news/detect', {
        method: 'POST',
        body: JSON.stringify({
          content,
          url: url || undefined,
          source: source || undefined
        })
      });

      if (response.success) {
        setDetection(response.detection);
        toast.success('Fake news detection completed!');
      } else {
        toast.error('Failed to detect fake news');
      }
    } catch (error) {
      console.error('Error detecting fake news:', error);
      toast.error('Error detecting fake news');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'likely_fake': return 'text-red-600 bg-red-100';
      case 'suspicious': return 'text-yellow-600 bg-yellow-100';
      case 'likely_real': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Fake News Detection</h1>
        <p className="text-gray-600">Detect potential fake news using AI and multiple detection methods</p>
      </div>

      <div className="space-y-6">
        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Analyze Content</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content to Analyze
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter the news content or article text to analyze..."
                className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL (Optional)
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source (Optional)
                </label>
                <input
                  type="text"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="News source name"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <button
              onClick={detectFakeNews}
              disabled={loading || !content.trim()}
              className="w-full bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Analyzing...' : 'Detect Fake News'}
            </button>
          </div>
        </div>

        {/* Detection Results */}
        {detection && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Detection Results</h2>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Fake News Score</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(detection.fake_news_score * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Risk Level</div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(detection.risk_level)}`}>
                  {detection.risk_level.charAt(0).toUpperCase() + detection.risk_level.slice(1)}
                </span>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Confidence</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(detection.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Verdict</div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getVerdictColor(detection.verdict)}`}>
                  {detection.verdict.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </span>
              </div>
            </div>

            {/* Red Flags */}
            {detection.red_flags.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3 text-red-600">🚨 Red Flags Detected</h3>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <ul className="space-y-2">
                    {detection.red_flags.map((flag, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        <span className="text-sm text-red-700">{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {detection.recommendations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3 text-blue-600">💡 Recommendations</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <ul className="space-y-2">
                    {detection.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        <span className="text-sm text-blue-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Detection Methods */}
            <div>
              <h3 className="text-lg font-medium mb-3">🔍 Detection Methods</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {detection.detection_methods && (
                  <>
                    {detection.detection_methods.content_analysis && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">Content Analysis</h4>
                        <div className="text-sm text-gray-600">
                          Suspiciousness Score: {(detection.detection_methods.content_analysis.suspiciousness_score * 100).toFixed(1)}%
                        </div>
                      </div>
                    )}
                    
                    {detection.detection_methods.source_credibility && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">Source Credibility</h4>
                        <div className="text-sm text-gray-600">
                          Credibility Score: {(detection.detection_methods.source_credibility.credibility_score * 100).toFixed(1)}%
                        </div>
                      </div>
                    )}
                    
                    {detection.detection_methods.ai_analysis && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">AI Analysis</h4>
                        <div className="text-sm text-gray-600">
                          Fake News Probability: {(detection.detection_methods.ai_analysis.fake_news_probability * 100).toFixed(1)}%
                        </div>
                      </div>
                    )}
                    
                    {detection.detection_methods.fact_checking && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">Fact Checking</h4>
                        <div className="text-sm text-gray-600">
                          Fact Check Score: {(detection.detection_methods.fact_checking.fact_check_score * 100).toFixed(1)}%
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FakeNewsDetection;
