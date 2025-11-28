"""
Guided Workflow Module - Expert + Child-Friendly System

Converts blueprint into actionable steps with:
- Phase-based organization (A-G)
- Child-friendly explanations (12-year-old level)
- Validation checks
- Progress tracking per phase
- Cost-efficient Replit prompts

ALWAYS returns valid JSON.
"""

import json
from typing import Dict, Any, List
from modules.build_planner import generate_build_prompt, generate_fix_prompt


def create_workflow(blueprint: Dict[str, Any], idea: str = "") -> Dict[str, Any]:
    """
    Convert a blueprint into a guided workflow with phases.
    
    Args:
        blueprint: Output from build_planner.generate_blueprint()
        idea: Original app idea for context
        
    Returns:
        Workflow with phases, steps, progress tracking, validation
    """
    print(f"[GUIDED_WORKFLOW] Creating phase-based workflow from blueprint")
    
    try:
        if not blueprint:
            return {
                "success": False,
                "error": "No building plan provided",
                "workflow": None
            }
        
        steps = blueprint.get("build_steps", [])
        
        if not steps:
            steps = generate_fallback_steps(idea, blueprint)
        
        for i, step in enumerate(steps):
            step["order"] = i + 1
            if "status" not in step:
                step["status"] = "pending"
            if "id" not in step:
                step["id"] = i + 1
            if "priority" not in step:
                step["priority"] = area_to_priority(step.get("area", "feature"))
            if "category" not in step:
                step["category"] = step.get("area", "feature")
        
        phases = blueprint.get("phases", [])
        if not phases:
            phases = generate_phases_from_steps(steps)
        
        phase_progress = calculate_phase_progress(phases, steps)
        
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.get("status") == "completed")
        progress_percent = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0
        
        grouped = {
            "A": [s for s in steps if s.get("priority") == "A"],
            "B": [s for s in steps if s.get("priority") == "B"],
            "C": [s for s in steps if s.get("priority") == "C"]
        }
        
        workflow = {
            "idea": idea,
            "app_summary": blueprint.get("app_summary", blueprint.get("summary", "Let's build something awesome!")),
            "summary": blueprint.get("app_summary", blueprint.get("summary", "Let's build something awesome!")),
            "tech_stack": blueprint.get("tech_stack", {}),
            "directory_structure": blueprint.get("directory_structure", []),
            "user_flow": blueprint.get("user_flow", []),
            "phases": phases,
            "phase_progress": phase_progress,
            "build_steps": steps,
            "steps": steps,
            "grouped_steps": grouped,
            "progress": {
                "total": total_steps,
                "completed": completed_steps,
                "percent": progress_percent,
                "current_step": get_current_step_number(steps),
                "next_step": get_next_step_id(steps)
            },
            "phase": determine_current_phase(phase_progress),
            "progress_hint": blueprint.get("progress_hint", "Follow each step to build your app!"),
            "testing_unlocked": progress_percent >= 70
        }
        
        print(f"[GUIDED_WORKFLOW] Created workflow with {total_steps} steps in {len(phases)} phases")
        
        return {
            "success": True,
            "workflow": workflow
        }
        
    except Exception as e:
        print(f"[GUIDED_WORKFLOW] Exception: {e}")
        return {
            "success": False,
            "error": f"Couldn't create your building plan: {str(e)[:100]}",
            "workflow": None
        }


def area_to_priority(area: str) -> str:
    """Convert area to priority level."""
    priority_map = {
        "frontend": "A",
        "backend": "A",
        "database": "A",
        "ai_logic": "B",
        "integration": "B",
        "ux": "C"
    }
    return priority_map.get(area, "B")


