# AI Build Coach

## Overview
AI Build Coach is a modular web service with two main features:
1. **Website Analysis** - Paste a URL and get AI-powered feedback on UX, SEO, and competitors
2. **Build Planner (AI)** - Describe your app idea and get a step-by-step building plan

**Current State:** Full AI optimization layer with dual-tab homepage. Build Planner is now a standalone main tab visible immediately on load.

## Homepage Layout
- **Main Navigation**: Two tabs at the top - "Website Analysis" and "Build Planner (AI)" with NEW badge
- **Website Analysis**: URL input + analysis tabs (Overview, Design, SEO, Test, Competitors, Fix List)
- **Build Planner**: Idea input + micro-task workflow generator with Copy buttons
- Both sections are fully independent and always accessible

## Project Structure

```
.
├── main.py                 # FastAPI backend with all routes
├── utils/                  # Shared utilities
│   ├── __init__.py
│   ├── ai_wrapper.py       # smart_ai() with caching, retries, token management
│   └── browser_fetch.py    # Safe HTML fetching with fallbacks
├── modules/                # Analysis modules
│   ├── __init__.py
│   ├── analyse_html.py     # HTML structure analysis
│   ├── auto_test.py        # Automated browser testing
│   ├── ux_review.py        # AI-enhanced UX review
│   ├── seo_ai.py           # AI-enhanced SEO analysis
│   ├── competitor_ai.py    # AI competitor discovery and comparison
│   ├── generate_prompts.py # Fix prompt generation
│   └── task_manager.py     # Task organisation
├── frontend/               # Web interface
│   ├── index.html          # Main page
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
└── replit.md               # This file
```

## API Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/` | GET | Serves frontend HTML page | Working |
| `/full-analysis` | POST | Complete analysis (Basic + UX + SEO + Competitor) | Working |
| `/analyse` | POST | HTML structure analysis with tasks | Working |
| `/auto-test` or `/autotest` | POST | Simple HTTP-based website health check | Working |
| `/plan` | POST | AI improvement plan with priorities and tasks | Working |
| `/ux-check` | POST | Rule-based UX review | Working |
| `/ux-ai` | POST | AI-enhanced UX review with fix prompts | Working |
| `/seo-ai` | POST | AI-enhanced SEO analysis with fix prompts | Working |
| `/competitor-ai` | POST | AI competitor discovery and comparison | Working |
| `/workflow` | POST | Generate build workflow from idea | Working |
| `/workflow/update` | POST | Update workflow task status | Working |
| `/generate-prompt` | POST | Generate build prompt for specific step | Working |
| `/fix-error` | POST | Generate fix prompt from error message | Working |
| `/build-plan` | POST | Generate project blueprint from idea | Working |

**Notes:**
- Frontend uses `/full-analysis` for website analysis workflow
- Frontend uses `/workflow` for Build Flow (idea-to-app) workflow
- All POST endpoints accept JSON body and return valid JSON

## Utils Package

### ai_wrapper.py
- `smart_ai(prompt, model, cache_key, max_retry, temperature, max_tokens)` - Unified AI call with:
  - In-memory caching by prompt/cache_key
  - Auto-retry on failure (default 3 attempts)
  - Markdown code block stripping from responses
  - Token limit management
- `safe_json_ai(prompt, cache_key, max_tokens, temperature, default_response)` - AI call that ALWAYS returns valid JSON:
  - Catches JSONDecodeError and returns error dict with raw output
  - Never raises, never returns non-dict
  - Validates JSON structure before returning
- `validate_json_response(response, required_keys)` - Validate JSON response
- `extract_limited_html(html, limit)` - HTML size reduction
- `clear_cache()` - Clear AI response cache
- `get_cache_stats()` - Get cache statistics

### browser_fetch.py
- `fetch_html(url, timeout)` - Safe HTML fetching with script removal
- `fetch_html_with_status(url, timeout)` - Detailed fetch with status info

## Modules Overview

1. **analyse_html.py** - Download and analyse HTML structure
2. **auto_test.py** - Simple HTTP-based health check (no browser automation)
3. **ux_review.py** - Rule-based UX checks + AI enhancement via smart_ai
4. **seo_ai.py** - SEO data extraction + AI analysis via smart_ai
5. **competitor_ai.py** - AI competitor discovery + comparison via smart_ai
6. **generate_prompts.py** - Generate copy-paste fix prompts (placeholder)
7. **task_manager.py** - Organise tasks and track progress (placeholder)

## AI Integration

