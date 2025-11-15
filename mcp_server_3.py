from mcp.server.fastmcp import FastMCP, Context
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re
import random
from pydantic import BaseModel, Field
from models import SearchInput, UrlInput
# Note: FastMCP handles string returns automatically, no need for PythonCodeOutput wrapper


@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    position: int


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class DuckDuckGoSearcher:
    BASE_URL = "https://html.duckduckgo.com/html" 
    # Enhanced headers to better mimic real Chrome browser and avoid bot detection
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Cache-Control": "max-age=0",
        "Referer": "https://duckduckgo.com/",
        "DNT": "1"  # Do Not Track
    }

    def __init__(self):
        self.rate_limiter = RateLimiter()

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format results in a natural language style that's easier for LLMs to process"""
        if not results:
            return "No search results were found. Possible reasons: 1) DuckDuckGo detected automated requests (bot detection), 2) The query returned no matches, 3) Rate limiting blocked the request. Suggestions: Try rephrasing the query, wait a few minutes before retrying, or use document search instead."

        output = []
        output.append(f"Found {len(results)} search results:\n")

        for result in results:
            output.append(f"{result.position}. {result.title}")
            output.append(f"   URL: {result.link}")
            output.append(f"   Summary: {result.snippet}")
            output.append("")  # Empty line between results

        return "\n".join(output)

    async def search(
        self, query: str, ctx: Context, max_results: int = 10
    ) -> List[SearchResult]:
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()

            # Add small random delay to mimic human behavior (0.5-2 seconds)
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Create form data for POST request
            data = {
                "q": query,
                "b": "",
                "kl": "",
            }

            await ctx.info(f"Searching DuckDuckGo for: {query}")

            # Use persistent cookies to maintain session (helps avoid bot detection)
            async with httpx.AsyncClient(
                follow_redirects=True,
                cookies={"kl": "us-en", "p": "-2"}  # Default DuckDuckGo cookies
            ) as client:
                result = await client.post(
                    self.BASE_URL, 
                    data=data, 
                    headers=self.HEADERS, 
                    timeout=30.0
                )
                result.raise_for_status()

            # Parse HTML result
            soup = BeautifulSoup(result.text, "html.parser")
            if not soup:
                await ctx.error("Failed to parse HTML result")
                return []

            # Check for bot detection / CAPTCHA pages
            page_text = soup.get_text().lower()
            if any(indicator in page_text for indicator in ["captcha", "verify you're human", "bot detection", "access denied"]):
                await ctx.error("DuckDuckGo bot detection triggered - request blocked")
                return []

            # Check for rate limiting messages
            if "rate limit" in page_text or "too many requests" in page_text:
                await ctx.error("DuckDuckGo rate limit exceeded")
                return []

            results = []
            # Try multiple CSS selector patterns (DuckDuckGo may change structure)
            result_elements = soup.select(".result") or soup.select(".web-result") or soup.select("article.result")
            
            if not result_elements:
                # Check if page loaded but has no results (legitimate empty result)
                if "no results" in page_text or "didn't find" in page_text:
                    await ctx.info("Query returned no results (not a bot detection issue)")
                else:
                    await ctx.error("Could not find result elements - HTML structure may have changed")
                return []

            for result in result_elements:
                # Try multiple title selector patterns
                title_elem = (result.select_one(".result__title") or 
                             result.select_one(".result-title") or 
                             result.select_one("h2") or
                             result.select_one("a.result__a"))
                
                if not title_elem:
                    continue

                link_elem = title_elem.find("a") if title_elem.name != "a" else title_elem
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                link = link_elem.get("href", "")

                # Skip ad results
                if "y.js" in link or "ad" in link.lower():
                    continue

                # Clean up DuckDuckGo redirect URLs
                if link.startswith("//duckduckgo.com/l/?uddg="):
                    link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])

                # Try multiple snippet selector patterns
                snippet_elem = (result.select_one(".result__snippet") or 
                               result.select_one(".result-snippet") or
                               result.select_one(".snippet"))
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                if title:  # Only add if we have a title
                    results.append(
                        SearchResult(
                            title=title,
                            link=link,
                            snippet=snippet,
                            position=len(results) + 1,
                        )
                    )

                if len(results) >= max_results:
                    break

            await ctx.info(f"Successfully found {len(results)} results")
            return results

        except httpx.TimeoutException:
            await ctx.error("Search request timed out")
            return []
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            await ctx.error(f"Unexpected error during search: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return []


class WebContentFetcher:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=20)

    async def fetch_and_parse(self, url: str, ctx: Context) -> str:
        """Fetch and parse content from a webpage"""
        try:
            await self.rate_limiter.acquire()

            await ctx.info(f"Fetching content from: {url}")

            async with httpx.AsyncClient() as client:
                result = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    follow_redirects=True,
                    timeout=30.0,
                )
                result.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(result.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Get the text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"

            await ctx.info(
                f"Successfully fetched and parsed content ({len(text)} characters)"
            )
            return text

        except httpx.TimeoutException:
            await ctx.error(f"Request timed out for URL: {url}")
            return "Error: The request timed out while trying to fetch the webpage."
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            await ctx.error(f"Error fetching content from {url}: {str(e)}")
            return f"Error: An unexpected error occurred while fetching the webpage ({str(e)})"


# Initialize FastMCP server
mcp = FastMCP("ddg-search")
searcher = DuckDuckGoSearcher()
fetcher = WebContentFetcher()


@mcp.tool()
async def duckduckgo_search_results(input: SearchInput, ctx: Context) -> str:
    """Search DuckDuckGo. Usage: input={"input": {"query": "latest AI developments", "max_results": 5} } result = await mcp.call_tool('duckduckgo_search_results', input)"""
    try:
        results = await searcher.search(input.query, ctx, input.max_results)
        # Return string directly - FastMCP will handle the response format
        return searcher.format_results_for_llm(results)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"


@mcp.tool()
async def download_raw_html_from_url(input: UrlInput, ctx: Context) -> str:
    """Fetch webpage content. Usage: input={"input": {"url": "https://example.com"} } result = await mcp.call_tool('download_raw_html_from_url', input)"""
    # Return string directly - FastMCP will handle the response format
    return await fetcher.fetch_and_parse(input.url, ctx)


if __name__ == "__main__":
    print("mcp_server_3.py starting")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
        print("\nShutting down...")