# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import uuid
import threading
import queue
from typing import Any, Dict

from flask import current_app
from models import db, TextbookExample, SkillInfo
from core.gencode.services.component_tracker_service import _fetch_tracker_row
from core.gencode.services.gencode_status_query_service import (
    resolve_admin_project_root,
    inspect_component_production_sync,
)

def resolve_preview_component(example_id: int) -> Dict[str, Any]:
    """
    Resolve the preview source path and metadata for a given textbook example.
    """
    textbook_example = db.session.get(TextbookExample, example_id)
    if not textbook_example:
        raise ValueError("textbook_example_not_found")

    skill_id = str(textbook_example.skill_id or "").strip()
    if not skill_id:
        raise ValueError("missing_skill_id")

    skill_info = db.session.get(SkillInfo, skill_id)
    skill_name = skill_info.skill_ch_name if skill_info else skill_id

    raw_conn = db.engine.raw_connection()
    try:
        tracker = _fetch_tracker_row(raw_conn, textbook_example_id=example_id)
    finally:
        raw_conn.close()

    component_id = str((tracker or {}).get("component_id") or "").strip()
    if not component_id:
        from core.gencode.services.component_tracker_service import derive_component_id
        component_id = derive_component_id(example_id)

    project_root = resolve_admin_project_root(current_app.root_path)

    dryrun_generate = project_root / "reports/gencode_v3_dryrun" / skill_id / "components" / component_id / "generate.py"
    prod_generate = project_root / "agent_skills_v3" / skill_id / "components" / component_id / "generate.py"

    gencode_status = (tracker or {}).get("gencode_status")

    is_dryrun = False
    generate_path = None

    # Determine loading source
    if gencode_status == "verified" and dryrun_generate.is_file():
        generate_path = dryrun_generate
        is_dryrun = True
    elif prod_generate.is_file():
        generate_path = prod_generate
        is_dryrun = False
    else:
        raise FileNotFoundError("generate_file_not_found")

    # Production sync check
    induced_spec_payload = {}
    payload_raw = (tracker or {}).get("induced_spec_payload")
    if payload_raw:
        if isinstance(payload_raw, dict):
            induced_spec_payload = payload_raw
        else:
            try:
                induced_spec_payload = json.loads(str(payload_raw))
            except Exception:
                pass

    sync_status = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        textbook_example_id=example_id,
        tracker_payload=induced_spec_payload,
        tracker_updated_at=(tracker or {}).get("updated_at"),
        project_root=project_root,
    )
    production_contains_latest = sync_status.get("production_contains_latest", False)

    return {
        "textbook_example_id": example_id,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "component_id": component_id,
        "artifact_source": "dryrun" if is_dryrun else "production",
        "artifact_path": str(generate_path),
        "updated_at": (tracker or {}).get("updated_at"),
        "production_contains_latest": production_contains_latest,
    }

def _load_module_from_file_isolated(file_path: Path):
    module_name = f"preview_v3_{file_path.stem}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{file_path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_with_timeout(func, timeout_seconds=5.0, *args, **kwargs):
    q = queue.Queue()

    def worker():
        try:
            res = func(*args, **kwargs)
            q.put((True, res))
        except Exception as e:
            q.put((False, e))

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    try:
        success, val = q.get(timeout=timeout_seconds)
        if success:
            return val
        else:
            raise val
    except queue.Empty:
        raise TimeoutError("Execution timed out")

def generate_component_preview(example_id: int, seed: int = 42, timeout_seconds: float = 5.0) -> Dict[str, Any]:
    """
    Load the resolved generate.py component and call generate() safely under a timeout.
    """
    resolved = resolve_preview_component(example_id)
    artifact_path = resolved["artifact_path"]

    # Load module isolated
    module = _load_module_from_file_isolated(Path(artifact_path))
    generate_fn = getattr(module, "generate", None)
    if not callable(generate_fn):
        raise RuntimeError("generate_function_not_callable")

    # Run safely with timeout
    payload = run_with_timeout(generate_fn, timeout_seconds, seed=seed)
    if not isinstance(payload, dict):
        raise RuntimeError("generate_must_return_dict")

    # Extract required fields from response contract
    question_text = str(payload.get("question_text") or payload.get("question") or "").strip()
    choices = payload.get("choices")

    ac = payload.get("answer_contract") or {}
    answer_type = str(ac.get("answer_type") or payload.get("answer_type") or "").strip()
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    problem_type_id = str(
        payload.get("problem_type_id")
        or metadata.get("problem_type_id")
        or payload.get("problem_type")
        or ""
    ).strip()

    correct_answer = str(payload.get("correct_answer") or payload.get("answer") or "").strip()

    return {
        "success": True,
        "example_id": example_id,
        "skill_id": resolved["skill_id"],
        "component_id": resolved["component_id"],
        "artifact_source": resolved["artifact_source"],
        "artifact_path": artifact_path,
        "problem_type_id": problem_type_id,
        "question": {
            "question_text": question_text,
            "choices": choices if choices is not None else [],
            "answer_type": answer_type,
            "answer": correct_answer,
            "explanation": str(payload.get("explanation") or ""),
            "image_base64": str(payload.get("image_base64") or ""),
            "table_data": payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {},
            "subquestions": payload.get("subquestions") if isinstance(payload.get("subquestions"), list) else [],
            "visual_spec": payload.get("visual_spec") if isinstance(payload.get("visual_spec"), dict) else {},
        }
    }
