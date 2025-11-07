# Google Gemini Setup Guide

Complete step-by-step guide to configure Google Gemini for the GTM Automation Workflow.

## 🎯 Why Google Gemini?

- ✅ **Completely FREE** - No credit card required
- ✅ **Generous limits** - 60 requests/minute
- ✅ **High quality** - Google's latest AI model
- ✅ **No billing** - Free forever tier

## 📋 Step-by-Step Setup

### Step 1: Get Google Gemini API Key

1. **Go to Google AI Studio**:
   - Visit: https://makersuite.google.com/app/apikey
   - OR visit: https://aistudio.google.com/app/apikey

2. **Sign in with Google Account**:
   - Use your Google account (Gmail account works)
   - If you don't have one, create a free Gmail account first

3. **Create API Key**:
   - Click **"Create API Key"** button
   - Select **"Create API key in new project"** (or use existing project)
   - Click **"Create API key"**

4. **Copy Your API Key**:
   - The key will be displayed (looks like: `AIzaSyAbc123def456ghi789...`)
   - ⚠️ **Copy it immediately** - you may not see it again!
   - Click **"Copy"** or highlight and copy the key

### Step 2: Install Required Package

Make sure you have the Google Generative AI package installed:

```bash
pip install google-generativeai
```

Or if using venv:
```bash
source venv/bin/activate
pip install google-generativeai
```

### Step 3: Configure .env File

1. **Open your `.env` file**:
   ```bash
   nano .env
   # or use your favorite editor
   ```

2. **Add Gemini configuration**:
   ```bash
   # AI Provider - Set to 'gemini'
   AI_PROVIDER=gemini
   
   # Google Gemini API Key
   GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```

3. **Save and exit** (in nano: `Ctrl+X`, then `Y`, then `Enter`)

### Step 4: Verify Configuration

Run the setup helper to verify:

```bash
python setup_helper.py
```

You should see:
```
✅ Google Gemini API configured
```

### Step 5: Test the Workflow

Run a test to make sure everything works:

```bash
python workflow.py --dry-run
```

You should see Gemini processing posts without errors!

## 📝 Complete .env Example

Here's what your `.env` should look like with Gemini:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=GTMAutomation/1.0

# AI Provider - Use Gemini
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr678stu901vwx234yz

# Google Sheets Credentials
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/google_sheets_credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id

# Slack Webhook (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Keywords to monitor
KEYWORDS=retention marketing,Shopify growth,customer churn,growth hacking,conversion optimization

# Reddit subreddits to monitor
SUBREDDITS=marketing,entrepreneur,startups,smallbusiness,shopify
```

## 🎛️ Optional: Custom Model Selection

By default, the system uses `gemini-pro`. You can override this in `.env`:

```bash
# Use Gemini Pro Vision (for image analysis)
AI_MODEL=gemini-pro-vision

# Or stick with the default
AI_MODEL=gemini-pro
```

## ✅ Verification Checklist

- [ ] Gemini API key obtained from https://makersuite.google.com/app/apikey
- [ ] `google-generativeai` package installed
- [ ] `AI_PROVIDER=gemini` set in `.env`
- [ ] `GEMINI_API_KEY=your_key` set in `.env`
- [ ] Setup helper shows ✅ for Gemini
- [ ] Test run completes successfully

## 🐛 Troubleshooting

### "API key not found"
- Make sure `GEMINI_API_KEY` is set in `.env`
- Check there are no extra spaces around the key
- Verify the key starts with `AIzaSy`

### "Module not found: google.generativeai"
```bash
pip install google-generativeai
```

### "Invalid API key"
- Regenerate your API key at https://makersuite.google.com/app/apikey
- Make sure you copied the entire key (they're long!)

### "Rate limit exceeded"
- Gemini free tier: 60 requests/minute
- If you hit the limit, wait a minute and try again
- Consider processing fewer posts per run

### "Model not found"
- Default model is `gemini-pro`
- Try: `AI_MODEL=gemini-pro` in `.env`
- Check available models at: https://ai.google.dev/models

## 📊 Gemini Free Tier Limits

- **Requests per minute**: 60
- **Requests per day**: 1,500
- **Tokens per minute**: 32,000
- **Cost**: FREE forever!

## 🔗 Useful Links

- **Get API Key**: https://makersuite.google.com/app/apikey
- **Documentation**: https://ai.google.dev/docs
- **Available Models**: https://ai.google.dev/models
- **Pricing**: https://ai.google.dev/pricing (Free tier available)

## 🚀 Next Steps

Once Gemini is configured:

1. **Test with dry-run**:
   ```bash
   python workflow.py --dry-run
   ```

2. **Run full workflow**:
   ```bash
   python workflow.py
   ```

3. **Check results in Google Sheets**

## 💡 Pro Tips

- Gemini is fast and free, perfect for testing
- The free tier is generous enough for most use cases
- No credit card required - truly free
- Quality is comparable to GPT-4 for classification tasks

## 🎉 You're All Set!

Your GTM Automation Workflow is now using Google Gemini completely free!

