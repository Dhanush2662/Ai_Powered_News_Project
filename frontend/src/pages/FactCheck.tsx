import React, { useState } from 'react';
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  PhotoIcon,
  LinkIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import API_ENDPOINTS from '../config/api';

interface FactCheckResult {
  claim: string;
  verdict: 'true' | 'false' | 'misleading' | 'unverified';
  confidence_score: number;
  evidence: string[];
  sources: string[];
  explanation: string;
  fact_check_id?: string;
}

const FactCheck: React.FC = () => {
  const [claim, setClaim] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<FactCheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'text' | 'url' | 'file'>('text');

  const handleVerifyClaim = async () => {
    if (!claim.trim() && !url && !file) {
      toast.error('Please provide a claim to verify');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.FACT_CHECK, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim: claim.trim() || undefined,
          url: url || undefined,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Fact check completed successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Fact check failed');
      }
    } catch (error) {
      toast.error('Error performing fact check');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/fact-check/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('File processed successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'File processing failed');
      }
    } catch (error) {
      toast.error('Error processing file');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUrlCheck = async () => {
    if (!url.trim()) {
      toast.error('Please provide a URL to check');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/fact-check/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('URL fact check completed successfully');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'URL fact check failed');
      }
    } catch (error) {
      toast.error('Error checking URL');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'true':
        return 'text-green-600 bg-green-100';
      case 'false':
        return 'text-red-600 bg-red-100';
      case 'misleading':
        return 'text-yellow-600 bg-yellow-100';
      case 'unverified':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'true':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'false':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'misleading':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'unverified':
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
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
        <h1 className="text-3xl font-bold text-gray-900">Fact Check</h1>
        <p className="text-gray-600">Verify claims and statements using AI-powered fact checking</p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                activeTab === 'text'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <DocumentTextIcon className="h-4 w-4 inline mr-2" />
              Text Claim
            </button>
            <button
              onClick={() => setActiveTab('url')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                activeTab === 'url'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <LinkIcon className="h-4 w-4 inline mr-2" />
              URL
            </button>
            <button
              onClick={() => setActiveTab('file')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
                activeTab === 'file'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <PhotoIcon className="h-4 w-4 inline mr-2" />
              File Upload
            </button>
          </div>
        </div>

        {/* Text Input */}
        {activeTab === 'text' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Claim to Verify
              </label>
              <textarea
                placeholder="Enter the claim or statement you want to fact-check..."
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleVerifyClaim}
              disabled={loading || !claim.trim()}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="loading-spinner mr-2"></div>
              ) : (
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
              )}
              Verify Claim
            </button>
          </div>
        )}

        {/* URL Input */}
        {activeTab === 'url' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                URL to Check
              </label>
              <div className="relative">
                <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="url"
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
            <button
              onClick={handleUrlCheck}
              disabled={loading || !url.trim()}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="loading-spinner mr-2"></div>
              ) : (
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
              )}
              Check URL
            </button>
          </div>
        )}

        {/* File Upload */}
        {activeTab === 'file' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload File (Image or PDF)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <ArrowUpTrayIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer text-primary-600 hover:text-primary-700 font-medium"
                >
                  Choose a file
                </label>
                <p className="text-gray-500 text-sm mt-2">
                  or drag and drop
                </p>
                {file && (
                  <p className="text-sm text-gray-600 mt-2">
                    Selected: {file.name}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={handleFileUpload}
              disabled={loading || !file}
              className="btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="loading-spinner mr-2"></div>
              ) : (
                <PhotoIcon className="h-5 w-5 mr-2" />
              )}
              Process File
            </button>
          </div>
        )}
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Fact Check Results</h3>
            
            {/* Verdict */}
            <div className="flex items-center space-x-4 mb-6">
              {getVerdictIcon(result.verdict)}
              <div>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getVerdictColor(result.verdict)}`}>
                  {result.verdict.charAt(0).toUpperCase() + result.verdict.slice(1)}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Confidence: <span className={getConfidenceColor(result.confidence_score)}>{(result.confidence_score * 100).toFixed(1)}%</span>
                </p>
              </div>
            </div>

            {/* Claim */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-900 mb-2">Claim</h4>
              <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">
                {result.claim}
              </p>
            </div>

            {/* Explanation */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-900 mb-2">Explanation</h4>
              <p className="text-gray-700 leading-relaxed">
                {result.explanation}
              </p>
            </div>

            {/* Evidence */}
            {result.evidence.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-medium text-gray-900 mb-2">Supporting Evidence</h4>
                <ul className="space-y-2">
                  {result.evidence.map((item, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sources */}
            {result.sources.length > 0 && (
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">Sources</h4>
                <div className="space-y-2">
                  {result.sources.map((source, index) => (
                    <a
                      key={index}
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-primary-600 hover:text-primary-700 text-sm"
                    >
                      {source}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">How to use this tool</h3>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>• Enter a claim or statement to verify its accuracy</li>
              <li>• Upload images or PDFs containing claims to extract and verify</li>
              <li>• Provide URLs to fact-check entire articles or social media posts</li>
              <li>• Get detailed explanations with supporting evidence and sources</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FactCheck;
