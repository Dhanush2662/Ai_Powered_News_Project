import React, { useState } from 'react';
import { ScaleIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ConsensusScore: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!url.trim()) {
      toast.error('Please enter a valid URL');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implement consensus score API call
      // const response = await fetchFromAPI('/api/consensus-score', {
      //   method: 'POST',
      //   data: { url }
      // });
      
      // Mock result for now
      setTimeout(() => {
        setResult({
          score: 0.75,
          sources_analyzed: 5,
          consensus_level: 'High',
          summary: 'Most sources agree on the main facts presented in this article.'
        });
        setLoading(false);
        toast.success('Consensus analysis completed!');
      }, 2000);
    } catch (error) {
      toast.error('Error analyzing consensus');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Consensus Score</h1>
        <p className="text-gray-600">Analyze how multiple sources agree on news content</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Article URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter article URL to analyze consensus..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            <ScaleIcon className="h-4 w-4" />
            <span>{loading ? 'Analyzing...' : 'Analyze Consensus'}</span>
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Consensus Analysis Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{(result.score * 100).toFixed(0)}%</div>
              <div className="text-sm text-gray-600">Consensus Score</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{result.sources_analyzed}</div>
              <div className="text-sm text-gray-600">Sources Analyzed</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{result.consensus_level}</div>
              <div className="text-sm text-gray-600">Consensus Level</div>
            </div>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">Summary</h3>
            <p className="text-gray-700">{result.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsensusScore;