from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional
import json
from datetime import datetime, timedelta

from database import get_db, NewsArticle
from scraper import VnExpressScraper
from schemas import (
    NewsArticleResponse, 
    NewsArticleList, 
    ScrapeRequest, 
    ScrapeResponse,
    CategoryResponse,
    StatsResponse
)

app = FastAPI(
    title="VnExpress News Scraper API",
    description="API for scraping and accessing VnExpress news articles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper
scraper = VnExpressScraper()

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VnExpress News Scraper API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "scrape": "/scrape",
            "articles": "/articles",
            "search": "/articles/search",
            "categories": "/categories",
            "stats": "/stats"
        }
    }

@app.post("/scrape", response_model=ScrapeResponse, tags=["Scraping"])
async def scrape_news(
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scrape news articles from VnExpress"""
    try:
        # Add scraping task to background
        background_tasks.add_task(
            scrape_articles_background,
            scrape_request.category,
            scrape_request.limit,
            db
        )
        
        return ScrapeResponse(
            success=True,
            message=f"Scraping started for category '{scrape_request.category or 'all'}' with limit {scrape_request.limit}",
            scraped_count=0,
            total_articles=db.query(NewsArticle).count()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scrape: {str(e)}")

async def scrape_articles_background(category: Optional[str], limit: int, db: Session):
    """Background task for scraping articles"""
    try:
        # Scrape articles
        articles_data = scraper.scrape_multiple_articles(category or '', limit)
        
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
        
        db.commit()
        print(f"Successfully scraped {scraped_count} new articles")
        
    except Exception as e:
        print(f"Error in background scraping: {e}")
        db.rollback()

@app.get("/articles", response_model=NewsArticleList, tags=["Articles"])
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Articles per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    db: Session = Depends(get_db)
):
    """Get articles with pagination and filtering"""
    try:
        # Build query
        query = db.query(NewsArticle).filter(NewsArticle.is_active == True)
        
        # Apply filters
        if category:
            query = query.filter(NewsArticle.category.ilike(f"%{category}%"))
        
        if search:
            search_filter = func.lower(NewsArticle.title).contains(search.lower()) | \
                          func.lower(NewsArticle.content).contains(search.lower())
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        articles = query.order_by(desc(NewsArticle.published_date)).offset(offset).limit(limit).all()
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit
        
        return NewsArticleList(
            articles=articles,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")

@app.get("/articles/{article_id}", response_model=NewsArticleResponse, tags=["Articles"])
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID"""
    try:
        article = db.query(NewsArticle).filter(
            NewsArticle.id == article_id,
            NewsArticle.is_active == True
        ).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Increment view count
        article.view_count += 1
        db.commit()
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving article: {str(e)}")

@app.get("/articles/search/{query}", response_model=NewsArticleList, tags=["Articles"])
async def search_articles(
    query: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Articles per page"),
    db: Session = Depends(get_db)
):
    """Search articles by query in title and content"""
    try:
        # Build search query
        search_filter = func.lower(NewsArticle.title).contains(query.lower()) | \
                       func.lower(NewsArticle.content).contains(query.lower()) | \
                       func.lower(NewsArticle.summary).contains(query.lower())
        
        query_obj = db.query(NewsArticle).filter(
            and_(NewsArticle.is_active == True, search_filter)
        )
        
        # Get total count
        total = query_obj.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        articles = query_obj.order_by(desc(NewsArticle.published_date)).offset(offset).limit(limit).all()
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit
        
        return NewsArticleList(
            articles=articles,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching articles: {str(e)}")

@app.get("/categories", response_model=CategoryResponse, tags=["Categories"])
async def get_categories(db: Session = Depends(get_db)):
    """Get all available categories with article counts"""
    try:
        # Get categories from scraper
        scraper_categories = [
            {"slug": slug, "name": name, "count": 0}
            for slug, name in scraper.categories.items()
        ]
        
        # Get actual counts from database
        category_counts = db.query(
            NewsArticle.category,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.is_active == True
        ).group_by(NewsArticle.category).all()
        
        # Update counts
        count_dict = {cat: count for cat, count in category_counts}
        for cat_info in scraper_categories:
            cat_info['count'] = count_dict.get(cat_info['name'], 0)
        
        return CategoryResponse(categories=scraper_categories)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics about scraped articles"""
    try:
        # Total articles
        total_articles = db.query(NewsArticle).count()
        
        # Active articles
        active_articles = db.query(NewsArticle).filter(NewsArticle.is_active == True).count()
        
        # Articles by category
        category_stats = db.query(
            NewsArticle.category,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.is_active == True
        ).group_by(NewsArticle.category).all()
        
        articles_by_category = {cat: count for cat, count in category_stats}
        
        # Recent articles (last 24 hours)
        recent_date = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(NewsArticle).filter(
            and_(
                NewsArticle.scraped_date >= recent_date,
                NewsArticle.is_active == True
            )
        ).count()
        
        return StatsResponse(
            total_articles=total_articles,
            articles_by_category=articles_by_category,
            recent_articles_count=recent_articles,
            active_articles_count=active_articles
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@app.delete("/articles/{article_id}", tags=["Articles"])
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Soft delete an article (mark as inactive)"""
    try:
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article.is_active = False
        db.commit()
        
        return {"message": f"Article {article_id} has been deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting article: {str(e)}")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VnExpress News Scraper API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)