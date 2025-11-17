#!/usr/bin/env python3
"""
Test script for the scraper with mock data
Demonstrates scraper functionality without requiring internet access
"""

from unittest.mock import Mock, patch
from scraper import Game8Scraper
import json


def create_mock_html(title, content, links):
    """Create a mock HTML page"""
    links_html = ''.join([f'<a href="{link}">Link</a>' for link in links])
    return f"""
    <html>
        <head><title>{title}</title></head>
        <body>
            <nav>Navigation</nav>
            <div class="content">
                <h1>{title}</h1>
                <p>{content}</p>
                {links_html}
            </div>
            <script>console.log('test');</script>
        </body>
    </html>
    """


def test_scraper():
    """Test the scraper with mock responses"""
    print("Testing Game8 Scraper with mock data...\n")
    
    # Create mock responses
    mock_pages = {
        'https://game8.co/games/Honkai-Star-Rail': {
            'title': 'Honkai Star Rail Wiki - Game8',
            'content': 'Welcome to the Honkai Star Rail wiki guide. Find character builds, team comps, and more.',
            'links': [
                'https://game8.co/games/Honkai-Star-Rail/characters',
                'https://game8.co/games/Honkai-Star-Rail/guides'
            ]
        },
        'https://game8.co/games/Honkai-Star-Rail/characters': {
            'title': 'Character List - Honkai Star Rail',
            'content': 'Complete list of all playable characters with their elements and paths.',
            'links': [
                'https://game8.co/games/Honkai-Star-Rail/characters/stelle'
            ]
        },
        'https://game8.co/games/Honkai-Star-Rail/guides': {
            'title': 'Beginner Guide - Honkai Star Rail',
            'content': 'Essential tips for new players starting their journey.',
            'links': []
        }
    }
    
    def mock_get(url, headers=None, timeout=None):
        """Mock requests.get"""
        response = Mock()
        response.status_code = 200
        if url in mock_pages:
            page = mock_pages[url]
            response.content = create_mock_html(
                page['title'],
                page['content'],
                page['links']
            ).encode('utf-8')
        else:
            response.content = b'<html><body>404 Not Found</body></html>'
        return response
    
    # Test with mocked requests
    with patch('requests.get', side_effect=mock_get):
        scraper = Game8Scraper(
            start_url='https://game8.co/games/Honkai-Star-Rail',
            max_pages=5,
            delay=0.1  # Fast for testing
        )
        
        print("1. Testing scraper initialization...")
        assert scraper.start_url == 'https://game8.co/games/Honkai-Star-Rail'
        assert scraper.max_pages == 5
        print("   ✓ Initialization successful\n")
        
        print("2. Testing URL validation...")
        valid_url = 'https://game8.co/games/Honkai-Star-Rail/characters'
        invalid_url = 'https://example.com/test'
        assert scraper.is_valid_url(valid_url) == True
        assert scraper.is_valid_url(invalid_url) == False
        print(f"   ✓ {valid_url} - Valid")
        print(f"   ✓ {invalid_url} - Invalid\n")
        
        print("3. Testing page scraping...")
        data = scraper.scrape()
        print(f"   ✓ Scraped {len(data)} pages\n")
        
        print("4. Verifying scraped data...")
        for i, page in enumerate(data[:3], 1):
            print(f"   Page {i}:")
            print(f"     URL: {page['url']}")
            print(f"     Title: {page['title']}")
            print(f"     Content length: {page['content_length']} chars")
            print(f"     Links found: {page['links_found']}")
        print()
        
        print("5. Testing JSON export...")
        scraper.save_to_json('test_mock_output.json')
        
        # Verify JSON file
        with open('test_mock_output.json', 'r') as f:
            saved_data = json.load(f)
        
        assert 'metadata' in saved_data
        assert 'pages' in saved_data
        assert len(saved_data['pages']) > 0
        print(f"   ✓ Exported {len(saved_data['pages'])} pages to test_mock_output.json\n")
        
        print("6. Analyzing collected data...")
        print(f"   Total pages visited: {len(scraper.visited_urls)}")
        print(f"   Total content collected: {sum(p.get('content_length', 0) for p in data)} chars")
        print(f"   Average links per page: {sum(p.get('links_found', 0) for p in data) / len(data):.1f}")
        print()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nThe scraper is ready to use with real websites.")
    print("Run: python main.py --help for usage instructions")


if __name__ == '__main__':
    test_scraper()
