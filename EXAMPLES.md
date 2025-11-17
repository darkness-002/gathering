# Example Usage

This file contains examples of how to use the Game8 Honkai Star Rail scraper.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run with Default Settings
```bash
python main.py
```

This will scrape up to 50 pages starting from https://game8.co/games/Honkai-Star-Rail

## Advanced Examples

### Scrape More Pages
```bash
python main.py --max-pages 100
```

### Custom Output File
```bash
python main.py --output honkai_data.json
```

### Slower Rate (More Respectful)
```bash
python main.py --delay 2.0
```

### Combined Options
```bash
python main.py --max-pages 200 --delay 1.5 --output full_scrape.json
```

## Using as a Library

```python
from scraper import Game8Scraper

# Create scraper
scraper = Game8Scraper(
    start_url='https://game8.co/games/Honkai-Star-Rail',
    max_pages=50,
    delay=1.0
)

# Scrape data
data = scraper.scrape()

# Access scraped data
for page in data:
    print(f"Title: {page['title']}")
    print(f"Content length: {page['content_length']}")
    print(f"Links found: {page['links_found']}")
    print("---")

# Save to file
scraper.save_to_json('output.json')
```

## Processing the Output

The scraper creates a JSON file with this structure:

```python
import json

# Load scraped data
with open('scraped_data.json', 'r') as f:
    data = json.load(f)

# Get metadata
print(f"Scraped {data['metadata']['pages_scraped']} pages")
print(f"Started from: {data['metadata']['start_url']}")

# Process pages
for page in data['pages']:
    if 'error' not in page:
        print(f"\nPage: {page['title']}")
        print(f"URL: {page['url']}")
        print(f"Content preview: {page['content'][:200]}...")
```

## Testing

Run the test suite to verify functionality:

```bash
python test_scraper.py
```

This runs the scraper with mock data to verify all components work correctly.

## Tips

1. **Start Small**: Test with `--max-pages 10` first to ensure everything works
2. **Be Respectful**: Use appropriate delays (1-2 seconds minimum)
3. **Monitor Progress**: Watch the console output to see scraping progress
4. **Check Output**: Verify the JSON file after scraping completes
5. **Filter Data**: Process the JSON to extract specific information you need

## Common Use Cases

### Scrape Character Information
The scraper will automatically find and follow links to character pages.

### Collect Build Guides
Guide pages are discovered and scraped automatically.

### Gather Team Compositions
Team composition information is extracted from relevant pages.

### Extract Item Database
Item and equipment information is collected from database pages.
