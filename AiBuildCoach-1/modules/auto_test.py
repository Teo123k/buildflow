"""
Auto-Test Module - Website Health Check

Fast QA testing that checks essential website health:
- Load time
- Status code
- Title tag, meta description, H1
- Links validation
- Basic accessibility tags

Returns detailed, actionable issues with exact fixes.
"""

import httpx
import time
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en"
}


def run_basic_autotest(url: str) -> Dict[str, Any]:
    """
    Run fast QA tests on a website.
    
    Checks:
    - Load time (should be under 3s)
    - Status code (should be 200)
    - Title tag exists
    - Meta description exists
    - H1 exists
    - Links are valid
    - Basic accessibility tags
    
    Returns detailed issues with exact code fixes.
    """
    print(f"[AUTO_TEST] Starting QA tests for: {url}")
    
    result = {
        "success": True,
        "url": url,
        "summary": "",
        "status": "Working",
        "response_time_ms": 0,
        "status_code": 200,
        "checks_passed": [],
        "issues": []
    }
    
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            response = client.get(url, headers=BROWSER_HEADERS)
        
        response_time = (time.time() - start_time) * 1000
        result["response_time_ms"] = round(response_time, 0)
        result["status_code"] = response.status_code
        
        if response_time > 3000:
            result["status"] = "Slow"
            result["issues"].append({
                "title": "Page loads too slowly",
                "description": f"Your page took {round(response_time/1000, 1)} seconds to load. Users expect pages to load in under 3 seconds.",
                "location": "Server / Assets",
                "steps_to_fix": [
                    "Step 1: Compress your images using tools like TinyPNG",
                    "Step 2: Minimize your CSS and JavaScript files",
                    "Step 3: Enable browser caching on your server",
                    "Step 4: Consider using a CDN for static assets"
                ],
                "code_fix": '```html\n<!-- Add to <head> to preload critical assets -->\n<link rel="preload" href="style.css" as="style">\n<link rel="preload" href="main.js" as="script">\n```',
                "files_to_modify": ["index.html"],
                "prompt_to_apply_fix": "Optimize my website loading speed by compressing images and minifying CSS/JS files."
            })
        else:
            result["checks_passed"].append(f"Fast load time ({round(response_time)}ms)")
        
        if response.status_code >= 400:
            result["success"] = False
            result["status"] = "Error"
            result["issues"].append({
                "title": f"Server error {response.status_code}",
                "description": f"The server returned error code {response.status_code}. This means visitors cannot access your page.",
                "location": "Server configuration",
                "steps_to_fix": [
                    "Step 1: Check if your server is running",
                    "Step 2: Verify the URL is correct",
                    "Step 3: Check server logs for errors",
                    "Step 4: Ensure your hosting is active"
                ],
                "code_fix": "```\n# Check server status and logs\n# This is a server configuration issue\n```",
                "files_to_modify": [],
                "prompt_to_apply_fix": f"Debug why my server is returning a {response.status_code} error."
            })
            result["summary"] = f"Critical: Server returned error {response.status_code}"
            return result
        else:
            result["checks_passed"].append(f"Status code OK ({response.status_code})")
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        check_results = run_all_checks(soup, url)
        result["checks_passed"].extend(check_results["passed"])
        result["issues"].extend(check_results["issues"])
        
        issue_count = len(result["issues"])
        if issue_count == 0:
            result["summary"] = "All QA tests passed! Your website looks healthy."
            result["status"] = "Healthy"
        elif issue_count <= 2:
            result["summary"] = f"Found {issue_count} minor issue(s) to fix."
            result["status"] = "Needs attention"
        else:
            result["summary"] = f"Found {issue_count} issues that should be fixed."
            result["status"] = "Needs work"
        
        print(f"[AUTO_TEST] Complete for: {url} - {len(result['checks_passed'])} passed, {issue_count} issues")
        return result
        
    except httpx.TimeoutException:
        print(f"[AUTO_TEST] Timeout for: {url}")
        return {
            "success": False,
            "url": url,
            "summary": "Website timed out - could not connect within 10 seconds.",
            "status": "Timeout",
            "response_time_ms": 10000,
            "status_code": 0,
            "checks_passed": [],
            "issues": [{
                "title": "Website timeout",
                "description": "Your website took too long to respond. This could mean the server is down or overloaded.",
                "location": "Server",
                "steps_to_fix": [
                    "Step 1: Check if your server is running",
                    "Step 2: Check your hosting provider's status page",
                    "Step 3: Look at server resource usage (CPU, memory)",
                    "Step 4: Check if the domain DNS is configured correctly"
                ],
                "code_fix": "```\n# Server configuration issue - no code fix available\n# Contact your hosting provider if the issue persists\n```",
                "files_to_modify": [],
                "prompt_to_apply_fix": "Debug why my website is timing out and not responding."
            }]
        }
    except Exception as e:
        print(f"[AUTO_TEST] Error for: {url} - {e}")
        return {
            "success": False,
            "url": url,
            "summary": f"Could not connect to website: {str(e)[:50]}",
            "status": "Error",
            "response_time_ms": 0,
            "status_code": 0,
            "checks_passed": [],
            "issues": [{
                "title": "Connection failed",
                "description": f"Could not connect to the website. Error: {str(e)[:100]}",
                "location": "URL / Network",
                "steps_to_fix": [
                    "Step 1: Verify the URL is correct and includes https://",
                    "Step 2: Check if the website is accessible in a browser",
                    "Step 3: Ensure there are no firewall blocks",
                    "Step 4: Try again in a few minutes"
                ],
                "code_fix": "```\n# Network or URL issue - verify the URL is correct\n```",
                "files_to_modify": [],
                "prompt_to_apply_fix": "Help me debug why I cannot connect to my website."
            }]
        }


