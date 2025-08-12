import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import API_ENDPOINTS from '../config/api';

interface BiasAnalysisResult {
  bias_score: number;
  bias_direction: string;
  biased_words: string[];
  emotional_tone: string;
  confidence_score: number;
  neutral_summary: string;
  recommendations: string[];
}

const BiasAnalysis: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [url, setUrl] = useState(searchParams.get('url') || '');
  const [content, setContent] = useState('');
  const [analysisResult, setAnalysisResult] = useState<BiasAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'analyze' | 'summarize'>('analyze');

  useEffect(() => {
    if (url) {
      handleAnalyze();
    }
  }, [url]);

  const handleAnalyze = async () => {
    if (!url && !content.trim()) {
      toast.error('Please provide a URL or content to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.ANALYZE_BIAS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content.trim() || url || '',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        toast.success('Analysis completed successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Analysis failed');
      }
    } catch (error) {
      toast.error('Error performing analysis');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!url && !content.trim()) {
      toast.error('Please provide a URL or content to summarize');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.ANALYZE_BIAS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content.trim() || url || '',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(prev => prev ? { ...prev, neutral_summary: result.neutral_summary } : result);
        toast.success('Neutral summary generated successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Summary generation failed');
      }
    } catch (error) {
      toast.error('Error generating summary');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBiasColor = (biasScore: number) => {
    if (biasScore < -0.3) return 'bias-left';
    if (biasScore > 0.3) return 'bias-right';
    return 'bias-center';
  };

  const getBiasLabel = (biasScore: number) => {
    if (biasScore < -0.3) return 'Left-leaning';
    if (biasScore > 0.3) return 'Right-leaning';
    return 'Neutral';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'confidence-high';
    if (confidence >= 0.4) return 'confidence-medium';
    return 'confidence-low';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Bias Analysis</h1>
        <p className="text-gray-600">Analyze news articles for political bias and generate neutral summaries</p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              News Article URL
            </label>
            <div className="relative">
              <DocumentTextIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="url"
                placeholder="https://example.com/news-article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Or paste article content directly
            </label>
            <textarea
              placeholder="Paste the article content here..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="loading-spinner mr-2"></div>
              ) : (
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
              )}
              Analyze Bias
            </button>
            <button
              onClick={handleGenerateSummary}
              disabled={loading}
              className="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors duration-200 flex items-center justify-center"
            >
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Generate Neutral Summary
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Bias Score */}
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Bias Analysis Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {(analysisResult.bias_score * 100).toFixed(1)}%
                </div>
                <div className={`bias-indicator ${getBiasColor(analysisResult.bias_score)}`}>
                  {getBiasLabel(analysisResult.bias_score)}
                </div>
                <p className="text-sm text-gray-600 mt-2">Bias Score</p>
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {analysisResult.emotional_tone}
                </div>
                <p className="text-sm text-gray-600">Emotional Tone</p>
              </div>

              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${getConfidenceColor(analysisResult.confidence_score)}`}>
                  {(analysisResult.confidence_score * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">Confidence</p>
              </div>
            </div>
          </div>

          {/* Biased Words */}
          {analysisResult.biased_words.length > 0 && (
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Detected Biased Words</h3>
              <div className="flex flex-wrap gap-2">
                {analysisResult.biased_words.map((word, index) => (
                  <span
                    key={index}
                    className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Neutral Summary */}
          {analysisResult.neutral_summary && (
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Neutral Summary</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 leading-relaxed">
                  {analysisResult.neutral_summary}
                </p>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analysisResult.recommendations.length > 0 && (
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h3>
              <div className="space-y-3">
                {analysisResult.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">{recommendation}</p>
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
          <ExclamationTriangleIcon className="h-6 w-6 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">How to use this tool</h3>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>• Paste a news article URL or content to analyze for political bias</li>
              <li>• Our AI will detect biased language, emotional tone, and political leanings</li>
              <li>• Generate neutral summaries that present balanced perspectives</li>
              <li>• Get recommendations for finding alternative viewpoints</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiasAnalysis;
