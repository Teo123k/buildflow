"""
Competitor AI Module - Strategic Competitive Intelligence

Deep competitive analysis that identifies 3-5 real competitors,
extracts feature gaps, and provides actionable implementation steps.
ALWAYS returns valid JSON - never raises, never returns invalid data.
"""

import json
from typing import Dict, List, Any

from utils.ai_wrapper import safe_json_ai, extract_limited_html, DEFAULT_MODEL


def discover_competitors_ai(main_url: str, html: str) -> List[str]:
    """
    Find 3-5 real competitors based on category detection.
    ALWAYS returns a list (possibly empty).
    """
    print(f"[COMPETITOR_AI] Discovering competitors for: {main_url}")
    
    try:
        limited_html = extract_limited_html(html, limit=2000)
        
        prompt = f"""You are a competitive intelligence analyst.
Analyze this website and identify its category, then find 3-5 of its REAL top competitors.

Website: {main_url}

HTML snippet:
{limited_html[:1500]}

RULES:
1. First detect the category (e.g., portfolio, e-commerce, SaaS, blog, booking, learning platform, etc.)
2. Find 3-5 REAL competitor URLs that are:
   - In the same category
   - Well-known alternatives users would consider
   - Active and legitimate websites
3. Do NOT make up fake URLs
4. Prefer well-known competitors in the space

Respond ONLY with valid JSON. No markdown:
{{
  "category": "detected category",
  "competitors": ["https://competitor1.com", "https://competitor2.com", "https://competitor3.com"]
}}"""

        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"competitors-discover-{main_url}",
            max_tokens=300,
            temperature=0.2,
            default_response={"category": "unknown", "competitors": []}
        )
        
        if "error" in result:
            print(f"[COMPETITOR_AI] Error discovering: {result.get('error')}")
            return []
        
        competitors = result.get("competitors", [])
        if isinstance(competitors, list):
            valid = [url for url in competitors if isinstance(url, str) and url.startswith('http')]
            print(f"[COMPETITOR_AI] Found {len(valid[:5])} competitors in category: {result.get('category', 'unknown')}")
            return valid[:5]
        
        return []
        
    except Exception as e:
        print(f"[COMPETITOR_AI] Exception in discover: {e}")
        return []


def run_competitor_ai(main_html: str, main_url: str, competitor_html_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Deep strategic competitor analysis.
    ALWAYS returns valid JSON dict with feature gaps and implementation steps.
    """
    print(f"[COMPETITOR_AI] Running strategic analysis for: {main_url}")
    
    try:
        limited_main = extract_limited_html(main_html, limit=2500)
        
        comp_list = list(competitor_html_map.items())[:3]
        comp_text = ""
        for url, html in comp_list:
            snippet = extract_limited_html(html, limit=1200)
            comp_text += f"\n--- {url} ---\n{snippet[:1000]}\n"
        
        prompt = f"""You are a senior product strategist and competitive intelligence analyst.

Analyze this website against its competitors and provide strategic insights.

TARGET SITE: {main_url}
{limited_main[:2000]}

COMPETITORS:
{comp_text[:3000]}

ANALYSIS REQUIREMENTS:
1. Identify the category and market position
2. For each competitor, extract:
   - Key features the target is missing
   - UX/UI advantages
   - Content and conversion strengths
3. Identify specific feature gaps with implementation steps
4. Provide actionable business opportunities

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "summary": "One paragraph strategic assessment of competitive position",
  "category_detected": "e.g., SaaS, Portfolio, E-commerce",
  "competitors_analyzed": [
    {{
      "name": "Competitor Name",
      "url": "https://...",
      "key_features": ["specific feature 1", "specific feature 2"],
      "ux_strengths": ["specific UX advantage"],
      "what_to_copy": ["specific pattern or feature to implement"]
    }}
  ],
  "feature_gaps": [
    {{
      "title": "Missing Feature Name",
      "description": "What is missing and why it matters",
      "competitors_who_have_it": ["competitor1", "competitor2"],
      "priority": "high",
      "why_you_need_it": "Business reason",
      "steps_to_fix": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ..."
      ],
      "code_fix": "```html\\n<exact code example>\\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "AI prompt to implement this feature"
    }}
  ],
  "strengths": ["What target site does well vs competitors"],
  "weaknesses": ["Where target site falls short"],
  "business_opportunities": ["Strategic product direction ideas"],
  "final_recommendations": ["Most important changes to implement first"]
}}

