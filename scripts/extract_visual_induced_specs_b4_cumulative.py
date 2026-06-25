# -*- coding: utf-8 -*-
"""One-shot visual induced-spec extraction for B4 cumulative-frequency examples.

Gemini is used ONLY to read original textbook text/table/image and emit JSON spec.
Does NOT generate production generate.py or touch tracker/publish.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
EXAMPLE_IDS = [3830, 3831, 3832, 3833, 3834]
SCHEMA_VERSION = "visual_induced_spec.v1"
PROMPT_VERSION = "b4_cumulative_visual_extract.v1"
OUTPUT_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_induced_specs" / SKILL_ID

REQUIRED_TOP_LEVEL = {
    "example_id",
    "source_has_visual",
    "visual_type",
    "cumulative_direction",
    "question_target",
    "source_topology",
    "axis_spec",
    "table_spec",
    "graph_spec",
    "answer_dependencies",
    "mathematical_relations",
    "required_student_visible_elements",
    "source_isomorphism_constraints",
    "uncertainties",
    "confidence",
}

VISUAL_TYPES = {
    "cumulative_frequency_graph",
    "cumulative_frequency_table",
    "frequency_table_with_cumulative_fields",
    "mixed",
    "none",
}
CUMULATIVE_DIRECTIONS = {"less_than", "greater_than", "both", "not_applicable"}
QUESTION_TARGETS = {
    "read_cumulative_value",
    "construct_cumulative_table",
    "recover_class_frequency",
    "compare_intervals",
    "read_graph",
    "other",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_rows(example_ids: list[int]) -> dict[int, dict[str, Any]]:
    import sqlite3

    from core.gencode.services.v3_source_topology_service import parse_textbook_notes

    conn = sqlite3.connect(str(PROJECT_ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    rows: dict[int, dict[str, Any]] = {}
    for eid in example_ids:
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        if not row:
            raise SystemExit(f"textbook_example_id {eid} not found")
        data = dict(row)
        data["notes_parsed"] = parse_textbook_notes(data.get("notes"))
        rows[eid] = data
    conn.close()
    return rows


def _source_sha256(row: dict[str, Any]) -> str:
    payload = "".join(
        str(row.get(k) or "")
        for k in ("problem_text", "correct_answer", "detailed_solution", "source_description")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _attachment_paths(row: dict[str, Any]) -> list[str]:
    notes = row.get("notes_parsed") or {}
    paths: list[str] = []
    for asset in notes.get("image_assets") or []:
        if not isinstance(asset, dict):
            continue
        for key in ("path", "rel_path", "file_path", "image_path", "value"):
            val = str(asset.get(key) or "").strip()
            if val and not val.startswith("data:"):
                paths.append(val)
    return paths


def _resolve_existing_attachments(paths: list[str]) -> list[str]:
    found: list[str] = []
    for rel in paths:
        candidates = [
            PROJECT_ROOT / rel,
            PROJECT_ROOT / "static" / rel,
            PROJECT_ROOT / "uploads" / rel,
        ]
        for candidate in candidates:
            if candidate.is_file():
                found.append(str(candidate))
                break
    return found


def _audit_source(row: dict[str, Any]) -> dict[str, Any]:
    notes = row.get("notes_parsed") or {}
    problem_text = str(row.get("problem_text") or "")
    answer = str(row.get("correct_answer") or "").strip()
    attachment_paths = _attachment_paths(row)
    resolved_files = _resolve_existing_attachments(attachment_paths)
    has_image_flag = bool(notes.get("has_image"))
    missing_docx = bool(notes.get("missing_docx_image_asset"))
    data_omitted = "數據略" in problem_text
    image_pending = "圖片待補" in problem_text
    table_in_text = bool(
        re.search(r"成績[:：]", problem_text)
        or re.search(r"\b[abcd]\b", problem_text, flags=re.IGNORECASE)
        or re.search(r"\d+\s*[~～\-]\s*\d+\s*[\(（]\d+人", problem_text)
    )
    needs_graph = any(
        token in problem_text
        for token in ("折線圖", "累積次數分配折線圖", "如右圖", "如右所示")
    ) or ("如右" in problem_text and "表" not in problem_text)
    answer_missing = answer in {"", "略", "需視圖表數據而定"}

    blockers: list[str] = []
    if data_omitted:
        blockers.append("stem_data_omitted")
    if answer_missing:
        blockers.append("answer_not_verifiable")
    if needs_graph and (missing_docx or image_pending) and not resolved_files:
        blockers.append("required_graph_image_missing")
    if has_image_flag and missing_docx and not resolved_files and needs_graph:
        blockers.append("missing_docx_image_asset")
    if needs_graph and not table_in_text and not resolved_files and answer_missing:
        blockers.append("graph_only_without_attachments")

    text_table_complete = table_in_text and not data_omitted and not answer_missing
    graph_blockers = {
        "required_graph_image_missing",
        "missing_docx_image_asset",
        "graph_only_without_attachments",
    }
    if text_table_complete and not needs_graph:
        blockers = [b for b in blockers if b not in graph_blockers]

    eligible = len(blockers) == 0

    return {
        "example_id": int(row["id"]),
        "source_sha256": _source_sha256(row),
        "has_problem_text": bool(problem_text.strip()),
        "has_answer": bool(answer),
        "has_solution": bool(str(row.get("detailed_solution") or "").strip()),
        "has_image_flag": has_image_flag,
        "missing_docx_image_asset": missing_docx,
        "image_attachment_paths_declared": attachment_paths,
        "image_attachment_files_resolved": resolved_files,
        "table_embedded_in_text": table_in_text,
        "text_table_complete": text_table_complete,
        "needs_graph": needs_graph,
        "data_omitted_in_stem": data_omitted,
        "answer_verifiable": not answer_missing,
        "preflight_blockers": blockers,
        "gemini_eligible": eligible,
        "gemini_mode": "text_and_image" if resolved_files else ("text_only" if text_table_complete else "blocked"),
    }


def _build_prompt(row: dict[str, Any], audit: dict[str, Any]) -> str:
    return (
        "You are extracting a reusable VISUAL/TABLE induced specification from an original textbook item.\n"
        "Return STRICT JSON only. Do NOT output Python code.\n"
        "Distinguish: frequency polygon vs cumulative frequency polygon; below vs above cumulative;\n"
        "class midpoint vs class boundary; frequency vs cumulative frequency; adjacent cumulative difference.\n"
        "If the source does not confirm a field, put it in uncertainties and lower confidence.\n"
        "Never invent graph points or table numbers not supported by the provided source.\n\n"
        f"Schema version: {SCHEMA_VERSION}\n"
        f"example_id: {row['id']}\n"
        f"source_description: {row.get('source_description', '')}\n"
        f"problem_text: {row.get('problem_text', '')}\n"
        f"correct_answer: {row.get('correct_answer', '')}\n"
        f"detailed_solution: {row.get('detailed_solution', '')}\n"
        f"source_audit: {json.dumps(audit, ensure_ascii=False)}\n\n"
        "Required JSON keys:\n"
        "example_id, source_has_visual, visual_type, cumulative_direction, question_target,\n"
        "source_topology, axis_spec, table_spec, graph_spec, answer_dependencies,\n"
        "mathematical_relations, required_student_visible_elements, source_isomorphism_constraints,\n"
        "uncertainties, confidence\n"
    )


def _validate_spec(spec: dict[str, Any], *, audit: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"passed": False, "errors": ["spec_not_object"]}

    missing = sorted(REQUIRED_TOP_LEVEL - set(spec.keys()))
    if missing:
        errors.extend([f"missing_key:{k}" for k in missing])

    if str(spec.get("visual_type") or "") not in VISUAL_TYPES:
        errors.append("invalid_visual_type")
    if str(spec.get("cumulative_direction") or "") not in CUMULATIVE_DIRECTIONS:
        errors.append("invalid_cumulative_direction")
    if str(spec.get("question_target") or "") not in QUESTION_TARGETS:
        errors.append("invalid_question_target")

    confidence = spec.get("confidence")
    try:
        conf_val = float(confidence)
    except (TypeError, ValueError):
        conf_val = -1.0
        errors.append("invalid_confidence")
    if conf_val < 0.85:
        errors.append("confidence_below_gate")

    for field in ("answer_dependencies", "required_student_visible_elements"):
        val = spec.get(field)
        if not isinstance(val, list) or not val:
            errors.append(f"empty_{field}")

    raw = json.dumps(spec, ensure_ascii=False)
    if "def generate" in raw or "import " in raw:
        errors.append("contains_python_code")

    placeholders = ("TODO", "TBD", "placeholder", "待補", "未知", "unknown_value")
    if any(p in raw for p in placeholders) and conf_val >= 0.85:
        errors.append("unresolved_placeholder_at_high_confidence")

    # cumulative direction consistency
    stem = str(audit.get("problem_text_preview") or "")
    direction = str(spec.get("cumulative_direction") or "")
    if "以下累積" in stem and direction == "greater_than":
        errors.append("cumulative_direction_mismatch_below_stem")
    if "以上累積" in stem and direction == "less_than":
        errors.append("cumulative_direction_mismatch_above_stem")

    return {"passed": not errors, "errors": errors, "confidence": conf_val}


def _call_gemini(prompt: str, image_paths: list[str]) -> tuple[dict[str, Any] | None, str, str]:
    from core.ai_wrapper import resolve_gemini_api_key, get_ai_client

    api_key, _src = resolve_gemini_api_key()
    if not api_key:
        return None, "", "gemini_api_key_missing"

    client = get_ai_client("gencode")
    image_path = image_paths[0] if image_paths else None
    response = client.generate_content(prompt, image_path=image_path)
    text = str(getattr(response, "text", None) or response or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, text, f"json_parse_failed:{exc}"
    model_name = str(getattr(client, "model_name", "") or getattr(client, "model", "") or "gemini")
    return parsed, text, model_name


def _artifact_path(example_id: int) -> Path:
    return OUTPUT_ROOT / f"src_{example_id}_visual_induced_spec.json"


def _load_cached(example_id: int, source_sha: str) -> dict[str, Any] | None:
    path = _artifact_path(example_id)
    if not path.is_file():
        return None
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if (
        cached.get("source_sha256") == source_sha
        and cached.get("validation", {}).get("passed") is True
        and cached.get("generator_usable") is True
    ):
        return cached
    return None


def _blocked_artifact(row: dict[str, Any], audit: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "skill_id": SKILL_ID,
        "component_id": f"src_{row['id']}",
        "example_id": int(row["id"]),
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "extraction_timestamp": _utc_now(),
        "source_sha256": audit["source_sha256"],
        "gemini_model": None,
        "gemini_calls": 0,
        "status": "blocked_missing_source",
        "block_reason": reason,
        "source_audit": audit,
        "validation": {"passed": False, "errors": audit.get("preflight_blockers") or [reason]},
        "human_confirmed": False,
        "generator_usable": False,
        "spec": None,
    }


def extract_one(row: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    audit = _audit_source(row)
    audit["problem_text_preview"] = str(row.get("problem_text") or "")[:240]
    source_sha = audit["source_sha256"]

    if not force:
        cached = _load_cached(int(row["id"]), source_sha)
        if cached is not None:
            cached["cache_hit"] = True
            return cached

    if not audit["gemini_eligible"]:
        artifact = _blocked_artifact(
            row,
            audit,
            reason=";".join(audit.get("preflight_blockers") or ["not_eligible"]),
        )
        return artifact

    prompt = _build_prompt(row, audit)
    gemini_calls = 0
    repair_calls = 0
    spec: dict[str, Any] | None = None
    raw_text = ""
    model_name = ""
    last_error = ""

    for attempt in ("primary", "repair"):
        if attempt == "repair" and repair_calls >= 1:
            break
        gemini_calls += 1
        parsed, raw_text, model_name = _call_gemini(
            prompt if attempt == "primary" else (
                prompt
                + "\n\nPrevious JSON failed validation. Return corrected STRICT JSON only. Errors:\n"
                + last_error
            ),
            audit.get("image_attachment_files_resolved") or [],
        )
        if parsed is None:
            last_error = model_name
            if model_name == "gemini_api_key_missing":
                break
            if attempt == "primary":
                repair_calls += 1
            continue
        validation = _validate_spec(parsed, audit=audit)
        if validation["passed"]:
            spec = parsed
            last_error = ""
            break
        last_error = json.dumps(validation["errors"], ensure_ascii=False)
        if attempt == "primary":
            repair_calls += 1

    if spec is None:
        return {
            "skill_id": SKILL_ID,
            "component_id": f"src_{row['id']}",
            "example_id": int(row["id"]),
            "schema_version": SCHEMA_VERSION,
            "prompt_version": PROMPT_VERSION,
            "extraction_timestamp": _utc_now(),
            "source_sha256": source_sha,
            "gemini_model": model_name or None,
            "gemini_calls": gemini_calls,
            "repair_calls": repair_calls,
            "status": "gemini_failed_or_invalid",
            "source_audit": audit,
            "validation": {"passed": False, "errors": [last_error or "no_valid_spec"]},
            "human_confirmed": False,
            "generator_usable": False,
            "raw_gemini_text": raw_text[:4000],
            "spec": None,
        }

    conf = float(spec.get("confidence") or 0.0)
    return {
        "skill_id": SKILL_ID,
        "component_id": f"src_{row['id']}",
        "example_id": int(row["id"]),
        "schema_version": SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "extraction_timestamp": _utc_now(),
        "source_sha256": source_sha,
        "gemini_model": model_name,
        "gemini_calls": gemini_calls,
        "repair_calls": repair_calls,
        "status": "extracted",
        "source_audit": audit,
        "validation": _validate_spec(spec, audit=audit),
        "human_confirmed": False,
        "generator_usable": conf >= 0.85,
        "spec": spec,
    }


def write_artifacts(results: list[dict[str, Any]]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for item in results:
        path = _artifact_path(int(item["example_id"]))
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "skill_id": SKILL_ID,
        "generated_at": _utc_now(),
        "gemini_calls_total": sum(int(r.get("gemini_calls") or 0) for r in results),
        "repair_calls_total": sum(int(r.get("repair_calls") or 0) for r in results),
        "results": [
            {
                "example_id": r["example_id"],
                "status": r["status"],
                "gemini_calls": r.get("gemini_calls", 0),
                "generator_usable": r.get("generator_usable"),
                "block_reason": r.get("block_reason"),
            }
            for r in results
        ],
    }
    (OUTPUT_ROOT / "_extraction_run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Ignore validated cache")
    args = parser.parse_args()

    rows = _load_rows(EXAMPLE_IDS)
    results = [extract_one(rows[eid], force=args.force) for eid in EXAMPLE_IDS]
    write_artifacts(results)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