Uses user's own OpenAI API key (OPENAI_API_KEY secret). NOT Replit's AI integration.

### Model Configuration
- **DEFAULT_MODEL** = `gpt-4.1` - Used for all thinking-heavy tasks (UX, SEO, Planner, Workflow, Competitor analysis)
- **CHEAP_MODEL** = `gpt-4o-mini` - Used for simple/mechanical tasks (prompt improvement, light helpers)

Models are configured in `utils/ai_wrapper.py`. To change the default model, update the constants there.

### Pattern
Rule-based logic first, then AI enhancement layer with fallback.

All AI modules use the `smart_ai` wrapper for:
- Caching to avoid redundant API calls
- Automatic retries on failure
- Token limit management via `extract_limited_html`
- Model selection via `model` parameter (defaults to DEFAULT_MODEL)

## Running the Project

The server runs on port 5000:
```bash
python main.py
```

## UX AI Output Format

The `/ux-ai` endpoint returns detailed, actionable issues with this structure:
```json
{
  "summary": "Short explanation of main UX problems",
  "issues": [
    {
      "title": "Short issue title",
      "description": "What is wrong in plain English",
      "location": "file > element (e.g., index.html > .hero-title)",
      "why_it_matters": "Simple reason why this hurts UX",
      "steps_to_fix": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
      "code_fix": "```html\n<exact code>\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "Ready-to-use AI prompt"
    }
  ],
  "ai_tasks": [...],
  "exact_fixes": [...],
  "fix_prompt": "Master prompt for all fixes"
}
```

## SEO AI Output Format

The `/seo-ai` endpoint returns detailed SEO analysis with exact meta tags and code patches:
```json
{
  "summary": "One sentence about critical SEO issues",
  "score": 75,
  "suggested_keywords": ["keyword1", "keyword2", "keyword3"],
  "issues": [
    {
      "title": "Short issue title",
      "description": "What is wrong and why it affects rankings",
      "location": "index.html > <head>",
      "why_it_matters": "How this affects Google ranking",
      "steps_to_fix": ["Step 1: ...", "Step 2: ..."],
      "code_fix": "```html\n<meta name=\"description\" content=\"...\">\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "Ready-to-use AI prompt"
    }
  ],
  "ai_tasks": [...],
  "exact_fixes": [...],
  "fix_prompt": "Master prompt for all fixes",
  "extracted_data": { /* raw SEO data */ }
}
```

## Auto Test Output Format

The `/auto-test` endpoint returns QA test results with detailed issues:
```json
{
  "success": true,
  "url": "https://example.com",
  "summary": "Found 2 issues that should be fixed.",
  "status": "Needs attention",
  "response_time_ms": 450,
  "status_code": 200,
  "checks_passed": ["Title tag exists", "Has viewport meta"],
  "issues": [
    {
      "title": "Missing meta description",
      "description": "Your page has no meta description...",
      "location": "index.html > <head>",
      "steps_to_fix": ["Step 1: ...", "Step 2: ..."],
      "code_fix": "```html\n<meta name=\"description\" content=\"...\">\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "Add a meta description tag..."
    }
  ]
}
```

## Recent Changes

- **Dual-Tab Homepage** - Two main sections: "Website Analysis" and "Build Planner (AI)" always visible on homepage
- **Build Planner as Main Tab** - Standalone feature with star icon, NEW badge, hero section, and independent workflow
- **Copy Buttons** - "Copy All Prompts" and "Copy Build Plan" buttons in Build Planner for easy export
- **Theme Toggle** - Light/dark mode toggle with localStorage persistence
- **Friendly Alerts** - Kid-friendly error messages with emojis (e.g., "Tell me what you want to build! ✨")
- **Enhanced Auto Test** - QA tests now return detailed issues with exact code fixes and step-by-step instructions
- **Enhanced UX AI** - Detailed output with exact file locations, step-by-step fixes, code patches, and 12-year-old-friendly explanations
- **Always Valid JSON** - All endpoints now wrapped in try/except, ALWAYS return valid JSON (never HTML/text/tracebacks)
- **Safe JSON AI** - New safe_json_ai() function that validates AI responses and returns error JSON if invalid
- **Console Logging** - All endpoints print [ENDPOINT] logs showing success/failure for debugging
- **New /plan Endpoint** - Generates improvement plan with priorities, quick wins, and long-term goals
- **Endpoint Aliases** - /autotest, /ux, /seo, /competitors now work alongside existing paths
- **Auto-Test Simplified** - Simple HTTP fetch-based testing (no browser automation)
- **Fix Prompt Modal** - "Get Fix Prompt" buttons on all tasks with copy-paste prompts
- **Competitor Limit** - Maximum 2 competitors for cost efficiency
- **AI Optimization Layer** - smart_ai wrapper with caching, retries, and token management
- **Modern Tab Navigation** - SaaS-style interface with 6 tabs
- **Task State Persistence** - Checkbox state saved in localStorage per category

## Competitor AI Output Format

The `/competitor-ai` endpoint returns deep strategic competitive analysis with this structure:
```json
{
  "summary": "Strategic assessment of competitive position",
  "category_detected": "e.g., SaaS, Portfolio, E-commerce",
  "competitors_analyzed": [
    {
      "name": "Competitor Name",
      "url": "https://...",
      "key_features": ["specific feature 1", "specific feature 2"],
      "ux_strengths": ["specific UX advantage"],
      "what_to_copy": ["specific pattern or feature to implement"]
    }
  ],
  "feature_gaps": [
    {
      "title": "Missing Feature Name",
      "description": "What is missing and why it matters",
      "competitors_who_have_it": ["competitor1", "competitor2"],
      "priority": "high | medium | low",
      "why_you_need_it": "Business reason",
      "steps_to_fix": ["Step 1: ...", "Step 2: ..."],
      "code_fix": "```html\n<exact code>\n```",
      "files_to_modify": ["index.html"],
      "prompt_to_apply_fix": "Ready-to-use AI prompt"
    }
  ],
  "strengths": ["What target site does well vs competitors"],
  "weaknesses": ["Where target site falls short"],
  "business_opportunities": ["Strategic product direction ideas"],
  "final_recommendations": ["Most important changes to implement first"],
  "ai_tasks": [...],
  "fix_prompt": "Master prompt for all implementations"
}
```

## Build Flow (Expert + Child-Friendly Mode)

The `/workflow` endpoint generates COMPLETE build plans for any app idea, from simple todo apps to complex AI systems with multiple agents.

**Mode:** Single "expert but child-friendly" mode - plans like a senior architect, explains like a 12-year-old.

### JSON Output Format
```json
{
  "app_summary": "1-2 sentence overview in simple language",
  "tech_stack": {
    "frontend": "React or HTML/CSS/JS",
    "backend": "Python/FastAPI",
    "database": "PostgreSQL or Supabase",
    "ai": "OpenAI API or none",
    "storage": "Supabase Storage or local"
  },
  "directory_structure": ["main.py - The brain", "templates/ - Pages"],
  "phases": [
    {
      "id": "A",
      "name": "Phase A – Foundation",
      "description": "Setting up the basics!",
      "steps": [1, 2, 3]
    }
  ],
  "build_steps": [
    {
      "id": 1,
      "title": "Create the homepage",
      "area": "frontend | backend | database | ai_logic | integration | ux",
      "why_it_matters": "Simple reason for a 12-year-old",
      "files_to_edit": ["templates/index.html"],
      "micro_step_instructions": ["Step 1: ...", "Step 2: ..."],
      "replit_prompt": "Short prompt under 50 words",
      "validation_check": ["Check if page loads", "Check if button appears"]
    }
  ],
  "user_flow": ["Step 1: User does X", "Step 2: User sees Y"],
  "progress_hint": "Friendly sentence about progress"
}
```

### Build Phases
- **Phase A – Foundation**: Project structure, basic frontend/backend, routing, auth
- **Phase B – Core Data & Storage**: Database tables, storage setup, relationships
- **Phase C – File Upload & Organization**: Upload flows, file processing, organization
- **Phase D – AI Agents**: Agent logic, communication, database interactions
- **Phase E – Student Dashboard & UI**: Main views, lists, progress displays
- **Phase F – Lessons & Quizzes**: Content generation, scoring, feedback
- **Phase G – Quality & Polish**: Error states, loading states, basic tests

### Key Features
- Covers FULL architecture for complex systems (AI agents, dashboards, file uploads)
- 25-40 steps for complete MVP coverage
- Child-friendly explanations with professional engineering standards
- Cost-efficient Replit prompts under 50 words each
- Phase-based progress tracking with visual indicators
- Validation checks so users know when they're done
- Self-check: AI validates completeness before returning plan

## Next Steps

1. Create prompt generation in generate_prompts.py
2. Build task management in task_manager.py

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- httpx - HTTP client for fetching external URLs
- openai - OpenAI API client
- beautifulsoup4 - HTML parsing
