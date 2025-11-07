"""
Slack notification module for high-priority posts
"""
import requests
from typing import Dict
from config import Config


class SlackNotifier:
    """Send Slack notifications for high-relevance posts"""
    
    def __init__(self):
        """Initialize Slack webhook URL"""
        self.webhook_url = Config.SLACK_WEBHOOK_URL
    
    def notify_high_priority_post(self, result: Dict):
        """
        Send Slack notification for high-priority post
        
        Args:
            result: Dictionary containing post data, classification, and engagement
        """
        if not self.webhook_url:
            return
        
        post_data = result.get('post_data', {})
        classification = result.get('classification', {})
        engagement = result.get('engagement', {})
        
        relevance_score = classification.get('relevance_score', 0.0)
        intent = classification.get('intent', 'unknown')
        priority = engagement.get('priority', 'medium')
        
        # Only notify for high relevance or high priority
        if relevance_score < Config.HIGH_RELEVANCE_THRESHOLD and priority != 'high':
            return
        
        title = post_data.get('title', 'No title')
        link = post_data.get('link', '')
        subreddit = post_data.get('subreddit', '')
        summary = result.get('summary', '')[:300]
        comment_draft = engagement.get('comment_draft', '')[:200]
        
        # Format Slack message
        message = {
            "text": f"🔥 High-Priority Post Found in r/{subreddit}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🔥 High-Priority Post: {title[:100]}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Relevance Score:* {relevance_score:.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Intent:* {intent}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Subreddit:* r/{subreddit}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Priority:* {priority.upper()}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{summary}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Suggested Comment:*\n{comment_draft}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Post"
                            },
                            "url": link,
                            "style": "primary"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            print(f"Slack notification sent for post: {title[:50]}")
        except Exception as e:
            print(f"Error sending Slack notification: {str(e)}")

