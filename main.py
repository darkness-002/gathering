

import argparse
from scraper import UniversalCrawler


def main():
    parser = argparse.ArgumentParser(description="Universal web scraping engine")
    parser.add_argument(
        '--url',
        type=str,
        default="https://game8.co/games/Honkai-Star-Rail",
        help="Starting URL to scrape",
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help="Maximum number of pages to scrape (default: 50)",
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help="Delay between request batches in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="How many pages to process concurrently (default: 3)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["requests", "playwright"],
        default="requests",
        help="Fetch mode: lightweight requests or JS-capable playwright",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="crawl_data.db",
        help="SQLite database path for persistence (default: crawl_data.db)",
    )
    parser.add_argument(
        '--output',
        type=str,
        default="scraped_data.json",
        help="Output JSON file (default: scraped_data.json)",
    )
    
    args = parser.parse_args()
    
    crawler = UniversalCrawler(
        start_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay,
        concurrency=args.concurrency,
        fetch_mode=args.mode,
        db_path=args.db_path,
    )

    crawler.scrape()
    crawler.save_to_json(args.output)

    print("\nScraping complete!")
    print(f"Pages scraped: {len(crawler.visited_urls)}")
    print(f"Output saved to: {args.output}")


if __name__ == "__main__":
    main()
