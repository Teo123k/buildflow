"""
Prompt Generation Module

Will later generate simple copy-paste prompts to fix issues in Replit.

This module will be responsible for:
- Taking analysis results from other modules
- Converting issues into clear, actionable fix instructions
- Generating copy-paste prompts for Replit AI
- Formatting prompts for easy user consumption
- Prioritising fixes by severity and impact
"""

from utils.ai_wrapper import smart_ai, CHEAP_MODEL


def improve_task_with_ai(issue: str, base_task: str) -> dict:
    """
    Enhance a task with AI-generated explanation and improved prompt.
    
    Uses CHEAP_MODEL for this lighter mechanical task.
    
    Args:
        issue: The detected issue string (e.g., "missing title")
        base_task: The rule-based task description
        
    Returns:
        Dictionary with:
        - explanation: Why this issue matters
        - ai_prompt: Improved copy-paste prompt for fixing
        
        Falls back to basic structure if AI call fails.
    """
    result = {
        "explanation": "",
        "ai_prompt": ""
    }
    
    try:
        prompt = f"""You are a website improvement assistant. Given an issue and a basic task, provide:
1. A brief explanation (1-2 sentences) of why this issue matters for the website
2. A simple, clear prompt that a developer can copy-paste to fix it

Keep both responses short and avoid code blocks. Use plain English.

Issue: {issue}
Basic task: {base_task}

Respond in this exact format:
EXPLANATION: [brief explanation]
PROMPT: [copy-paste prompt]"""
        
        response_text = smart_ai(
            prompt,
            model=CHEAP_MODEL,
            cache_key=f"improve-task-{issue[:50]}",
            max_tokens=200,
            temperature=0.2
        )
        
        if "EXPLANATION:" in response_text and "PROMPT:" in response_text:
            parts = response_text.split("PROMPT:")
            explanation_part = parts[0].replace("EXPLANATION:", "").strip()
            prompt_part = parts[1].strip() if len(parts) > 1 else ""
            
            result["explanation"] = explanation_part[:200]
            result["ai_prompt"] = prompt_part[:300]
        else:
            result["explanation"] = base_task
            result["ai_prompt"] = base_task
            
    except Exception as e:
        result["explanation"] = base_task
        result["ai_prompt"] = base_task
    
    return result


def format_issue_for_prompt(issue: dict) -> str:
    """
    Format a single issue into a clear description for a prompt.
    
    Args:
        issue: Issue dictionary from analysis
        
    Returns:
        Formatted issue description
    """
    pass


def generate_fix_prompt(issue: dict) -> str:
    """
    Generate a copy-paste prompt to fix a specific issue.
    
    Args:
        issue: Issue dictionary from analysis
        
    Returns:
        Ready-to-use fix prompt for Replit
    """
    pass


def prioritise_issues(issues: list) -> list:
    """
    Sort issues by severity and impact.
    
    Args:
        issues: List of issues from analysis
        
    Returns:
        Sorted list of issues (highest priority first)
    """
    pass


def group_related_issues(issues: list) -> dict:
    """
    Group related issues together for batch fixing.
    
    Args:
        issues: List of issues
        
    Returns:
        Dictionary of grouped issues
    """
    pass


def generate_step_by_step_guide(issues: list) -> list:
    """
    Generate a step-by-step guide to fix all issues.
    
    Args:
        issues: List of prioritised issues
        
    Returns:
        List of steps with prompts
    """
    pass


def generate_all_prompts(analysis_results: dict) -> dict:
    """
    Main entry point for prompt generation.
    
    Takes complete analysis results and generates:
    1. Prioritised list of issues
    2. Individual fix prompts for each issue
    3. Step-by-step fixing guide
    4. Grouped prompts for related issues
    
    Args:
        analysis_results: Complete analysis from all modules
        
    Returns:
        Dictionary containing all generated prompts
    """
    pass
