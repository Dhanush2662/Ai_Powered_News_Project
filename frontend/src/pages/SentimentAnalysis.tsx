import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { fetchFromAPI } from '../api/fetchNews';

interface SentimentAnalysis {
  overall_sentiment: number;
  sentiment_label: string;
  confidence_score: number;
  detailed_analysis: any;
  emotional_indicators: any;
  sentiment_timeline: any[];
}

const SentimentAnalysis: React.FC = () => {
  const [textContent, setTextContent] = useState('');
  const [analysis, setAnalysis] = useState<SentimentAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    if (!textContent.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchFromAPI('/sentiment/analyze', {
        method: 'POST',
        body: JSON.stringify({ content: textContent })
      });

      if (response.success) {
        setAnalysis(response.analysis);
        toast.success('Sentiment analysis completed!');
      } else {
        toast.error('Failed to analyze sentiment');
      }
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
      toast.error('Error analyzing sentiment');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (label: string) => {
    switch (label.toLowerCase()) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      case 'neutral': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sentiment Analysis</h1>
        <p className="text-gray-600">Analyze the emotional tone and sentiment of news content</p>
      </div>

      <div className="space-y-6">
        {/* Text Input */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold mb-4">Analyze Sentiment</h2>
          <textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            placeholder="Enter text content to analyze for sentiment..."
            className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={analyzeSentiment}
            disabled={loading || !textContent.trim()}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze Sentiment'}
          </button>
        </div>

        {/* Analysis Results */}
        {analysis && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Sentiment Score</div>
                <div className="text-2xl font-bold text-gray-900">
                  {analysis.overall_sentiment.toFixed(3)}
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Sentiment Label</div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(analysis.sentiment_label)}`}>
                  {analysis.sentiment_label.charAt(0).toUpperCase() + analysis.sentiment_label.slice(1)}
                </span>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Confidence</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(analysis.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Emotional Indicators */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-3">Positive Words</h4>
                <div className="text-sm text-green-600">
                  {analysis.emotional_indicators.positive_words.length > 0 
                    ? analysis.emotional_indicators.positive_words.join(', ')
                    : 'None detected'
                  }
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-3">Negative Words</h4>
                <div className="text-sm text-red-600">
                  {analysis.emotional_indicators.negative_words.length > 0 
                    ? analysis.emotional_indicators.negative_words.join(', ')
                    : 'None detected'
                  }
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SentimentAnalysis;
