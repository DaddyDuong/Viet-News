from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class NewsArticleBase(BaseModel):
    title: str = Field(..., description="Article title")
    content: Optional[str] = Field(None, description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    author: Optional[str] = Field(None, description="Article author")
    category: Optional[str] = Field(None, description="Article category")
    url: str = Field(..., description="Article URL")
    image_url: Optional[str] = Field(None, description="Article image URL")
    published_date: Optional[datetime] = Field(None, description="Article published date")
    tags: Optional[str] = Field(None, description="Article tags as JSON string")

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticleResponse(NewsArticleBase):
    id: int
    scraped_date: datetime
    is_active: bool
    view_count: int
    
    class Config:
        from_attributes = True

class NewsArticleList(BaseModel):
    articles: List[NewsArticleResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class ScrapeRequest(BaseModel):
    category: Optional[str] = Field(None, description="Category to scrape (optional)")
    limit: int = Field(20, description="Number of articles to scrape", ge=1, le=100)

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    scraped_count: int
    total_articles: int

class CategoryResponse(BaseModel):
    categories: List[dict]

class StatsResponse(BaseModel):
    total_articles: int
    articles_by_category: dict
    recent_articles_count: int
    active_articles_count: int