def run_all_checks(soup: BeautifulSoup, url: str) -> Dict[str, List]:
    """Run all QA checks on the HTML."""
    passed = []
    issues = []
    
    title_result = check_title(soup)
    if title_result["passed"]:
        passed.append(title_result["message"])
    else:
        issues.append(title_result["issue"])
    
    meta_result = check_meta_description(soup)
    if meta_result["passed"]:
        passed.append(meta_result["message"])
    else:
        issues.append(meta_result["issue"])
    
    h1_result = check_h1(soup)
    if h1_result["passed"]:
        passed.append(h1_result["message"])
    else:
        issues.append(h1_result["issue"])
    
    viewport_result = check_viewport(soup)
    if viewport_result["passed"]:
        passed.append(viewport_result["message"])
    else:
        issues.append(viewport_result["issue"])
    
    links_result = check_links(soup, url)
    if links_result["passed"]:
        passed.append(links_result["message"])
    if links_result.get("issue"):
        issues.append(links_result["issue"])
    
    alt_result = check_image_alt(soup)
    if alt_result["passed"]:
        passed.append(alt_result["message"])
    if alt_result.get("issue"):
        issues.append(alt_result["issue"])
    
    lang_result = check_lang_attribute(soup)
    if lang_result["passed"]:
        passed.append(lang_result["message"])
    else:
        issues.append(lang_result["issue"])
    
    return {"passed": passed, "issues": issues}