def generate_phases_from_steps(steps: List[Dict]) -> List[Dict]:
    """Generate phases from steps based on their area."""
    phase_map = {
        "backend": ("A", "Phase A – Foundation", "Setting up the basics!"),
        "frontend": ("A", "Phase A – Foundation", "Setting up the basics!"),
        "database": ("B", "Phase B – Core Data", "Teaching your app to remember things!"),
        "ai_logic": ("D", "Phase D – AI Agents", "Creating the AI brains!"),
        "integration": ("E", "Phase E – Integration", "Connecting all the pieces!"),
        "ux": ("G", "Phase G – Polish", "Making it perfect!")
    }
    
    phase_groups = {}
    for step in steps:
        area = step.get("area", step.get("category", "feature"))
        phase_id, phase_name, phase_desc = phase_map.get(area, ("B", "Phase B – Building", "Building features!"))
        
        if phase_id not in phase_groups:
            phase_groups[phase_id] = {
                "id": phase_id,
                "name": phase_name,
                "description": phase_desc,
                "steps": []
            }
        phase_groups[phase_id]["steps"].append(step.get("id", 0))
    
    return sorted(phase_groups.values(), key=lambda x: x["id"])


def calculate_phase_progress(phases: List[Dict], steps: List[Dict]) -> List[Dict]:
    """Calculate progress for each phase."""
    step_status = {s.get("id"): s.get("status", "pending") for s in steps}
    
    phase_progress = []
    for phase in phases:
        phase_steps = phase.get("steps", [])
        total = len(phase_steps)
        completed = sum(1 for sid in phase_steps if step_status.get(sid) == "completed")
        percent = int((completed / total * 100)) if total > 0 else 0
        
        phase_progress.append({
            "id": phase.get("id"),
            "name": phase.get("name"),
            "description": phase.get("description"),
            "total": total,
            "completed": completed,
            "percent": percent,
            "status": "completed" if percent == 100 else ("in_progress" if percent > 0 else "pending")
        })
    
    return phase_progress


def determine_current_phase(phase_progress: List[Dict]) -> Dict[str, Any]:
    """Determine which phase the user is currently in."""
    for phase in phase_progress:
        if phase.get("status") != "completed":
            return {
                "name": phase.get("name", "Building"),
                "id": phase.get("id", "A"),
                "description": phase.get("description", "Working on your app!"),
                "emoji": get_phase_emoji(phase.get("id", "A")),
                "percent": phase.get("percent", 0),
                "encouragement": get_phase_encouragement(phase.get("id", "A"), phase.get("percent", 0))
            }
    
    return {
        "name": "Complete",
        "id": "Z",
        "description": "Your app is ready!",
        "emoji": "🚀",
        "percent": 100,
        "encouragement": "Congratulations! You built an app! Time to publish!"
    }


def get_phase_emoji(phase_id: str) -> str:
    """Get emoji for a phase."""
    emojis = {
        "A": "🏗️",
        "B": "💾",
        "C": "📁",
        "D": "🤖",
        "E": "📱",
        "F": "📚",
        "G": "✨"
    }
    return emojis.get(phase_id, "🔨")


def get_phase_encouragement(phase_id: str, percent: int) -> str:
    """Get encouraging message for current phase progress."""
    if percent == 0:
        return "Let's get started! This is going to be awesome!"
    elif percent < 50:
        return "Great progress! Keep going, you're doing amazing!"
    elif percent < 100:
        return "Almost done with this phase! You're so close!"
    else:
        return "Phase complete! On to the next adventure!"


