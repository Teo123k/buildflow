from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.supabase_client import supabase
from models.project_model import ProjectCreateRequest

app = FastAPI()

# Allow frontend / Appsmith / Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running successfully"}

@app.post("/projects")
def create_project(payload: ProjectCreateRequest):
    data = {
        "title": payload.title,
        "description": payload.description,
        "platform": payload.platform
    }
    result = supabase.table("projects").insert(data).execute()
    return {"status": "success", "data": result.data}

@app.get("/projects")
def list_projects():
    result = supabase.table("projects").select("*").execute()
    return {"status": "success", "data": result.data}
