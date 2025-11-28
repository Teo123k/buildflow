"""
AI Build Coach - Main FastAPI Backend

ALWAYS returns valid JSON - never returns HTML, plain text, or tracebacks.
All endpoints are wrapped in try/except with proper error handling.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any
from typing import Optional
from modules.analyse_html import fetch_raw_html, analyze_basic_structure
from modules.task_manager import generate_tasks
from modules.auto_test import run_basic_autotest
from modules.ux_review import run_ux_review, get_issue_summary, run_ux_review_ai
from modules.seo_ai import run_seo_ai
from modules.competitor_ai import discover_competitors_ai, run_competitor_ai
from modules.build_planner import generate_blueprint, generate_fix_prompt
from modules.guided_workflow import create_workflow, update_step_status, get_step_prompt, get_next_step, generate_all_prompts, get_fix_prompt
from utils.ai_wrapper import extract_limited_html, clear_cache, safe_json_ai, DEFAULT_MODEL


app = FastAPI(
    title="AI Build Coach",
    description="A modular web service for website analysis and improvement recommendations",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    """Request model for URL-based endpoints."""
    url: str


class IdeaRequest(BaseModel):
    """Request model for idea-based endpoints."""
    idea: str


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating workflow step status."""
    workflow: Dict[str, Any]
    step_id: int
    status: str


class FixErrorRequest(BaseModel):
    """Request model for error fix prompt generation."""
    error_message: str
    context: Optional[str] = ""


class PromptRequest(BaseModel):
    """Request model for generating a build prompt."""
    step: Dict[str, Any]
    context: Optional[str] = ""


def safe_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure response is always a valid JSON-serializable dict."""
    if not isinstance(data, dict):
        return {"error": "Invalid response format", "raw": str(data)[:500]}
    return data


@app.post("/analyse")
async def analyse_website(request: URLRequest):
    """Basic HTML structure analysis. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /analyse called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /analyse fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "fetch": fetch_result,
                "structure": None,
                "tasks": []
            })
        
        structure_result = analyze_basic_structure(fetch_result["html"])
        tasks = generate_tasks(structure_result.get("basic_issues", []))
        
        print(f"[ENDPOINT] /analyse success for: {request.url}")
        return safe_response({
            "success": True,
            "fetch": fetch_result,
            "structure": structure_result,
            "tasks": tasks
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /analyse exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Analysis failed: {str(e)[:100]}",
            "fetch": None,
            "structure": None,
            "tasks": []
        })


