#!/usr/bin/env python3
"""
Post Tracker - Prevents duplicate news posts
============================================

Tracks which article URLs have been posted to prevent
posting the same news multiple times.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set
from loguru import logger


class PostTracker:
    """Tracks posted articles to prevent duplicates."""
    
    def __init__(self, tracker_file: str = "posted_articles.json"):
        """
        Initialize post tracker.
        
        Args:
            tracker_file: Path to JSON file storing posted article URLs
        """
        self.tracker_file = Path(tracker_file)
        self.posted_urls: Dict[str, str] = {}  # url -> timestamp
        self._load_tracker()
    
    def _load_tracker(self):
        """Load posted URLs from tracker file."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    self.posted_urls = json.load(f)
                logger.info(f"Loaded {len(self.posted_urls)} posted URLs from tracker")
            except Exception as e:
                logger.error(f"Failed to load tracker file: {e}")
                self.posted_urls = {}
        else:
            logger.info("No existing tracker file found, starting fresh")
            self.posted_urls = {}
    
    def _save_tracker(self):
        """Save posted URLs to tracker file."""
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.posted_urls, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.posted_urls)} posted URLs to tracker")
        except Exception as e:
            logger.error(f"Failed to save tracker file: {e}")
    
    def is_posted(self, url: str) -> bool:
        """
        Check if an article URL has already been posted.
        
        Args:
            url: Article URL to check
            
        Returns:
            True if already posted, False otherwise
        """
        return url in self.posted_urls
    
    def mark_as_posted(self, url: str):
        """
        Mark an article URL as posted.
        
        Args:
            url: Article URL to mark as posted
        """
        self.posted_urls[url] = datetime.now().isoformat()
        self._save_tracker()
    
    def mark_batch_as_posted(self, urls: List[str]):
        """
        Mark multiple article URLs as posted.
        
        Args:
            urls: List of article URLs to mark as posted
        """
        timestamp = datetime.now().isoformat()
        for url in urls:
            self.posted_urls[url] = timestamp
        self._save_tracker()
    
    def filter_new_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter out articles that have already been posted.
        
        Args:
            articles: List of article dicts with 'url' key
            
        Returns:
            List of articles that haven't been posted yet
        """
        new_articles = []
        duplicate_count = 0
        
        for article in articles:
            url = article.get('url')
            if not url:
                continue
            
            if self.is_posted(url):
                duplicate_count += 1
                logger.debug(f"Skipping already posted: {url}")
            else:
                new_articles.append(article)
        
        logger.info(f"Filtered articles: {len(new_articles)} new, {duplicate_count} duplicates")
        return new_articles
    
    def cleanup_old_entries(self, days: int = 30):
        """
        Remove entries older than specified days to prevent tracker from growing indefinitely.
        
        Args:
            days: Remove entries older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.posted_urls)
        
        # Filter out old entries
        self.posted_urls = {
            url: timestamp
            for url, timestamp in self.posted_urls.items()
            if datetime.fromisoformat(timestamp) > cutoff_date
        }
        
        removed_count = original_count - len(self.posted_urls)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old entries (older than {days} days)")
            self._save_tracker()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about tracked posts.
        
        Returns:
            Dictionary with tracker statistics
        """
        if not self.posted_urls:
            return {
                'total_posted': 0,
                'oldest_post': None,
                'newest_post': None
            }
        
        timestamps = [datetime.fromisoformat(ts) for ts in self.posted_urls.values()]
        
        return {
            'total_posted': len(self.posted_urls),
            'oldest_post': min(timestamps).isoformat(),
            'newest_post': max(timestamps).isoformat()
        }


def main():
    """Test the post tracker."""
    tracker = PostTracker()
    
    # Show stats
    stats = tracker.get_stats()
    print("Post Tracker Statistics:")
    print(f"  Total posted articles: {stats['total_posted']}")
    if stats['oldest_post']:
        print(f"  Oldest post: {stats['oldest_post']}")
        print(f"  Newest post: {stats['newest_post']}")
    
    # Cleanup old entries
    tracker.cleanup_old_entries(days=30)


if __name__ == '__main__':
    main()
