# Gathering Documentation

This document covers architecture, components, workflows, data formats, and extension points for Gathering.

## 1. Architecture Overview

Gathering uses a provider-based architecture:

- Universal crawler handles queueing, fetch, concurrency, delays, robots checks, and persistence.
- Providers implement extraction and link discovery for specific site patterns.
- Factory routing selects the right provider per URL.

Core flow:

1. Start from seed URL.
2. Route URL to a provider (`ScraperFactory`).
3. Fetch HTML (`requests` or `playwright`).
4. Extract content and links using provider.
5. Validate output with Pydantic schema.
6. Persist page to SQLite.
7. Repeat until max page limit is reached.

## 2. Components

### 2.1 `BaseScraper`

Abstract interface for providers:

- `extract_content(html: str, url: str) -> dict`
- `get_links(html: str, current_url: str) -> list[str]`
- `is_valid_url(url: str, root_domain: Optional[str]) -> bool`

Utilities included in base class:

- `clean_text(...)`
- `html_to_markdown(...)`
- `density_extract(...)` (fallback heuristic)

### 2.2 Providers

- `Game8Provider`: Game8-specific filtering and selectors.
- `WikiProvider`: Wiki/Fandom extraction behavior.
- `NewsProvider`: Generic news/article patterns.
- `GenericAIProvider`: Unknown-site fallback using density heuristics.

Note: `GenericAIProvider` currently uses heuristic extraction, not a live LLM call.

### 2.3 Factory Router

`ScraperFactory` returns a matching provider based on URL. If no known provider matches, it returns `GenericAIProvider`.

### 2.4 Universal Crawler

`UniversalCrawler` supports:

- URL queue + visited set
- async batch scraping with configurable concurrency
- delay between batches
- robots.txt checks per domain
- `requests` mode (default)
- optional `playwright` mode for JS-heavy pages
- persistence to SQLite via `SQLiteStore`

### 2.5 Data Schema

`PageSchema` normalizes each page record:

- `url`
- `title`
- `content`
- `content_markdown`
- `content_length`
- `links_found`
- `provider`
- `extraction_method`
- `timestamp`
- `error` (optional)

### 2.6 Persistence

`SQLiteStore` creates a `pages` table:

- `url` (primary key)
- `provider`
- `crawled_at`
- `status` (`ok` or `error`)
- `payload` (full JSON record)

Writes use upsert behavior on `url`.

## 3. CLI Usage

### Basic

```bash
python main.py --url "https://game8.co/games/Honkai-Star-Rail"
```

### Advanced

```bash
python main.py \
  --url "https://honkai.fandom.com/wiki/Honkai:_Star_Rail_Wiki" \
  --max-pages 200 \
  --delay 0.5 \
  --concurrency 5 \
  --mode requests \
  --db-path crawl_data.db \
  --output scraped_data.json
```

### Arguments

- `--url`: crawl seed
- `--max-pages`: page cap
- `--delay`: inter-batch sleep in seconds
- `--concurrency`: concurrent pages per batch
- `--mode`: `requests` or `playwright`
- `--db-path`: sqlite file path
- `--output`: json export file path

## 4. Streamlit Dashboard

Run:

```bash
streamlit run dashboard.py
```

Dashboard capabilities:

- Source selection: SQLite or JSON
- Filters: provider, host, status, content length, title contains
- Metrics: pages, ok/errors, avg content length
- Charts: provider/host/status distributions
- Table and detail viewer for each page
- Download filtered output

## 5. Python API Usage

```python
from scraper import UniversalCrawler

crawler = UniversalCrawler(
    start_url="https://game8.co/games/Honkai-Star-Rail",
    max_pages=50,
    delay=1.0,
    concurrency=3,
    fetch_mode="requests",
    db_path="crawl_data.db",
)

pages = crawler.scrape()
crawler.save_to_json("scraped_data.json")
```

Backward-compatible API:

```python
from scraper import Game8Scraper

scraper = Game8Scraper(start_url="https://game8.co/games/Honkai-Star-Rail")
pages = scraper.scrape()
scraper.save_to_json("scraped_data.json")
```

## 6. Extending with New Providers

To add a provider:

1. Subclass `BaseScraper`.
2. Implement `matches`, `extract_content`, `get_links`.
3. Add provider instance to `ScraperFactory.providers`.
4. Add tests with mocked HTML.

Skeleton:

```python
class MySiteProvider(BaseScraper):
    name = "mysite"

    def matches(self, url: str) -> bool:
        return "mysite.com" in url

    def extract_content(self, html: str, url: str) -> dict:
        # parse + return schema fields
        ...

    def get_links(self, html: str, current_url: str) -> list[str]:
        # collect next links
        ...
```

## 7. Testing

Run:

```bash
python test_scraper.py
```

Current tests cover:

- provider routing behavior
- universal crawl flow
- sqlite + json export behavior
- backward compatibility path (`Game8Scraper`)

## 8. Troubleshooting

### Streamlit not found

Install dependencies:

```bash
pip install -r requirements.txt
```

If using an externally managed Python on macOS, install in user space:

```bash
python3 -m pip install --user --break-system-packages -r requirements.txt
```

### Playwright mode errors

Install browser runtime:

```bash
pip install playwright
playwright install
```

### Empty or noisy extraction

- tune provider selectors for target site
- reduce crawl scope with stricter URL validation
- increase filtering in provider-specific logic

## 9. Roadmap

- Add true LLM-backed extraction for `GenericAIProvider`
- Add retry/backoff policies
- Add resumable queue snapshots
- Add richer dashboard analytics and search
