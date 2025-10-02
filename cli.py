#!/usr/bin/env python3
"""
VnExpress News Scraper - Command Line Interface
Usage: python cli.py [command] [options]
"""

import argparse
import sys
import json
from datetime import datetime
from scraper import VnExpressScraper
from database import SessionLocal, NewsArticle

def scrape_command(args):
    """Scrape news articles"""
    scraper = VnExpressScraper()
    
    print(f"Starting scraping...")
    print(f"Category: {args.category or 'All'}")
    print(f"Limit: {args.limit}")
    
    # Scrape articles
    articles = scraper.scrape_multiple_articles(args.category, args.limit)
    
    if args.save:
        # Save to database
        db = SessionLocal()
        saved_count = 0
        
        for article_data in articles:
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
                saved_count += 1
        
        db.commit()
        db.close()
        
        print(f"Saved {saved_count} new articles to database")
    
    if args.output:
        # Save to JSON file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2, default=str)
        print(f"Saved articles to {args.output}")
    
    print(f"Scraped {len(articles)} articles")

def list_command(args):
    """List articles from database"""
    db = SessionLocal()
    
    query = db.query(NewsArticle).filter(NewsArticle.is_active == True)
    
    if args.category:
        query = query.filter(NewsArticle.category.ilike(f"%{args.category}%"))
    
    articles = query.order_by(NewsArticle.scraped_date.desc()).limit(args.limit).all()
    
    print(f"Found {len(articles)} articles:")
    print("-" * 80)
    
    for article in articles:
        print(f"ID: {article.id}")
        print(f"Title: {article.title[:100]}...")
        print(f"Category: {article.category}")
        print(f"Author: {article.author}")
        print(f"Published: {article.published_date}")
        print(f"URL: {article.url}")
        print("-" * 80)
    
    db.close()

def stats_command(args):
    """Show statistics"""
    db = SessionLocal()
    
    total_articles = db.query(NewsArticle).count()
    active_articles = db.query(NewsArticle).filter(NewsArticle.is_active == True).count()
    
    # Category statistics
    from sqlalchemy import func
    category_stats = db.query(
        NewsArticle.category,
        func.count(NewsArticle.id).label('count')
    ).filter(
        NewsArticle.is_active == True
    ).group_by(NewsArticle.category).all()
    
    print("=== VnExpress News Scraper Statistics ===")
    print(f"Total articles: {total_articles}")
    print(f"Active articles: {active_articles}")
    print(f"Inactive articles: {total_articles - active_articles}")
    print()
    print("Articles by category:")
    for category, count in category_stats:
        print(f"  {category or 'Unknown'}: {count}")
    
    db.close()

def categories_command(args):
    """List available categories"""
    scraper = VnExpressScraper()
    
    print("Available categories:")
    print("-" * 30)
    for slug, name in scraper.categories.items():
        print(f"{slug:15} - {name}")

def export_command(args):
    """Export articles to JSON"""
    db = SessionLocal()
    
    query = db.query(NewsArticle).filter(NewsArticle.is_active == True)
    
    if args.category:
        query = query.filter(NewsArticle.category.ilike(f"%{args.category}%"))
    
    articles = query.all()
    
    # Convert to dict
    articles_data = []
    for article in articles:
        article_dict = {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'summary': article.summary,
            'author': article.author,
            'category': article.category,
            'url': article.url,
            'image_url': article.image_url,
            'published_date': article.published_date.isoformat() if article.published_date else None,
            'scraped_date': article.scraped_date.isoformat(),
            'view_count': article.view_count,
            'tags': article.tags
        }
        articles_data.append(article_dict)
    
    # Save to file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(articles_data)} articles to {args.output}")
    
    db.close()

def main():
    parser = argparse.ArgumentParser(description='VnExpress News Scraper CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape news articles')
    scrape_parser.add_argument('--category', '-c', help='Category to scrape')
    scrape_parser.add_argument('--limit', '-l', type=int, default=20, help='Number of articles to scrape')
    scrape_parser.add_argument('--save', '-s', action='store_true', help='Save to database')
    scrape_parser.add_argument('--output', '-o', help='Output JSON file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List articles from database')
    list_parser.add_argument('--category', '-c', help='Filter by category')
    list_parser.add_argument('--limit', '-l', type=int, default=10, help='Number of articles to show')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Categories command
    categories_parser = subparsers.add_parser('categories', help='List available categories')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export articles to JSON')
    export_parser.add_argument('--category', '-c', help='Filter by category')
    export_parser.add_argument('--output', '-o', required=True, help='Output JSON file')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        scrape_command(args)
    elif args.command == 'list':
        list_command(args)
    elif args.command == 'stats':
        stats_command(args)
    elif args.command == 'categories':
        categories_command(args)
    elif args.command == 'export':
        export_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()