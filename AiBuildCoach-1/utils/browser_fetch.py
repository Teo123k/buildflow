"""
Browser Fetch Module - Safe HTML Fetching

Provides graceful HTML fetching with fallbacks and cleaning.
Optimized for both external websites and Replit preview URLs.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any
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
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}


def is_replit_url(url: str) -> bool:
    """Check if URL is a Replit preview URL."""
    url_lower = url.lower()
    return any(x in url_lower for x in [".replit.", "spock.", ".repl.co", "replit.dev"])


def fetch_html(url: str) -> str:
    """
    Fetch HTML with browser-like behavior.
    
    Features:
    - 20 second timeout (45 for Replit URLs)
    - Real browser User-Agent and headers
    - follow_redirects=True
    - Retry logic (3 attempts)
    - SSL fallback for problematic sites
    - Returns cleaned HTML text
    
    Args:
        url: URL to fetch
        
    Returns:
        Prettified HTML string or fallback error HTML
    """
    is_replit = is_replit_url(url)
    timeout = 45 if is_replit else 20
    
    for attempt in range(3):
        try:
            with httpx.Client(
                follow_redirects=True, 
                timeout=timeout,
                verify=True
            ) as client:
                res = client.get(url, headers=BROWSER_HEADERS)
                res.raise_for_status()
                html = res.text
                
                if len(html) < 50:
                    print(f"Empty response from {url}, retrying...")
                    time.sleep(1)
                    continue
                
                soup = BeautifulSoup(html, "html.parser")
                
                for tag in soup.find_all(['script', 'noscript']):
                    tag.decompose()
                for style in soup.find_all('style'):
                    if len(style.get_text()) > 500:
                        style.decompose()
                
                return soup.prettify()
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code} for {url}")
            return f"<html><body>HTTP Error: {e.response.status_code}</body></html>"
            
        except (httpx.SSLError, httpx.ConnectError) as e:
            print(f"SSL/Connect error on attempt {attempt+1}, trying without SSL verification: {e}")
            try:
                with httpx.Client(
                    follow_redirects=True,
                    timeout=timeout,
                    verify=False
                ) as client:
                    res = client.get(url, headers=BROWSER_HEADERS)
                    html = res.text
                    
                    if len(html) >= 50:
                        soup = BeautifulSoup(html, "html.parser")
                        for tag in soup.find_all(['script', 'noscript']):
                            tag.decompose()
                        return soup.prettify()
            except Exception as fallback_error:
                print(f"SSL fallback also failed: {fallback_error}")
            time.sleep(1)
            
        except Exception as e:
            print(f"Fetch attempt {attempt+1} failed: {e}")
            time.sleep(1)
    
    return "<html><body>Unable to fetch (timeout or blocked after 3 attempts).</body></html>"


def fetch_html_with_status(url: str) -> Dict[str, Any]:
    """
    Fetches HTML with detailed status information.
    Uses browser-like behavior with retries.
    
    Features:
    - 20 second timeout (45 for Replit URLs)
    - Real browser headers
    - Retry logic (3 attempts)
    - SSL fallback
    
    Returns:
        Dictionary with success status, HTML content, status_code, and any errors
    """
    is_replit = is_replit_url(url)
    timeout = 45 if is_replit else 20
    
    last_error = None
    
    for attempt in range(3):
        try:
            with httpx.Client(
                follow_redirects=True,
                timeout=timeout,
                verify=True
            ) as client:
                response = client.get(url, headers=BROWSER_HEADERS)
                response.raise_for_status()
                
                text = response.text
                if len(text) < 50:
                    last_error = "Empty or minimal response"
                    print(f"Empty response, attempt {attempt+1}")
                    time.sleep(1)
                    continue
                
                soup = BeautifulSoup(text, 'html.parser')
                
                for tag in soup.find_all(['script', 'noscript']):
                    tag.decompose()
                
                return {
                    "success": True,
                    "html": soup.prettify(),
                    "status_code": response.status_code,
                    "error": None
                }
                
        except httpx.TimeoutException:
            last_error = f"Request timed out (>{timeout}s)"
            print(f"Timeout on attempt {attempt+1}")
            time.sleep(1)
            
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "html": "",
                "status_code": e.response.status_code,
                "error": f"HTTP error: {e.response.status_code}"
            }
            
        except (httpx.SSLError, httpx.ConnectError) as e:
            print(f"SSL/Connect error, trying without verification: {e}")
            try:
                with httpx.Client(
                    follow_redirects=True,
                    timeout=timeout,
                    verify=False
                ) as client:
                    response = client.get(url, headers=BROWSER_HEADERS)
                    text = response.text
                    
                    if len(text) >= 50:
                        soup = BeautifulSoup(text, 'html.parser')
                        for tag in soup.find_all(['script', 'noscript']):
                            tag.decompose()
                        return {
                            "success": True,
                            "html": soup.prettify(),
                            "status_code": response.status_code,
                            "error": None
                        }
            except Exception as fallback_error:
                last_error = str(fallback_error)
            time.sleep(1)
            
        except Exception as e:
            last_error = str(e)
            print(f"Fetch attempt {attempt+1} failed: {e}")
            time.sleep(1)
    
    return {
        "success": False,
        "html": "",
        "status_code": None,
        "error": last_error or "Failed after 3 attempts"
    }
