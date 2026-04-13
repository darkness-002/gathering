# Example Usage

This file contains practical examples for the universal provider-based scraper.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with defaults:

```bash
python main.py --url "https://game8.co/games/Honkai-Star-Rail"
```

## CLI Examples

Scrape more pages with moderate concurrency:

```bash
python main.py --url "https://game8.co/games/Honkai-Star-Rail" --max-pages 200 --concurrency 5 --delay 0.5
```

Use persistence and custom output:

```bash
python main.py --url "https://honkai.fandom.com/wiki/Honkai:_Star_Rail_Wiki" --db-path fandom.db --output fandom.json
```

Enable JS rendering for dynamic pages:

```bash
python main.py --url "https://example.com/news" --mode playwright --max-pages 30
```

## Using as a Library

```python
from scraper import UniversalCrawler

crawler = UniversalCrawler(
    start_url="https://game8.co/games/Honkai-Star-Rail",
    max_pages=25,
    delay=1.0,
    concurrency=3,
    fetch_mode="requests",
    db_path="crawl_data.db",
)

pages = crawler.scrape()
crawler.save_to_json("output.json")

for page in pages:
    print(page["provider"], page["title"], page["links_found"])
```

Backward-compatible wrapper:

```python
from scraper import Game8Scraper

scraper = Game8Scraper(
    start_url="https://game8.co/games/Honkai-Star-Rail",
    max_pages=10,
    delay=0.5,
)

data = scraper.scrape()
scraper.save_to_json("game8.json")
```

## Running Tests

```bash
python test_scraper.py
```

## Run Dashboard

```bash
streamlit run dashboard.py
```
