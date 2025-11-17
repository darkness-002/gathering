# Gathering - Game8 Honkai Star Rail Web Scraper

A Python web scraper designed to gather text data from the Honkai Star Rail section of game8.co. This tool crawls through pages, collects text content, and follows internal links to build a comprehensive dataset for AI training purposes.

## What Does This Tool Do?

This scraper automatically:
1. **Visits web pages** on game8.co related to Honkai Star Rail
2. **Extracts text content** including character guides, game mechanics, build recommendations, team compositions, and strategy information
3. **Discovers new pages** by following links within the same section
4. **Stores all collected data** in a structured JSON format for easy processing and analysis
5. **Respects the website** by adding delays between requests and identifying itself properly

The scraped data can be used to train AI models to help players make informed decisions about characters, team compositions, and game strategies.

## Features

- **Intelligent Crawling**: Automatically discovers and follows links within the Honkai Star Rail section
- **Text Extraction**: Extracts meaningful text content from web pages
- **Respectful Scraping**: Includes delays between requests and proper user-agent identification
- **Data Export**: Saves collected data in JSON format for easy processing
- **Configurable**: Customizable parameters for maximum pages, delays, and starting URLs

## How It Works

The scraper operates in several steps:

### 1. Initialization
- Starts at the specified URL (default: https://game8.co/games/Honkai-Star-Rail)
- Creates a queue to manage URLs to visit
- Sets up tracking for already-visited pages to avoid duplicates

### 2. Page Crawling (BFS Algorithm)
The scraper uses **Breadth-First Search (BFS)** traversal:
- Takes the next URL from the queue
- Sends an HTTP request to fetch the page
- Respects rate limits by waiting (default: 1 second) between requests

### 3. Content Extraction
For each page visited:
- **HTML Parsing**: Uses BeautifulSoup to parse the page structure
- **Content Cleaning**: Removes navigation, scripts, styles, headers, and footers
- **Text Extraction**: Extracts meaningful text from the main content
- **Link Discovery**: Finds all links (`<a>` tags) on the page

### 4. Link Filtering
The scraper validates each discovered link:
- ✅ Must be from game8.co domain
- ✅ Must contain "Honkai-Star-Rail" in the path
- ❌ Skips external sites
- ❌ Skips non-content URLs (PDFs, images, fragments, JavaScript)
- ❌ Skips already-visited pages

### 5. Data Storage
Valid links are added to the queue, and the process repeats until:
- The maximum page limit is reached (`--max-pages`), OR
- No more links are in the queue

All scraped data is stored in memory during execution and written to a JSON file at the end.

### 6. Error Handling
- Network errors are logged and the scraper continues with the next URL
- Failed pages are recorded with error information
- The scraper is resilient to individual page failures

### Architecture Diagram

```
[Start URL] → [URL Queue]
                  ↓
          [Fetch Page (with delay)]
                  ↓
          [Parse HTML with BeautifulSoup]
                  ↓
          [Extract Text & Links]
                  ↓
    [Filter Links] → [Add Valid Links to Queue]
                  ↓
          [Store Page Data]
                  ↓
          [Repeat until done]
                  ↓
          [Save JSON File]
```

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

### Where is the Data Stored?

By default, scraped data is saved to a file called **`scraped_data.json`** in the current directory. You can change this location using the `--output` parameter:

```bash
python main.py --output /path/to/your/data.json
```

### How is the Data Structured?

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

### Data Fields Explained

**Metadata Section:**
- `start_url`: The initial URL where scraping began
- `pages_scraped`: Total number of pages successfully scraped
- `timestamp`: When the scraping session completed

**Pages Array - Each Page Contains:**
- `url`: The full URL of the scraped page
- `title`: The page title (from HTML `<title>` tag)
- `content`: Extracted text content (cleaned, up to 5000 characters shown)
- `content_length`: Total character count of the extracted content
- `links_found`: Number of valid internal links discovered on this page
- `timestamp`: When this specific page was scraped

### Accessing Your Data

After scraping, you can process the JSON file:

```python
import json

# Load the scraped data
with open('scraped_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access metadata
print(f"Scraped {data['metadata']['pages_scraped']} pages")

# Process each page
for page in data['pages']:
    print(f"Title: {page['title']}")
    print(f"Content: {page['content'][:200]}...")  # First 200 chars
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

To use this scraper, you need:

### System Requirements
- **Python 3.7 or higher** - The programming language used
- **Internet connection** - To access game8.co
- **At least 50MB free disk space** - For storing scraped data

### Python Dependencies
Install these using `pip install -r requirements.txt`:
- **requests** (>=2.31.0) - For making HTTP requests to web pages
- **beautifulsoup4** (>=4.12.0) - For parsing HTML and extracting content
- **lxml** (>=4.9.0) - Fast HTML/XML parser used by BeautifulSoup

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

Users are responsible for ensuring their use of this tool complies with all applicable laws and the website's terms of service. This tool should be used responsibly and ethically.