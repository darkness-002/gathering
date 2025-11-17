# Gathering - Game8 Honkai Star Rail Web Scraper

A Python web scraper designed to gather text data from the Honkai Star Rail section of game8.co. This tool crawls through pages, collects text content, and follows internal links to build a comprehensive dataset for AI training purposes.

## Features

- **Intelligent Crawling**: Automatically discovers and follows links within the Honkai Star Rail section
- **Text Extraction**: Extracts meaningful text content from web pages
- **Respectful Scraping**: Includes delays between requests and proper user-agent identification
- **Data Export**: Saves collected data in JSON format for easy processing
- **Configurable**: Customizable parameters for maximum pages, delays, and starting URLs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/darkness-002/gathering.git
cd gathering
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python main.py
```

This will:
- Start from https://game8.co/games/Honkai-Star-Rail
- Scrape up to 50 pages
- Use a 1-second delay between requests
- Save output to `scraped_data.json`

### Advanced Usage

Customize the scraping parameters:

```bash
python main.py --url "https://game8.co/games/Honkai-Star-Rail" \
               --max-pages 100 \
               --delay 2.0 \
               --output my_data.json
```

#### Parameters:

- `--url`: Starting URL to scrape (default: https://game8.co/games/Honkai-Star-Rail)
- `--max-pages`: Maximum number of pages to scrape (default: 50)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--output`: Output JSON file path (default: scraped_data.json)

### Using as a Module

You can also use the scraper in your own Python code:

```python
from scraper import Game8Scraper

# Create scraper instance
scraper = Game8Scraper(
    start_url='https://game8.co/games/Honkai-Star-Rail',
    max_pages=50,
    delay=1.0
)

# Run the scraper
data = scraper.scrape()

# Save to file
scraper.save_to_json('output.json')
```

## Output Format

The scraper generates a JSON file with the following structure:

```json
{
  "metadata": {
    "start_url": "https://game8.co/games/Honkai-Star-Rail",
    "pages_scraped": 50,
    "timestamp": "2024-01-01 12:00:00"
  },
  "pages": [
    {
      "url": "https://game8.co/games/Honkai-Star-Rail/...",
      "title": "Page Title",
      "content": "Extracted text content...",
      "content_length": 12345,
      "links_found": 25,
      "timestamp": "2024-01-01 12:00:01"
    }
  ]
}
```

## Ethical Scraping

This tool is designed for educational and research purposes. It follows best practices for web scraping:

- **Respectful delays**: Default 1-second delay between requests to avoid overloading servers
- **User-agent identification**: Clearly identifies itself as a scraper
- **Scope limitation**: Only scrapes the Honkai Star Rail section of game8.co
- **Terms of Service**: The website's ToS has been reviewed and allows scraping

## Use Case

This scraper is intended to gather data for training AI tools that can help players with:
- Character selection and building
- Team composition recommendations
- Game progression guidance
- Strategy optimization

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

Users are responsible for ensuring their use of this tool complies with all applicable laws and the website's terms of service. This tool should be used responsibly and ethically.