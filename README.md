# GTM Automation Workflow

An AI-driven automation system for tracking and engaging with potential customers in online communities (Reddit). This workflow monitors Reddit posts, uses AI to classify relevance and intent, generates engagement suggestions, and stores results in Arango and displays it in a React UI.

## Features

- **Source Tracking**: Monitors Reddit for posts matching specified keywords
- **AI-Powered Scoring**: Uses OpenAI GPT to classify posts by relevance and intent
- **Engagement Generation**: Creates personalized comment/DM suggestions
- **Data Storage**: Automatically stores results in Arango
- **Slack Notifications**: Optional alerts for high-priority posts
- **Deduplication**: Tracks processed posts to avoid duplicates

## Requirements

- Python 3.8+
- Reddit API credentials
- GeminiAI API key
- Arango collection creation
- (Optional) Slack webhook URL

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Reddit API:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note your `client_id` and `client_secret`

4. **Set up Gemini API:**
   - Kindly refer to SETUP_GEMINI

5. **Set up Arango db:**
6. - Install arango,create gmt,gmt_weekly_report collection and Arango url to .env

6. **Set up Slack (Optional):**
   - Go to your Slack workspace
   - Create an incoming webhook: https://api.slack.com/messaging/webhooks
   - Copy the webhook URL

7. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Fill in all required values:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your credentials:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     REDDIT_USER_AGENT=GTMAutomation/1.0
     
     GEMINI_API_KEY=your_openai_key_here

     
     SLACK_WEBHOOK_URL=your_webhook_url_here  # Optional
     
     KEYWORDS=retention marketing,Shopify growth,customer churn,growth hacking
     SUBREDDITS=marketing,entrepreneur,startups,smallbusiness
     ```


## Usage

### Basic Run

```bash
python workflow.py
```

### Dry Run (Test without writing to sheets)

```bash
python workflow.py --dry-run
```

### Scheduling

To run automatically, use a cron job or task scheduler:

**Linux/Mac (cron):**
```bash
# Run every 4 hours
0 */4 * * * cd /path/to/project && /usr/bin/python3 workflow.py
```

**Windows (Task Scheduler):**
- Create a task that runs `python workflow.py` on your desired schedule

## How It Works

1. **Monitoring**: Scans specified subreddits for posts containing keywords
2. **Filtering**: Removes duplicates and posts older than 24 hours (configurable)
3. **AI Classification**: Uses OpenAI to:
   - Score relevance (0.0-1.0)
   - Classify intent (question, complaint, vendor_search, etc.)
   - Generate reasoning
4. **Engagement Generation**: Creates personalized comment/DM suggestions based on post intent
5. **Storage**: Writes results to Google Sheets with all relevant data
6. **Notifications**: Sends Slack alerts for high-priority posts (relevance > 0.85)


## Configuration

Edit `config.py` to adjust:

- `RELEVANCE_THRESHOLD`: Minimum score to consider relevant (default: 0.7)
- `HIGH_RELEVANCE_THRESHOLD`: Score that triggers Slack alerts (default: 0.85)
- `MAX_POSTS_PER_SUBREDDIT`: Limit posts per subreddit per run (default: 50)
- `MAX_POST_AGE_HOURS`: Only consider posts from last N hours (default: 24)

## Customization

### Add More Keywords

Edit `.env`:
```
KEYWORDS=keyword1,keyword2,keyword3
```

### Monitor Different Subreddits

Edit `.env`:
```
SUBREDDITS=subreddit1,subreddit2,subreddit3
```

### Change AI Model

Edit `ai_scorer.py`:
```python
self.model = "gemini 2.5-flash"  # Cheaper option
```

## Troubleshooting

### Reddit API Errors
- Verify your Reddit credentials are correct
- Check that your user agent is unique
- Ensure you're not hitting rate limits

### GeminiAI API Errors
- Verify your API key is valid
- Check your OpenAI account has credits
- Consider using `gemini-2.5-flash` for cost savings



### No Posts Found
- Verify keywords are correctly formatted (comma-separated)
- Check that subreddit names are valid
- Ensure posts are recent (within 24 hours by default)

## Cost Considerations

- **Reddit API**: Free
- **Slack**: Free for webhooks

## Ui Side Configuration:
- npm i
- cd Client
- node server
- cd ..
- npm run dev




