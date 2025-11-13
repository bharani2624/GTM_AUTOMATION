"""
Configuration module for GTM Automation Workflow
"""
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    """Application configuration"""
    
    # Reddit Configuration
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'GTMAutomation/1.0')
    
    # AI Provider Configuration
    # Options: 'openai', 'openrouter', 'groq', 'together', 'gemini'
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter').lower()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDSULfAB4OQw4KbW7k4VavycmOvSp-0zOU')
    
    # Model selection (varies by provider)
    AI_MODEL = os.getenv('AI_MODEL', '')

    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

    # Slack Configuration (Optional)
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    
    # Monitoring Configuration
    KEYWORDS = [k.strip() for k in os.getenv('KEYWORDS', '').split(',') if k.strip()]
    SUBREDDITS = [s.strip() for s in os.getenv('SUBREDDITS', '').split(',') if s.strip()]
    
    # Scoring Thresholds
    RELEVANCE_THRESHOLD = 0.2  # Posts with relevance > 0.7 are considered relevant
    HIGH_RELEVANCE_THRESHOLD = 0.25  # Posts above this trigger alerts
    
    # Post Limits
    MAX_POSTS_PER_SUBREDDIT = 50  # Limit posts per subreddit per run
    MAX_POST_AGE_HOURS = 72  # Only consider posts from last 72 hours

    # ArangoDB Configuration
    ARANGO_HOST = "http://192.168.2.90:8529"
    ARANGO_USERNAME = "root"
    ARANGO_PASSWORD = ""
    ARANGO_DB = "gtm"
    ARANGO_COLLECTION = "gtm_posts"

