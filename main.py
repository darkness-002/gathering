#!/usr/bin/env python3
"""
Main entry point for the Game8 Honkai Star Rail scraper
"""

import argparse
from scraper import Game8Scraper


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Honkai Star Rail data from game8.co'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='https://game8.co/games/Honkai-Star-Rail',
        help='Starting URL to scrape (default: https://game8.co/games/Honkai-Star-Rail)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum number of pages to scrape (default: 50)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='scraped_data.json',
        help='Output JSON file (default: scraped_data.json)'
    )
    
    args = parser.parse_args()
    
    # Create and run scraper
    scraper = Game8Scraper(
        start_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    # Scrape the website
    scraper.scrape()
    
    # Save results
    scraper.save_to_json(args.output)
    
    print(f"\nScraping complete!")
    print(f"Pages scraped: {len(scraper.visited_urls)}")
    print(f"Output saved to: {args.output}")


if __name__ == '__main__':
    main()
