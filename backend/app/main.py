from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.use_cases.analyze_repo import execute_repo_analysis

app = FastAPI(title="RepoDoc API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repo_url: str


@app.post("/api/v1/repos/analyze")
async def analyze_repo(request: AnalyzeRequest):
    result = await execute_repo_analysis(request.repo_url)

    if result.get("status") == "error":
        raise HTTPException(status_code=422, detail=result.get("message", "Analysis failed."))

    return result
