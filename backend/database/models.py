from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class NewsSource(Base):
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    bias_score = Column(Float, default=0.0)  # -5 to +5 scale
    political_lean = Column(String)  # left, center, right
    country = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    url = Column(String)
    published_at = Column(DateTime(timezone=True))
    source_id = Column(Integer, ForeignKey("news_sources.id"))
    topic = Column(String, index=True)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source = relationship("NewsSource", back_populates="articles")
    bias_analyses = relationship("BiasAnalysis", back_populates="article")
    fact_checks = relationship("FactCheck", back_populates="article")
    user_feedbacks = relationship("UserFeedback", back_populates="article")

class BiasAnalysis(Base):
    __tablename__ = "bias_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    bias_score = Column(Float)  # -5 to +5 scale
    emotional_tone = Column(String)  # positive, negative, neutral
    biased_words = Column(Text)  # JSON array of biased words
    neutral_summary = Column(Text)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    article = relationship("Article", back_populates="bias_analyses")

class FactCheck(Base):
    __tablename__ = "fact_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    claim = Column(Text)
    verdict = Column(String)  # real, fake, needs_context
    confidence_score = Column(Float)
    evidence = Column(Text)  # JSON array of evidence
    fact_check_date = Column(DateTime(timezone=True), server_default=func.now())
    
    article = relationship("Article", back_populates="fact_checks")

class CoverageComparison(Base):
    __tablename__ = "coverage_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    left_articles = Column(Text)  # JSON array of article IDs
    center_articles = Column(Text)  # JSON array of article IDs
    right_articles = Column(Text)  # JSON array of article IDs
    comparison_date = Column(DateTime(timezone=True), server_default=func.now())

class UserFeedback(Base):
    __tablename__ = "user_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    user_id = Column(String, index=True)  # Can be anonymous or user ID
    feedback_type = Column(String)  # rating, comment, report, helpful
    rating = Column(Float)  # 1-5 scale for ratings
    comment = Column(Text)  # User comment
    helpful_votes = Column(Integer, default=0)  # Number of helpful votes
    report_reason = Column(String)  # For reported content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    article = relationship("Article", back_populates="user_feedbacks")

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    overall_sentiment = Column(Float)  # -1 to +1 scale
    sentiment_label = Column(String)  # positive, negative, neutral
    confidence_score = Column(Float)
    detailed_analysis = Column(Text)  # JSON object
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

class FakeNewsDetection(Base):
    __tablename__ = "fake_news_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    fake_news_score = Column(Float)  # 0 to 1 scale
    risk_level = Column(String)  # low, medium, high
    confidence_score = Column(Float)
    verdict = Column(String)  # likely_real, suspicious, likely_fake
    red_flags = Column(Text)  # JSON array
    detection_date = Column(DateTime(timezone=True), server_default=func.now())
