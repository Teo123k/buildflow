"""
Build Planner Module - Expert + Child-Friendly System

Converts ANY app idea (including complex multi-agent systems) into a COMPLETE build plan.
- Covers full architecture: front-end, back-end, database, AI agents, storage, dashboards
- Broken into small, child-friendly steps
- Each step has a short, cost-efficient Replit prompt
- ALWAYS returns valid JSON only

ONE MODE: Expert architecture + 12-year-old-friendly explanations.
"""

import json
from typing import Dict, Any, List

from utils.ai_wrapper import safe_json_ai, DEFAULT_MODEL


def generate_blueprint(idea: str) -> Dict[str, Any]:
    """
    Convert an app idea into a COMPLETE build plan with phases.
    Handles complex systems like AI tutors, multi-agent systems, dashboards, etc.
    ALWAYS returns valid JSON dict.
    """
    print(f"[BUILD_PLANNER] Generating expert blueprint for: {idea[:80]}...")
    
    try:
        if not idea or not idea.strip():
            return {
                "success": False,
                "error": "Please tell me what app you want to build!",
                "blueprint": None
            }
        
        prompt = f"""You are a senior full-stack engineer who explains things so a 12-year-old can follow.

The user wants to build:
"{idea}"

Create a COMPLETE build plan that covers the ENTIRE system architecture.

CRITICAL RULES:
1. Cover ALL features mentioned in the idea - do NOT stop after login/homepage
2. Plan until a working MVP of the WHOLE system is possible
3. For complex systems (AI agents, multi-user, dashboards), you MUST include ALL components
4. Each step modifies only 1-2 files
5. Each step does ONE thing only
6. Use simple words a 12-year-old can understand, but keep the engineering professional
7. Keep replit_prompt under 50 words
8. Aim for 25-40 solid steps that cover the whole system

SELF-CHECK BEFORE RESPONDING:
Ask yourself: "If this were my production app, is anything big missing?"
- Did I cover frontend, backend, database, AI logic (if any), storage, and basic testing?
- Does every core feature from the idea have at least one build step?
- If the user mentioned AI agents, did I include ALL of them?
- If the user mentioned dashboards, did I include the dashboard views?
- If the user mentioned file uploads, did I include upload AND processing flows?

If anything important is missing, ADD the missing steps.

PHASES (use these exact names):
- Phase A – Foundation: project structure, basic frontend shell, basic backend, routing, auth
- Phase B – Core Data & Storage: database tables, storage setup, table relationships
- Phase C – File Upload & Organization: upload flows, file processing, organization logic
- Phase D – AI Agents: each agent's logic, how they communicate, database interactions
- Phase E – Student Dashboard & UI: main views, lists, progress displays, action buttons
- Phase F – Lessons & Quizzes: content generation, scoring, feedback, progress updates
- Phase G – Quality & Polish: error states, loading states, basic tests, dark mode

Skip phases that don't apply to the idea (e.g., skip Phase C if no file uploads).

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "app_summary": "1-2 sentence overview in simple language",
  "tech_stack": {{
    "frontend": "HTML/CSS/JS or React",
    "backend": "Python/FastAPI",
    "database": "PostgreSQL or Supabase",
    "ai": "OpenAI API or none",
    "storage": "local or Supabase Storage or none"
  }},
  "directory_structure": [
    "main.py - The brain of your app",
    "templates/ - HTML pages your users see"
  ],
  "phases": [
    {{
      "id": "A",
      "name": "Phase A – Foundation",
      "description": "Setting up the basics - like building the foundation of a house!",
      "steps": [1, 2, 3]
    }}
  ],
  "build_steps": [
    {{
      "id": 1,
      "title": "Create the homepage",
      "area": "frontend",
      "why_it_matters": "Every app needs a front door - this is yours!",
      "files_to_edit": ["templates/index.html"],
      "micro_step_instructions": [
        "Step 1: Create a new file called index.html",
        "Step 2: Add a welcome message",
        "Step 3: Add a button for the main action"
      ],
      "replit_prompt": "Create templates/index.html with a welcome page. Add heading and button. Keep minimal.",
      "validation_check": [
        "Page loads without errors",
        "Welcome message is visible",
        "Button appears and can be clicked"
      ]
    }}
  ],
  "user_flow": ["Step 1: User does X", "Step 2: User sees Y"],
  "progress_hint": "These steps will build your complete working app!"
}}

AREA VALUES (pick one per step):
- frontend: UI components, pages, styling
- backend: API routes, server logic
- database: tables, queries, migrations
- ai_logic: AI agent code, prompts, responses
- integration: connecting parts together
- ux: polish, error states, loading states

STEP TONE EXAMPLES:
- "This step makes a home page – like the front door of your app."
- "This step teaches the computer how to store student progress."
- "This step creates the AI teacher's brain – it decides what to teach next."

STRICT JSON RULES:
1. Output ONLY valid JSON - no markdown, no code blocks, no text before or after
2. Start with {{ and end with }}
3. All arrays contain only strings (except build_steps and phases which contain objects)
4. NO trailing commas
5. Escape quotes with \\"
6. NO comments in JSON

Your response must be 100% valid JSON starting with {{ and ending with }}.
"""

        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"blueprint-expert-{idea[:100]}",
            max_tokens=6000,
            temperature=0.2,
            default_response={
                "app_summary": "Let's build something awesome!",
                "tech_stack": {"frontend": "HTML/CSS/JS", "backend": "Python/FastAPI", "database": "PostgreSQL"},
                "directory_structure": [],
                "phases": [],
                "build_steps": [],
                "user_flow": [],
                "progress_hint": "Follow each step to build your app!"
            }
        )
        
        if "error" in result and "AI" in result.get("error", ""):
            print(f"[BUILD_PLANNER] AI error: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error"),
                "blueprint": None
            }
        
        blueprint = parse_expert_blueprint(result, idea)
        
        print(f"[BUILD_PLANNER] Success - {len(blueprint.get('build_steps', []))} steps in {len(blueprint.get('phases', []))} phases")
        
        return {
            "success": True,
            "idea": idea,
            "blueprint": blueprint
        }
        
    except Exception as e:
        print(f"[BUILD_PLANNER] Exception: {e}")
        return {
            "success": False,
            "error": f"Couldn't create your building plan: {str(e)[:100]}",
            "blueprint": None
        }


