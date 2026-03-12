from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from workflows.agent_workflow import AgentWorkflowService

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency in local dev
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parent / ".env")


class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, description="User question or task for the agent platform.")


class AskResponse(BaseModel):
    status: str
    result: dict[str, Any]


app = FastAPI(title="multi-agent-ai-platform", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
workflow_service = AgentWorkflowService()


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "multi-agent-ai-platform",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "workflow": "langgraph + crewai + autogen + langchain + chromadb",
    }


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    result = workflow_service.run(payload.query)
    return AskResponse(status="success", result=result)
