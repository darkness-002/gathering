"""Universal provider-based web scraping engine."""

import asyncio
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Dict, List, Optional, Set
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError

try:
    from markdownify import markdownify as to_markdown
except ImportError:  # pragma: no cover - optional dependency fallback
    to_markdown = None


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PageSchema(BaseModel):
    """Strong schema for all page records produced by the crawler."""

    url: str
    title: str = "No Title"
    content: str = ""
    content_markdown: str = ""
    content_length: int = 0
    links_found: int = 0
    provider: str = "unknown"
    extraction_method: str = "selector"
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    error: Optional[str] = None


class BaseScraper(ABC):
    """Provider interface every site-specific extractor must implement."""

    name = "base"

    def matches(self, url: str) -> bool:
        return False

    @abstractmethod
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML."""

    @abstractmethod
    def get_links(self, html: str, current_url: str) -> List[str]:
        """Extract next crawl links from HTML."""

    def is_valid_url(self, url: str, root_domain: Optional[str] = None) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if root_domain and parsed.netloc != root_domain:
            return False
        blocked_tokens = [
            "javascript:",
            "mailto:",
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".zip",
        ]
        lowered = url.lower()
        return not any(token in lowered for token in blocked_tokens)

    def clean_text(self, soup: BeautifulSoup) -> str:
        for node in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            node.decompose()
        return " ".join(soup.get_text(separator=" ", strip=True).split())

    def html_to_markdown(self, html: str) -> str:
        if to_markdown is not None:
            return to_markdown(html, strip=["script", "style", "nav", "footer", "header", "aside"])
        soup = BeautifulSoup(html, "lxml")
        return self.clean_text(soup)

    def density_extract(self, soup: BeautifulSoup) -> str:
        """Fallback extraction based on text density for robust unknown-site scraping."""
        candidates = soup.select("article, main, section, div")
        best_text = ""
        best_score = -1
        for node in candidates:
            paragraphs = node.find_all(["p", "li"])
            if not paragraphs:
                continue
            text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
            score = len(text)
            if score > best_score:
                best_score = score
                best_text = " ".join(text.split())
        return best_text or self.clean_text(soup)


class Game8Provider(BaseScraper):
    name = "game8"

    def matches(self, url: str) -> bool:
        return "game8.co" in urlparse(url).netloc

    def is_valid_url(self, url: str, root_domain: Optional[str] = None) -> bool:
        if not super().is_valid_url(url, root_domain=root_domain):
            return False
        return "Honkai-Star-Rail" in url

    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else "No Title"
        main = soup.select_one("article, main, .p-entry__content")
        content = self.clean_text(main if main is not None else soup)
        return {
            "title": title,
            "content": content[:10000],
            "content_markdown": self.html_to_markdown(str(main if main is not None else soup)),
            "content_length": len(content),
            "extraction_method": "game8_selector",
        }

    def get_links(self, html: str, current_url: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        root_domain = urlparse(current_url).netloc
        links: List[str] = []
        for anchor in soup.find_all("a", href=True):
            url = urljoin(current_url, anchor["href"]).split("#")[0]
            if self.is_valid_url(url, root_domain=root_domain):
                links.append(url)
        return links


class WikiProvider(BaseScraper):
    name = "wiki"

    def matches(self, url: str) -> bool:
        host = urlparse(url).netloc
        return "wiki" in host or "fandom.com" in host

    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else "No Title"
        main = soup.select_one("#mw-content-text, .mw-parser-output, article, main")
        content = self.clean_text(main if main is not None else soup)
        return {
            "title": title,
            "content": content[:10000],
            "content_markdown": self.html_to_markdown(str(main if main is not None else soup)),
            "content_length": len(content),
            "extraction_method": "wiki_selector",
        }

    def get_links(self, html: str, current_url: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        root_domain = urlparse(current_url).netloc
        links: List[str] = []
        for anchor in soup.find_all("a", href=True):
            url = urljoin(current_url, anchor["href"]).split("#")[0]
            if self.is_valid_url(url, root_domain=root_domain):
                links.append(url)
        return links


class NewsProvider(BaseScraper):
    name = "news"

    def matches(self, url: str) -> bool:
        lowered = url.lower()
        return any(token in lowered for token in ["/news", "blog", "article"])

    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else "No Title"
        main = soup.select_one("article, main, [role='main']")
        content = self.clean_text(main if main is not None else soup)
        return {
            "title": title,
            "content": content[:10000],
            "content_markdown": self.html_to_markdown(str(main if main is not None else soup)),
            "content_length": len(content),
            "extraction_method": "news_selector",
        }

    def get_links(self, html: str, current_url: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        root_domain = urlparse(current_url).netloc
        links: List[str] = []
        for anchor in soup.find_all("a", href=True):
            url = urljoin(current_url, anchor["href"]).split("#")[0]
            if self.is_valid_url(url, root_domain=root_domain):
                links.append(url)
        return links


class GenericAIProvider(BaseScraper):
    """Fallback provider that uses heuristics suitable for unknown websites."""

    name = "generic_ai"

    def matches(self, url: str) -> bool:
        return True

    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else "No Title"
        content = self.density_extract(soup)
        return {
            "title": title,
            "content": content[:10000],
            "content_markdown": self.html_to_markdown(html),
            "content_length": len(content),
            "extraction_method": "density_fallback",
        }

    def get_links(self, html: str, current_url: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        root_domain = urlparse(current_url).netloc
        links: List[str] = []
        for anchor in soup.find_all("a", href=True):
            url = urljoin(current_url, anchor["href"]).split("#")[0]
            if self.is_valid_url(url, root_domain=root_domain):
                links.append(url)
        return links


class ScraperFactory:
    """Domain router that maps URLs to provider implementations."""

    def __init__(self):
        self.providers = [Game8Provider(), WikiProvider(), NewsProvider()]
        self.default_provider = GenericAIProvider()

    def get_scraper(self, url: str) -> BaseScraper:
        for provider in self.providers:
            if provider.matches(url):
                return provider
        return self.default_provider


class SQLiteStore:
    """Simple persistence layer so crawls can survive interruptions."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pages (
                    url TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    crawled_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, page: Dict[str, Any]) -> None:
        status = "error" if page.get("error") else "ok"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO pages (url, provider, crawled_at, status, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    provider=excluded.provider,
                    crawled_at=excluded.crawled_at,
                    status=excluded.status,
                    payload=excluded.payload
                """,
                (
                    page["url"],
                    page.get("provider", "unknown"),
                    page.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
                    status,
                    json.dumps(page, ensure_ascii=False),
                ),
            )
            conn.commit()

    def read_all(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT payload FROM pages ORDER BY crawled_at").fetchall()
        return [json.loads(row[0]) for row in rows]


class UniversalCrawler:
    """Universal crawler that delegates extraction to pluggable providers."""

    def __init__(
        self,
        start_url: str,
        max_pages: int = 50,
        delay: float = 1.0,
        concurrency: int = 3,
        fetch_mode: str = "requests",
        db_path: str = "crawl_data.db",
    ):
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = delay
        self.concurrency = max(1, concurrency)
        self.fetch_mode = fetch_mode

        self.visited_urls: Set[str] = set()
        self.to_visit: deque[str] = deque([start_url])
        self.scraped_data: List[Dict[str, Any]] = []

        self.factory = ScraperFactory()
        self.store = SQLiteStore(db_path)
        self._robots_cache: Dict[str, robotparser.RobotFileParser] = {}

        self.headers = {
            "User-Agent": "UniversalGatheringBot/2.0 (Educational purpose; +https://github.com/darkness-002/gathering)"
        }

    def _can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = self._robots_cache.get(robots_url)
        if parser is None:
            parser = robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                return True
            self._robots_cache[robots_url] = parser
        return parser.can_fetch(self.headers["User-Agent"], url)

    async def _fetch_html(self, url: str) -> str:
        if self.fetch_mode == "playwright":
            try:
                from playwright.async_api import async_playwright
            except ImportError as exc:
                raise RuntimeError(
                    "Playwright mode requested but playwright is not installed. "
                    "Install with: pip install playwright && playwright install"
                ) from exc

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle")
                html = await page.content()
                await browser.close()
                return html

        def _request() -> str:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text

        return await asyncio.to_thread(_request)

    async def _scrape_page(self, url: str) -> Dict[str, Any]:
        provider = self.factory.get_scraper(url)
        try:
            if not self._can_fetch(url):
                raise PermissionError("Blocked by robots.txt")

            logger.info("Scraping [%s]: %s", provider.name, url)
            html = await self._fetch_html(url)
            content_data = provider.extract_content(html, url)
            links = provider.get_links(html, url)

            for link in links:
                if link not in self.visited_urls and link not in self.to_visit:
                    self.to_visit.append(link)

            page = {
                "url": url,
                "provider": provider.name,
                "links_found": len(links),
                **content_data,
            }
            return PageSchema.model_validate(page).model_dump()
        except (requests.RequestException, RuntimeError, PermissionError) as exc:
            logger.error("Error scraping %s: %s", url, exc)
            fallback = {
                "url": url,
                "provider": provider.name,
                "title": "No Title",
                "content": "",
                "content_markdown": "",
                "content_length": 0,
                "links_found": 0,
                "extraction_method": "error",
                "error": str(exc),
            }
            return PageSchema.model_validate(fallback).model_dump()
        except ValidationError as exc:
            logger.error("Schema validation failed for %s: %s", url, exc)
            return {
                "url": url,
                "provider": provider.name,
                "title": "No Title",
                "content": "",
                "content_markdown": "",
                "content_length": 0,
                "links_found": 0,
                "extraction_method": "schema_error",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(exc),
            }

    async def scrape_async(self) -> List[Dict[str, Any]]:
        logger.info("Starting universal crawl from %s", self.start_url)
        logger.info(
            "Max pages: %s | Delay: %ss | Concurrency: %s | Mode: %s",
            self.max_pages,
            self.delay,
            self.concurrency,
            self.fetch_mode,
        )

        while self.to_visit and len(self.visited_urls) < self.max_pages:
            batch: List[str] = []
            while self.to_visit and len(batch) < self.concurrency and len(self.visited_urls) + len(batch) < self.max_pages:
                candidate = self.to_visit.popleft()
                if candidate in self.visited_urls or candidate in batch:
                    continue
                batch.append(candidate)

            if not batch:
                break

            results = await asyncio.gather(*(self._scrape_page(url) for url in batch))
            for page in results:
                self.visited_urls.add(page["url"])
                self.scraped_data.append(page)
                self.store.save(page)

            if self.delay > 0:
                await asyncio.sleep(self.delay)

        logger.info("Crawl complete. Visited %s pages.", len(self.visited_urls))
        return self.scraped_data

    def scrape(self) -> List[Dict[str, Any]]:
        return asyncio.run(self.scrape_async())

    def save_to_json(self, filename: str = "scraped_data.json") -> None:
        pages = self.store.read_all() if self.store else self.scraped_data
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "metadata": {
                        "start_url": self.start_url,
                        "pages_scraped": len(self.visited_urls),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "fetch_mode": self.fetch_mode,
                        "concurrency": self.concurrency,
                    },
                    "pages": pages,
                },
                handle,
                indent=2,
                ensure_ascii=False,
            )
        logger.info("Data saved to %s", filename)


class Game8Scraper:
    """Backward-compatible wrapper around the new universal crawler."""

    def __init__(self, start_url: str, max_pages: int = 50, delay: float = 1.0):
        self.engine = UniversalCrawler(
            start_url=start_url,
            max_pages=max_pages,
            delay=delay,
            concurrency=1,
            fetch_mode="requests",
        )
        self.start_url = self.engine.start_url
        self.max_pages = self.engine.max_pages
        self.delay = self.engine.delay
        self.visited_urls = self.engine.visited_urls
        self.to_visit = self.engine.to_visit
        self.scraped_data = self.engine.scraped_data

    def is_valid_url(self, url: str) -> bool:
        root_domain = urlparse(self.start_url).netloc
        return Game8Provider().is_valid_url(url, root_domain=root_domain)

    def scrape(self) -> List[Dict[str, Any]]:
        self.scraped_data = self.engine.scrape()
        self.visited_urls = self.engine.visited_urls
        self.to_visit = self.engine.to_visit
        return self.scraped_data

    def save_to_json(self, filename: str = "scraped_data.json") -> None:
        self.engine.save_to_json(filename)
