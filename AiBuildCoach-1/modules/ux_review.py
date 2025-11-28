"""
UX Review Module - AI-Enhanced UX Evaluation

Detailed, specific, actionable UX analysis with exact file locations,
step-by-step fixes, and code patches. Simple enough for a 12-year-old.
ALWAYS returns valid JSON.
"""

import re
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from utils.ai_wrapper import safe_json_ai, extract_limited_html, DEFAULT_MODEL


def run_ux_review(html: str) -> Dict[str, List[Dict[str, Any]]]:
    """Run rule-based UX review."""
    soup = BeautifulSoup(html, 'html.parser')
    
    return {
        "readability_issues": check_readability(soup, html),
        "layout_issues": check_layout(soup, html),
        "mobile_issues": check_mobile(soup, html),
        "accessibility_issues": check_accessibility(soup)
    }


def check_readability(soup: BeautifulSoup, html: str) -> List[Dict[str, Any]]:
    """Check readability issues."""
    issues = []
    
    small_font_pattern = re.compile(r'font-size:\s*(\d+)(px|pt)', re.IGNORECASE)
    for match in small_font_pattern.finditer(html):
        size = int(match.group(1))
        unit = match.group(2).lower()
        if unit == 'px' and size < 14:
            issues.append({
                "type": "small_font",
                "severity": "medium",
                "message": f"Text is too small ({size}px)",
                "element": "font-size CSS"
            })
            break
    
    paragraphs = soup.find_all('p')
    for i, p in enumerate(paragraphs[:5]):
        text = p.get_text(strip=True)
        if len(text) > 300:
            issues.append({
                "type": "text_wall",
                "severity": "low",
                "message": "Very long paragraph found",
                "element": f"Paragraph {i + 1}"
            })
            break
    
    return issues


def check_layout(soup: BeautifulSoup, html: str) -> List[Dict[str, Any]]:
    """Check layout issues."""
    issues = []
    
    if 'margin: 0' in html and 'padding: 0' in html:
        issues.append({
            "type": "missing_spacing",
            "severity": "medium",
            "message": "No spacing between elements",
            "element": "CSS layout"
        })
    
    return issues


def check_mobile(soup: BeautifulSoup, html: str) -> List[Dict[str, Any]]:
    """Check mobile responsiveness."""
    issues = []
    
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport:
        issues.append({
            "type": "missing_viewport",
            "severity": "high",
            "message": "Missing viewport meta tag",
            "element": "<head>"
        })
    
    fixed_widths = re.findall(r'width:\s*(\d{4,})px', html)
    if fixed_widths:
        issues.append({
            "type": "fixed_width",
            "severity": "medium",
            "message": "Fixed pixel widths may break on mobile",
            "element": "CSS width"
        })
    
    return issues