def generate_fallback_steps(idea: str, blueprint: Dict) -> List[Dict]:
    """Generate steps from old blueprint format or create defaults."""
    steps = []
    step_id = 1
    
    for db in blueprint.get("database", []):
        steps.append({
            "id": step_id,
            "title": f"Create {db.get('table', 'data')} table",
            "area": "database",
            "why_it_matters": f"Your app needs to remember {db.get('table', 'your data')} information!",
            "files_to_edit": ["database.py", "models.py"],
            "micro_step_instructions": [
                f"Step 1: Create the {db.get('table', 'data')} table structure",
                f"Step 2: Add fields: {', '.join(db.get('fields', ['id'])[:4])}",
                "Step 3: Test the database connection"
            ],
            "replit_prompt": f"Create {db.get('table', 'data')} table with: {', '.join(db.get('fields', ['id'])[:5])}. Use SQLAlchemy.",
            "validation_check": ["Database connects", "Table exists", "Can add test row"],
            "priority": "A",
            "category": "database",
            "status": "pending"
        })
        step_id += 1
    
    for page in blueprint.get("pages", []):
        steps.append({
            "id": step_id,
            "title": f"Build {page.get('name', 'a page')}",
            "area": "frontend",
            "why_it_matters": "This is what your users will see!",
            "files_to_edit": [f"templates/{page.get('name', 'page').lower().replace(' ', '_')}.html"],
            "micro_step_instructions": [
                f"Step 1: Create the HTML file for {page.get('name', 'the page')}",
                "Step 2: Add the main content and layout",
                "Step 3: Add basic styling"
            ],
            "replit_prompt": f"Create {page.get('name', 'page')} - {page.get('description', 'a page')}. Use Jinja2. Keep minimal.",
            "validation_check": ["Page loads without errors", "Content displays correctly"],
            "priority": "A",
            "category": "frontend",
            "status": "pending"
        })
        step_id += 1
    
    for endpoint in blueprint.get("endpoints", []):
        steps.append({
            "id": step_id,
            "title": f"Add {endpoint.get('method', 'POST')} {endpoint.get('path', '/api/action')}",
            "area": "backend",
            "why_it_matters": "This is how your frontend talks to your backend!",
            "files_to_edit": ["main.py"],
            "micro_step_instructions": [
                f"Step 1: Add route for {endpoint.get('path', '/api/action')}",
                f"Step 2: Accept {endpoint.get('method', 'POST')} requests",
                "Step 3: Return JSON response"
            ],
            "replit_prompt": f"Add {endpoint.get('method', 'POST')} {endpoint.get('path', '/api/action')} - {endpoint.get('description', 'action')}. Return JSON.",
            "validation_check": ["Route responds", "Returns valid JSON"],
            "priority": "B",
            "category": "backend",
            "status": "pending"
        })
        step_id += 1
    
    if not steps:
        steps = [
            {
                "id": 1,
                "title": "Set up your project",
                "area": "backend",
                "why_it_matters": "Every app needs a good foundation!",
                "files_to_edit": ["main.py"],
                "micro_step_instructions": [
                    "Step 1: Create main.py",
                    "Step 2: Add basic FastAPI setup",
                    "Step 3: Run and test"
                ],
                "replit_prompt": f"Create FastAPI app for: {idea[:50]}. Add home route. Run on port 5000.",
                "validation_check": ["Server starts", "Home page loads"],
                "priority": "A",
                "category": "setup",
                "status": "pending"
            }
        ]
    
    return steps


def get_current_step_number(steps: List[Dict]) -> int:
    """Get the order number of the current (first non-completed) step."""
    for step in steps:
        if step.get("status") != "completed":
            return step.get("order", 1)
    return len(steps)


def get_next_step_id(steps: List[Dict]) -> int:
    """Get the ID of the next uncompleted step."""
    for step in steps:
        if step.get("status") != "completed":
            return step.get("id", 1)
    return 0


