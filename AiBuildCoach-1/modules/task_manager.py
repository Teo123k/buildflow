"""
Task Manager Module

Converts analysis issues and auto-test results into trackable tasks.

This module will be responsible for:
- Converting analysis issues into trackable tasks
- Converting auto-test results into actionable tasks
- Organising tasks into logical modules/categories
- Managing task status (pending, in-progress, completed)
- Providing checklist functionality
- Tracking user progress
"""

from modules.generate_prompts import improve_task_with_ai


def generate_tasks(basic_issues: list) -> list:
    """
    Convert basic issues into actionable task items.
    
    Uses rule-based mappings to create tasks from issues detected during
    basic HTML structure analysis.
    
    Args:
        basic_issues: List of issue strings from analyze_basic_structure()
        
    Returns:
        List of task dictionaries with issue, task, prompt, and done status
    """
    issue_mappings = {
        "missing title": {
            "task": "Add a title tag to the page.",
            "prompt": "Add a <title>Your Page Title</title> tag inside the <head> section. Make it descriptive and under 60 characters."
        },
        "missing meta description": {
            "task": "Add a meta description tag.",
            "prompt": "Add a <meta name='description' content='Brief description of your page'> tag inside the <head> section. Keep it under 160 characters."
        },
        "no H1 tags": {
            "task": "Add a main heading (H1) to the page.",
            "prompt": "Add one clear <h1> tag that describes the main topic of the page. This should be unique and meaningful."
        },
        "multiple H1 tags": {
            "task": "Use only one H1 tag per page.",
            "prompt": "Review your page and keep only one <h1> tag. The other heading levels should be <h2>, <h3>, etc. H1 should be for the main page title only."
        },
        "empty body": {
            "task": "Add meaningful content to the page body.",
            "prompt": "Add content inside the <body> tag. The page appears empty or has no visible text content."
        }
    }
    
    tasks = []
    
    for issue in basic_issues:
        if issue in issue_mappings:
            mapping = issue_mappings[issue]
            base_task = mapping["task"]
            base_prompt = mapping["prompt"]
        else:
            base_task = f"Fix: {issue}"
            base_prompt = f"Address the following issue: {issue}"
        
        ai_enhanced = improve_task_with_ai(issue, base_task)
        
        task = {
            "issue": issue,
            "task": base_task,
            "prompt": base_prompt,
            "ai_explanation": ai_enhanced["explanation"],
            "ai_prompt": ai_enhanced["ai_prompt"],
            "done": False
        }
        tasks.append(task)
    
    return tasks


def create_task(issue: dict, category: str) -> dict:
    """
    Create a task from an analysis issue.
    
    Args:
        issue: Issue dictionary from analysis
        category: Category/module for this task
        
    Returns:
        Task dictionary with id, description, status, etc.
    """
    pass


def organise_into_modules(tasks: list) -> dict:
    """
    Organise tasks into logical modules/categories.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        Dictionary of modules with their tasks
    """
    pass


def update_task_status(task_id: str, new_status: str) -> dict:
    """
    Update the status of a specific task.
    
    Args:
        task_id: ID of the task to update
        new_status: New status (pending, in-progress, completed)
        
    Returns:
        Updated task dictionary
    """
    pass


def get_checklist(module_name: str = None) -> list:
    """
    Get checklist of tasks, optionally filtered by module.
    
    Args:
        module_name: Optional module name to filter by
        
    Returns:
        List of tasks as checklist items
    """
    pass


def calculate_progress(tasks: list) -> dict:
    """
    Calculate overall progress and per-module progress.
    
    Args:
        tasks: List of all tasks
        
    Returns:
        Progress statistics
    """
    pass


def generate_progress_report(tasks: list) -> dict:
    """
    Generate a comprehensive progress report.
    
    Args:
        tasks: List of all tasks
        
    Returns:
        Progress report with statistics and summaries
    """
    pass


