from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4


TASK_STATE_DIR_NAME = "task_states"
TASK_STATE_STATUSES = {"queued", "running", "succeeded", "failed"}


def create_task_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{uuid4().hex[:12]}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_task_state_path(output_dir: Path, task_id: str) -> Path:
    task_state_dir = output_dir.resolve().parent / TASK_STATE_DIR_NAME
    task_state_dir.mkdir(parents=True, exist_ok=True)
    return task_state_dir / f"{Path(task_id).name}.json"


def write_task_state(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    temp_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def init_task_state(
    path: Path,
    *,
    task_id: str,
    mode: str,
    paper_path: Path,
    template_path: Path | None,
) -> tuple[dict[str, Any], float]:
    now = utc_now_iso()
    state = {
        "task_id": task_id,
        "status": "running",
        "mode": mode,
        "created_at": now,
        "updated_at": now,
        "started_at": now,
        "finished_at": None,
        "duration_ms": 0,
        "input_files": {
            "paper_path": str(paper_path),
            "template_path": str(template_path) if template_path else None,
        },
        "output_files": {
            "formatted_docx": None,
            "report_json": None,
            "agent_trace_json": None,
        },
        "classification": None,
        "before_score": None,
        "after_score": None,
        "ai_used": None,
        "ai_score": None,
        "fallback_used": False,
        "error": None,
        "agent_trace_steps_count": 0,
    }
    write_task_state(path, state)
    return state, perf_counter()


def update_task_state(
    path: Path,
    state: dict[str, Any],
    *,
    status: str,
    started_at: float,
    result: dict[str, Any] | None = None,
    error: str | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    if status not in TASK_STATE_STATUSES:
        raise ValueError(f"invalid task state status: {status}")

    now = utc_now_iso()
    updated = dict(state)
    updated["status"] = status
    updated["updated_at"] = now
    updated["duration_ms"] = max(0, round((perf_counter() - started_at) * 1000))

    if status in {"succeeded", "failed"}:
        updated["finished_at"] = now

    if result:
        apply_result_fields(updated, result, output_dir=output_dir)

    if error:
        updated["error"] = error

    write_task_state(path, updated)
    return updated


def apply_result_fields(state: dict[str, Any], result: dict[str, Any], *, output_dir: Path | None) -> None:
    state["classification"] = result.get("classification")
    state["before_score"] = result.get("before_score")
    state["after_score"] = result.get("after_score")

    score_breakdown = result.get("score_breakdown") or {}
    if isinstance(score_breakdown, dict):
        state["ai_used"] = score_breakdown.get("ai_used")
        state["ai_score"] = score_breakdown.get("ai_score")

    trace = result.get("agent_trace")
    if isinstance(trace, list):
        state["agent_trace_steps_count"] = len(trace)
        state["fallback_used"] = any(bool(item.get("fallback_used")) for item in trace if isinstance(item, dict))

    filename = result.get("filename")
    if filename and output_dir:
        state["output_files"] = {
            **state.get("output_files", {}),
            "formatted_docx": str(output_dir / Path(str(filename)).name),
        }
