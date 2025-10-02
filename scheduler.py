from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal, NewsArticle
from scraper import VnExpressScraper
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = VnExpressScraper()
        
    def start(self):
        """Start the scheduler"""
        # Schedule scraping every 30 minutes
        self.scheduler.add_job(
            func=self.scheduled_scrape,
            trigger=IntervalTrigger(minutes=30),
            id='scrape_news',
            name='Scrape VnExpress News',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("News scheduler started - scraping every 30 minutes")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("News scheduler stopped")
    
    def scheduled_scrape(self):
        """Scheduled scraping task"""
        try:
            logger.info("Starting scheduled news scraping...")
            
            # Scrape from multiple categories with more articles per category
            categories = ['', 'thoi-su', 'the-gioi', 'kinh-doanh', 'the-thao', 'giai-tri', 'suc-khoe', 'giao-duc']
            total_scraped = 0
            
            db = SessionLocal()
            
            for category in categories:
                try:
                    logger.info(f"Scraping category: {category or 'homepage'}")
                    # Increase limit to get more articles per category
                    articles_data = self.scraper.scrape_multiple_articles(category, 15)
                    
                    scraped_count = 0
                    for article_data in articles_data:
                        # Check if article already exists
                        existing_article = db.query(NewsArticle).filter(
                            NewsArticle.url == article_data['url']
                        ).first()
                        
                        if not existing_article:
                            # Create new article
                            db_article = NewsArticle(
                                title=article_data.get('title', ''),
                                content=article_data.get('content', ''),
                                summary=article_data.get('summary', ''),
                                author=article_data.get('author', ''),
                                category=article_data.get('category', ''),
                                url=article_data['url'],
                                image_url=article_data.get('image_url', ''),
                                published_date=article_data.get('published_date'),
                                tags=json.dumps(article_data.get('tags', []), ensure_ascii=False)
                            )
                            
                            db.add(db_article)
                            scraped_count += 1
                    
                    total_scraped += scraped_count
                    logger.info(f"Scraped {scraped_count} new articles from {category or 'homepage'}")
                    
                except Exception as e:
                    logger.error(f"Error scraping category {category}: {e}")
                    continue
            
            db.commit()
            db.close()
            
            logger.info(f"Scheduled scraping completed. Total new articles: {total_scraped}")
            
        except Exception as e:
            logger.error(f"Error in scheduled scraping: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()

# Global scheduler instance
scheduler = NewsScheduler()