def update_step_status(workflow: Dict, step_id: int, new_status: str) -> Dict[str, Any]:
    """
    Update the status of a step and recalculate progress.
    """
    try:
        steps = workflow.get("build_steps", workflow.get("steps", []))
        
        for step in steps:
            if step.get("id") == step_id:
                step["status"] = new_status
                break
        
        total = len(steps)
        completed = sum(1 for s in steps if s.get("status") == "completed")
        percent = int((completed / total * 100)) if total > 0 else 0
        
        workflow["build_steps"] = steps
        workflow["steps"] = steps
        workflow["progress"] = {
            "total": total,
            "completed": completed,
            "percent": percent,
            "current_step": get_current_step_number(steps),
            "next_step": get_next_step_id(steps)
        }
        
        phases = workflow.get("phases", [])
        if phases:
            workflow["phase_progress"] = calculate_phase_progress(phases, steps)
            workflow["phase"] = determine_current_phase(workflow["phase_progress"])
        else:
            workflow["phase"] = determine_phase_by_percent(percent)
        
        workflow["testing_unlocked"] = percent >= 70
        
        grouped = {
            "A": [s for s in steps if s.get("priority") == "A"],
            "B": [s for s in steps if s.get("priority") == "B"],
            "C": [s for s in steps if s.get("priority") == "C"]
        }
        workflow["grouped_steps"] = grouped
        
        return {
            "success": True,
            "workflow": workflow
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:100],
            "workflow": workflow
        }


def determine_phase_by_percent(progress_percent: int) -> Dict[str, Any]:
    """Determine phase based on overall progress percentage."""
    if progress_percent < 30:
        return {
            "name": "Foundation",
            "id": "A",
            "description": "Setting up the basics!",
            "emoji": "🏗️",
            "percent": progress_percent,
            "encouragement": "Great start! You're building something awesome!"
        }
    elif progress_percent < 70:
        return {
            "name": "Building",
            "id": "B",
            "description": "Adding the main features!",
            "emoji": "🔨",
            "percent": progress_percent,
            "encouragement": "You're doing amazing! The app is taking shape!"
        }
    elif progress_percent < 100:
        return {
            "name": "Polish",
            "id": "G",
            "description": "Making it perfect!",
            "emoji": "✨",
            "percent": progress_percent,
            "encouragement": "So close! Just a few more touches!"
        }
    else:
        return {
            "name": "Complete",
            "id": "Z",
            "description": "Your app is ready!",
            "emoji": "🚀",
            "percent": 100,
            "encouragement": "Congratulations! Time to publish!"
        }


def get_step_prompt(step: Dict, context: str = "") -> str:
    """Get the Replit prompt for a specific step."""
    if step.get("replit_prompt"):
        return step["replit_prompt"]
    return generate_build_prompt(step, context)


def get_fix_prompt(error_message: str, step: Dict = {}) -> str:
    """Generate a fix prompt for an error."""
    context = ""
    if step:
        context = f"Working on: {step.get('title', 'task')} - {step.get('why_it_matters', '')}"
    return generate_fix_prompt(error_message, context)


def get_next_step(workflow: Dict) -> Dict[str, Any]:
    """Get the next uncompleted step in the workflow."""
    steps = workflow.get("build_steps", workflow.get("steps", []))
    
    for step in steps:
        if step.get("status") != "completed":
            return {
                "success": True,
                "step": step,
                "prompt": step.get("replit_prompt", get_step_prompt(step, workflow.get("summary", "")))
            }
    
    return {
        "success": True,
        "step": None,
        "message": "All steps completed! Your app is ready for testing and publishing!"
    }


def generate_all_prompts(workflow: Dict) -> Dict[str, str]:
    """Pre-generate prompts for all steps."""
    prompts = {}
    context = workflow.get("summary", "")
    
    for step in workflow.get("build_steps", workflow.get("steps", [])):
        step_id = step.get("id", 0)
        prompts[str(step_id)] = step.get("replit_prompt", get_step_prompt(step, context))
    
    return prompts


def get_step_details(step: Dict) -> Dict[str, Any]:
    """Get full details for a step."""
    return {
        "id": step.get("id"),
        "title": step.get("title", "Step"),
        "area": step.get("area", step.get("category", "feature")),
        "why_it_matters": step.get("why_it_matters", step.get("what_this_step_is", "")),
        "files_to_edit": step.get("files_to_edit", []),
        "micro_step_instructions": step.get("micro_step_instructions", []),
        "replit_prompt": step.get("replit_prompt", ""),
        "validation_check": step.get("validation_check", []),
        "priority": step.get("priority", "B"),
        "status": step.get("status", "pending")
    }
