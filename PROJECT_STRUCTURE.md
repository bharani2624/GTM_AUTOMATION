# Project Structure

```
gtm-automation/
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick setup guide
├── PROJECT_STRUCTURE.md         # This file
├── requirements.txt             # Python dependencies
├── env_template.txt             # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── config.py                    # Configuration management
├── workflow.py                   # Main workflow orchestrator
│
├── reddit_monitor.py            # Reddit API integration
├── ai_scorer.py                 # AI classification & scoring
├── engagement_generator.py      # Engagement suggestion generation
├── sheets_manager.py            # Google Sheets integration
├── slack_notifier.py            # Slack notifications
├── trends_analyzer.py           # Bonus: Trends analysis
│
├── setup_helper.py              # Configuration verification script
│
└── credentials/                 # Credentials directory (not in git)
    └── google_sheets_credentials.json
```

## Module Descriptions

### Core Modules

- **config.py**: Centralized configuration management using environment variables
- **workflow.py**: Main orchestrator that coordinates all components

### Integration Modules

- **reddit_monitor.py**: Monitors Reddit for posts matching keywords
  - Searches multiple subreddits
  - Filters by keywords and time window
  - Deduplicates posts
  - Extracts post metadata

- **ai_scorer.py**: AI-powered classification using OpenAI
  - Scores relevance (0.0-1.0)
  - Classifies intent (question, complaint, vendor_search, etc.)
  - Generates post summaries
  - Fallback classification if API fails

- **engagement_generator.py**: Generates personalized engagement suggestions
  - Creates comment drafts
  - Creates DM drafts
  - Suggests engagement strategy
  - Assigns priority levels



- **slack_notifier.py**: Slack webhook notifications
  - Sends alerts for high-priority posts
  - Formats rich Slack messages
  - Includes engagement suggestions

### Bonus Modules

- **trends_analyzer.py**: Analyzes trends over time
  - Weekly statistics
  - Intent distribution
  - Subreddit distribution
  - Trend direction (increasing/stable/decreasing)

### Utility Scripts

- **setup_helper.py**: Verifies configuration
  - Checks all required credentials
  - Validates file paths
  - Provides helpful error messages

## Data Flow

```
1. Reddit Monitor
   ↓ (posts)
2. AI Scorer
   ↓ (classification)
3. Engagement Generator
   ↓ (suggestions)
4. Arango Manager
   ↓ (storage)
5. Slack Notifier (optional)
   ↓ (alerts)
```

## Configuration Flow

1. User sets up API credentials
2. Creates `.env` file from template
3. Runs `setup_helper.py` to verify
4. Runs `workflow.py` to execute

## Extension Points

- **LinkedIn Support**: Add `linkedin_monitor.py` similar to `reddit_monitor.py`
- **Sentiment Analysis**: Extend `ai_scorer.py` with sentiment scoring
- **Airtable Support**: Add `airtable_manager.py` similar to `sheets_manager.py`
- **Email Notifications**: Add `email_notifier.py` similar to `slack_notifier.py`
- **Feedback Loop**: Track engagement success and fine-tune scoring

