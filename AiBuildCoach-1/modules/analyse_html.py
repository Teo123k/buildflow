"""
HTML Analysis Module

Will later download external HTML, analyse structure, and produce basic issues.

This module will be responsible for:
- Fetching HTML content from external URLs
- Parsing HTML structure (DOM tree)
- Identifying structural issues (missing elements, improper nesting)
- Detecting broken or malformed HTML
- Returning a list of HTML-related issues
"""

import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def is_replit_url(url: str) -> bool:
    """Check if URL is a Replit preview URL."""
    url_lower = url.lower()
    return any(x in url_lower for x in [".replit.", "spock.", ".repl.co", "replit.dev"])


def fetch_raw_html(url: str) -> dict:
    """
    Fetch raw HTML from any external URL or Replit preview URL.
    
    Features:
    - 20 second timeout (45 for Replit URLs)
    - Real browser User-Agent and headers
    - follow_redirects=True
    - Retry logic (3 attempts)
    - SSL fallback for problematic sites
    
    Args:
        url: The URL to fetch HTML from
        
    Returns:
        Dictionary with keys:
        - success (bool): Whether the fetch was successful
        - status_code (int or None): HTTP status code
        - html (str): Raw HTML content (empty string if failed)
        - error (str): Error message if failed (empty string if successful)
    """
    result = {
        "success": False,
        "status_code": None,
        "html": "",
        "error": ""
    }
    
    try:
        parsed_url = urlparse(url)
        
        if not url.strip():
            result["error"] = "URL cannot be empty"
            return result
            
        if not parsed_url.scheme:
            url = "https://" + url
            parsed_url = urlparse(url)
            
        if parsed_url.scheme not in ("http", "https"):
            result["error"] = f"Invalid scheme: {parsed_url.scheme}. Only http and https are supported."
            return result
        
        is_replit = is_replit_url(url)
        timeout = 45 if is_replit else 20
        
        last_error = None
        
        for attempt in range(3):
            try:
                with httpx.Client(
                    verify=True,
                    timeout=timeout,
                    follow_redirects=True
                ) as client:
                    response = client.get(url, headers=BROWSER_HEADERS)
                    
                    result["status_code"] = response.status_code
                    
                    if response.status_code == 200:
                        html_text = response.text
                        if len(html_text) < 50:
                            last_error = "Empty or slow response from server"
                            time.sleep(1)
                            continue
                        result["success"] = True
                        result["html"] = html_text
                        return result
                    else:
                        result["error"] = f"HTTP {response.status_code}: {response.reason_phrase}"
                        return result
                        
            except (httpx.SSLError, httpx.ConnectError) as ssl_err:
                print(f"SSL/Connect error on attempt {attempt+1}, trying without SSL: {ssl_err}")
                try:
                    with httpx.Client(
                        verify=False,
                        timeout=timeout,
                        follow_redirects=True
                    ) as client:
                        response = client.get(url, headers=BROWSER_HEADERS)
                        result["status_code"] = response.status_code
                        
                        if response.status_code == 200:
                            html_text = response.text
                            if len(html_text) >= 50:
                                result["success"] = True
                                result["html"] = html_text
                                return result
                except Exception as fallback_err:
                    last_error = str(fallback_err)
                time.sleep(1)
                
            except httpx.TimeoutException:
                last_error = f"Request timeout (> {timeout} seconds)"
                print(f"Timeout on attempt {attempt+1}")
                time.sleep(1)
                
            except Exception as e:
                last_error = str(e)
                print(f"Fetch attempt {attempt+1} failed: {e}")
                time.sleep(1)
        
        result["error"] = last_error or "Failed after 3 attempts"
        
    except ValueError as e:
        result["error"] = f"Invalid URL: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {type(e).__name__}: {str(e)}"
    
    return result


def analyze_basic_structure(html: str) -> dict:
    """
    Analyse basic HTML structure and detect common issues.
    
    Extracts:
    - Title tag
    - Meta description
    - All H1 tags
    - All H2 tags
    - Count of P tags
    
    Detects issues:
    - Missing title
    - Missing meta description
    - No H1 tags
    - Multiple H1 tags
    - Empty body
    
    Args:
        html: Raw HTML content
        
    Returns:
        Dictionary with structure data and detected issues
    """
    result = {
        "title": None,
        "description": None,
        "h1": [],
        "h2": [],
        "p_count": 0,
        "basic_issues": []
    }
    
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)
        else:
            result["basic_issues"].append("missing title")
        
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            result["description"] = meta_desc.get("content")
        else:
            result["basic_issues"].append("missing meta description")
        
        h1_tags = soup.find_all("h1")
        result["h1"] = [h1.get_text(strip=True) for h1 in h1_tags]
        
        if not h1_tags:
            result["basic_issues"].append("no H1 tags")
        elif len(h1_tags) > 1:
            result["basic_issues"].append("multiple H1 tags")
        
        h2_tags = soup.find_all("h2")
        result["h2"] = [h2.get_text(strip=True) for h2 in h2_tags]
        
        p_tags = soup.find_all("p")
        result["p_count"] = len(p_tags)
        
        body = soup.find("body")
        if not body or not body.get_text(strip=True):
            result["basic_issues"].append("empty body")
            
    except Exception as e:
        result["basic_issues"].append(f"parsing error: {str(e)}")
    
    return result


async def fetch_html(url: str) -> str:
    """
    Fetch HTML content from an external URL.
    
    Args:
        url: The URL to fetch HTML from
        
    Returns:
        Raw HTML content as string
    """
    pass


async def parse_html(html: str) -> dict:
    """
    Parse HTML content and extract structure information.
    
    Args:
        html: Raw HTML content
        
    Returns:
        Dictionary containing parsed structure data
    """
    pass


async def analyse_structure(parsed_html: dict) -> list:
    """
    Analyse the HTML structure and identify issues.
    
    Args:
        parsed_html: Parsed HTML data from parse_html()
        
    Returns:
        List of structural issues found
    """
    pass


async def run_html_analysis(url: str) -> dict:
    """
    Main entry point for HTML analysis.
    
    Orchestrates the full HTML analysis pipeline:
    1. Fetch HTML from URL
    2. Parse the HTML structure
    3. Analyse for issues
    4. Return comprehensive report
    
    Args:
        url: The URL to analyse
        
    Returns:
        Complete HTML analysis report
    """
    pass
