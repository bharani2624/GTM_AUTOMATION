"""
Main GTM Automation Workflow Orchestrator
"""
from unittest.mock import sentinel

from reddit_monitor import RedditMonitor
from ai_scorer import AIScorer
from engagement_generator import EngagementGenerator
from arango_manager import ArangoManager
from slack_notifier import SlackNotifier
from typing import List, Dict
import time
from datetime import datetime


class GTMAutomationWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self, dry_run: bool = False):
        """Initialize all components"""
        self.dry_run = dry_run
        self.monitor = RedditMonitor()
        self.scorer = AIScorer()
        self.engagement_gen = EngagementGenerator()
        
        # Initialize Arango/Slack only if not in dry-run
        if not self.dry_run:
            self.arango = ArangoManager()
            self.slack = SlackNotifier()
            # Track processed posts to avoid duplicates using DB
            self.processed_post_ids = self.arango.get_existing_post_ids()
            print(f"Loaded {len(self.processed_post_ids)} existing post IDs for deduplication")
        else:
            self.arango = None
            self.slack = None
            self.processed_post_ids = set()
            print("Dry-run mode: Skipping ArangoDB/Slack initialization")
    
    def run(self, dry_run: bool = False) -> Dict:
        """
        Execute the complete workflow
        
        Args:
            dry_run: If True, don't write to sheets or send notifications
            
        Returns:
            Dictionary with execution summary
        """
        print("=" * 60)
        print("GTM Automation Workflow Started")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Step 1: Monitor Reddit for posts
        print("\n[Step 1] Monitoring Reddit for posts...")
        posts = self.monitor.search_posts()
        print(f"Found {len(posts)} posts matching keywords")
        
        # Filter out already processed posts
        new_posts = [p for p in posts if p['post_id'] not in self.processed_post_ids]
        print(f"Found {len(new_posts)} new posts (after deduplication)")
        
        if not new_posts:
            print("No new posts to process")
            return {
                'total_posts': len(posts),
                'new_posts': 0,
                'processed': 0,
                'relevant_posts': 0,
                'high_priority': 0
            }
        
        # Step 2: Score and classify posts
        print("\n[Step 2] Classifying and scoring posts with AI...")
        results = []
        relevant_count = 0
        high_priority_count = 0
        
        for i, post in enumerate(new_posts, 1):
            print(f"Processing post {i}/{len(new_posts)}: {post['title'][:50]}...")
            
            # Classify post
            classification = self.scorer.classify_and_score(post)
            
            # Only process relevant posts further
            if classification.get('is_relevant', False):
                relevant_count += 1
                
                # Generate summary
                summary = self.scorer.generate_summary(post)
                
                # Generate engagement suggestion
                engagement = self.engagement_gen.generate_suggestion(post, classification)

                sentiment=self.scorer.generate_sentiment(post)
                
                result = {
                    'post_data': post,
                    'classification': classification,
                    'engagement': engagement,
                    'summary': summary,
                    'sentiment':sentiment
                }
                
                results.append(result)
                
                # Check if high priority
                if classification.get('relevance_score', 0.0) >= 0.85 or \
                   engagement.get('priority') == 'high':
                    high_priority_count += 1
                    print(f"  ⚠️  High-priority post detected!")
                
                # Rate limiting
                time.sleep(1)  # Be respectful to APIs
        
        print(f"\n[Step 2 Complete] {relevant_count} relevant posts found")
        print(f"  - High priority: {high_priority_count}")
        
        # Step 3: Store results in ArangoDB
        if results and not dry_run and self.arango is not None:
            print("\n[Step 3] Storing results in ArangoDB...")
            self.arango.add_results(results)
            print(f"Stored {len(results)} results")
        
        # Step 4: Send Slack notifications for high-priority posts
        if results and not dry_run and self.slack is not None:
            print("\n[Step 4] Sending Slack notifications...")
            notification_count = 0
            for result in results:
                classification = result.get('classification', {})
                engagement = result.get('engagement', {})
                
                if classification.get('relevance_score', 0.0) >= 0.85 or \
                   engagement.get('priority') == 'high':
                    self.slack.notify_high_priority_post(result)
                    notification_count += 1
            
            print(f"Sent {notification_count} Slack notifications")
        
        # Update processed post IDs
        for post in new_posts:
            self.processed_post_ids.add(post['post_id'])
        
        # Summary
        print("\n" + "=" * 60)
        print("Workflow Complete!")
        print("=" * 60)
        print(f"Total posts found: {len(posts)}")
        print(f"New posts: {len(new_posts)}")
        print(f"Relevant posts: {relevant_count}")
        print(f"High-priority posts: {high_priority_count}")
        print("=" * 60)
        
        return {
            'total_posts': len(posts),
            'new_posts': len(new_posts),
            'processed': len(results),
            'relevant_posts': relevant_count,
            'high_priority': high_priority_count
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GTM Automation Workflow')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run without writing to sheets or sending notifications')
    args = parser.parse_args()
    
    workflow = GTMAutomationWorkflow(dry_run=args.dry_run)
    summary = workflow.run(dry_run=args.dry_run)
    
    print("\nExecution Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

