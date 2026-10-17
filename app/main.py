"""Inbound API của Travel Agent Hà Nội (Phần 1)."""
import json
import logging
import time
import uuid

from fastapi import FastAPI, Request

from app import config
from app.core.orchestrator import plan_trip
from app.domain.knowledge_repo import KnowledgeRepository
from app.schemas import TaskRequest

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("agent")

app = FastAPI(title="Hanoi Travel Agent", version="0.1.0")
repo = KnowledgeRepository(config.KNOWLEDGE_PATH)


def agent_card() -> dict:
    return {
        "agent_id": config.AGENT_ID,
        "group_id": config.GROUP_ID,
        "domain": "travel",
        "scope": "Hà Nội",
        "capabilities": ["search_destination", "estimate_budget", "build_itinerary", "plan_trip"],
        "endpoint": config.PUBLIC_URL,
        "status": "online",
    }


@app.middleware("http")
async def telemetry(request: Request, call_next):
    """Ghi log JSON cho mỗi request: correlation_id, latency, status (nền cho Telemetry port)."""
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = cid
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Correlation-ID"] = cid
    log.info(json.dumps({
        "agent_id": config.AGENT_ID, "correlation_id": cid, "method": request.method,
        "path": request.url.path, "status": response.status_code, "latency_ms": latency_ms,
    }, ensure_ascii=False))
    return response


@app.get("/health")
def health():
    return {"status": "ok", "agent_id": config.AGENT_ID, "knowledge_version": repo.version}


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return agent_card()


@app.post("/v1/tasks")
def create_task(req: TaskRequest, request: Request):
    result = plan_trip(repo, req)
    return {
        "message_id": str(uuid.uuid4()),
        "correlation_id": request.state.correlation_id,
        "agent_id": config.AGENT_ID,
        "status": "ok",
        "result": result,
    }
