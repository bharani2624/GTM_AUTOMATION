import json

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pandas.core.indexes.base import str_t

from sheets_manager import SheetsManager
from config import Config
from arango_manager import ArangoManager


class TrendsAnalyzer:
    """Analyze trends in relevant posts over time"""
    
    def __init__(self):
        """Initialize with sheets manager"""
        self.sheets = SheetsManager()
        self.arango=ArangoManager()
    
    def get_weekly_stats(self, weeks: int = 4) -> Dict:
        """
        Get weekly statistics for relevant posts
        
        Args:
            weeks: Number of weeks to analyze
            
        Returns:
            Dictionary with weekly statistics
        """
        try:
            # Read all data from sheet
            data = self.arango.get_existing_posts()
            
            if not data:
                return {
                    'total_posts': 0,
                    'weeks': [],
                    'by_intent': {},
                    'by_subreddit': {},
                    'trend': 'insufficient_data'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Parse timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter to last N weeks
            cutoff_date = datetime.now() - timedelta(weeks=weeks)
            df = df[df['timestamp'] >= cutoff_date]
            
            # Calculate weekly stats
            df['Week'] = df['timestamp'].dt.to_period('W')
            weekly_stats = df.groupby('Week').agg({
                'post_link': 'count',
                'relevance_score': 'mean',
                'intent': lambda x: x.value_counts().to_dict()
            }).to_dict()
            
            # Get intent distribution
            intent_dist = df['intent'].value_counts().to_dict()
            
            # Get subreddit distribution
            subreddit_dist = df['subreddit'].value_counts().to_dict()
            
            # Calculate trend
            if len(df) >= 2:
                recent_week = df[df['timestamp'] >= datetime.now() - timedelta(weeks=1)].shape[0]
                previous_week = df[(df['timestamp'] >= datetime.now() - timedelta(weeks=2)) & 
                                   (df['timestamp'] < datetime.now() - timedelta(weeks=1))].shape[0]
                
                if recent_week > previous_week * 1.2:
                    trend = 'increasing'
                elif recent_week < previous_week * 0.8:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'total_posts': len(df),
                'weeks': [str(week) for week in sorted(df['Week'].unique())],
                'weekly_counts': {
                    str(week): count for week, count in 
                    df.groupby('Week').size().items()
                },
                'average_relevance': df['relevance_score'].mean(),
                'by_intent': intent_dist,
                'by_subreddit': subreddit_dist,
                'trend': trend,
                'high_priority_count': len(df[df['Priority'] == 'high']) if 'Priority' in df.columns else 0
            }
        
        except Exception as e:
            print(f"Error analyzing trends: {str(e)}")
            return {
                'error': str(e),
                'total_posts': 0
            }
    
    def print_summary(self, stats: Dict):
        """Print a formatted summary of trends"""
        print("\n" + "=" * 60)
        print("TRENDS ANALYSIS")
        print("=" * 60)

        if stats.get('error'):
            print(f"Error: {stats['error']}")
            return

        print(f"\nTotal Posts (Last 4 Weeks): {stats.get('total_posts', 0)}")
        print(f"Average relevance_score: {stats.get('average_relevance', 0):.2f}")
        print(f"Trend: {stats.get('trend', 'unknown').upper()}")
        print(f"High Priority Posts: {stats.get('high_priority_count', 0)}")

        print("\n--- Weekly Breakdown ---")
        for week, count in stats.get('weekly_counts', {}).items():
            print(f"  {week}: {count} posts")

        print("\n--- By intent ---")
        for intent, count in stats.get('by_intent', {}).items():
            print(f"  {intent}: {count}")

        print("\n--- By subreddit ---")
        for subreddit, count in list(stats.get('by_subreddit', {}).items())[:5]:
            print(f"  r/{subreddit}: {count}")

        print("=" * 60 + "\n")

    def save_trends_analysis(self, stats: Dict, analysis_id: Optional[str] = None):
        """
        Save trends analysis to ArangoDB

        Args:
            stats: Dictionary containing trends statistics
            analysis_id: Optional custom ID for the document

        Returns:
            Document key of the saved record
        """

        # Prepare document
        document = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_posts': stats.get('total_posts', 0),
            'average_relevance': stats.get('average_relevance', 0),
            'trend': stats.get('trend', 'unknown'),
            'high_priority_count': stats.get('high_priority_count', 0),
            'weekly_counts': stats.get('weekly_counts', {}),
            'by_intent': stats.get('by_intent', {}),
            'by_subreddit': stats.get('by_subreddit', {}),
            'error': stats.get('error')
        }
        try:
            res = self.arango.insert_weekly_trends(json.dumps(document, indent=2))
            return res
        except Exception as e:
            return {"error":e}

    def run(self):
        """Run trends analysis"""
        analyzer = TrendsAnalyzer()
        stats = analyzer.get_weekly_stats(weeks=4)
        analyzer.print_summary(stats)
        return analyzer.save_trends_analysis(stats)




