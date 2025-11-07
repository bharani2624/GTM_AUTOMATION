"""
Google Sheets integration for storing results
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict
from config import Config
from datetime import datetime


class SheetsManager:
    """Manage Google Sheets operations"""
    
    def __init__(self):
        """Initialize Google Sheets client"""
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
            scopes=scope
        )
        
        self.client = gspread.authorize(creds)
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.sheet = None
        self._initialize_sheet()
    
    def _initialize_sheet(self):
        """Open or create the sheet and set up headers"""
        try:
            self.sheet = self.client.open_by_key(self.sheet_id).sheet1
        except Exception as e:
            print(f"Error opening sheet: {str(e)}")
            print("Please ensure the sheet ID is correct and the service account has access")
            raise
        
        # Check if headers exist, if not create them
        try:
            headers = self.sheet.row_values(1)
            expected_headers = [
                'Timestamp', 'Post Link', 'Post Title', 'Post Summary', 
                'Author', 'Subreddit', 'Relevance Score', 'Is Relevant',
                'Intent', 'Intent Score', 'Engagement Comment', 'Engagement DM',
                'Engagement Strategy', 'Priority', 'AI Reasoning'
            ]
            
            if not headers or headers != expected_headers:
                self.sheet.clear()
                self.sheet.append_row(expected_headers)
                # Format header row
                self.sheet.format('A1:O1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                })
        
        except Exception as e:
            print(f"Error checking headers: {str(e)}")
    
    def add_results(self, results: List[Dict]):
        """
        Add results to Google Sheet
        
        Args:
            results: List of dictionaries with post data, classification, and engagement
        """
        rows_to_add = []
        
        for result in results:
            post_data = result.get('post_data', {})
            classification = result.get('classification', {})
            engagement = result.get('engagement', {})
            
            row = [
                datetime.now().isoformat(),  # Timestamp
                post_data.get('link', ''),  # Post Link
                post_data.get('title', ''),  # Post Title
                result.get('summary', ''),  # Post Summary
                post_data.get('author', ''),  # Author
                post_data.get('subreddit', ''),  # Subreddit
                classification.get('relevance_score', 0.0),  # Relevance Score
                classification.get('is_relevant', False),  # Is Relevant
                classification.get('intent', ''),  # Intent
                classification.get('intent_score', 0.0),  # Intent Score
                engagement.get('comment_draft', ''),  # Engagement Comment
                engagement.get('dm_draft', ''),  # Engagement DM
                engagement.get('strategy', ''),  # Engagement Strategy
                engagement.get('priority', ''),  # Priority
                classification.get('reasoning', '')  # AI Reasoning
            ]
            
            rows_to_add.append(row)
        
        if rows_to_add:
            try:
                self.sheet.append_rows(rows_to_add)
                print(f"Added {len(rows_to_add)} rows to Google Sheet")
            except Exception as e:
                print(f"Error adding rows to sheet: {str(e)}")
    
    def get_existing_post_ids(self, limit: int = 1000) -> set:
        """Get post IDs that already exist in the sheet (for deduplication)"""
        try:
            # Get post links from column B (index 2)
            links = self.sheet.col_values(2)[1:]  # Skip header
            post_ids = set()
            
            for link in links:
                # Extract post ID from Reddit URL
                if 'reddit.com' in link:
                    parts = link.split('/')
                    if 'comments' in parts:
                        idx = parts.index('comments')
                        if idx + 1 < len(parts):
                            post_ids.add(parts[idx + 1])
            
            return post_ids
        
        except Exception as e:
            print(f"Error reading existing posts: {str(e)}")
            return set()

