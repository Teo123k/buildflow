"""
Competitor AI Placeholder Module
Provides structure for competitor comparison without AI calls.
Will be enhanced with OpenAI integration later.
"""

from typing import Dict, List, Any


def run_competitor_ai_placeholder(main_html: str, main_url: str, competitors: List[str]) -> Dict[str, Any]:
    """
    Placeholder function for competitor analysis.
    Returns structured data without making any AI calls.
    
    Args:
        main_html: HTML content of the main website
        main_url: URL of the main website being analyzed
        competitors: List of competitor URLs to compare against
    
    Returns:
        Dict with placeholder comparison data
    """
    return {
        "summary": "Competitor comparison placeholder. AI analysis will be added in a future update to provide detailed competitive insights.",
        "main_url": main_url,
        "competitors": [
            {
                "url": comp_url,
                "status": "placeholder",
                "what_they_do_well": [
                    "Placeholder: Strong visual design",
                    "Placeholder: Clear call-to-action buttons"
                ],
                "what_they_do_poorly": [
                    "Placeholder: Slow page load times",
                    "Placeholder: Complex navigation structure"
                ],
                "lessons_to_use": [
                    "Placeholder: Consider similar hero section layout",
                    "Placeholder: Adopt their pricing table format"
                ]
            }
            for comp_url in competitors
        ],
        "ai_tasks": [
            {
                "issue": "Placeholder: Competitive feature gap identified",
                "task": "Placeholder: Implement feature parity with competitors",
                "priority": "medium"
            },
            {
                "issue": "Placeholder: Design element missing",
                "task": "Placeholder: Add trust indicators like competitors",
                "priority": "low"
            }
        ],
        "exact_fixes": [
            {
                "selector": "<header>",
                "fix": "Placeholder: Add trust badges similar to competitors",
                "code": "<!-- Trust badges section -->\n<div class=\"trust-badges\">\n  <img src=\"badge1.png\" alt=\"Trusted\">\n</div>"
            },
            {
                "selector": "<section class=\"cta\">",
                "fix": "Placeholder: Improve CTA visibility",
                "code": "<button class=\"cta-button primary\">Get Started Free</button>"
            }
        ],
        "fix_prompt": """COMPETITOR ANALYSIS IMPROVEMENTS:

SUMMARY:
This is a placeholder competitive analysis. Enable AI to get real insights.

WHAT COMPETITORS DO WELL:
1. [Placeholder] Strong visual hierarchy
2. [Placeholder] Clear value propositions

RECOMMENDED IMPROVEMENTS:
1. [Placeholder] Add social proof elements
2. [Placeholder] Improve above-the-fold content

EXACT FIXES TO APPLY:
1. Add trust badges to header
2. Enhance CTA button styling

Note: Run with AI enabled to get personalized competitive insights."""
    }
