#!/usr/bin/env python3
"""
Comprehensive Test Script for News Analysis Platform
Tests all 8 required features to ensure they are working correctly.
"""

import requests
import json
import time
from typing import Dict, Any

class NewsAnalysisTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
    
    def test_feature_1_news_aggregation(self) -> Dict[str, Any]:
        """Test Feature 1: Aggregating News from Different Channels"""
        print("🔍 Testing Feature 1: News Aggregation...")
        
        try:
            # Test news feed endpoint
            response = requests.get(f"{self.base_url}/api/news/feed")
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    print(f"✅ News aggregation working - Found {len(articles)} articles")
                    return {
                        "status": "PASS",
                        "articles_count": len(articles),
                        "sample_article": articles[0] if articles else None
                    }
                else:
                    print("⚠️ News aggregation returned empty results")
                    return {"status": "WARNING", "message": "No articles found"}
            else:
                print(f"❌ News aggregation failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ News aggregation error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_2_bias_detection(self) -> Dict[str, Any]:
        """Test Feature 2: Detecting Political Bias"""
        print("🔍 Testing Feature 2: Bias Detection...")
        
        try:
            # Test bias analysis endpoint
            test_content = "This is a test article with some political content."
            response = requests.post(
                f"{self.base_url}/api/bias/analyze",
                json={"content": test_content}
            )
            
            if response.status_code == 200:
                data = response.json()
                bias_score = data.get('bias_score', 0)
                print(f"✅ Bias detection working - Score: {bias_score}")
                return {
                    "status": "PASS",
                    "bias_score": bias_score,
                    "analysis": data
                }
            else:
                print(f"❌ Bias detection failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Bias detection error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_3_truth_trustworthiness(self) -> Dict[str, Any]:
        """Test Feature 3: Truth/Trustworthiness Score"""
        print("🔍 Testing Feature 3: Truth/Trustworthiness Score...")
        
        try:
            # Test fact checking endpoint
            test_claim = "The Earth is round."
            response = requests.post(
                f"{self.base_url}/api/fact-check/verify",
                json={"claim": test_claim}
            )
            
            if response.status_code == 200:
                data = response.json()
                confidence = data.get('confidence_score', 0)
                print(f"✅ Truth/Trustworthiness working - Confidence: {confidence}")
                return {
                    "status": "PASS",
                    "confidence_score": confidence,
                    "verdict": data.get('verdict', 'unknown')
                }
            else:
                print(f"❌ Truth/Trustworthiness failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Truth/Trustworthiness error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_4_fact_checking(self) -> Dict[str, Any]:
        """Test Feature 4: Fact-Checking Service"""
        print("🔍 Testing Feature 4: Fact-Checking Service...")
        
        try:
            # Test fact checking with URL
            test_url = "https://example.com/test-article"
            response = requests.post(
                f"{self.base_url}/api/fact-check/verify-url",
                json={"url": test_url}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Fact-checking service working")
                return {
                    "status": "PASS",
                    "verdict": data.get('verdict', 'unknown'),
                    "evidence_count": len(data.get('evidence', []))
                }
            else:
                print(f"❌ Fact-checking failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Fact-checking error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_5_coverage_comparison(self) -> Dict[str, Any]:
        """Test Feature 5: Comparing How Channels Report the Same News"""
        print("🔍 Testing Feature 5: Coverage Comparison...")
        
        try:
            # Test coverage comparison endpoint
            test_topic = "politics"
            response = requests.get(
                f"{self.base_url}/api/coverage/compare",
                params={"topic": test_topic}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Coverage comparison working")
                return {
                    "status": "PASS",
                    "topic": test_topic,
                    "comparison_data": data
                }
            else:
                print(f"❌ Coverage comparison failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Coverage comparison error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_6_sentiment_analysis(self) -> Dict[str, Any]:
        """Test Feature 6: Sentiment Analysis"""
        print("🔍 Testing Feature 6: Sentiment Analysis...")
        
        try:
            # Test sentiment analysis endpoint
            test_content = "This is a positive and wonderful article about great achievements."
            response = requests.post(
                f"{self.base_url}/api/sentiment/analyze",
                json={"content": test_content}
            )
            
            if response.status_code == 200:
                data = response.json()
                sentiment = data.get('analysis', {}).get('sentiment_label', 'unknown')
                print(f"✅ Sentiment analysis working - Sentiment: {sentiment}")
                return {
                    "status": "PASS",
                    "sentiment_label": sentiment,
                    "overall_sentiment": data.get('analysis', {}).get('overall_sentiment', 0)
                }
            else:
                print(f"❌ Sentiment analysis failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Sentiment analysis error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_7_fake_news_detection(self) -> Dict[str, Any]:
        """Test Feature 7: Fake News Detection"""
        print("🔍 Testing Feature 7: Fake News Detection...")
        
        try:
            # Test fake news detection endpoint
            test_content = "BREAKING: You won't believe this SHOCKING news! 100% guaranteed!"
            response = requests.post(
                f"{self.base_url}/api/fake-news/detect",
                json={"content": test_content}
            )
            
            if response.status_code == 200:
                data = response.json()
                risk_level = data.get('detection', {}).get('risk_level', 'unknown')
                print(f"✅ Fake news detection working - Risk Level: {risk_level}")
                return {
                    "status": "PASS",
                    "risk_level": risk_level,
                    "fake_news_score": data.get('detection', {}).get('fake_news_score', 0)
                }
            else:
                print(f"❌ Fake news detection failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Fake news detection error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def test_feature_8_user_feedback(self) -> Dict[str, Any]:
        """Test Feature 8: User Feedback System"""
        print("🔍 Testing Feature 8: User Feedback System...")
        
        try:
            # Test feedback submission
            test_feedback = {
                "article_id": 1,
                "user_id": "test_user",
                "feedback_type": "rating",
                "rating": 4.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/feedback/submit",
                json=test_feedback
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User feedback system working")
                return {
                    "status": "PASS",
                    "message": data.get('message', 'Feedback submitted'),
                    "feedback_id": data.get('feedback_id')
                }
            else:
                print(f"❌ User feedback failed - Status: {response.status_code}")
                return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ User feedback error: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all feature tests"""
        print("🚀 Starting comprehensive feature testing...")
        print("=" * 60)
        
        # Test all 8 features
        self.test_results = {
            "feature_1_news_aggregation": self.test_feature_1_news_aggregation(),
            "feature_2_bias_detection": self.test_feature_2_bias_detection(),
            "feature_3_truth_trustworthiness": self.test_feature_3_truth_trustworthiness(),
            "feature_4_fact_checking": self.test_feature_4_fact_checking(),
            "feature_5_coverage_comparison": self.test_feature_5_coverage_comparison(),
            "feature_6_sentiment_analysis": self.test_feature_6_sentiment_analysis(),
            "feature_7_fake_news_detection": self.test_feature_7_fake_news_detection(),
            "feature_8_user_feedback": self.test_feature_8_user_feedback()
        }
        
        # Generate summary
        self.generate_summary()
        
        return self.test_results
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'FAIL')
        warning_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'WARNING')
        
        print(f"Total Features Tested: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        
        print("\n📋 Feature Status:")
        for feature_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"{status_icon} {feature_name.replace('_', ' ').title()}: {status}")
        
        if failed_tests == 0:
            print("\n🎉 All features are working correctly!")
        else:
            print(f"\n⚠️ {failed_tests} feature(s) need attention.")

def main():
    """Main test runner"""
    tester = NewsAnalysisTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to 'test_results.json'")

if __name__ == "__main__":
    main()
