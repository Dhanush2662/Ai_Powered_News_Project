import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { fetchFromAPI } from '../api/fetchNews';

interface Feedback {
  article_id: number;
  user_id: string;
  feedback_type: string;
  rating?: number;
  comment?: string;
  report_reason?: string;
}

interface ArticleFeedback {
  article_id: number;
  statistics: {
    average_rating: number;
    total_ratings: number;
    total_comments: number;
    total_reports: number;
    total_helpful_votes: number;
  };
  ratings_distribution: Record<string, number>;
  recent_comments: Array<{
    id: number;
    comment: string;
    user_id: string;
    created_at: string;
    helpful_votes: number;
  }>;
}

const UserFeedback: React.FC = () => {
  const [feedback, setFeedback] = useState<Feedback>({
    article_id: 0,
    user_id: 'anonymous',
    feedback_type: 'rating'
  });
  const [articleFeedback, setArticleFeedback] = useState<ArticleFeedback | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('submit');

  const submitFeedback = async () => {
    if (!feedback.article_id) {
      toast.error('Please enter an article ID');
      return;
    }

    if (feedback.feedback_type === 'rating' && (!feedback.rating || feedback.rating < 1 || feedback.rating > 5)) {
      toast.error('Please provide a valid rating (1-5)');
      return;
    }

    if (feedback.feedback_type === 'comment' && !feedback.comment?.trim()) {
      toast.error('Please provide a comment');
      return;
    }

    if (feedback.feedback_type === 'report' && !feedback.report_reason?.trim()) {
      toast.error('Please provide a report reason');
      return;
    }

    setLoading(true);
    try {
      const response = await fetchFromAPI('/feedback/submit', {
        method: 'POST',
        body: JSON.stringify(feedback)
      });

      if (response.success) {
        toast.success(response.message);
        setFeedback({
          article_id: 0,
          user_id: 'anonymous',
          feedback_type: 'rating'
        });
      } else {
        toast.error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast.error('Error submitting feedback');
    } finally {
      setLoading(false);
    }
  };

  const loadArticleFeedback = async () => {
    if (!feedback.article_id) return;

    try {
      const response = await fetchFromAPI(`/feedback/article/${feedback.article_id}`);
      if (response.success) {
        setArticleFeedback(response.feedback);
      }
    } catch (error) {
      console.error('Error loading article feedback:', error);
    }
  };

  useEffect(() => {
    if (feedback.article_id && activeTab === 'view') {
      loadArticleFeedback();
    }
  }, [feedback.article_id, activeTab]);

  const renderStars = (rating: number) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`text-lg ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">User Feedback</h1>
        <p className="text-gray-600">Rate articles, leave comments, and view community feedback</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
        <button
          onClick={() => setActiveTab('submit')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'submit'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Submit Feedback
        </button>
        <button
          onClick={() => setActiveTab('view')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'view'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          View Feedback
        </button>
      </div>

      {activeTab === 'submit' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Submit Feedback</h2>
            
            <div className="space-y-4">
              {/* Article ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Article ID
                </label>
                <input
                  type="number"
                  value={feedback.article_id || ''}
                  onChange={(e) => setFeedback({...feedback, article_id: parseInt(e.target.value) || 0})}
                  placeholder="Enter article ID"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* User ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User ID (Optional)
                </label>
                <input
                  type="text"
                  value={feedback.user_id}
                  onChange={(e) => setFeedback({...feedback, user_id: e.target.value})}
                  placeholder="anonymous"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Feedback Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback Type
                </label>
                <select
                  value={feedback.feedback_type}
                  onChange={(e) => setFeedback({...feedback, feedback_type: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="rating">Rating</option>
                  <option value="comment">Comment</option>
                  <option value="report">Report</option>
                  <option value="helpful">Helpful Vote</option>
                </select>
              </div>

              {/* Rating */}
              {feedback.feedback_type === 'rating' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rating (1-5 stars)
                  </label>
                  <div className="flex items-center space-x-4">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        onClick={() => setFeedback({...feedback, rating})}
                        className={`text-2xl ${feedback.rating && feedback.rating >= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                      >
                        ★
                      </button>
                    ))}
                    {feedback.rating && (
                      <span className="text-sm text-gray-600">
                        {feedback.rating} star{feedback.rating !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Comment */}
              {feedback.feedback_type === 'comment' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Comment
                  </label>
                  <textarea
                    value={feedback.comment || ''}
                    onChange={(e) => setFeedback({...feedback, comment: e.target.value})}
                    placeholder="Share your thoughts about this article..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Report Reason */}
              {feedback.feedback_type === 'report' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Report Reason
                  </label>
                  <textarea
                    value={feedback.report_reason || ''}
                    onChange={(e) => setFeedback({...feedback, report_reason: e.target.value})}
                    placeholder="Please explain why you're reporting this article..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}

              <button
                onClick={submitFeedback}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'view' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">View Article Feedback</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Article ID
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value={feedback.article_id || ''}
                    onChange={(e) => setFeedback({...feedback, article_id: parseInt(e.target.value) || 0})}
                    placeholder="Enter article ID"
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={loadArticleFeedback}
                    className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Load
                  </button>
                </div>
              </div>
            </div>

            {/* Feedback Statistics */}
            {articleFeedback && (
              <div className="mt-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {articleFeedback.statistics.average_rating.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Average Rating</div>
                    {articleFeedback.statistics.average_rating > 0 && (
                      <div className="mt-1">{renderStars(Math.round(articleFeedback.statistics.average_rating))}</div>
                    )}
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {articleFeedback.statistics.total_ratings}
                    </div>
                    <div className="text-sm text-gray-600">Total Ratings</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {articleFeedback.statistics.total_comments}
                    </div>
                    <div className="text-sm text-gray-600">Comments</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {articleFeedback.statistics.total_reports}
                    </div>
                    <div className="text-sm text-gray-600">Reports</div>
                  </div>
                </div>

                {/* Recent Comments */}
                {articleFeedback.recent_comments.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium mb-4">Recent Comments</h3>
                    <div className="space-y-3">
                      {articleFeedback.recent_comments.map((comment) => (
                        <div key={comment.id} className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-sm text-gray-600">User: {comment.user_id}</span>
                            <span className="text-sm text-gray-600">
                              {new Date(comment.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-gray-800">{comment.comment}</p>
                          {comment.helpful_votes > 0 && (
                            <div className="mt-2 text-sm text-gray-600">
                              👍 {comment.helpful_votes} helpful vote{comment.helpful_votes !== 1 ? 's' : ''}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserFeedback;
