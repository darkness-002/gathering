#!/usr/bin/env python3
"""Tests for the universal provider-based scraping engine."""

import json
import os
from unittest.mock import Mock, patch

from scraper import Game8Scraper, ScraperFactory, UniversalCrawler


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
    """Test provider routing, crawling, and backward compatibility with mock responses."""
    print("Testing Universal Scraper with mock data...\n")

    mock_pages = {
        "https://game8.co/games/Honkai-Star-Rail": {
            "title": "Honkai Star Rail Wiki - Game8",
            "content": "Welcome to the Honkai Star Rail wiki guide. Find character builds, team comps, and more.",
            "links": [
                "https://game8.co/games/Honkai-Star-Rail/characters",
                "https://game8.co/games/Honkai-Star-Rail/guides",
            ],
        },
        "https://game8.co/games/Honkai-Star-Rail/characters": {
            "title": "Character List - Honkai Star Rail",
            "content": "Complete list of all playable characters with their elements and paths.",
            "links": ["https://game8.co/games/Honkai-Star-Rail/characters/stelle"],
        },
        "https://game8.co/games/Honkai-Star-Rail/guides": {
            "title": "Beginner Guide - Honkai Star Rail",
            "content": "Essential tips for new players starting their journey.",
            "links": [],
        },
    }

    def mock_get(url, headers=None, timeout=None):
        """Mock requests.get."""
        response = Mock()
        response.status_code = 200
        if url in mock_pages:
            page = mock_pages[url]
            html = create_mock_html(page["title"], page["content"], page["links"])
            response.text = html
            response.content = html.encode("utf-8")
        else:
            response.text = "<html><body>404 Not Found</body></html>"
            response.content = response.text.encode("utf-8")

        response.raise_for_status = Mock()
        return response

    with patch("requests.get", side_effect=mock_get):
        print("1. Testing dynamic provider routing...")
        factory = ScraperFactory()
        assert factory.get_scraper("https://game8.co/games/Honkai-Star-Rail").name == "game8"
        assert factory.get_scraper("https://honkai.fandom.com/wiki/Characters").name == "wiki"
        assert factory.get_scraper("https://unknown.example.com/page").name == "generic_ai"
        print("   ✓ Factory routes to game8/wiki/generic providers\n")

        print("2. Testing universal crawler with persistence...")
        db_path = "test_crawl.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        crawler = UniversalCrawler(
            start_url="https://game8.co/games/Honkai-Star-Rail",
            max_pages=3,
            delay=0,
            concurrency=2,
            db_path=db_path,
        )
        data = crawler.scrape()
        assert len(data) == 3
        assert all("provider" in page for page in data)
        assert all("content_markdown" in page for page in data)
        print("   ✓ Universal crawler scraped and validated 3 pages\n")

        print("3. Testing backward-compatible Game8Scraper wrapper...")
        scraper = Game8Scraper(
            start_url="https://game8.co/games/Honkai-Star-Rail",
            max_pages=5,
            delay=0,
        )
        assert scraper.start_url == "https://game8.co/games/Honkai-Star-Rail"
        assert scraper.max_pages == 5
        valid_url = "https://game8.co/games/Honkai-Star-Rail/characters"
        invalid_url = "https://example.com/test"
        assert scraper.is_valid_url(valid_url) is True
        assert scraper.is_valid_url(invalid_url) is False
        print(f"   ✓ {valid_url} - Valid")
        print(f"   ✓ {invalid_url} - Invalid\n")

        print("4. Testing compatibility scrape path...")
        game8_data = scraper.scrape()
        print(f"   ✓ Scraped {len(game8_data)} pages through wrapper\n")

        print("5. Verifying scraped data...")
        for i, page in enumerate(data[:3], 1):
            print(f"   Page {i}:")
            print(f"     URL: {page['url']}")
            print(f"     Title: {page['title']}")
            print(f"     Content length: {page['content_length']} chars")
            print(f"     Links found: {page['links_found']}")
            print(f"     Provider: {page['provider']}")
        print()

        print("6. Testing JSON export...")
        crawler.save_to_json("test_mock_output.json")
        with open("test_mock_output.json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        assert "metadata" in saved_data
        assert "pages" in saved_data
        assert len(saved_data["pages"]) > 0
        print(f"   ✓ Exported {len(saved_data['pages'])} pages to test_mock_output.json\n")

        print("7. Analyzing collected data...")
        print(f"   Total pages visited: {len(scraper.visited_urls)}")
        print(f"   Total content collected: {sum(p.get('content_length', 0) for p in data)} chars")
        print(f"   Average links per page: {sum(p.get('links_found', 0) for p in data) / len(data):.1f}")
        print()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nThe universal scraper is ready to use with real websites.")
    print("Run: python main.py --help for usage instructions")

    for path in ["test_mock_output.json", "test_crawl.db", "crawl_data.db"]:
        if os.path.exists(path):
            os.remove(path)


if __name__ == '__main__':
    test_scraper()