Provide 2-4 feature gaps with specific implementation steps.
Focus on high-impact, actionable improvements."""

        print(f"[COMPETITOR_AI] Calling AI for strategic analysis: {main_url}")
        
        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"comp-strategic-{main_url}",
            max_tokens=2500,
            temperature=0.2,
            default_response={
                "summary": "Analysis complete",
                "category_detected": "unknown",
                "competitors_analyzed": [],
                "feature_gaps": [],
                "strengths": [],
                "weaknesses": [],
                "business_opportunities": [],
                "final_recommendations": []
            }
        )
        
        if "error" in result:
            print(f"[COMPETITOR_AI] AI error: {result.get('error')}")
            return fallback_response(main_url, list(competitor_html_map.keys()))
        
        parsed = parse_competitor_result(result, main_url, list(competitor_html_map.keys()))
        print(f"[COMPETITOR_AI] Success for: {main_url} - {len(parsed.get('feature_gaps', []))} gaps identified")
        return parsed
        
    except Exception as e:
        print(f"[COMPETITOR_AI] Exception: {e}")
        return fallback_response(main_url, list(competitor_html_map.keys()))


def parse_competitor_result(result: Dict, main_url: str, competitors: List[str]) -> Dict[str, Any]:
    """Parse AI result into structured response with feature gaps."""
    summary = result.get("summary", "Analysis complete")
    if isinstance(summary, dict):
        summary = str(summary)
    
    category = result.get("category_detected", "Unknown")
    
    def to_string_list(data, default, max_items=5):
        if not isinstance(data, list):
            return default
        return [str(item)[:200] for item in data[:max_items]]
    
    strengths = to_string_list(result.get("strengths"), ["Site is online and functional"])
    weaknesses = to_string_list(result.get("weaknesses"), ["Analysis needed"])
    business_opportunities = to_string_list(result.get("business_opportunities"), [])
    final_recommendations = to_string_list(result.get("final_recommendations"), [])
    
    competitors_analyzed = []
    for comp in result.get("competitors_analyzed", [])[:5]:
        if isinstance(comp, dict):
            competitors_analyzed.append({
                "name": str(comp.get("name", "Competitor")),
                "url": str(comp.get("url", "")),
                "key_features": to_string_list(comp.get("key_features"), []),
                "ux_strengths": to_string_list(comp.get("ux_strengths"), []),
                "what_to_copy": to_string_list(comp.get("what_to_copy"), [])
            })
    
    feature_gaps = []
    for gap in result.get("feature_gaps", [])[:6]:
        if isinstance(gap, dict):
            validated_gap = {
                "title": str(gap.get("title", gap.get("gap", "Feature Gap"))),
                "description": str(gap.get("description", "")),
                "competitors_who_have_it": to_string_list(gap.get("competitors_who_have_it"), []),
                "priority": str(gap.get("priority", "medium")),
                "why_you_need_it": str(gap.get("why_you_need_it", "")),
                "steps_to_fix": gap.get("steps_to_fix", gap.get("how_to_add_it", [])),
                "code_fix": str(gap.get("code_fix", gap.get("code_patch", ""))),
                "files_to_modify": gap.get("files_to_modify", ["index.html"]),
                "prompt_to_apply_fix": str(gap.get("prompt_to_apply_fix", ""))
            }
            
            if not isinstance(validated_gap["steps_to_fix"], list):
                validated_gap["steps_to_fix"] = [str(validated_gap["steps_to_fix"])]
            if not isinstance(validated_gap["files_to_modify"], list):
                validated_gap["files_to_modify"] = [str(validated_gap["files_to_modify"])]
            
            feature_gaps.append(validated_gap)
    
    ai_tasks = []
    for gap in feature_gaps[:4]:
        ai_tasks.append({
            "issue": gap["title"],
            "task": gap["description"] or gap["why_you_need_it"],
            "priority": gap["priority"],
            "element": ", ".join(gap["competitors_who_have_it"][:2]) if gap["competitors_who_have_it"] else ""
        })
    
    improvements = final_recommendations[:3] if final_recommendations else [gap["title"] for gap in feature_gaps[:3]]
    
    fix_prompt = generate_fix_prompt(feature_gaps, main_url)
    
    return {
        "summary": str(summary),
        "category_detected": str(category),
        "competitors_analyzed": competitors_analyzed,
        "feature_gaps": feature_gaps,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvements": improvements,
        "business_opportunities": business_opportunities,
        "final_recommendations": final_recommendations,
        "ai_tasks": ai_tasks,
        "fix_prompt": fix_prompt
    }


def generate_fix_prompt(feature_gaps: List[Dict], url: str) -> str:
    """Generate comprehensive fix prompt for all feature gaps."""
    if not feature_gaps:
        return "No feature gaps identified - your site is competitive!"
    
    lines = [
        f"Implement these competitive improvements for {url}:\n"
    ]
    
    for i, gap in enumerate(feature_gaps[:4], 1):
        lines.append(f"## Gap {i}: {gap['title']}")
        if gap.get("description"):
            lines.append(f"Problem: {gap['description']}")
        if gap.get("why_you_need_it"):
            lines.append(f"Why: {gap['why_you_need_it']}")
        if gap.get("competitors_who_have_it"):
            lines.append(f"Competitors with this: {', '.join(gap['competitors_who_have_it'][:3])}")
        lines.append("")
        
        if gap.get("steps_to_fix"):
            lines.append("Steps:")
            for step in gap["steps_to_fix"]:
                lines.append(f"  {step}")
            lines.append("")
        
        if gap.get("code_fix"):
            lines.append(f"Code: {gap['code_fix']}")
        lines.append("")
    
    lines.append("Apply these changes to match or exceed your competitors.")
    
    return "\n".join(lines)


def fallback_response(main_url: str, competitors: List[str]) -> Dict[str, Any]:
    """Fallback when AI fails."""
    return {
        "summary": "Could not complete competitive analysis. Please try again.",
        "category_detected": "Unknown",
        "competitors_analyzed": [],
        "feature_gaps": [],
        "strengths": ["Your site is online and accessible"],
        "weaknesses": ["Full analysis unavailable"],
        "improvements": ["Retry the competitive analysis"],
        "business_opportunities": [],
        "final_recommendations": ["Run analysis again for insights"],
        "ai_tasks": [{
            "issue": "Analysis incomplete",
            "task": "Try running competitor analysis again",
            "priority": "medium",
            "element": ""
        }],
        "fix_prompt": "Competitive analysis needs to be retried for actionable insights."
    }