@app.post("/auto-test")
@app.post("/autotest")
async def auto_test_website(request: URLRequest):
    """Simple website health check. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /autotest called for: {request.url}")
    
    try:
        result = run_basic_autotest(request.url)
        
        print(f"[ENDPOINT] /autotest success for: {request.url}")
        return safe_response({
            "success": result.get("success", False),
            "url": str(result.get("url", request.url)),
            "status": str(result.get("status", "Unknown")),
            "response_time_ms": int(result.get("response_time_ms", 0)),
            "checks": list(result.get("checks", [])),
            "issues": list(result.get("issues", [])),
            "tasks": list(result.get("tasks", []))
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /autotest exception: {e}")
        return safe_response({
            "success": False,
            "url": request.url,
            "status": "Error",
            "response_time_ms": 0,
            "checks": [],
            "issues": [f"Test failed: {str(e)[:100]}"],
            "tasks": []
        })


@app.post("/ux")
@app.post("/ux-check")
async def ux_check(request: URLRequest):
    """Rule-based UX review. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /ux called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /ux fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "issues": None,
                "summary": None
            })
        
        issues = run_ux_review(fetch_result["html"])
        summary = get_issue_summary(issues)
        
        print(f"[ENDPOINT] /ux success for: {request.url}")
        return safe_response({
            "success": True,
            "url": request.url,
            "issues": issues,
            "summary": summary
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /ux exception: {e}")
        return safe_response({
            "success": False,
            "error": f"UX check failed: {str(e)[:100]}",
            "issues": None,
            "summary": None
        })


@app.post("/ux-ai")
async def ux_ai_check(request: URLRequest):
    """AI-enhanced UX review. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /ux-ai called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /ux-ai fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "ux_data": None
            })
        
        ux_result = run_ux_review_ai(fetch_result["html"], request.url)
        
        print(f"[ENDPOINT] /ux-ai success for: {request.url}")
        return safe_response({
            "success": True,
            "url": request.url,
            "ux_data": ux_result
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /ux-ai exception: {e}")
        return safe_response({
            "success": False,
            "error": f"UX AI check failed: {str(e)[:100]}",
            "ux_data": None
        })


@app.post("/seo")
@app.post("/seo-check")
@app.post("/seo-ai")
async def seo_ai_check(request: URLRequest):
    """AI-enhanced SEO review. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /seo called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /seo fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "seo_data": None
            })
        
        seo_result = run_seo_ai(fetch_result["html"], request.url)
        
        print(f"[ENDPOINT] /seo success for: {request.url}")
        return safe_response({
            "success": True,
            "url": request.url,
            "seo_data": seo_result
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /seo exception: {e}")
        return safe_response({
            "success": False,
            "error": f"SEO check failed: {str(e)[:100]}",
            "seo_data": None
        })


@app.post("/competitors")
@app.post("/competitor-ai")
async def competitor_ai_check(request: URLRequest):
    """AI competitor analysis. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /competitors called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /competitors fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch main URL")),
                "competitor_data": None
            })
        
        main_html = fetch_result["html"]
        
        competitors = discover_competitors_ai(request.url, main_html)
        
        competitor_html_map = {}
        competitors_fetched = []
        
        for comp_url in competitors[:2]:
            try:
                comp_result = fetch_raw_html(comp_url)
                if comp_result.get("success"):
                    competitor_html_map[comp_url] = comp_result["html"][:3000]
                    competitors_fetched.append({"url": comp_url, "success": True})
                else:
                    competitors_fetched.append({
                        "url": comp_url,
                        "success": False,
                        "error": str(comp_result.get("error", "Failed"))
                    })
            except Exception as ce:
                competitors_fetched.append({
                    "url": comp_url,
                    "success": False,
                    "error": str(ce)[:50]
                })
        
        if competitor_html_map:
            competitor_result = run_competitor_ai(main_html, request.url, competitor_html_map)
        else:
            competitor_result = {
                "summary": "No competitors could be fetched for comparison.",
                "strengths": [],
                "weaknesses": [],
                "improvements": ["Try again with a different URL"],
                "ai_tasks": [],
                "exact_fixes": [],
                "fix_prompt": "Competitor analysis unavailable."
            }
        
        print(f"[ENDPOINT] /competitors success for: {request.url}")
        return safe_response({
            "success": True,
            "url": request.url,
            "auto_detected_competitors": competitors,
            "competitors_fetched": competitors_fetched,
            "competitor_data": competitor_result
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /competitors exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Competitor analysis failed: {str(e)[:100]}",
            "competitor_data": None
        })


@app.post("/plan")
async def generate_plan(request: URLRequest):
    """Generate an improvement plan. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /plan called for: {request.url}")
    
    try:
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /plan fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "plan": None
            })
        
        limited_html = extract_limited_html(fetch_result["html"], limit=2000)
        
        prompt = f"""Analyze this website and create a short improvement plan.

URL: {request.url}
HTML snippet:
{limited_html[:1500]}

Respond ONLY with valid JSON. No markdown, no explanation:
{{
  "summary": "One sentence about the website",
  "priorities": ["priority 1", "priority 2", "priority 3"],
  "quick_wins": ["quick win 1", "quick win 2"],
  "long_term": ["long term goal 1", "long term goal 2"],
  "tasks": [
    {{"issue": "Problem", "task": "What to do", "priority": "high"}}
  ]
}}

Keep everything SHORT. Maximum 5 tasks."""

        result = safe_json_ai(
            prompt,
            model=DEFAULT_MODEL,
            cache_key=f"plan-{request.url}",
            max_tokens=600,
            temperature=0.2,
            default_response={"summary": "Plan unavailable", "priorities": [], "quick_wins": [], "long_term": [], "tasks": []}
        )
        
        if "error" in result and "AI" in result.get("error", ""):
            print(f"[ENDPOINT] /plan AI error: {result.get('error')}")
        
        summary = result.get("summary", "Plan generated")
        if isinstance(summary, dict):
            summary = str(summary)
        
        priorities = result.get("priorities", [])
        if not isinstance(priorities, list):
            priorities = []
        priorities = [str(p) for p in priorities[:5]]
        
        quick_wins = result.get("quick_wins", [])
        if not isinstance(quick_wins, list):
            quick_wins = []
        quick_wins = [str(q) for q in quick_wins[:3]]
        
        long_term = result.get("long_term", [])
        if not isinstance(long_term, list):
            long_term = []
        long_term = [str(l) for l in long_term[:3]]
        
        tasks = result.get("tasks", [])
        plan_tasks = []
        for t in tasks[:5]:
            if isinstance(t, dict):
                plan_tasks.append({
                    "issue": str(t.get("issue", "Task")),
                    "task": str(t.get("task", "")),
                    "priority": str(t.get("priority", "medium"))
                })
        
        print(f"[ENDPOINT] /plan success for: {request.url}")
        return safe_response({
            "success": True,
            "url": request.url,
            "plan": {
                "summary": str(summary),
                "priorities": priorities,
                "quick_wins": quick_wins,
                "long_term": long_term,
                "tasks": plan_tasks
            }
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /plan exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Plan generation failed: {str(e)[:100]}",
            "plan": None
        })