def parse_expert_blueprint(result: Dict, idea: str) -> Dict[str, Any]:
    """Parse and validate expert blueprint with phases structure."""
    
    def ensure_list(data, default=[]):
        if isinstance(data, list):
            return data
        return default
    
    def ensure_string(data, default=""):
        if isinstance(data, str):
            return data
        return str(data) if data else default
    
    app_summary = ensure_string(result.get("app_summary"), f"Building: {idea[:50]}")
    
    tech_stack = result.get("tech_stack", {})
    if not isinstance(tech_stack, dict):
        tech_stack = {}
    
    directory_structure = ensure_list(result.get("directory_structure"), [
        "main.py - Your app's brain",
        "templates/ - HTML pages",
        "static/ - CSS and images",
        "models/ - Database structures"
    ])
    
    build_steps = []
    for i, step in enumerate(ensure_list(result.get("build_steps"))[:50]):
        if isinstance(step, dict):
            parsed_step = {
                "id": step.get("id", i + 1),
                "title": ensure_string(step.get("title"), f"Step {i + 1}"),
                "area": ensure_string(step.get("area"), "feature"),
                "why_it_matters": ensure_string(
                    step.get("why_it_matters") or step.get("why_this_step_matters"), 
                    ""
                ),
                "files_to_edit": ensure_list(step.get("files_to_edit"), ["main.py"]),
                "micro_step_instructions": ensure_list(step.get("micro_step_instructions"), []),
                "replit_prompt": ensure_string(step.get("replit_prompt"), ""),
                "validation_check": ensure_list(step.get("validation_check"), ["Check if it works"]),
                "status": "pending"
            }
            
            if not parsed_step["micro_step_instructions"]:
                parsed_step["micro_step_instructions"] = [
                    f"Step 1: Open {parsed_step['files_to_edit'][0] if parsed_step['files_to_edit'] else 'the file'}",
                    "Step 2: Make the changes described",
                    "Step 3: Save and test"
                ]
            
            build_steps.append(parsed_step)
    
    if not build_steps:
        build_steps = generate_default_steps(idea)
    
    phases = []
    for phase in ensure_list(result.get("phases")):
        if isinstance(phase, dict):
            parsed_phase = {
                "id": ensure_string(phase.get("id"), "A"),
                "name": ensure_string(phase.get("name"), "Phase"),
                "description": ensure_string(phase.get("description"), "Building this part of your app"),
                "steps": ensure_list(phase.get("steps"), [])
            }
            phases.append(parsed_phase)
    
    if not phases:
        phases = generate_phases_from_steps(build_steps)
    
    user_flow = ensure_list(result.get("user_flow"), ["Open the app", "Use the main feature", "See the result"])
    progress_hint = ensure_string(result.get("progress_hint"), "Follow each step to build your complete app!")
    
    return {
        "app_summary": app_summary,
        "summary": app_summary,
        "tech_stack": {
            "frontend": ensure_string(tech_stack.get("frontend"), "HTML/CSS/JS"),
            "backend": ensure_string(tech_stack.get("backend"), "Python/FastAPI"),
            "database": ensure_string(tech_stack.get("database"), "PostgreSQL"),
            "ai": ensure_string(tech_stack.get("ai"), "none"),
            "storage": ensure_string(tech_stack.get("storage"), "local")
        },
        "directory_structure": directory_structure[:12],
        "phases": phases,
        "build_steps": build_steps,
        "user_flow": user_flow[:8],
        "progress_hint": progress_hint
    }