def check_accessibility(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Check accessibility issues."""
    issues = []
    
    images = soup.find_all('img')
    missing_alt = 0
    for img in images[:10]:
        alt = img.get('alt', '')
        if not alt or alt.strip() == '':
            missing_alt += 1
    
    if missing_alt > 0:
        issues.append({
            "type": "missing_alt",
            "severity": "high",
            "message": f"{missing_alt} images missing alt text",
            "element": "<img> tags"
        })
    
    buttons = soup.find_all('button')
    for i, btn in enumerate(buttons[:5]):
        text = btn.get_text(strip=True)
        aria = btn.get('aria-label', '')
        if not text and not aria:
            issues.append({
                "type": "empty_button",
                "severity": "high",
                "message": "Button has no text or label",
                "element": f"Button {i + 1}"
            })
            break
    
    return issues


def get_issue_summary(results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate issue summary."""
    total = sum(len(issues) for issues in results.values())
    by_severity = {"high": 0, "medium": 0, "low": 0}
    
    for issues in results.values():
        for issue in issues:
            severity = issue.get("severity", "medium")
            by_severity[severity] = by_severity.get(severity, 0) + 1
    
    return {
        "total_issues": total,
        "by_severity": by_severity,
        "needs_attention": by_severity["high"] > 0
    }


def run_ux_review_ai(html: str, url: str = "") -> Dict[str, Any]:
    """
    Run AI-enhanced UX review with detailed, actionable feedback.
    ALWAYS returns valid JSON - never raises, never returns invalid data.
    
    Returns specific file locations, step-by-step fixes, and exact code patches.
    """
    print(f"[UX_REVIEW] Starting detailed UX analysis for: {url}")
    
    try:
        rule_based_issues = run_ux_review(html)
        
        all_issues = []
        for category, issues in rule_based_issues.items():
            for issue in issues:
                all_issues.append({
                    "category": category.replace("_issues", ""),
                    "message": issue["message"],
                    "element": issue.get("element", ""),
                    "severity": issue.get("severity", "medium")
                })
        
        limited_html = extract_limited_html(html, limit=4000)
        
        issues_context = ""
        if all_issues:
            issues_context = "Rule-based issues detected:\n" + "\n".join([
                f"- {i['message']} (in {i['element']})" for i in all_issues[:8]
            ])
        
        prompt = f"""You are a senior UX/UI designer and front-end engineer.
Your job is to deeply analyze the website HTML and generate specific, detailed, actionable UX improvements.

STRICT RULES:
- NEVER be vague.
- ALWAYS give exact steps.
- ALWAYS include exact code fixes.
- ALWAYS include exact file + location (e.g., "index.html > .hero-title", "style.css > .btn-primary")
- ALWAYS explain like teaching a 12-year-old.
- ALWAYS output only valid JSON.

Website URL: {url}

{issues_context}

HTML to analyze:
```html
{limited_html}
```

Analyze:
1. Visual hierarchy - Are important things big and obvious?
2. Spacing - Is there enough room between things?
3. Color contrast - Can you read everything easily?
4. Section layout - Does the page flow logically?
5. Typography - Are fonts readable and consistent?
6. Button clarity - Are buttons obvious and clickable?
7. Mobile responsiveness - Will it work on phones?
8. Interaction feedback - Do buttons show when clicked?

Respond ONLY with this exact JSON structure (no markdown, no explanation):
{{
  "summary": "Short 1-2 sentence explanation of the main UX problems found.",
  "issues": [
    {{
      "title": "Short issue title (5-7 words max)",
      "description": "What is wrong in plain English. Be specific about what you see.",
      "location": "Exact file and element path (e.g., index.html > section.hero > h1.title)",
      "why_it_matters": "Simple, clear reason why this hurts the user experience.",
      "steps_to_fix": [
        "Step 1: Open the file...",
        "Step 2: Find the element...",
        "Step 3: Change the value..."
      ],
      "code_fix": "```html\\n<exact code to copy-paste>\\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "A ready-to-use prompt for an AI assistant to apply this exact fix."
    }}
  ]
}}

Return 3-6 issues maximum. Focus on the most impactful problems first.
If the page looks good, return fewer issues.
Every issue MUST have a specific code_fix with working code."""

        print(f"[UX_REVIEW] Calling AI for detailed analysis: {url}")
        
        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"ux-detailed-{url}",
            max_tokens=2000,
            temperature=0.2,
            default_response={"summary": "Analysis complete", "issues": []}
        )
        
        if "error" in result:
            print(f"[UX_REVIEW] AI error: {result.get('error')}")
            return generate_detailed_fallback(all_issues, url)
        
        summary = result.get("summary", "UX analysis complete.")
        if isinstance(summary, dict):
            summary = summary.get("text", str(summary))
        
        issues = result.get("issues", [])
        validated_issues = []
        
        for issue in issues[:6]:
            if isinstance(issue, dict):
                validated_issue = {
                    "title": str(issue.get("title", "UX Issue")),
                    "description": str(issue.get("description", "")),
                    "location": str(issue.get("location", "index.html")),
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
        
        fix_prompt = generate_master_fix_prompt(validated_issues, url)
        
        print(f"[UX_REVIEW] Success for: {url} - {len(validated_issues)} detailed issues")
        
        return {
            "summary": str(summary),
            "issues": validated_issues,
            "recommendations": [issue["title"] for issue in validated_issues[:3]],
            "ai_tasks": ai_tasks,
            "exact_fixes": exact_fixes,
            "fix_prompt": fix_prompt
        }
        
    except Exception as e:
        print(f"[UX_REVIEW] Exception: {e}")
        return {
            "summary": "UX analysis encountered an error.",
            "issues": [],
            "recommendations": [],
            "ai_tasks": [],
            "exact_fixes": [],
            "fix_prompt": "Please try again.",
            "error": str(e)[:100]
        }


def generate_master_fix_prompt(issues: List[Dict], url: str) -> str:
    """Generate a comprehensive copy-paste prompt for all fixes."""
    if not issues:
        return "No fixes needed - your UX looks good!"
    
    lines = [
        f"Fix these UX issues for {url}:\n"
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
    
    lines.append("Apply all these fixes to improve the user experience.")
    
    return "\n".join(lines)


def generate_detailed_fallback(issues: List[Dict], url: str) -> Dict[str, Any]:
    """Generate detailed fallback response when AI fails."""
    fallback_issues = []
    
    for issue in issues[:5]:
        msg = issue.get("message", "")
        element = issue.get("element", "")
        
        fallback_issue = {
            "title": msg[:50] if msg else "UX Issue",
            "description": f"This issue was detected: {msg}",
            "location": f"index.html > {element}" if element else "index.html",
            "why_it_matters": "This affects how users experience your website.",
            "steps_to_fix": [
                "Step 1: Open the file mentioned in location",
                "Step 2: Find the element or CSS property",
                "Step 3: Apply the code fix below"
            ],
            "code_fix": get_fallback_code_fix(msg),
            "files_to_modify": ["index.html", "style.css"],
            "prompt_to_apply_fix": f"Fix this UX issue: {msg}"
        }
        fallback_issues.append(fallback_issue)
    
    ai_tasks = []
    for issue in fallback_issues:
        ai_tasks.append({
            "issue": issue["title"],
            "task": issue["description"],
            "priority": "medium",
            "element": issue["location"]
        })
    
    return {
        "summary": f"Found {len(fallback_issues)} UX issues that need attention.",
        "issues": fallback_issues,
        "recommendations": [issue["title"] for issue in fallback_issues[:3]],
        "ai_tasks": ai_tasks,
        "exact_fixes": [{
            "selector": issue["location"],
            "fix": issue["title"],
            "code": issue["code_fix"],
            "steps": issue["steps_to_fix"]
        } for issue in fallback_issues],
        "fix_prompt": generate_master_fix_prompt(fallback_issues, url)
    }


def get_fallback_code_fix(message: str) -> str:
    """Get fallback code fix based on issue message."""
    msg_lower = message.lower()
    
    if "viewport" in msg_lower:
        return '```html\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n```'
    elif "alt" in msg_lower:
        return '```html\n<img src="your-image.jpg" alt="Descriptive text about this image">\n```'
    elif "small" in msg_lower or "font" in msg_lower:
        return '```css\nbody {\n  font-size: 16px;\n  line-height: 1.6;\n}\n```'
    elif "button" in msg_lower:
        return '```html\n<button type="button" aria-label="Click to submit">Submit</button>\n```'
    elif "spacing" in msg_lower:
        return '```css\n.container {\n  padding: 20px;\n  margin: 0 auto;\n  gap: 16px;\n}\n```'
    elif "width" in msg_lower or "mobile" in msg_lower:
        return '```css\n.container {\n  width: 100%;\n  max-width: 1200px;\n}\n```'
    else:
        return '```css\n/* Review and update this element */\n```'
