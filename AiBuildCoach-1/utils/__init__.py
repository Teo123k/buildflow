"""
Utils Package - AI Wrapper and Browser Fetch Utilities
"""

from .ai_wrapper import smart_ai, extract_limited_html, clear_cache, get_cache_stats
from .browser_fetch import fetch_html, fetch_html_with_status

__all__ = [
    'smart_ai',
    'extract_limited_html', 
    'clear_cache',
    'get_cache_stats',
    'fetch_html',
    'fetch_html_with_status'
]