def generate_phases_from_steps(steps: List[Dict]) -> List[Dict]:
    """Generate phases from steps based on their area/category."""
    area_to_phase = {
        "frontend": ("A", "Phase A – Foundation"),
        "backend": ("B", "Phase B – Core Logic"),
        "database": ("B", "Phase B – Core Data"),
        "ai_logic": ("D", "Phase D – AI Agents"),
        "integration": ("E", "Phase E – Integration"),
        "ux": ("G", "Phase G – Polish")
    }
    
    phase_groups = {}
    for step in steps:
        area = step.get("area", "feature")
        phase_id, phase_name = area_to_phase.get(area, ("B", "Phase B – Building"))
        
        if phase_id not in phase_groups:
            phase_groups[phase_id] = {
                "id": phase_id,
                "name": phase_name,
                "description": get_phase_description(phase_id),
                "steps": []
            }
        phase_groups[phase_id]["steps"].append(step.get("id", 0))
    
    return sorted(phase_groups.values(), key=lambda x: x["id"])


def get_phase_description(phase_id: str) -> str:
    """Get child-friendly description for a phase."""
    descriptions = {
        "A": "Setting up the basics - like building the foundation of a house!",
        "B": "Adding the main features - your app is taking shape!",
        "C": "Setting up file uploads - so your app can receive files!",
        "D": "Creating the AI brains - this is where the magic happens!",
        "E": "Building the main screens - what your users will see!",
        "F": "Adding lessons and quizzes - the learning parts!",
        "G": "Making it perfect - the final polish!"
    }
    return descriptions.get(phase_id, "Building more features!")


def generate_default_steps(idea: str) -> List[Dict]:
    """Generate default steps if AI fails."""
    return [
        {
            "id": 1,
            "title": "Set up project structure",
            "area": "backend",
            "why_it_matters": "Like building a house - you need the foundation first!",
            "files_to_edit": ["main.py"],
            "micro_step_instructions": [
                "Step 1: Create main.py if it doesn't exist",
                "Step 2: Add the basic FastAPI setup",
                "Step 3: Run it to make sure it works"
            ],
            "replit_prompt": "Create FastAPI app in main.py with '/' route returning 'Hello World'. Run on port 5000.",
            "validation_check": ["Server starts without errors", "Visiting / shows Hello World"],
            "status": "pending"
        },
        {
            "id": 2,
            "title": "Create the homepage",
            "area": "frontend",
            "why_it_matters": "This is the front door of your app!",
            "files_to_edit": ["templates/index.html"],
            "micro_step_instructions": [
                "Step 1: Create templates folder",
                "Step 2: Create index.html inside it",
                "Step 3: Add a welcome message"
            ],
            "replit_prompt": f"Create templates/index.html for: {idea[:50]}. Add heading and button.",
            "validation_check": ["Page loads", "Heading is visible", "Button appears"],
            "status": "pending"
        },
        {
            "id": 3,
            "title": "Add basic styling",
            "area": "frontend",
            "why_it_matters": "People like apps that look good!",
            "files_to_edit": ["static/style.css"],
            "micro_step_instructions": [
                "Step 1: Create static folder",
                "Step 2: Create style.css",
                "Step 3: Add modern styling"
            ],
            "replit_prompt": "Create static/style.css with modern styling: nice fonts, colors, button effects.",
            "validation_check": ["CSS file loads", "Page looks styled"],
            "status": "pending"
        },
        {
            "id": 4,
            "title": "Set up database",
            "area": "database",
            "why_it_matters": "Your app needs to remember things!",
            "files_to_edit": ["models.py", "database.py"],
            "micro_step_instructions": [
                "Step 1: Create database.py for connection",
                "Step 2: Create models.py for tables",
                "Step 3: Test the connection"
            ],
            "replit_prompt": "Create database.py with PostgreSQL connection using SQLAlchemy. Add models.py with basic User table.",
            "validation_check": ["Database connects", "Tables exist"],
            "status": "pending"
        },
        {
            "id": 5,
            "title": "Add main feature",
            "area": "backend",
            "why_it_matters": "This is what makes your app special!",
            "files_to_edit": ["main.py"],
            "micro_step_instructions": [
                "Step 1: Add the main API route",
                "Step 2: Connect to database",
                "Step 3: Return the result"
            ],
            "replit_prompt": f"Add main feature for: {idea[:40]}. Create POST route, connect to database, return JSON.",
            "validation_check": ["Route responds", "Returns correct data"],
            "status": "pending"
        }
    ]


def generate_build_prompt(task: Dict, context: str = "") -> str:
    """
    Generate a minimal, cost-efficient Replit prompt for a step.
    """
    if task.get("replit_prompt"):
        return task["replit_prompt"]
    
    task_name = task.get("title", task.get("name", "Task"))
    task_desc = task.get("why_it_matters", task.get("description", ""))
    files = task.get("files_to_edit", ["main.py"])
    
    prompt = f"""{task_name}

{task_desc}

Files: {', '.join(files[:2])}

Keep changes minimal. Do only this task."""
    
    return prompt


def generate_fix_prompt(error_message: str, context: str = "") -> str:
    """
    Generate a minimal fix prompt for an error.
    """
    if not error_message or not error_message.strip():
        return "Please paste the error message you're seeing."
    
    error_short = error_message[:400]
    
    prompt = f"""Fix this error:

{error_short}

{f'Context: {context[:150]}' if context else ''}

Rules:
- Smallest fix only
- Don't change other things
- Explain in 1 sentence what you fixed"""
    
    return prompt
