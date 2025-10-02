import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
import random

class VnExpressScraper:
    def __init__(self):
        self.base_url = "https://vnexpress.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Category mappings
        self.categories = {
            'thoi-su': 'Thời sự',
            'goc-nhin': 'Góc nhìn',
            'the-gioi': 'Thế giới',
            'kinh-doanh': 'Kinh doanh',
            'bat-dong-san': 'Bất động sản',
            'khoa-hoc': 'Khoa học',
            'giai-tri': 'Giải trí',
            'the-thao': 'Thể thao',
            'phap-luat': 'Pháp luật',
            'giao-duc': 'Giáo dục',
            'suc-khoe': 'Sức khỏe',
            'doi-song': 'Đời sống',
            'du-lich': 'Du lịch',
            'so-hoa': 'Số hóa',
            'xe': 'Xe',
            'oto': 'Ô tô'
        }
    
    def get_article_links(self, category: str = '', limit: int = 20) -> List[str]:
        """Get article links from VnExpress homepage or category page"""
        try:
            if category and category in self.categories:
                url = f"{self.base_url}/{category}"
            else:
                url = self.base_url
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            article_links = []
            
            # Multiple selectors for different article types
            article_selectors = [
                'article.item-news',
                '.item-news',
                '.title-news',
                '.item-news-common',
                '.box-category-item',
                '.list-news-subfolder .item-news'
            ]
            
            # Try different selectors to get more articles
            for selector in article_selectors:
                articles = soup.select(selector)
                for article in articles:
                    if len(article_links) >= limit:
                        break
                    link_tag = article.find('a', href=True)
                    if link_tag and link_tag['href']:
                        full_url = urljoin(self.base_url, link_tag['href'])
                        if self.is_valid_article_url(full_url) and full_url not in article_links:
                            article_links.append(full_url)
            
            # Additional articles from all links on page
            if len(article_links) < limit:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    if len(article_links) >= limit:
                        break
                    href = link.get('href', '')
                    if href and self.is_valid_article_url(href):
                        full_url = urljoin(self.base_url, href)
                        if full_url not in article_links:
                            article_links.append(full_url)
            
            return article_links[:limit]
            
        except Exception as e:
            print(f"Error getting article links: {e}")
            return []
    
    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid VnExpress article"""
        if not url or not isinstance(url, str):
            return False
        
        # Check if it's a VnExpress URL
        if 'vnexpress.net' not in url:
            return False
        
        # Check if it contains article ID pattern
        if re.search(r'-\d+\.html$', url):
            return True
        
        return False
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape a single article from VnExpress"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article data
            article_data = {
                'url': url,
                'title': self.extract_title(soup),
                'content': self.extract_content(soup),
                'summary': self.extract_summary(soup),
                'author': self.extract_author(soup),
                'category': self.extract_category(url, soup),
                'published_date': self.extract_published_date(soup),
                'image_url': self.extract_image_url(soup),
                'tags': self.extract_tags(soup)
            }
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            return article_data
            
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        title_selectors = [
            'h1.title-detail',
            'h1.title_news_detail',
            'h1.title-news',
            'h1',
            '.title-detail',
            '.title_news_detail'
        ]
        
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                return title_tag.get_text(strip=True)
        
        return ""
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content"""
        content_selectors = [
            '.fck_detail',
            '.Normal',
            'article .content-detail',
            '.content_detail',
            '.article-content'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Remove ads and unwanted elements
                for unwanted in content_div.find_all(['script', 'style', '.VCSortableInPreviewMode']):
                    unwanted.decompose()
                
                # Get text content
                paragraphs = content_div.find_all('p')
                if paragraphs:
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    return content
                else:
                    return content_div.get_text(strip=True)
        
        return ""
    
    def extract_summary(self, soup: BeautifulSoup) -> str:
        """Extract article summary/description"""
        summary_selectors = [
            '.description',
            '.sapo',
            '.Lead',
            'p.description',
            '.article-summary'
        ]
        
        for selector in summary_selectors:
            summary_tag = soup.select_one(selector)
            if summary_tag:
                return summary_tag.get_text(strip=True)
        
        return ""
    
    def extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        author_selectors = [
            '.author',
            '.article-author',
            '.byline',
            '.writer'
        ]
        
        for selector in author_selectors:
            author_tag = soup.select_one(selector)
            if author_tag:
                return author_tag.get_text(strip=True)
        
        return ""
    
    def extract_category(self, url: str, soup: BeautifulSoup) -> str:
        """Extract article category"""
        # Try to get category from URL
        for cat_slug, cat_name in self.categories.items():
            if f'/{cat_slug}/' in url:
                return cat_name
        
        # Try to get from breadcrumb
        breadcrumb = soup.select_one('.breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) > 1:
                return links[1].get_text(strip=True)
        
        return "Khác"
    
    def extract_published_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract article published date"""
        date_selectors = [
            '.date',
            '.time',
            '.publish-time',
            '.article-date'
        ]
        
        for selector in date_selectors:
            date_tag = soup.select_one(selector)
            if date_tag:
                date_text = date_tag.get_text(strip=True)
                return self.parse_vietnamese_date(date_text)
        
        return None
    
    def extract_image_url(self, soup: BeautifulSoup) -> str:
        """Extract main article image"""
        img_selectors = [
            '.fig-picture img',
            '.photo img',
            'article img',
            '.content-detail img'
        ]
        
        for selector in img_selectors:
            img_tag = soup.select_one(selector)
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = self.base_url + img_url
                return img_url
        
        return ""
    
    def extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags"""
        tags = []
        
        # Try to find tags in various locations
        tag_selectors = [
            '.tags a',
            '.article-tags a',
            '.tag-list a'
        ]
        
        for selector in tag_selectors:
            tag_elements = soup.select(selector)
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
        
        return tags
    
    def parse_vietnamese_date(self, date_text: str) -> Optional[datetime]:
        """Parse Vietnamese date format"""
        try:
            # Remove common Vietnamese date prefixes
            date_text = re.sub(r'^(Ngày|ngày|Thứ.*?,?\s*)', '', date_text.strip())
            
            # Handle different date formats
            patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD format
                            year, month, day = map(int, groups)
                        else:  # DD/MM/YYYY or DD-MM-YYYY format
                            day, month, year = map(int, groups)
                        
                        return datetime(year, month, day)
            
            return None
            
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
            return None
    
    def scrape_multiple_articles(self, category: str = '', limit: int = 20) -> List[Dict]:
        """Scrape multiple articles"""
        print(f"Getting article links for category: {category}")
        article_links = self.get_article_links(category, limit)
        
        # If we don't have enough links from main page, try to get more from paginated results
        if len(article_links) < limit and category:
            print(f"Found {len(article_links)} links, trying to get more from page 2...")
            page2_links = self.get_article_links_from_page(category, 2, limit - len(article_links))
            article_links.extend(page2_links)
        
        print(f"Found {len(article_links)} article links")
        articles = []
        
        for i, url in enumerate(article_links, 1):
            print(f"Scraping article {i}/{len(article_links)}: {url}")
            article_data = self.scrape_article(url)
            if article_data:
                articles.append(article_data)
        
        return articles
    
    def get_article_links_from_page(self, category: str, page: int, limit: int = 10) -> List[str]:
        """Get article links from a specific page number"""
        try:
            if category and category in self.categories:
                url = f"{self.base_url}/{category}-p{page}"
            else:
                return []
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            article_links = []
            
            # Find article links on paginated page
            articles = soup.find_all('article', class_='item-news')
            for article in articles[:limit]:
                link_tag = article.find('a', href=True)
                if link_tag and link_tag['href']:
                    full_url = urljoin(self.base_url, link_tag['href'])
                    if self.is_valid_article_url(full_url):
                        article_links.append(full_url)
            
            return article_links
            
        except Exception as e:
            print(f"Error getting article links from page {page}: {e}")
            return []