def check_title(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for title tag."""
    title = soup.find('title')
    if title and title.get_text(strip=True):
        title_text = title.get_text(strip=True)
        return {"passed": True, "message": f"Title tag exists ({len(title_text)} chars)"}
    
    return {
        "passed": False,
        "issue": {
            "title": "Missing page title",
            "description": "Your page has no <title> tag. This is what appears in browser tabs and Google search results.",
            "location": "index.html > <head>",
            "steps_to_fix": [
                "Step 1: Open index.html",
                "Step 2: Find the <head> section",
                "Step 3: Add a <title> tag with your page name"
            ],
            "code_fix": '```html\n<head>\n  <title>Your Page Title | Your Brand</title>\n</head>\n```',
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": "Add a descriptive title tag to my HTML page in the <head> section."
        }
    }


def check_meta_description(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for meta description."""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        content = meta_desc.get('content', '')
        return {"passed": True, "message": f"Meta description exists ({len(content)} chars)"}
    
    return {
        "passed": False,
        "issue": {
            "title": "Missing meta description",
            "description": "Your page has no meta description. This text appears under your title in Google search results.",
            "location": "index.html > <head>",
            "steps_to_fix": [
                "Step 1: Open index.html",
                "Step 2: Find the <head> section",
                "Step 3: Add a meta description tag (150-160 characters)"
            ],
            "code_fix": '```html\n<head>\n  <meta name="description" content="Write a compelling description of your page here. Keep it between 150-160 characters for best results in search engines.">\n</head>\n```',
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": "Add a meta description tag to my HTML page that describes what the page is about."
        }
    }


def check_h1(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for H1 heading."""
    h1_tags = soup.find_all('h1')
    if h1_tags:
        if len(h1_tags) == 1:
            return {"passed": True, "message": "Has one H1 heading"}
        else:
            return {
                "passed": False,
                "issue": {
                    "title": f"Multiple H1 headings ({len(h1_tags)})",
                    "description": f"Your page has {len(h1_tags)} H1 tags. You should only have one main heading per page.",
                    "location": "index.html > <body>",
                    "steps_to_fix": [
                        "Step 1: Find all <h1> tags in your HTML",
                        "Step 2: Keep only the most important one as <h1>",
                        "Step 3: Change the others to <h2> or <h3>"
                    ],
                    "code_fix": '```html\n<!-- Keep ONE h1 for your main heading -->\n<h1>Your Main Page Title</h1>\n\n<!-- Use h2 for section headings -->\n<h2>Section Heading</h2>\n```',
                    "files_to_modify": ["index.html"],
                    "prompt_to_apply_fix": "Fix my HTML so there is only one H1 heading. Change extra H1s to H2 tags."
                }
            }
    
    return {
        "passed": False,
        "issue": {
            "title": "Missing H1 heading",
            "description": "Your page has no H1 heading. The H1 tells search engines and users what your page is about.",
            "location": "index.html > <body>",
            "steps_to_fix": [
                "Step 1: Open index.html",
                "Step 2: Find the main content area",
                "Step 3: Add an <h1> tag with your main page title"
            ],
            "code_fix": '```html\n<body>\n  <h1>Your Main Page Heading</h1>\n  <!-- rest of your content -->\n</body>\n```',
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": "Add an H1 heading to my HTML page that describes the main topic."
        }
    }


def check_viewport(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for viewport meta tag."""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        return {"passed": True, "message": "Has viewport meta (mobile-friendly)"}
    
    return {
        "passed": False,
        "issue": {
            "title": "Not mobile-friendly",
            "description": "Your page is missing the viewport meta tag. Without it, your site won't display correctly on phones and tablets.",
            "location": "index.html > <head>",
            "steps_to_fix": [
                "Step 1: Open index.html",
                "Step 2: Find the <head> section",
                "Step 3: Add the viewport meta tag"
            ],
            "code_fix": '```html\n<head>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>\n```',
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": "Add a viewport meta tag to make my page mobile-friendly."
        }
    }


def check_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """Check links on the page."""
    links = soup.find_all('a', href=True)
    
    if not links:
        return {
            "passed": False,
            "message": "No links found",
            "issue": {
                "title": "No links on page",
                "description": "Your page has no links. Links help users navigate and help search engines understand your site structure.",
                "location": "index.html > <body>",
                "steps_to_fix": [
                    "Step 1: Add navigation links to other pages",
                    "Step 2: Add links to relevant external resources",
                    "Step 3: Make sure all links have descriptive text"
                ],
                "code_fix": '```html\n<nav>\n  <a href="/">Home</a>\n  <a href="/about">About</a>\n  <a href="/contact">Contact</a>\n</nav>\n```',
                "files_to_modify": ["index.html"],
                "prompt_to_apply_fix": "Add navigation links to my HTML page."
            }
        }
    
    empty_links = []
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href in ['#', '', 'javascript:void(0)'] and not text:
            empty_links.append(href)
    
    if empty_links:
        return {
            "passed": True,
            "message": f"Has {len(links)} links",
            "issue": {
                "title": f"{len(empty_links)} empty or broken links",
                "description": "Some links on your page are empty or have no destination. These confuse users and hurt accessibility.",
                "location": "index.html > <a> tags",
                "steps_to_fix": [
                    "Step 1: Find all links with href='#' or empty href",
                    "Step 2: Either add a real destination or remove the link",
                    "Step 3: Make sure all links have descriptive text"
                ],
                "code_fix": '```html\n<!-- Bad: empty link -->\n<a href="#">Click here</a>\n\n<!-- Good: real destination -->\n<a href="/about">Learn more about us</a>\n```',
                "files_to_modify": ["index.html"],
                "prompt_to_apply_fix": "Fix empty and broken links in my HTML. Replace # links with real destinations."
            }
        }
    
    return {"passed": True, "message": f"Has {len(links)} valid links"}


def check_image_alt(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check images for alt text."""
    images = soup.find_all('img')
    
    if not images:
        return {"passed": True, "message": "No images to check"}
    
    missing_alt = []
    for img in images:
        alt = img.get('alt')
        if alt is None or alt.strip() == '':
            src = img.get('src', 'unknown')[:30]
            missing_alt.append(src)
    
    if missing_alt:
        return {
            "passed": False,
            "message": f"{len(missing_alt)} images missing alt text",
            "issue": {
                "title": f"{len(missing_alt)} images missing alt text",
                "description": "Some images don't have alt text. Alt text is required for accessibility and helps with SEO.",
                "location": "index.html > <img> tags",
                "steps_to_fix": [
                    "Step 1: Find all <img> tags in your HTML",
                    "Step 2: Add an alt attribute to each one",
                    "Step 3: Write a brief description of what the image shows"
                ],
                "code_fix": '```html\n<!-- Add alt text describing the image -->\n<img src="team-photo.jpg" alt="Our team members standing in the office">\n\n<!-- For decorative images, use empty alt -->\n<img src="decorative-line.png" alt="">\n```',
                "files_to_modify": ["index.html"],
                "prompt_to_apply_fix": f"Add alt text to the {len(missing_alt)} images that are missing it. Describe what each image shows."
            }
        }
    
    return {"passed": True, "message": f"All {len(images)} images have alt text"}


def check_lang_attribute(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check for lang attribute on html tag."""
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        lang = html_tag.get('lang')
        return {"passed": True, "message": f"Has lang attribute ({lang})"}
    
    return {
        "passed": False,
        "issue": {
            "title": "Missing language attribute",
            "description": "Your HTML tag is missing the lang attribute. This helps screen readers and search engines understand what language your page is in.",
            "location": "index.html > <html>",
            "steps_to_fix": [
                "Step 1: Open index.html",
                "Step 2: Find the opening <html> tag",
                "Step 3: Add the lang attribute with your language code"
            ],
            "code_fix": '```html\n<!-- For English -->\n<html lang="en">\n\n<!-- For Spanish -->\n<html lang="es">\n\n<!-- For French -->\n<html lang="fr">\n```',
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": "Add a lang attribute to my HTML tag to specify the page language."
        }
    }


async def run_full_autotest(url: str) -> Dict[str, Any]:
    """Async wrapper for the basic autotest."""
    return run_basic_autotest(url)
