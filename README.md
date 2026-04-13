# Gathering

Universal provider-based web scraping engine with an interactive Streamlit dashboard.

Gathering separates crawling from extraction so you can reuse one core engine across many websites.

## Highlights

- Provider pattern architecture (`BaseScraper` + `ScraperFactory`)
- Concurrent crawling with configurable batching
- Requests mode and optional Playwright mode
- HTML to Markdown normalization
- Schema-validated page output via Pydantic
- SQLite persistence for interrupted crawl recovery
- Streamlit dashboard for analysis and filtering
- Backward compatibility wrapper for existing `Game8Scraper` usage

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run a crawl:

```bash
python main.py --url "https://game8.co/games/Honkai-Star-Rail" --max-pages 25 --concurrency 3 --output scraped_data.json
```

3. Open the dashboard:

```bash
streamlit run dashboard.py
```

## CLI Usage

```bash
python main.py \
  --url "https://honkai.fandom.com/wiki/Honkai:_Star_Rail_Wiki" \
  --max-pages 100 \
  --delay 0.5 \
  --concurrency 5 \
  --mode requests \
  --db-path crawl_data.db \
  --output scraped_data.json
```

### CLI Flags

- `--url`: Start URL
- `--max-pages`: Maximum pages to crawl
- `--delay`: Delay between request batches (seconds)
- `--concurrency`: Pages processed concurrently
- `--mode`: `requests` or `playwright`
- `--db-path`: SQLite output path
- `--output`: JSON output path

## Dashboard

The dashboard (`dashboard.py`) supports:

- Loading from SQLite (`crawl_data.db`) or JSON (`scraped_data.json`)
- Filtering by provider, host, status, content length, and title search
- Summary metrics and distribution charts
- Per-page inspection (metadata, markdown, extracted text)
- Export of filtered records

## Project Files

- `scraper.py`: Core engine, providers, routing, persistence, schema
- `main.py`: CLI entrypoint
- `dashboard.py`: Streamlit data explorer
- `test_scraper.py`: Mocked validation tests
- `EXAMPLES.md`: Practical run examples
- `DOCUMENTATION.md`: Full technical documentation

## Development

Run tests:

```bash
python test_scraper.py
```

Playwright mode setup (optional):

```bash
pip install playwright
playwright install
```

## Documentation

See full docs in `DOCUMENTATION.md`.

## Ethical Use

Use responsibly and comply with target website terms and robots policies.
