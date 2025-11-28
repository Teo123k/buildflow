"""
SEO AI Module - AI-Enhanced SEO Analysis

Detailed, specific, actionable SEO analysis with exact meta tags,
code patches, and step-by-step fixes.
ALWAYS returns valid JSON - never raises, never returns invalid data.
Uses the user's own OPENAI_API_KEY from environment secrets.
"""

import os
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, Any, List

from utils.ai_wrapper import safe_json_ai, extract_limited_html, DEFAULT_MODEL


def run_seo_ai(html: str, url: str) -> Dict[str, Any]:
    """
    Run AI-enhanced SEO analysis with detailed, actionable fixes.
    ALWAYS returns valid JSON dict.
    """
    print(f"[SEO_AI] Starting detailed SEO analysis for: {url}")
    
    try:
        seo_data = extract_seo_data(html, url)
        rule_based_issues = run_rule_based_seo_check(seo_data)
        
        limited_html = extract_limited_html(html, limit=3000)
        
        issues_context = ""
        if rule_based_issues:
            issues_context = "Rule-based issues detected:\n" + "\n".join([
                f"- {i['message']} ({i['severity']} priority)" for i in rule_based_issues[:8]
            ])
        
        prompt = f"""You are a senior SEO specialist and full-stack engineer.
Analyze the site for REAL SEO issues and provide exact, detailed fixes.

STRICT RULES:
- NEVER say "improve SEO" - be specific about WHAT to improve.
- ALWAYS show exact meta tags to add.
- ALWAYS show exact <head> edits.
- ALWAYS give exact keywords based on the page content.
- ALWAYS include code patches with minimal, working updates.
- ALWAYS output valid JSON only.

Website URL: {url}

Current SEO Data:
- Title: "{seo_data['title']}" ({seo_data['title_length']} chars)
- Meta Description: "{seo_data['meta_description'][:100]}..." ({seo_data['meta_description_length']} chars)
- H1 Tags: {seo_data['h1_count']} found - {seo_data['headings'].get('h1', ['None'])}
- Word Count: {seo_data['word_count']}
- Images without alt: {seo_data['images_without_alt']} of {seo_data['total_images']}
- Has Canonical: {'Yes' if seo_data['canonical'] else 'No'}
- Has OG Tags: {'Yes' if seo_data['og_tags'] else 'No'}
- Has Schema: {'Yes' if seo_data['has_schema'] else 'No'}
- Has Viewport: {'Yes' if seo_data['has_viewport'] else 'No'}
- Language: {seo_data['lang'] or 'Not set'}

{issues_context}

HTML snippet:
```html
{limited_html}
```

Check for:
1. Missing or weak title tag (should be 50-60 chars, include primary keyword)
2. Missing or weak meta description (should be 150-160 chars)
3. Missing Open Graph tags (og:title, og:description, og:image)
4. Missing or multiple H1 tags
5. Weak or missing keywords in content
6. Images missing alt text
7. Missing canonical URL
8. Bad link structure

Respond ONLY with this exact JSON structure (no markdown, no explanation):
{{
  "summary": "One sentence summary of the most critical SEO issues.",
  "score": 75,
  "suggested_keywords": ["keyword1", "keyword2", "keyword3"],
  "issues": [
    {{
      "title": "Short issue title (5-7 words)",
      "description": "What is wrong and why it matters for search rankings.",
      "location": "Exact location (e.g., index.html > <head>, index.html > <body> > first section)",
      "why_it_matters": "How this affects Google ranking or user clicks.",
      "steps_to_fix": [
        "Step 1: Open index.html",
        "Step 2: Find the <head> section",
        "Step 3: Add the code below"
      ],
      "code_fix": "```html\\n<exact meta tag or code to add>\\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "A ready-to-use prompt for AI to apply this exact fix."
    }}
  ]
}}

Return 3-6 issues maximum, ordered by impact. Every issue MUST have working code_fix."""

        print(f"[SEO_AI] Calling AI for detailed analysis: {url}")
        
        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"seo-detailed-{url}",
            max_tokens=2000,
            temperature=0.2,
            default_response={"summary": "Analysis complete", "score": 50, "issues": []}
        )
        
        if "error" in result:
            print(f"[SEO_AI] AI error: {result.get('error')}")
            return generate_detailed_fallback(seo_data, rule_based_issues, url)
        
        parsed = parse_detailed_result(result, seo_data, rule_based_issues, url)
        print(f"[SEO_AI] Success for: {url} - score: {parsed.get('score', 50)}, issues: {len(parsed.get('issues', []))}")
        return parsed
        
    except Exception as e:
        print(f"[SEO_AI] Exception: {e}")
        return {
            "summary": "SEO analysis encountered an error.",
            "score": 50,
            "issues": [],
            "suggested_keywords": [],
            "recommendations": [],
            "ai_tasks": [],
            "exact_fixes": [],
            "fix_prompt": "Please try again.",
            "error": str(e)[:100]
        }


