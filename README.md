# VnExpress News Scraper

A comprehensive automation tool that scrapes news articles from VnExpress and provides a REST API to access the scraped data.

## Features

- **Automated News Scraping**: Scrapes news articles from VnExpress including title, content, summary, author, category, images, and metadata
- **REST API**: Provides endpoints to access, search, and manage scraped articles
- **Database Storage**: Stores articles in SQLite database with proper indexing
- **Background Scheduling**: Automatically scrapes new articles every 30 minutes
- **Category Support**: Supports all major VnExpress categories (Thời sự, Thế giới, Kinh doanh, etc.)
- **Search Functionality**: Full-text search across article titles and content
- **Pagination**: Efficient pagination for large datasets
- **CLI Tool**: Command-line interface for manual operations
- **Statistics**: Comprehensive statistics and analytics

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   The database will be automatically created when you first run the application.

## Usage

### Starting the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

### API Endpoints

#### Core Endpoints

- `GET /` - API information and available endpoints
- `POST /scrape` - Start scraping news articles
- `GET /articles` - Get articles with pagination and filtering
- `GET /articles/{id}` - Get a specific article
- `GET /articles/search/{query}` - Search articles
- `GET /categories` - Get available categories
- `GET /stats` - Get scraping statistics
- `GET /health` - Health check

#### Scraping Articles

```bash
# Scrape 20 articles from all categories
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20}'

# Scrape articles from specific category
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"category": "thoi-su", "limit": 10}'
```

#### Getting Articles

```bash
# Get articles with pagination
curl "http://localhost:8000/articles?page=1&limit=10"

# Filter by category
curl "http://localhost:8000/articles?category=thoi-su&page=1&limit=10"

# Search articles
curl "http://localhost:8000/articles/search/covid"
```

### Command Line Interface

The CLI tool provides additional functionality:

```bash
# Show available commands
python cli.py --help

# Scrape articles and save to database
python cli.py scrape --category thoi-su --limit 20 --save

# Scrape and save to JSON file
python cli.py scrape --limit 50 --output news.json

# List articles from database
python cli.py list --category "Thời sự" --limit 10

# Show statistics
python cli.py stats

# Show available categories
python cli.py categories

# Export articles to JSON
python cli.py export --output all_news.json
```

## Supported Categories

- **thoi-su** - Thời sự (Current Affairs)
- **goc-nhin** - Góc nhìn (Perspectives)
- **the-gioi** - Thế giới (World)
- **kinh-doanh** - Kinh doanh (Business)
- **bat-dong-san** - Bất động sản (Real Estate)
- **khoa-hoc** - Khoa học (Science)
- **giai-tri** - Giải trí (Entertainment)
- **the-thao** - Thể thao (Sports)
- **phap-luat** - Pháp luật (Law)
- **giao-duc** - Giáo dục (Education)
- **suc-khoe** - Sức khỏe (Health)
- **doi-song** - Đời sống (Lifestyle)
- **du-lich** - Du lịch (Travel)
- **so-hoa** - Số hóa (Digital)
- **xe** - Xe (Vehicles)
- **oto** - Ô tô (Cars)

## Database Schema

The application uses SQLite with the following main table:

### NewsArticle Table
- `id` - Primary key
- `title` - Article title
- `content` - Full article content
- `summary` - Article summary/description
- `author` - Article author
- `category` - Article category
- `url` - Original article URL (unique)
- `image_url` - Main article image URL
- `published_date` - Original publication date
- `scraped_date` - When the article was scraped
- `is_active` - Soft delete flag
- `view_count` - Number of times accessed via API
- `tags` - Article tags as JSON

## Configuration

### Scraping Settings

You can modify the scraping behavior in `scraper.py`:

- Change `User-Agent` for different browser simulation
- Adjust delays between requests in `scrape_article()`
- Modify category mappings in `categories` dict
- Update CSS selectors if VnExpress changes their layout

### Scheduling

The automatic scraping schedule can be modified in `scheduler.py`:

- Change interval from 30 minutes to desired frequency
- Add/remove categories from the `categories` list
- Adjust number of articles per category

### API Configuration

Modify `main.py` for API settings:

- Change port number in `uvicorn.run()`
- Adjust CORS settings for production
- Modify pagination limits
- Add authentication if needed

## Examples

### Python Usage

```python
from scraper import VnExpressScraper
from database import SessionLocal, NewsArticle

# Initialize scraper
scraper = VnExpressScraper()

# Scrape articles
articles = scraper.scrape_multiple_articles('thoi-su', 10)

# Save to database
db = SessionLocal()
for article_data in articles:
    db_article = NewsArticle(**article_data)
    db.add(db_article)
db.commit()
```

### API Response Example

```json
{
  "articles": [
    {
      "id": 1,
      "title": "Tin tức mới nhất từ VnExpress",
      "content": "Nội dung chi tiết của bài báo...",
      "summary": "Tóm tắt bài báo",
      "author": "Tác giả",
      "category": "Thời sự",
      "url": "https://vnexpress.net/tin-tuc-123456.html",
      "image_url": "https://i1-vnexpress.vnecdn.net/...",
      "published_date": "2024-01-15T10:30:00",
      "scraped_date": "2024-01-15T11:00:00",
      "is_active": true,
      "view_count": 5,
      "tags": "[\"tag1\", \"tag2\"]"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8
}
```

## Error Handling

The application includes comprehensive error handling:

- Network timeouts and connection errors
- Invalid article URLs
- Database connection issues
- Malformed HTML content
- Rate limiting protection

## Performance Considerations

- Uses connection pooling for database
- Implements random delays to avoid being blocked
- Background tasks for non-blocking scraping
- Efficient database queries with proper indexing
- Pagination to handle large datasets

## Contributing

To extend the scraper:

1. Add new CSS selectors for additional data fields
2. Implement new categories or news sources
3. Add new API endpoints for specific functionality
4. Improve error handling and logging

## License

This project is for educational and personal use. Please respect VnExpress's robots.txt and terms of service when scraping.

## Notes

- The scraper includes respectful delays to avoid overwhelming the target server
- Articles are stored with unique URL constraint to prevent duplicates
- The API includes CORS support for web applications
- All Vietnamese text is properly handled with UTF-8 encoding