def generate_tasks_from_autotest(autotest_results: dict) -> list:
    """
    Convert auto-test findings into actionable tasks.
    
    Reads all issues from auto-test results including:
    - Broken links (4xx, 5xx status codes)
    - JavaScript console errors
    - Missing/broken images
    - Interaction errors (failed button/link clicks)
    - Performance issues (slow load times, large files)
    
    Transforms each issue into a task with issue description, task, and prompt.
    
    Args:
        autotest_results: Complete auto-test results from run_basic_autotest()
        
    Returns:
        List of task dictionaries with issue, task, prompt, and done status
    """
    tasks = []
    
    # Extract data from autotest results
    page_info = autotest_results.get("page", {})
    link_results = autotest_results.get("link_results", [])
    interactions = autotest_results.get("interactions", {})
    performance = autotest_results.get("performance", {})
    
    # Task 1: Broken links
    broken_links = [l for l in link_results if l.get("status_code", 0) >= 400]
    for link in broken_links:
        status = link.get("status_code", "unknown")
        url = link.get("url", "")
        
        task = {
            "issue": f"Broken link: {url} → {status}",
            "task": f"Fix or remove the broken link to {url}.",
            "prompt": f"This link returns a {status} error. Either fix the target URL or remove the link if it's no longer needed.",
            "ai_explanation": "",
            "ai_prompt": "",
            "done": False
        }
        tasks.append(task)
    
    # Task 2: JS Console Errors
    js_errors = page_info.get("console_errors", [])
    if js_errors:
        for idx, error in enumerate(js_errors[:5]):  # Limit to first 5
            task = {
                "issue": f"JavaScript error: {error[:60]}",
                "task": "Fix the JavaScript error found in the browser console.",
                "prompt": f"Console error: {error}. Check your JavaScript code for this error and fix it.",
                "ai_explanation": "",
                "ai_prompt": "",
                "done": False
            }
            tasks.append(task)
    
    # Task 3: Missing Images
    missing_images = page_info.get("missing_images", [])
    if missing_images:
        task = {
            "issue": f"Missing {len(missing_images)} image(s)",
            "task": "Fix broken image links.",
            "prompt": f"The following images failed to load: {', '.join([img[:50] for img in missing_images[:3]])}. Check the image paths and fix the URLs.",
            "ai_explanation": "",
            "ai_prompt": "",
            "done": False
        }
        tasks.append(task)
    
    # Task 4: Interaction Errors
    interaction_errors = interactions.get("interaction_errors", [])
    for error in interaction_errors:
        task = {
            "issue": f"Interaction failed: {error[:60]}",
            "task": "Fix interactive element issues.",
            "prompt": f"An interactive element failed to respond: {error}. Test your buttons and forms.",
            "ai_explanation": "",
            "ai_prompt": "",
            "done": False
        }
        tasks.append(task)
    
    # Task 5: Performance Issues
    load_time = performance.get("load_time_ms", 0)
    if load_time and load_time > 3000:
        task = {
            "issue": f"Slow page load: {round(load_time)}ms",
            "task": "Optimize page load performance.",
            "prompt": f"Page takes {round(load_time)}ms to load. Consider optimizing images, minifying CSS/JS, or using a CDN.",
            "ai_explanation": "",
            "ai_prompt": "",
            "done": False
        }
        tasks.append(task)
    
    # Task 6: Large Files
    large_files = performance.get("large_files", [])
    if large_files:
        task = {
            "issue": f"Found {len(large_files)} large file(s)",
            "task": "Optimize or remove large assets.",
            "prompt": f"The following files are large: {', '.join(large_files[:2])}. Consider compressing images or splitting large files.",
            "ai_explanation": "",
            "ai_prompt": "",
            "done": False
        }
        tasks.append(task)
    
    return tasks


def create_task_list(analysis_results: dict) -> dict:
    """
    Main entry point for task management.
    
    Takes complete analysis results and creates:
    1. Individual tasks from each issue
    2. Organised modules with tasks
    3. Initial checklist
    4. Progress tracking structure
    
    Args:
        analysis_results: Complete analysis from all modules
        
    Returns:
        Complete task management structure
    """
    pass