@app.post("/full-analysis")
async def full_analysis(request: URLRequest):
    """Full website analysis. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /full-analysis called for: {request.url}")
    
    try:
        clear_cache()
        
        fetch_result = fetch_raw_html(request.url)
        
        if not fetch_result.get("success", False):
            print(f"[ENDPOINT] /full-analysis fetch failed: {fetch_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(fetch_result.get("error", "Failed to fetch URL")),
                "data": None
            })
        
        html = fetch_result["html"]
        url = request.url
        
        structure_result = analyze_basic_structure(html)
        basic_tasks = generate_tasks(structure_result.get("basic_issues", []))
        
        ux_result = run_ux_review_ai(html, url)
        seo_result = run_seo_ai(html, url)
        
        competitor_result = None
        auto_detected_competitors = []
        
        try:
            auto_detected_competitors = discover_competitors_ai(url, html)
            
            if auto_detected_competitors:
                competitor_html_map = {}
                for comp_url in auto_detected_competitors[:2]:
                    try:
                        comp_result = fetch_raw_html(comp_url)
                        if comp_result.get("success"):
                            competitor_html_map[comp_url] = comp_result["html"][:3000]
                    except Exception:
                        pass
                
                if competitor_html_map:
                    competitor_result = run_competitor_ai(html, url, competitor_html_map)
        except Exception as ce:
            print(f"[ENDPOINT] /full-analysis competitor error: {ce}")
        
        all_tasks = []
        
        for task in basic_tasks:
            if isinstance(task, dict):
                all_tasks.append({
                    "source": "basic",
                    "task": str(task.get("task", task.get("message", ""))),
                    "priority": str(task.get("priority", "medium")),
                    "category": "Structure"
                })
        
        for task in ux_result.get("ai_tasks", []):
            if isinstance(task, str):
                all_tasks.append({
                    "source": "ux",
                    "task": task,
                    "priority": "medium",
                    "category": "UX"
                })
            elif isinstance(task, dict):
                all_tasks.append({
                    "source": "ux",
                    "task": str(task.get("task", "")),
                    "priority": str(task.get("priority", "medium")),
                    "category": "UX"
                })
        
        for task in seo_result.get("ai_tasks", []):
            if isinstance(task, str):
                all_tasks.append({
                    "source": "seo",
                    "task": task,
                    "priority": "medium",
                    "category": "SEO"
                })
            elif isinstance(task, dict):
                all_tasks.append({
                    "source": "seo",
                    "task": str(task.get("task", "")),
                    "priority": str(task.get("priority", "medium")),
                    "category": "SEO"
                })
        
        if competitor_result:
            for task in competitor_result.get("ai_tasks", []):
                if isinstance(task, str):
                    all_tasks.append({
                        "source": "competitor",
                        "task": task,
                        "priority": "medium",
                        "category": "Competitor"
                    })
                elif isinstance(task, dict):
                    all_tasks.append({
                        "source": "competitor",
                        "task": str(task.get("task", "")),
                        "priority": str(task.get("priority", "medium")),
                        "category": "Competitor"
                    })
        
        ux_score = 0
        if isinstance(ux_result.get("summary"), dict):
            ux_score = ux_result["summary"].get("total_issues", 0)
        
        print(f"[ENDPOINT] /full-analysis success for: {request.url} - {len(all_tasks)} tasks")
        return safe_response({
            "success": True,
            "url": url,
            "basic": {
                "structure": structure_result,
                "tasks": basic_tasks
            },
            "ux": ux_result,
            "seo": seo_result,
            "competitor": {
                "auto_detected": auto_detected_competitors,
                "data": competitor_result
            } if competitor_result else None,
            "all_tasks": all_tasks,
            "stats": {
                "total_tasks": len(all_tasks),
                "by_source": {
                    "basic": sum(1 for t in all_tasks if t.get("source") == "basic"),
                    "ux": sum(1 for t in all_tasks if t.get("source") == "ux"),
                    "seo": sum(1 for t in all_tasks if t.get("source") == "seo"),
                    "competitor": sum(1 for t in all_tasks if t.get("source") == "competitor")
                },
                "ux_score": ux_score,
                "seo_score": seo_result.get("score", 0)
            }
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /full-analysis exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Full analysis failed: {str(e)[:100]}",
            "data": None
        })


@app.post("/build-plan")
async def build_plan(request: IdeaRequest):
    """Generate a blueprint from an app idea. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /build-plan called for idea: {request.idea[:50]}...")
    
    try:
        result = generate_blueprint(request.idea)
        
        if not result.get("success", False):
            print(f"[ENDPOINT] /build-plan failed: {result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(result.get("error", "Blueprint generation failed")),
                "blueprint": None
            })
        
        print(f"[ENDPOINT] /build-plan success")
        return safe_response(result)
        
    except Exception as e:
        print(f"[ENDPOINT] /build-plan exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Blueprint generation failed: {str(e)[:100]}",
            "blueprint": None
        })