def extract_seo_data(html: str, url: str) -> Dict[str, Any]:
    """Extract all SEO-relevant data from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    meta_description = ""
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_desc_tag:
        meta_description = meta_desc_tag.get('content', '')
    
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        headings[f'h{i}'] = [h.get_text(strip=True)[:50] for h in h_tags[:3]]
    
    body = soup.find('body')
    body_text = body.get_text(separator=' ', strip=True) if body else ""
    word_count = len(body_text.split())
    
    images = soup.find_all('img')
    images_without_alt = sum(1 for img in images if not img.get('alt'))
    
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    canonical = canonical_tag.get('href', '') if canonical_tag else ""
    
    og_tags = {}
    for og in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
        og_tags[og.get('property', '')] = og.get('content', '')[:50]
    
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    
    lang = soup.find('html')
    lang_attr = lang.get('lang', '') if lang else ''
    
    schema_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    
    links = soup.find_all('a', href=True)
    internal_links = sum(1 for a in links if a.get('href', '').startswith('/') or url in a.get('href', ''))
    
    return {
        "url": url,
        "title": title,
        "title_length": len(title),
        "meta_description": meta_description,
        "meta_description_length": len(meta_description),
        "headings": headings,
        "h1_count": len(headings.get('h1', [])),
        "word_count": word_count,
        "total_images": len(images),
        "images_without_alt": images_without_alt,
        "canonical": canonical,
        "og_tags": og_tags,
        "has_schema": len(schema_scripts) > 0,
        "has_viewport": viewport is not None,
        "lang": lang_attr,
        "internal_links": internal_links,
        "total_links": len(links)
    }


def run_rule_based_seo_check(data: Dict) -> List[Dict]:
    """Run rule-based SEO checks."""
    issues = []
    
    if not data["title"]:
        issues.append({"type": "missing_title", "severity": "high", "message": "Missing page title"})
    elif data["title_length"] < 30:
        issues.append({"type": "short_title", "severity": "medium", "message": f"Title too short ({data['title_length']} chars)"})
    elif data["title_length"] > 60:
        issues.append({"type": "long_title", "severity": "low", "message": f"Title may be truncated ({data['title_length']} chars)"})
    
    if not data["meta_description"]:
        issues.append({"type": "missing_meta", "severity": "high", "message": "Missing meta description"})
    elif data["meta_description_length"] < 120:
        issues.append({"type": "short_meta", "severity": "medium", "message": f"Meta description too short ({data['meta_description_length']} chars)"})
    elif data["meta_description_length"] > 160:
        issues.append({"type": "long_meta", "severity": "low", "message": f"Meta description may be truncated ({data['meta_description_length']} chars)"})
    
    if data["h1_count"] == 0:
        issues.append({"type": "missing_h1", "severity": "high", "message": "Missing H1 heading"})
    elif data["h1_count"] > 1:
        issues.append({"type": "multiple_h1", "severity": "medium", "message": f"Multiple H1 headings ({data['h1_count']})"})
    
    if not data["canonical"]:
        issues.append({"type": "missing_canonical", "severity": "medium", "message": "Missing canonical link"})
    
    if not data["og_tags"]:
        issues.append({"type": "missing_og", "severity": "medium", "message": "Missing Open Graph tags"})
    
    if not data["has_schema"]:
        issues.append({"type": "missing_schema", "severity": "low", "message": "No schema markup found"})
    
    if data["images_without_alt"] > 0:
        issues.append({"type": "missing_alt", "severity": "high", "message": f"{data['images_without_alt']} images missing alt text"})
    
    if not data["has_viewport"]:
        issues.append({"type": "missing_viewport", "severity": "high", "message": "Missing viewport meta tag"})
    
    if data["word_count"] < 300:
        issues.append({"type": "thin_content", "severity": "medium", "message": f"Low content ({data['word_count']} words)"})
    
    if not data["lang"]:
        issues.append({"type": "missing_lang", "severity": "low", "message": "Missing lang attribute on <html>"})
    
    return issues


def parse_detailed_result(result: Dict, seo_data: Dict, rule_issues: List[Dict], url: str) -> Dict[str, Any]:
    """Parse AI result into detailed SEO response."""
    summary = result.get("summary", "SEO analysis complete.")
    if isinstance(summary, dict):
        summary = str(summary)
    
    score = result.get("score", 50)
    if not isinstance(score, (int, float)):
        try:
            score = int(score)
        except:
            score = 50
    score = max(0, min(100, score))
    
    suggested_keywords = result.get("suggested_keywords", [])
    if not isinstance(suggested_keywords, list):
        suggested_keywords = []
    suggested_keywords = [str(k) for k in suggested_keywords[:5]]
    
    issues = result.get("issues", [])
    validated_issues = []
    
    for issue in issues[:6]:
        if isinstance(issue, dict):
            validated_issue = {
                "title": str(issue.get("title", "SEO Issue")),
                "description": str(issue.get("description", "")),
                "location": str(issue.get("location", "index.html > <head>")),
                "why_it_matters": str(issue.get("why_it_matters", "")),
                "steps_to_fix": issue.get("steps_to_fix", []),
                "code_fix": str(issue.get("code_fix", "")),
                "files_to_modify": issue.get("files_to_modify", ["index.html"]),
                "prompt_to_apply_fix": str(issue.get("prompt_to_apply_fix", ""))
            }
            
            if not isinstance(validated_issue["steps_to_fix"], list):
                validated_issue["steps_to_fix"] = [str(validated_issue["steps_to_fix"])]
            if not isinstance(validated_issue["files_to_modify"], list):
                validated_issue["files_to_modify"] = [str(validated_issue["files_to_modify"])]
                
            validated_issues.append(validated_issue)
    
    ai_tasks = []
    for issue in validated_issues:
        ai_tasks.append({
            "issue": issue["title"],
            "task": issue["description"],
            "priority": "high",
            "element": issue["location"]
        })
    
    exact_fixes = []
    for issue in validated_issues:
        exact_fixes.append({
            "selector": issue["location"],
            "fix": issue["title"],
            "code": issue["code_fix"],
            "steps": issue["steps_to_fix"]
        })
    
    recommendations = [issue["title"] for issue in validated_issues[:3]]
    
    fix_prompt = generate_master_fix_prompt(validated_issues, url)
    
    return {
        "summary": summary,
        "score": score,
        "suggested_keywords": suggested_keywords,
        "issues": validated_issues,
        "recommendations": recommendations,
        "ai_tasks": ai_tasks,
        "exact_fixes": exact_fixes,
        "fix_prompt": fix_prompt,
        "extracted_data": seo_data
    }


def generate_master_fix_prompt(issues: List[Dict], url: str) -> str:
    """Generate a comprehensive copy-paste prompt for all SEO fixes."""
    if not issues:
        return "No SEO fixes needed - your page is well optimized!"
    
    lines = [
        f"Fix these SEO issues for {url}:\n"
    ]
    
    for i, issue in enumerate(issues, 1):
        lines.append(f"## Issue {i}: {issue['title']}")
        lines.append(f"Location: {issue['location']}")
        lines.append(f"Problem: {issue['description']}")
        lines.append("")
        lines.append("Steps:")
        for step in issue.get("steps_to_fix", []):
            lines.append(f"  {step}")
        lines.append("")
        if issue.get("code_fix"):
            lines.append(f"Code: {issue['code_fix']}")
        lines.append("")
    
    lines.append("Apply all these fixes to improve search engine rankings.")
    
    return "\n".join(lines)


def generate_detailed_fallback(seo_data: Dict, issues: List[Dict], url: str) -> Dict[str, Any]:
    """Generate detailed fallback response when AI fails."""
    fallback_issues = []
    
    for issue in issues[:6]:
        issue_type = issue.get("type", "")
        msg = issue.get("message", "")
        severity = issue.get("severity", "medium")
        
        fallback_issue = {
            "title": msg[:50] if msg else "SEO Issue",
            "description": f"This issue was detected: {msg}",
            "location": get_issue_location(issue_type),
            "why_it_matters": get_why_it_matters(issue_type),
            "steps_to_fix": get_fallback_steps(issue_type),
            "code_fix": get_fallback_code_fix(issue_type, seo_data, url),
            "files_to_modify": ["index.html"],
            "prompt_to_apply_fix": f"Fix this SEO issue in my HTML: {msg}"
        }
        fallback_issues.append(fallback_issue)
    
    high_issues = sum(1 for i in issues if i.get("severity") == "high")
    medium_issues = sum(1 for i in issues if i.get("severity") == "medium")
    score = 100 - (high_issues * 15) - (medium_issues * 8)
    score = max(0, min(100, score))
    
    ai_tasks = []
    for issue in fallback_issues:
        ai_tasks.append({
            "issue": issue["title"],
            "task": issue["description"],
            "priority": "high",
            "element": issue["location"]
        })
    
    return {
        "summary": f"Found {len(fallback_issues)} SEO issues that need attention.",
        "score": score,
        "suggested_keywords": [],
        "issues": fallback_issues,
        "recommendations": [issue["title"] for issue in fallback_issues[:3]],
        "ai_tasks": ai_tasks,
        "exact_fixes": [{
            "selector": issue["location"],
            "fix": issue["title"],
            "code": issue["code_fix"],
            "steps": issue["steps_to_fix"]
        } for issue in fallback_issues],
        "fix_prompt": generate_master_fix_prompt(fallback_issues, url),
        "extracted_data": seo_data
    }


def get_issue_location(issue_type: str) -> str:
    """Get the location for a given issue type."""
    locations = {
        "missing_title": "index.html > <head>",
        "short_title": "index.html > <head> > <title>",
        "long_title": "index.html > <head> > <title>",
        "missing_meta": "index.html > <head>",
        "short_meta": "index.html > <head> > meta[name=description]",
        "long_meta": "index.html > <head> > meta[name=description]",
        "missing_h1": "index.html > <body>",
        "multiple_h1": "index.html > <body>",
        "missing_canonical": "index.html > <head>",
        "missing_og": "index.html > <head>",
        "missing_schema": "index.html > <head>",
        "missing_alt": "index.html > <img> tags",
        "missing_viewport": "index.html > <head>",
        "thin_content": "index.html > <body>",
        "missing_lang": "index.html > <html>"
    }
    return locations.get(issue_type, "index.html")


def get_why_it_matters(issue_type: str) -> str:
    """Get explanation of why this issue matters for SEO."""
    explanations = {
        "missing_title": "Google uses the title tag as the main headline in search results. Without it, your page won't rank well.",
        "short_title": "Short titles don't give Google enough information. You're missing a chance to include keywords.",
        "long_title": "Titles over 60 characters get cut off in search results. Users won't see your full message.",
        "missing_meta": "The meta description appears under your title in Google. Without it, Google picks random text from your page.",
        "short_meta": "Short descriptions don't convince users to click. You have space for 150-160 characters - use it!",
        "long_meta": "Descriptions over 160 characters get cut off. Your call-to-action might be hidden.",
        "missing_h1": "The H1 is the main headline Google looks for. It tells search engines what your page is about.",
        "multiple_h1": "Having multiple H1 tags confuses search engines about which headline is most important.",
        "missing_canonical": "Without a canonical URL, Google might index duplicate versions of your page.",
        "missing_og": "Open Graph tags control how your page looks when shared on Facebook, LinkedIn, and Twitter.",
        "missing_schema": "Schema markup helps Google show rich snippets like ratings, prices, and events in search results.",
        "missing_alt": "Alt text helps Google understand images. It's also required for accessibility.",
        "missing_viewport": "Without viewport meta, your page won't display correctly on mobile devices.",
        "thin_content": "Pages with little content rank poorly. Google prefers comprehensive, useful pages.",
        "missing_lang": "The lang attribute helps Google serve your page to users searching in that language."
    }
    return explanations.get(issue_type, "This affects your search engine ranking.")


def get_fallback_steps(issue_type: str) -> List[str]:
    """Get fallback steps for a given issue type."""
    return [
        "Step 1: Open index.html in your code editor",
        "Step 2: Find the location mentioned above",
        "Step 3: Add or modify the code as shown below",
        "Step 4: Save the file and refresh your page"
    ]


def get_fallback_code_fix(issue_type: str, data: Dict, url: str) -> str:
    """Get fallback code fix for a given issue type."""
    fixes = {
        "missing_title": '```html\n<title>Your Primary Keyword | Your Brand Name</title>\n```',
        "short_title": f'```html\n<title>{data.get("title", "Page Title")} | Your Brand - More Keywords</title>\n```',
        "missing_meta": '```html\n<meta name="description" content="Write a compelling 150-160 character description that includes your main keywords and encourages users to click through to your page.">\n```',
        "short_meta": f'```html\n<meta name="description" content="{data.get("meta_description", "")} Add more detail about your page here to reach 150-160 characters.">\n```',
        "missing_h1": '```html\n<h1>Your Main Page Heading with Primary Keyword</h1>\n```',
        "multiple_h1": '```html\n<!-- Keep only ONE h1 tag on your page -->\n<h1>Your Single Main Heading</h1>\n<!-- Change other h1 tags to h2 -->\n<h2>Secondary Heading</h2>\n```',
        "missing_canonical": f'```html\n<link rel="canonical" href="{url}">\n```',
        "missing_og": f'```html\n<meta property="og:title" content="Your Page Title">\n<meta property="og:description" content="Compelling description for social sharing">\n<meta property="og:image" content="{url}/og-image.jpg">\n<meta property="og:url" content="{url}">\n<meta property="og:type" content="website">\n```',
        "missing_schema": '```html\n<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "WebPage",\n  "name": "Your Page Title",\n  "description": "Your page description"\n}\n</script>\n```',
        "missing_alt": '```html\n<img src="your-image.jpg" alt="Descriptive text about this image including relevant keywords">\n```',
        "missing_viewport": '```html\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n```',
        "thin_content": '```html\n<!-- Add more content to your page -->\n<section>\n  <h2>Additional Section Heading</h2>\n  <p>Add 300+ words of valuable, keyword-rich content...</p>\n</section>\n```',
        "missing_lang": '```html\n<html lang="en">\n```'
    }
    return fixes.get(issue_type, '```html\n<!-- Add the missing element here -->\n```')
