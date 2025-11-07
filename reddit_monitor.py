"""
Reddit monitoring module for tracking posts and comments
"""
import praw
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config


class RedditMonitor:
    """Monitor Reddit for posts matching keywords"""
    
    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        self.keywords = Config.KEYWORDS
        self.subreddits = Config.SUBREDDITS
        self.max_age_hours = Config.MAX_POST_AGE_HOURS
    
    def _matches_keywords(self, text: str) -> bool:
        """Check if text contains any of the monitored keywords"""
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def _is_recent(self, post) -> bool:
        """Check if post is within the time window"""
        post_time = datetime.fromtimestamp(post.created_utc)
        age_hours = (datetime.now() - post_time).total_seconds() / 3600
        return age_hours <= self.max_age_hours
    
    def _extract_post_data(self, post) -> Dict:
        """Extract relevant data from Reddit post"""
        post_time = datetime.fromtimestamp(post.created_utc)
        
        return {
            'post_id': post.id,
            'title': post.title,
            'content': post.selftext if hasattr(post, 'selftext') else '',
            'author': str(post.author) if post.author else '[deleted]',
            'link': f"https://www.reddit.com{post.permalink}",
            'url': post.url if hasattr(post, 'url') else '',
            'subreddit': str(post.subreddit),
            'timestamp': post_time.isoformat(),
            'score': post.score,
            'num_comments': post.num_comments,
            'upvote_ratio': post.upvote_ratio if hasattr(post, 'upvote_ratio') else 0,
            'full_text': f"{post.title}\n\n{post.selftext}".strip()
        }
    
    def search_posts(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Search for posts matching keywords across specified subreddits
        
        Args:
            limit: Maximum posts per subreddit (defaults to config value)
            
        Returns:
            List of post dictionaries
        """
        all_posts = []
        seen_ids = set()
        limit = limit or Config.MAX_POSTS_PER_SUBREDDIT
        
        for subreddit_name in self.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search in new posts
                for post in subreddit.new(limit=limit):
                    if not self._is_recent(post):
                        continue
                    
                    post_text = f"{post.title} {post.selftext}".lower()
                    if self._matches_keywords(post_text):
                        if post.id in seen_ids:
                            continue
                        seen_ids.add(post.id)
                        all_posts.append(self._extract_post_data(post))
                
                # Also search in hot posts
                for post in subreddit.hot(limit=max(1, limit // 2)):
                    if not self._is_recent(post):
                        continue
                    
                    post_text = f"{post.title} {post.selftext}".lower()
                    
                    if self._matches_keywords(post_text):
                        if post.id in seen_ids:
                            continue
                        seen_ids.add(post.id)
                        all_posts.append(self._extract_post_data(post))
            
            except Exception as e:
                print(f"Error monitoring subreddit {subreddit_name}: {str(e)}")
                continue
        
        return all_posts
    
    # def get_post_comments(self, post_id: str, subreddit: str, limit: int = 10) -> List[Dict]:
    #     """Get top comments for a specific post"""
    #     try:
    #         submission = self.reddit.submission(id=post_id)
    #         comments = []
    #
    #         submission.comments.replace_more(limit=0)
    #         for comment in submission.comments.list()[:limit]:
    #             if hasattr(comment, 'body') and comment.author:
    #                 comments.append({
    #                     'author': str(comment.author),
    #                     'content': comment.body,
    #                     'score': comment.score,
    #                     'timestamp': datetime.fromtimestamp(comment.created_utc).isoformat()
    #                 })
    #
    #         return comments
    #     except Exception as e:
    #         print(f"Error fetching comments for post {post_id}: {str(e)}")
    #         return []