@app.post("/workflow")
async def create_workflow_endpoint(request: IdeaRequest):
    """Generate blueprint and convert to workflow. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /workflow called for idea: {request.idea[:50]}...")
    
    try:
        blueprint_result = generate_blueprint(request.idea)
        
        if not blueprint_result.get("success", False):
            print(f"[ENDPOINT] /workflow blueprint failed: {blueprint_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(blueprint_result.get("error", "Blueprint generation failed")),
                "workflow": None
            })
        
        workflow_result = create_workflow(blueprint_result["blueprint"], request.idea)
        
        if not workflow_result.get("success", False):
            print(f"[ENDPOINT] /workflow creation failed: {workflow_result.get('error')}")
            return safe_response({
                "success": False,
                "error": str(workflow_result.get("error", "Workflow creation failed")),
                "workflow": None
            })
        
        workflow = workflow_result["workflow"]
        prompts = generate_all_prompts(workflow)
        
        print(f"[ENDPOINT] /workflow success - {workflow['progress']['total']} steps")
        return safe_response({
            "success": True,
            "idea": request.idea,
            "blueprint": blueprint_result["blueprint"],
            "workflow": workflow,
            "prompts": prompts,
            "next_step": get_next_step(workflow)
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /workflow exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Workflow creation failed: {str(e)[:100]}",
            "workflow": None
        })


@app.post("/workflow/update")
async def update_workflow(request: WorkflowUpdateRequest):
    """Update a step's status in the workflow. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /workflow/update called for step {request.step_id}")
    
    try:
        result = update_step_status(request.workflow, request.step_id, request.status)
        
        if not result.get("success", False):
            return safe_response({
                "success": False,
                "error": str(result.get("error", "Update failed")),
                "workflow": request.workflow
            })
        
        workflow = result["workflow"]
        
        print(f"[ENDPOINT] /workflow/update success - {workflow['progress']['percent']}% complete")
        return safe_response({
            "success": True,
            "workflow": workflow,
            "next_step": get_next_step(workflow),
            "testing_unlocked": workflow.get("testing_unlocked", False)
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /workflow/update exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Update failed: {str(e)[:100]}",
            "workflow": request.workflow
        })


@app.post("/generate-prompt")
async def generate_prompt(request: PromptRequest):
    """Generate a build prompt for a step. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /generate-prompt called")
    
    try:
        prompt = get_step_prompt(request.step, request.context or "")
        
        return safe_response({
            "success": True,
            "prompt": prompt,
            "step": request.step
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /generate-prompt exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Prompt generation failed: {str(e)[:100]}",
            "prompt": None
        })


@app.post("/fix-error")
async def fix_error(request: FixErrorRequest):
    """Generate a fix prompt for an error. ALWAYS returns valid JSON."""
    print(f"[ENDPOINT] /fix-error called")
    
    try:
        step_context = {"description": request.context} if request.context else {}
        prompt = get_fix_prompt(request.error_message, step_context)
        
        return safe_response({
            "success": True,
            "prompt": prompt
        })
        
    except Exception as e:
        print(f"[ENDPOINT] /fix-error exception: {e}")
        return safe_response({
            "success": False,
            "error": f"Fix prompt generation failed: {str(e)[:100]}",
            "prompt": None
        })


@app.get("/favicon.ico")
async def favicon():
    """Return empty response for favicon to avoid 404."""
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
