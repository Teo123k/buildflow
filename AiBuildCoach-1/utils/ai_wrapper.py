"""
AI Wrapper Module - Unified AI Orchestration

Provides:
- smart_ai(): Unified AI call with caching, retries, and JSON normalization
- safe_json_ai(): AI call that ALWAYS returns valid JSON
- extract_limited_html(): Token-efficient HTML extraction

Model Configuration:
- DEFAULT_MODEL: Advanced model for thinking-heavy tasks (UX, SEO, Planner, Workflow)
- CHEAP_MODEL: Cost-efficient model for simple/mechanical tasks
"""

from openai import OpenAI
import os
import json
import time
import re

DEFAULT_MODEL = "gpt-4.1"
CHEAP_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_ai_cache = {}


def smart_ai(prompt: str, model: str = None, cache_key: str = None, max_retry: int = 3, temperature: float = 0.2, max_tokens: int = 2000) -> str:
    """
    A unified AI wrapper to:
    - Cache repeated prompts
    - Retry on failure
    - Ensure valid JSON output
    - Reduce tokens via normalization
    
    Args:
        prompt: The prompt to send to the AI
        model: OpenAI model to use (default: DEFAULT_MODEL for advanced reasoning)
        cache_key: Optional cache key (defaults to first 200 chars of prompt)
        max_retry: Number of retry attempts on failure
        temperature: AI temperature setting (low for accuracy)
        max_tokens: Maximum tokens in response
        
    Returns:
        AI response string (cleaned of markdown code blocks)
    """
    use_model = model or DEFAULT_MODEL
    key = cache_key or prompt.strip()[:200]

    if key in _ai_cache:
        return _ai_cache[key]

    for attempt in range(max_retry):
        try:
            response = client.chat.completions.create(
                model=use_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            output = response.choices[0].message.content
            output = output.strip()

            if output.startswith("```"):
                lines = output.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                output = "\n".join(lines).strip()

            _ai_cache[key] = output
            return output

        except Exception as e:
            print(f"[AI_WRAPPER] Error attempt {attempt + 1} ({use_model}): {e}")
            time.sleep(1)

    return json.dumps({"error": "AI failed after retries"})


def clean_ai_json(ai_response: str) -> dict:
    """
    Clean AI response and extract valid JSON.
    
    Handles:
    - ```json code fences
    - Text before/after JSON
    - Invalid formatting
    - Truncated JSON (attempts to fix)
    
    Args:
        ai_response: Raw AI response string
        
    Returns:
        Parsed JSON dict
        
    Raises:
        Exception if JSON cannot be extracted/parsed
    """
    cleaned = ai_response.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fixed = fix_truncated_json(cleaned)
        return json.loads(fixed)


def fix_truncated_json(json_str: str) -> str:
    """
    Attempt to fix truncated JSON by closing open brackets and braces.
    """
    json_str = json_str.rstrip()
    
    if json_str.endswith(','):
        json_str = json_str[:-1]
    
    if json_str.endswith('"'):
        pass
    elif '"' in json_str:
        last_quote = json_str.rfind('"')
        second_last_quote = json_str.rfind('"', 0, last_quote)
        if second_last_quote != -1:
            between = json_str[second_last_quote+1:last_quote]
            if ':' in json_str[last_quote:]:
                json_str = json_str[:last_quote+1] + '""'
    
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    
    if json_str.rstrip().endswith(','):
        json_str = json_str.rstrip()[:-1]
    
    json_str += ']' * open_brackets
    json_str += '}' * open_braces
    
    return json_str


def safe_json_ai(prompt: str, model: str = None, cache_key: str = None, max_tokens: int = 1000, temperature: float = 0.2, default_response: dict = None) -> dict:
    """
    AI call that ALWAYS returns a valid JSON dict.
    
    If AI returns invalid JSON, returns:
    {"error": "AI returned invalid JSON", "raw": <raw_output>}
    
    Args:
        prompt: The prompt to send to AI (should request JSON output)
        model: OpenAI model to use (default: DEFAULT_MODEL)
        cache_key: Cache key for response caching
        max_tokens: Max tokens in response
        temperature: AI temperature
        default_response: Fallback dict if all else fails
        
    Returns:
        Always returns a valid dict (never raises, never returns non-dict)
    """
    if default_response is None:
        default_response = {"error": "AI unavailable", "raw": ""}
    
    try:
        raw_output = smart_ai(
            prompt,
            model=model,
            cache_key=cache_key,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not raw_output or not raw_output.strip():
            print(f"[AI_WRAPPER] Empty response for cache_key={cache_key}")
            return {"error": "AI returned empty response", "raw": ""}
        
        try:
            parsed = clean_ai_json(raw_output)
            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, list):
                return {"data": parsed, "raw": raw_output}
            else:
                return {"data": parsed, "raw": raw_output}
        except Exception as je:
            print(f"[AI_WRAPPER] JSON parse error for cache_key={cache_key}: {je}")
            print(f"[AI_WRAPPER] Raw output (first 500 chars): {raw_output[:500]}")
            return {
                "error": f"Invalid JSON from AI: {str(je)[:100]}",
                "raw": raw_output[:2000]
            }
            
    except Exception as e:
        print(f"[AI_WRAPPER] Exception in safe_json_ai: {e}")
        return {
            "error": f"AI call failed: {str(e)[:100]}",
            "raw": ""
        }


def validate_json_response(response: str, required_keys: list = None) -> tuple:
    """
    Validate that a response is valid JSON and optionally has required keys.
    
    Returns:
        (is_valid: bool, parsed_or_error: dict)
    """
    try:
        parsed = json.loads(response)
        if not isinstance(parsed, dict):
            return False, {"error": "Response is not a JSON object", "raw": response[:1000]}
        
        if required_keys:
            missing = [k for k in required_keys if k not in parsed]
            if missing:
                return False, {"error": f"Missing required keys: {missing}", "raw": response[:1000]}
        
        return True, parsed
    except json.JSONDecodeError as e:
        return False, {"error": f"Invalid JSON: {str(e)}", "raw": response[:1000]}


def extract_limited_html(html: str, limit: int = 8000) -> str:
    """
    Keeps HTML short enough to avoid token waste.
    Removes script tags, style blocks, large JSON blobs, comments.
    
    Args:
        html: Raw HTML string
        limit: Maximum character limit (default: 8000)
        
    Returns:
        Cleaned and truncated HTML
    """
    if not html:
        return ""
    
    clean = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<style.*?>.*?</style>", "", clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
    clean = re.sub(r"<noscript.*?>.*?</noscript>", "", clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'\s+', ' ', clean)
    clean = re.sub(r'data-[a-z-]+="[^"]*"', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\{[^}]{500,}\}', '{}', clean)
    
    return clean[:limit]


def clear_cache():
    """Clear the AI response cache."""
    global _ai_cache
    _ai_cache = {}


def get_cache_stats():
    """Get cache statistics."""
    return {
        "cached_prompts": len(_ai_cache),
        "cache_keys": list(_ai_cache.keys())[:10]
    }
