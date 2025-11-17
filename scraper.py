"""
Web Scraper for game8.co Honkai Star Rail
Gathers text data and follows links within the website
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import logging
from typing import Set, Dict, List
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Game8Scraper:
    """
    Web scraper for game8.co Honkai Star Rail content.
    Collects text data and follows internal links.
    """
    
    def __init__(self, start_url: str, max_pages: int = 50, delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            start_url: The starting URL to scrape
            max_pages: Maximum number of pages to scrape
            delay: Delay between requests in seconds (be respectful)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: deque = deque([start_url])
        self.scraped_data: List[Dict] = []
        self.base_domain = urlparse(start_url).netloc
        
        # User agent to identify the scraper
        self.headers = {
            'User-Agent': 'Game8Scraper/1.0 (Educational purpose; +https://github.com/darkness-002/gathering)'
        }
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL should be scraped.
        Only scrape URLs from the same domain and related to Honkai Star Rail.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL should be scraped, False otherwise
        """
        parsed = urlparse(url)
        
        # Must be from same domain
        if parsed.netloc != self.base_domain:
            return False
        
        # Must contain Honkai-Star-Rail in path
        if 'Honkai-Star-Rail' not in url:
            return False
        
        # Skip non-content URLs
        skip_patterns = ['#', 'javascript:', 'mailto:', '.pdf', '.jpg', '.png', '.gif']
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract meaningful text from the page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Extracted text content
        """
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        Extract all valid links from the page.
        
        Args:
            soup: BeautifulSoup object of the page
            current_url: Current page URL for resolving relative links
            
        Returns:
            List of valid URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(current_url, link['href'])
            # Remove fragments
            url = url.split('#')[0]
            if self.is_valid_url(url) and url not in self.visited_urls:
                links.append(url)
        
        return links
    
    def scrape_page(self, url: str) -> Dict:
        """
        Scrape a single page.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped data
        """
        try:
            logger.info(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "No Title"
            
            # Extract main content text
            content = self.extract_text(soup)
            
            # Extract links
            links = self.extract_links(soup, url)
            
            # Add new links to visit queue
            for link in links:
                if link not in self.visited_urls and link not in self.to_visit:
                    self.to_visit.append(link)
            
            page_data = {
                'url': url,
                'title': title_text,
                'content': content[:5000],  # Limit content length
                'content_length': len(content),
                'links_found': len(links),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return page_data
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def scrape(self) -> List[Dict]:
        """
        Start the scraping process.
        
        Returns:
            List of scraped page data
        """
        logger.info(f"Starting scrape from {self.start_url}")
        logger.info(f"Max pages: {self.max_pages}, Delay: {self.delay}s")
        
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.popleft()
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            page_data = self.scrape_page(url)
            self.scraped_data.append(page_data)
            
            # Be respectful - add delay between requests
            time.sleep(self.delay)
        
        logger.info(f"Scraping complete. Visited {len(self.visited_urls)} pages.")
        return self.scraped_data
    
    def save_to_json(self, filename: str = 'scraped_data.json'):
        """
        Save scraped data to JSON file.
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'start_url': self.start_url,
                    'pages_scraped': len(self.visited_urls),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                },
                'pages': self.scraped_data
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filename}")
