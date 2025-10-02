from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./vnexpress_news.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    category = Column(String, index=True, nullable=True)
    url = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True)
    published_date = Column(DateTime, nullable=True)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    tags = Column(String, nullable=True)  # JSON string of tags

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()