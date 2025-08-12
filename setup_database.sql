-- Database setup script for Bias News Checker
-- Run this in your PostgreSQL database

-- Create database
CREATE DATABASE bias_news_db;

-- Connect to the database
\c bias_news_db;

-- Create tables (these will be created automatically by SQLAlchemy, but here's the structure)
-- The actual tables will be created when you run the FastAPI application

-- Note: The application will automatically create all tables when it starts
-- This script is for reference only

-- Expected tables:
-- - news_sources
-- - articles  
-- - bias_analyses
-- - fact_checks
-- - coverage_comparisons

-- To run this project:
-- 1. Install PostgreSQL
-- 2. Create database: CREATE DATABASE bias_news_db;
-- 3. Update backend/.env with your database connection string
-- 4. Run the FastAPI application - it will create all tables automatically
