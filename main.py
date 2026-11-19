import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import store

app = FastAPI()


class RunRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/runs", status_code=202)
def create_run(req: RunRequest):
    run_id = str(uuid.uuid4())

    run = {
        "id": run_id,
        "question": req.question,
        "status": "queued",
        "answer": None,
        "steps": [],
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
    }

    store.save_run(run)
    store.enqueue(run_id)
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run