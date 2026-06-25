"""Read-only Gencode status query helpers for admin views."""

from __future__ import annotations

import sqlite3
import json
import ast
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]

NOT_CREATED_STATUS: dict[str, object] = {
    "status": "not_created",
    "component_id": None,
    "textbook_example_id": None,
    "presentation_mode": None,
    "problem_type_id": None,
    "has_payload": False,
    "error_log": None,
    "updated_at": None,
}

GENCODE_STATUS_LABELS: dict[str, str] = {
    "not_created": "未建立",
    "generating": "生成中",
    "draft_written": "草稿已寫入",
    "smoke_passed": "Smoke 通過",
    "verified": "已驗證",
    "failed": "失敗",
    "pending": "pending",
    "usable": "usable",
}

_STATUS_PRIORITY: dict[str, int] = {
    "not_created": 0,
    "pending": 1,
    "usable": 2,
    "generating": 3,
    "failed": 4,
    "draft_written": 5,
    "smoke_passed": 6,
    "verified": 7,
    "needs_human_review": 8,
}


def format_gencode_status_label(status: str) -> str:
    return GENCODE_STATUS_LABELS.get(str(status or "").strip(), str(status or "").strip() or "未建立")


TEACHER_V3_STATUS: dict[str, dict[str, object]] = {
    "not_generated": {
        "status_key": "not_generated",
        "label": "尚待驗證或尚未生成",
        "badge_class": "teacher-v3-not-generated",
        "icon": "⚪",
        "is_clickable": True,
    },
    "generating": {
        "status_key": "generating",
        "label": "生成中",
        "badge_class": "teacher-v3-generating",
        "icon": "🔵",
        "is_clickable": True,
    },
    "generated_not_packaged": {
        "status_key": "generated_not_packaged",
        "label": "已驗證／尚未封裝",
        "badge_class": "teacher-v3-generated-not-packaged",
        "icon": "🟡",
        "is_clickable": True,
    },
    "generation_incomplete": {
        "status_key": "generation_incomplete",
        "label": "生成未完成",
        "badge_class": "teacher-v3-generation-incomplete",
        "icon": "🟡",
        "is_clickable": True,
    },
    "failed": {
        "status_key": "failed",
        "label": "生成失敗",
        "badge_class": "teacher-v3-failed",
        "icon": "🔴",
        "is_clickable": True,
    },
    "published": {
        "status_key": "published",
        "label": "已經上線",
        "badge_class": "teacher-v3-published",
        "icon": "🟢",
        "is_clickable": True,
    },
    "unsupported": {
        "status_key": "unsupported",
        "label": "暫不支援",
        "badge_class": "teacher-v3-unsupported",
        "icon": "⚪",
        "is_clickable": True,
    },
}


def _teacher_status_payload(status_key: str) -> dict[str, object]:
    return dict(TEACHER_V3_STATUS.get(status_key, TEACHER_V3_STATUS["not_generated"]))


def resolve_teacher_facing_v3_status(
    *,
    gencode_status: str | None = None,
    has_tracker: bool = False,
    has_component: bool = False,
    has_generated_artifact: bool = False,
    integrity_gate_passed: bool | None = None,
    has_error: bool = False,
    production_contains_latest: bool = False,
) -> dict[str, object]:
    status = str(gencode_status or "").strip()
    if status == "unsupported":
        return _teacher_status_payload("unsupported")
    if has_error or status == "failed":
        return _teacher_status_payload("failed")
    if status in {"generating", "pending", "running", "queued"}:
        return _teacher_status_payload("generating")
    if status == "draft_written":
        if production_contains_latest:
            return _teacher_status_payload("published")
        if has_generated_artifact or integrity_gate_passed is True:
            return _teacher_status_payload("generated_not_packaged")
        return _teacher_status_payload("generation_incomplete")
    if status in {"verified", "smoke_passed"}:
        if production_contains_latest:
            return _teacher_status_payload("published")
        return _teacher_status_payload("generated_not_packaged")
    if status in {"draft", "pending"} or status.startswith("draft"):
        return _teacher_status_payload("not_generated")
    if has_tracker and (has_generated_artifact or has_component):
        if production_contains_latest:
            return _teacher_status_payload("published")
        return _teacher_status_payload("generated_not_packaged")
    if not has_tracker and not has_component and not has_generated_artifact:
        return _teacher_status_payload("not_generated")
    if status in {"not_created", "", "none"}:
        return _teacher_status_payload("not_generated")
    return _teacher_status_payload("generating")


def _payload_integrity_gate_passed(payload_raw: Any) -> bool | None:
    if payload_raw is None or str(payload_raw).strip() == "":
        return None
    try:
        payload = json.loads(str(payload_raw))
    except Exception:
        return None
    if not isinstance(payload, dict) or "integrity_gate_passed" not in payload:
        return None
    return bool(payload.get("integrity_gate_passed"))


def _parse_payload_dict(payload_raw: Any) -> dict[str, object]:
    if payload_raw is None or str(payload_raw).strip() == "":
        return {}
    if isinstance(payload_raw, dict):
        return payload_raw
    try:
        payload = json.loads(str(payload_raw))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_sha256(path: Path | None) -> str | None:
    if not path or not path.is_file():
        return None
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _timestamp_or_none(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, datetime):
        try:
            return value.timestamp()
        except Exception:
            return None
    text = str(value).strip().replace("Z", "+00:00")
    for candidate in (text, text.replace(" ", "T", 1)):
        try:
            return datetime.fromisoformat(candidate).timestamp()
        except Exception:
            continue
    return None


def _read_generator_specs(init_path: Path) -> list[dict[str, object]]:
    if not init_path.is_file():
        return []
    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "GENERATOR_SPECS" for target in node.targets)
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            return []
        if not isinstance(value, list):
            return []
        return [row for row in value if isinstance(row, dict)]
    return []


def load_v3_skill_generator_specs(
    *,
    skill_id: str,
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> list[dict[str, object]]:
    skill_key = str(skill_id or "").strip()
    if not skill_key:
        return []
    production_root = _resolve_base_path(production_base_dir, project_root)
    return _read_generator_specs(production_root / skill_key / "__init__.py")


def _production_specs_contains_component(
    specs: list[dict[str, object]],
    *,
    component_id: str,
    textbook_example_id: int | None,
) -> bool:
    for spec in specs:
        if str(spec.get("component_id") or "").strip() != component_id:
            continue
        if textbook_example_id is None:
            return True
        try:
            spec_example_id = int(spec.get("textbook_example_id"))
        except Exception:
            return True
        if spec_example_id == textbook_example_id:
            return True
    return False


def inspect_component_production_sync(
    *,
    skill_id: str,
    component_id: str | None,
    textbook_example_id: int | None = None,
    tracker_payload: Any = None,
    tracker_updated_at: Any = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> dict[str, object]:
    skill_key = str(skill_id or "").strip()
    component_key = str(component_id or "").strip()
    if not skill_key or not component_key:
        return {
            "production_contains_latest": False,
            "production_sync_method": "missing_component_id",
            "production_sync_reason": "missing_skill_or_component_id",
            "verified_component_hash": None,
            "production_component_hash": None,
            "published_component_hash": None,
        }

    dryrun_root = _resolve_base_path(dryrun_base_dir, project_root)
    production_root = _resolve_base_path(production_base_dir, project_root)
    verified_generate = dryrun_root / skill_key / "components" / component_key / "generate.py"
    production_generate = production_root / skill_key / "components" / component_key / "generate.py"
    verified_hash = _file_sha256(verified_generate)
    production_hash = _file_sha256(production_generate)
    payload = _parse_payload_dict(tracker_payload)
    published_hash = str(payload.get("published_generate_sha256") or "").strip() or None
    payload_verified_hash = str(payload.get("verified_generate_sha256") or "").strip() or None
    verified_artifact_path = str(payload.get("verified_artifact_path") or "").strip()
    verified_artifact_hash = None
    if verified_artifact_path:
        artifact_path = Path(verified_artifact_path)
        if not artifact_path.is_absolute():
            root = Path(project_root) if project_root is not None and str(project_root).strip() else PROJECT_ROOT
            artifact_path = root / artifact_path
        verified_artifact_hash = _file_sha256(artifact_path)

    if published_hash and production_hash and published_hash == production_hash:
        return {
            "production_contains_latest": True,
            "production_sync_method": "tracker_published_generate_sha256",
            "production_sync_reason": None,
            "verified_component_hash": verified_hash or payload_verified_hash or verified_artifact_hash,
            "production_component_hash": production_hash,
            "published_component_hash": published_hash,
            "verified_component_path": str(verified_generate),
            "production_component_path": str(production_generate),
        }
    if payload_verified_hash and production_hash and payload_verified_hash == production_hash:
        return {
            "production_contains_latest": True,
            "production_sync_method": "tracker_verified_generate_sha256",
            "production_sync_reason": None,
            "verified_component_hash": payload_verified_hash,
            "production_component_hash": production_hash,
            "published_component_hash": published_hash,
            "verified_component_path": str(verified_generate),
            "production_component_path": str(production_generate),
        }
    if verified_artifact_hash and production_hash and verified_artifact_hash == production_hash:
        return {
            "production_contains_latest": True,
            "production_sync_method": "tracker_verified_artifact_path_sha256",
            "production_sync_reason": None,
            "verified_component_hash": verified_artifact_hash,
            "production_component_hash": production_hash,
            "published_component_hash": published_hash,
            "verified_component_path": str(verified_artifact_path),
            "production_component_path": str(production_generate),
        }
    if verified_hash and production_hash and verified_hash == production_hash:
        return {
            "production_contains_latest": True,
            "production_sync_method": "current_dryrun_generate_sha256",
            "production_sync_reason": None,
            "verified_component_hash": verified_hash,
            "production_component_hash": production_hash,
            "published_component_hash": published_hash,
            "verified_component_path": str(verified_generate),
            "production_component_path": str(production_generate),
        }

    specs = load_v3_skill_generator_specs(
        skill_id=skill_key,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    specs_match = _production_specs_contains_component(
        specs,
        component_id=component_key,
        textbook_example_id=textbook_example_id,
    )
    tracker_ts = _timestamp_or_none(tracker_updated_at)
    production_ts = None
    if production_generate.is_file():
        production_ts = production_generate.stat().st_mtime
        init_path = production_root / skill_key / "__init__.py"
        if init_path.is_file():
            production_ts = max(production_ts, init_path.stat().st_mtime)
    if production_hash and specs_match and tracker_ts is not None and production_ts is not None and production_ts >= tracker_ts:
        return {
            "production_contains_latest": True,
            "production_sync_method": "legacy_generator_specs_component_match",
            "production_sync_reason": None,
            "verified_component_hash": verified_hash or payload_verified_hash or verified_artifact_hash,
            "production_component_hash": production_hash,
            "published_component_hash": published_hash,
            "verified_component_path": str(verified_generate),
            "production_component_path": str(production_generate),
        }

    reason = "hash_mismatch"
    if not production_hash:
        reason = "production_generate_missing"
    elif not (verified_hash or payload_verified_hash or verified_artifact_hash or published_hash):
        reason = "missing_verified_or_published_hash"
    elif not specs_match:
        reason = "production_manifest_missing_component"
    elif tracker_ts is not None and production_ts is not None and production_ts < tracker_ts:
        reason = "production_older_than_tracker"
    return {
        "production_contains_latest": False,
        "production_sync_method": "not_synced",
        "production_sync_reason": reason,
        "verified_component_hash": verified_hash,
        "production_component_hash": production_hash,
        "published_component_hash": published_hash,
        "verified_component_path": str(verified_generate),
        "production_component_path": str(production_generate),
    }


def _tracker_table_exists(conn: sqlite3.Connection) -> bool:
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='gencode_component_tracker'"
        ).fetchone()
        return row is not None
    except Exception:
        return False


def _row_value(row: Any, key: str, index: int) -> Any:
    if hasattr(row, "keys"):
        return row[key]
    return row[index]


def _normalize_example_ids(textbook_example_ids: list[int]) -> list[int]:
    normalized: list[int] = []
    seen: set[int] = set()
    for raw_id in textbook_example_ids:
        if isinstance(raw_id, bool) or not isinstance(raw_id, int):
            continue
        if raw_id in seen:
            continue
        seen.add(raw_id)
        normalized.append(raw_id)
    return sorted(normalized)


def _extract_payload_summary(payload_raw: Any) -> dict[str, object]:
    if payload_raw is None or str(payload_raw).strip() == "":
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    try:
        payload = json.loads(str(payload_raw))
    except Exception:
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    if not isinstance(payload, dict):
        return {
            "presentation_mode": None,
            "problem_type_id": None,
        }
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    return {
        "presentation_mode": (
            payload.get("presentation_mode")
            or metadata.get("presentation_mode")
            or payload.get("mode")
        ),
        "problem_type_id": (
            payload.get("problem_type_id")
            or metadata.get("problem_type_id")
            or payload.get("problem_type")
        ),
    }


def get_gencode_status_for_examples(
    conn: sqlite3.Connection,
    textbook_example_ids: list[int],
) -> dict[int, dict[str, object]]:
    """Read tracker rows for textbook examples without mutating the database."""
    example_ids = _normalize_example_ids(textbook_example_ids)
    result: dict[int, dict[str, object]] = {
        example_id: dict(NOT_CREATED_STATUS) for example_id in example_ids
    }
    if not example_ids or not _tracker_table_exists(conn):
        return result

    placeholders = ",".join("?" for _ in example_ids)
    rows = conn.execute(
        f"""
        SELECT textbook_example_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE textbook_example_id IN ({placeholders})
        ORDER BY textbook_example_id ASC, component_id ASC
        """,
        example_ids,
    ).fetchall()

    for row in rows:
        example_id = int(_row_value(row, "textbook_example_id", 0))
        payload_raw = _row_value(row, "induced_spec_payload", 3)
        payload_summary = _extract_payload_summary(payload_raw)
        result[example_id] = {
            "status": str(_row_value(row, "gencode_status", 2)),
            "component_id": str(_row_value(row, "component_id", 1)),
            "textbook_example_id": example_id,
            **payload_summary,
            "induced_spec_payload": payload_raw,
            "has_payload": payload_raw is not None and str(payload_raw).strip() != "",
            "error_log": _row_value(row, "gencode_error_log", 4),
            "updated_at": _row_value(row, "updated_at", 5),
        }
    return result


def _resolve_base_path(base_dir: str, project_root: str | Path | None) -> Path:
    base_path = Path(str(base_dir or "").strip())
    if base_path.is_absolute():
        return base_path
    if project_root is not None and str(project_root).strip():
        return Path(project_root) / base_path
    return PROJECT_ROOT / base_path


def inspect_gencode_files(
    *,
    skill_id: str,
    component_id: str | None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
    include_manifest: bool = True,
) -> dict[str, object]:
    """Read-only filesystem probes for dryrun and production component artifacts."""
    skill_key = str(skill_id or "").strip()
    component_key = str(component_id or "").strip()

    dryrun_root = _resolve_base_path(dryrun_base_dir, project_root)
    production_root = _resolve_base_path(production_base_dir, project_root)

    dryrun_component_dir = (
        dryrun_root / skill_key / "components" / component_key if component_key else None
    )
    production_component_dir = (
        production_root / skill_key / "components" / component_key if component_key else None
    )

    return {
        "dryrun_component_exists": bool(dryrun_component_dir and dryrun_component_dir.is_dir()),
        "dryrun_generate_exists": bool(
            dryrun_component_dir and (dryrun_component_dir / "generate.py").is_file()
        ),
        "dryrun_manifest_exists": (dryrun_root / skill_key / "component_manifest.json").is_file() if include_manifest else False,
        "production_component_exists": bool(
            production_component_dir and production_component_dir.is_dir()
        ),
        "production_generate_exists": bool(
            production_component_dir and (production_component_dir / "generate.py").is_file()
        ),
        "production_manifest_exists": (
            production_root / skill_key / "component_manifest.json"
        ).is_file() if include_manifest else False,
    }


def inspect_skill_production_files(
    *,
    skill_id: str,
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> dict[str, object]:
    """Read-only skill-level production probes for admin status summaries."""
    skill_key = str(skill_id or "").strip()
    root = Path(project_root) if project_root is not None and str(project_root).strip() else PROJECT_ROOT
    wrapper_path = root / "skills" / f"{skill_key}.py"
    v3_skill_dir = _resolve_base_path(production_base_dir, project_root) / skill_key
    
    wrapper_exists = wrapper_path.is_file()
    v3_skill_exists = v3_skill_dir.is_dir()
    if not v3_skill_exists:
        return {
            "production_wrapper_exists": wrapper_exists,
            "v3_package_exists": False,
            "generator_specs_count": 0,
            "production_component_count": 0,
        }

    components_dir = v3_skill_dir / "components"
    generator_specs_count = 0
    production_component_count = 0

    if components_dir.is_dir():
        production_component_count = sum(
            1 for component_dir in components_dir.iterdir()
            if component_dir.is_dir() and (component_dir / "generate.py").is_file()
        )

    init_path = v3_skill_dir / "__init__.py"
    if init_path.is_file():
        try:
            text = init_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text)
            for node in tree.body:
                if (
                    isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "GENERATOR_SPECS" for target in node.targets)
                    and isinstance(node.value, (ast.List, ast.Tuple))
                ):
                    generator_specs_count = len(node.value.elts)
                    break
        except Exception:
            generator_specs_count = 0

    return {
        "production_wrapper_exists": wrapper_path.is_file(),
        "v3_package_exists": v3_skill_dir.is_dir() and init_path.is_file(),
        "generator_specs_count": generator_specs_count,
        "production_component_count": production_component_count,
    }


def _bool_label(value: bool) -> str:
    return "是" if value else "否"


def build_admin_example_gencode_status_view(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    skill_id: str,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[str, object]:
    tracker_status = get_gencode_status_for_examples(conn, [textbook_example_id]).get(
        textbook_example_id,
        dict(NOT_CREATED_STATUS),
    )
    file_status = inspect_gencode_files(
        skill_id=skill_id,
        component_id=str(tracker_status.get("component_id") or "") or None,
        dryrun_base_dir=dryrun_base_dir,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    sync_status = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=str(tracker_status.get("component_id") or "") or None,
        textbook_example_id=textbook_example_id,
        tracker_payload=tracker_status.get("induced_spec_payload"),
        tracker_updated_at=tracker_status.get("updated_at"),
        dryrun_base_dir=dryrun_base_dir,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    status = str(tracker_status.get("status", "not_created"))
    v_hash = sync_status.get("verified_component_hash")
    payload = _parse_payload_dict(tracker_status.get("induced_spec_payload"))
    p_hash = str(payload.get("verified_generate_sha256") or "").strip() or None
    if status in {"verified", "smoke_passed"} and p_hash and v_hash and p_hash != v_hash:
        status = "pending"
    error_log = tracker_status.get("error_log")
    payload_raw = tracker_status.get("induced_spec_payload")
    from core.gencode.services.v3_skill_coverage_service import _payload_error_code
    from core.gencode.v3_error_codes import UNSUPPORTED_TASK_TYPE
    error_code = _payload_error_code(payload_raw, error_log)
    if error_code == UNSUPPORTED_TASK_TYPE or status == "unsupported":
        status = "unsupported"
    has_payload = bool(tracker_status.get("has_payload"))
    has_tracker = bool(tracker_status.get("component_id")) or status not in {"not_created", ""}
    teacher_status = resolve_teacher_facing_v3_status(
        gencode_status=status,
        has_tracker=has_tracker,
        has_component=bool(file_status.get("dryrun_component_exists") or file_status.get("production_component_exists")),
        has_generated_artifact=bool(file_status.get("dryrun_generate_exists") or file_status.get("production_generate_exists")),
        integrity_gate_passed=_payload_integrity_gate_passed(tracker_status.get("induced_spec_payload")),
        has_error=bool(tracker_status.get("error_log")),
        production_contains_latest=bool(sync_status.get("production_contains_latest")),
    )
    return {
        **tracker_status,
        **file_status,
        **sync_status,
        "teacher_status": teacher_status,
        "status_label": format_gencode_status_label(status),
        "has_payload_label": "有" if has_payload else "無",
        "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
        "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
    }


def build_admin_examples_gencode_status_map(
    conn: sqlite3.Connection,
    examples: list[tuple[int, str]],
    *,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
) -> dict[int, dict[str, object]]:
    example_ids = [example_id for example_id, _skill_id in examples]
    base_map = get_gencode_status_for_examples(conn, example_ids)
    status_map: dict[int, dict[str, object]] = {}
    for example_id, skill_id in examples:
        tracker_status = base_map.get(example_id, dict(NOT_CREATED_STATUS))
        file_status = inspect_gencode_files(
            skill_id=skill_id,
            component_id=str(tracker_status.get("component_id") or "") or None,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        sync_status = inspect_component_production_sync(
            skill_id=skill_id,
            component_id=str(tracker_status.get("component_id") or "") or None,
            textbook_example_id=example_id,
            tracker_payload=tracker_status.get("induced_spec_payload"),
            tracker_updated_at=tracker_status.get("updated_at"),
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        status = str(tracker_status.get("status", "not_created"))
        v_hash = sync_status.get("verified_component_hash")
        payload = _parse_payload_dict(tracker_status.get("induced_spec_payload"))
        p_hash = str(payload.get("verified_generate_sha256") or "").strip() or None
        if status in {"verified", "smoke_passed"} and p_hash and v_hash and p_hash != v_hash:
            status = "pending"
        error_log = tracker_status.get("error_log")
        payload_raw = tracker_status.get("induced_spec_payload")
        from core.gencode.services.v3_skill_coverage_service import _payload_error_code
        from core.gencode.v3_error_codes import UNSUPPORTED_TASK_TYPE
        error_code = _payload_error_code(payload_raw, error_log)
        if error_code == UNSUPPORTED_TASK_TYPE or status == "unsupported":
            status = "unsupported"
        has_payload = bool(tracker_status.get("has_payload"))
        has_tracker = bool(tracker_status.get("component_id")) or status not in {"not_created", ""}
        teacher_status = resolve_teacher_facing_v3_status(
            gencode_status=status,
            has_tracker=has_tracker,
            has_component=bool(file_status.get("dryrun_component_exists") or file_status.get("production_component_exists")),
            has_generated_artifact=bool(file_status.get("dryrun_generate_exists") or file_status.get("production_generate_exists")),
            integrity_gate_passed=_payload_integrity_gate_passed(tracker_status.get("induced_spec_payload")),
            has_error=bool(tracker_status.get("error_log")),
            production_contains_latest=bool(sync_status.get("production_contains_latest")),
        )
        status_map[example_id] = {
            **tracker_status,
            **file_status,
            **sync_status,
            "teacher_status": teacher_status,
            "status_label": format_gencode_status_label(status),
            "has_payload_label": "有" if has_payload else "無",
            "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
            "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
        }
    return status_map


def _get_tracker_rows_for_skill(conn: sqlite3.Connection, skill_id: str) -> list[dict[str, object]]:
    if not _tracker_table_exists(conn):
        return []
    rows = conn.execute(
        """
        SELECT textbook_example_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE skill_id = ?
        ORDER BY textbook_example_id ASC, component_id ASC
        """,
        (str(skill_id or "").strip(),),
    ).fetchall()
    parsed: list[dict[str, object]] = []
    for row in rows:
        payload_raw = _row_value(row, "induced_spec_payload", 3)
        payload_summary = _extract_payload_summary(payload_raw)
        parsed.append(
            {
                "textbook_example_id": int(_row_value(row, "textbook_example_id", 0)),
                "component_id": str(_row_value(row, "component_id", 1)),
                "status": str(_row_value(row, "gencode_status", 2)),
                **payload_summary,
                "induced_spec_payload": payload_raw,
                "has_payload": payload_raw is not None and str(payload_raw).strip() != "",
                "error_log": _row_value(row, "gencode_error_log", 4),
                "updated_at": _row_value(row, "updated_at", 5),
            }
        )
    return parsed


def build_admin_skill_gencode_status_view(
    conn: sqlite3.Connection,
    *,
    skill_id: str,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    audit_variation: bool = False,
) -> dict[str, object]:
    from core.gencode.services.v3_skill_coverage_service import (
        build_coverage_warnings,
        get_v3_skill_component_coverage,
    )
    from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility

    coverage = get_v3_skill_component_coverage(conn, skill_id)
    eligibility = evaluate_v3_publish_eligibility(conn, skill_id, coverage=coverage)
    coverage_warnings = build_coverage_warnings(coverage)
    rows = _get_tracker_rows_for_skill(conn, skill_id)
    if not rows:
        view = dict(NOT_CREATED_STATUS)
        file_status = inspect_gencode_files(
            skill_id=skill_id,
            component_id=None,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        status = "not_created"
        has_payload = False
        component_id = None
        error_log = None
        updated_at = None
        component_count = 0
    else:
        primary = max(rows, key=lambda row: _STATUS_PRIORITY.get(str(row["status"]), 0))
        status = str(primary["status"])
        component_id = ", ".join(str(row["component_id"]) for row in rows)
        has_payload = any(bool(row["has_payload"]) for row in rows)
        error_logs = [str(row["error_log"]) for row in rows if row.get("error_log")]
        error_log = error_logs[0] if error_logs else None
        updated_values = [str(row["updated_at"]) for row in rows if row.get("updated_at")]
        updated_at = max(updated_values) if updated_values else None
        component_count = len(rows)
        file_status = {
            "dryrun_component_exists": False,
            "dryrun_generate_exists": False,
            "dryrun_manifest_exists": inspect_gencode_files(
                skill_id=skill_id,
                component_id=None,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )["dryrun_manifest_exists"],
            "production_component_exists": False,
            "production_generate_exists": False,
            "production_manifest_exists": inspect_gencode_files(
                skill_id=skill_id,
                component_id=None,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )["production_manifest_exists"],
        }
        for row in rows:
            probes = inspect_gencode_files(
                skill_id=skill_id,
                component_id=str(row["component_id"]),
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                project_root=project_root,
            )
            for key in (
                "dryrun_component_exists",
                "dryrun_generate_exists",
                "production_component_exists",
                "production_generate_exists",
            ):
                file_status[key] = bool(file_status[key]) or bool(probes[key])

    missing_tracker_ids = [
        row["textbook_example_id"]
        for row in coverage.get("examples", [])
        if isinstance(row, dict) and row.get("status") == "missing_tracker"
    ]

    prod_info = inspect_skill_production_files(
        skill_id=skill_id,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    has_production = prod_info.get("production_wrapper_exists")
    has_published_package = bool(
        prod_info.get("v3_package_exists")
        and int(prod_info.get("production_component_count") or 0) > 0
    )
    source_type = "production" if has_production else "dryrun"
    total_examples = int(coverage.get("total_examples") or 0)
    verified_count = int(coverage.get("verified_count") or 0)
    published_component_ids: set[str] = set()
    stale_count = 0
    for row in rows:
        row_status = str(row.get("status"))
        sync_status = inspect_component_production_sync(
            skill_id=skill_id,
            component_id=str(row.get("component_id") or "") or None,
            textbook_example_id=int(row.get("textbook_example_id")),
            tracker_payload=row.get("induced_spec_payload"),
            tracker_updated_at=row.get("updated_at"),
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
        )
        if row_status in {"verified", "smoke_passed"}:
            v_hash = sync_status.get("verified_component_hash")
            payload = _parse_payload_dict(row.get("induced_spec_payload"))
            p_hash = str(payload.get("verified_generate_sha256") or "").strip() or None
            if p_hash and v_hash and p_hash != v_hash:
                row_status = "pending"
                stale_count += 1
        if row_status != "verified":
            continue
        if bool(sync_status.get("production_contains_latest")):
            published_component_ids.add(str(row.get("component_id")))
    verified_count = max(0, verified_count - stale_count)
    published_count = len(published_component_ids)
    generated_not_packaged_count = max(0, verified_count - published_count)
    failed_count = sum(1 for row in rows if str(row.get("status")) == "failed" or row.get("error_log"))
    # Map 'partially_published' status payload
    partially_published_payload = {
        "status_key": "partially_published",
        "label": f"部分上線 ({published_count}/{total_examples})",
        "badge_class": "teacher-v3-partially-published",
        "icon": "🟡",
        "is_clickable": True,
    }

    if published_count == total_examples and total_examples > 0 and generated_not_packaged_count == 0:
        teacher_status = _teacher_status_payload("published")
        teacher_status["label"] = "全部上線"
    elif published_count > 0:
        teacher_status = partially_published_payload
    elif failed_count > 0 and verified_count == 0:
        teacher_status = _teacher_status_payload("failed")
    elif verified_count > 0:
        teacher_status = _teacher_status_payload("generated_not_packaged")
    elif bool(file_status.get("dryrun_generate_exists") or file_status.get("production_generate_exists")):
        teacher_status = _teacher_status_payload("generated_not_packaged")
    elif any(str(row.get("status")) in {"generating", "pending"} for row in rows):
        teacher_status = _teacher_status_payload("generating")
    elif rows:
        teacher_status = _teacher_status_payload("generation_incomplete")
    else:
        teacher_status = _teacher_status_payload("not_generated")

    variation_report = {}
    if audit_variation and verified_count > 0:
        from core.gencode.services.v3_variation_audit_service import audit_skill_variation
        try:
            variation_report = audit_skill_variation(
                skill_id=skill_id,
                source=source_type,
                project_root=project_root,
                conn=conn,
            )
        except Exception:
            pass

    return {
        "status": status,
        "status_label": format_gencode_status_label(status),
        "component_id": component_id,
        "component_count": component_count,
        "has_payload": has_payload,
        "has_payload_label": "有" if has_payload else "無",
        "error_log": error_log,
        "updated_at": updated_at,
        "coverage": coverage,
        "coverage_summary": (
            f"V3: {coverage.get('verified_count', 0)}/{coverage.get('total_examples', 0)} verified"
        ),
        "total_examples": int(coverage.get("total_examples") or 0),
        "verified_count": verified_count,
        "available_count": verified_count,
        "published_count": published_count,
        "generated_not_packaged_count": generated_not_packaged_count,
        "failed_count": failed_count,
        "unsupported_count": int(coverage.get("unsupported_count") or 0),
        "missing_tracker_count": len(missing_tracker_ids),
        "coverage_missing_ids": missing_tracker_ids,
        "coverage_warnings": coverage_warnings,
        "publish_ready": bool(coverage.get("publish_ready")),
        "publish_eligibility": eligibility,
        "publish_eligible": bool(eligibility.get("allowed")),
        "publish_ineligible_reason": eligibility.get("reason"),
        "teacher_status": teacher_status,
        **file_status,
        **prod_info,
        "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
        "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
        "variation_status": variation_report.get("status"),
        "dynamic_count": variation_report.get("dynamic_count", 0),
        "static_count": variation_report.get("static_count", 0),
        "partially_dynamic_count": variation_report.get("partially_dynamic_count", 0),
        "variation_warning": variation_report.get("variation_warning", ""),
    }


def _fetch_batch_tracker_rows_for_skills(
    conn: sqlite3.Connection,
    skill_ids: list[str],
) -> dict[str, list[dict[str, object]]]:
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys or not _tracker_table_exists(conn):
        return {key: [] for key in keys}
    placeholders = ",".join("?" for _ in keys)
    rows = conn.execute(
        f"""
        SELECT skill_id, textbook_example_id, component_id, gencode_status,
               induced_spec_payload, gencode_error_log, updated_at
        FROM gencode_component_tracker
        WHERE skill_id IN ({placeholders})
        ORDER BY skill_id ASC, textbook_example_id ASC, component_id ASC
        """,
        keys,
    ).fetchall()
    grouped: dict[str, list[dict[str, object]]] = {key: [] for key in keys}
    for row in rows:
        skill_key = str(_row_value(row, "skill_id", 0))
        payload_raw = _row_value(row, "induced_spec_payload", 4)
        payload_summary = _extract_payload_summary(payload_raw)
        grouped.setdefault(skill_key, []).append(
            {
                "textbook_example_id": int(_row_value(row, "textbook_example_id", 1)),
                "component_id": str(_row_value(row, "component_id", 2)),
                "status": str(_row_value(row, "gencode_status", 3)),
                **payload_summary,
                "induced_spec_payload": payload_raw,
                "has_payload": payload_raw is not None and str(payload_raw).strip() != "",
                "error_log": _row_value(row, "gencode_error_log", 5),
                "updated_at": _row_value(row, "updated_at", 6),
            }
        )
    return grouped


def _batch_inspect_skill_production_files(
    skill_ids: list[str],
    *,
    production_base_dir: str = "agent_skills_v3",
    project_root: str | Path | None = None,
) -> dict[str, dict[str, object]]:
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys:
        return {}
    root = Path(project_root) if project_root is not None and str(project_root).strip() else PROJECT_ROOT
    skills_dir = root / "skills"
    production_root = _resolve_base_path(production_base_dir, project_root)
    wrapper_ids = (
        {path.stem for path in skills_dir.glob("*.py")}
        if skills_dir.is_dir()
        else set()
    )
    result: dict[str, dict[str, object]] = {}
    for skill_key in keys:
        v3_skill_dir = production_root / skill_key
        init_path = v3_skill_dir / "__init__.py"
        components_dir = v3_skill_dir / "components"
        production_component_count = 0
        if components_dir.is_dir():
            production_component_count = sum(
                1
                for component_dir in components_dir.iterdir()
                if component_dir.is_dir() and (component_dir / "generate.py").is_file()
            )
        result[skill_key] = {
            "production_wrapper_exists": skill_key in wrapper_ids,
            "v3_package_exists": v3_skill_dir.is_dir() and init_path.is_file(),
            "generator_specs_count": production_component_count,
            "production_component_count": production_component_count,
        }
    return result


def _lite_published_component_count(
    skill_key: str,
    tracker_rows: list[dict[str, object]],
    production_root: Path,
) -> int:
    published = 0
    for row in tracker_rows:
        if str(row.get("status")) != "verified":
            continue
        component_id = str(row.get("component_id") or "").strip()
        if not component_id:
            continue
        if (production_root / skill_key / "components" / component_id / "generate.py").is_file():
            published += 1
    return published


def _resolve_skill_level_teacher_status(
    *,
    total_examples: int,
    verified_count: int,
    failed_count: int,
    published_count: int,
    generated_not_packaged_count: int,
    tracker_rows: list[dict[str, object]],
    prod_info: dict[str, object],
    file_status: dict[str, object],
) -> dict[str, object]:
    partially_published_payload = {
        "status_key": "partially_published",
        "label": f"部分上線 ({published_count}/{total_examples})",
        "badge_class": "teacher-v3-partially-published",
        "icon": "🟡",
        "is_clickable": True,
    }
    if published_count == total_examples and total_examples > 0 and generated_not_packaged_count == 0:
        teacher_status = _teacher_status_payload("published")
        teacher_status["label"] = "全部上線"
    elif published_count > 0:
        teacher_status = partially_published_payload
    elif failed_count > 0 and verified_count == 0:
        teacher_status = _teacher_status_payload("failed")
    elif verified_count > 0:
        teacher_status = _teacher_status_payload("generated_not_packaged")
    elif bool(file_status.get("dryrun_generate_exists") or file_status.get("production_generate_exists")):
        teacher_status = _teacher_status_payload("generated_not_packaged")
    elif any(str(row.get("status")) in {"generating", "pending"} for row in tracker_rows):
        teacher_status = _teacher_status_payload("generating")
    elif tracker_rows:
        teacher_status = _teacher_status_payload("generation_incomplete")
    else:
        teacher_status = _teacher_status_payload("not_generated")
    if not prod_info.get("v3_package_exists") and teacher_status.get("status_key") == "published":
        teacher_status = _teacher_status_payload("generated_not_packaged")
    return teacher_status


def _build_skill_list_gencode_status_view(
    *,
    skill_id: str,
    coverage: dict[str, object],
    tracker_rows: list[dict[str, object]],
    prod_info: dict[str, object],
    production_root: Path,
    dryrun_root: Path,
    project_root: str | Path | None,
    dryrun_base_dir: str,
    production_base_dir: str,
) -> dict[str, object]:
    from core.gencode.services.v3_skill_coverage_service import build_coverage_warnings

    total_examples = int(coverage.get("total_examples") or 0)
    verified_count = int(coverage.get("verified_count") or 0)
    failed_count = int(coverage.get("failed_count") or 0)
    missing_tracker_ids = [
        row["textbook_example_id"]
        for row in coverage.get("examples", [])
        if isinstance(row, dict) and row.get("status") == "missing_tracker"
    ]
    published_count = _lite_published_component_count(skill_id, tracker_rows, production_root)
    generated_not_packaged_count = max(0, verified_count - published_count)
    coverage_warnings = build_coverage_warnings(coverage)

    if not tracker_rows:
        status = "not_created"
        component_id = None
        has_payload = False
        error_log = None
        updated_at = None
        component_count = 0
        file_status = inspect_gencode_files(
            skill_id=skill_id,
            component_id=None,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
            project_root=project_root,
            include_manifest=False,
        )
    else:
        primary = max(tracker_rows, key=lambda row: _STATUS_PRIORITY.get(str(row["status"]), 0))
        status = str(primary["status"])
        component_id = ", ".join(str(row["component_id"]) for row in tracker_rows)
        has_payload = any(bool(row.get("has_payload")) for row in tracker_rows)
        error_logs = [str(row.get("error_log")) for row in tracker_rows if row.get("error_log")]
        error_log = error_logs[0] if error_logs else None
        updated_values = [str(row.get("updated_at")) for row in tracker_rows if row.get("updated_at")]
        updated_at = max(updated_values) if updated_values else None
        component_count = len(tracker_rows)
        file_status = {
            "dryrun_component_exists": False,
            "dryrun_generate_exists": False,
            "dryrun_manifest_exists": False,
            "production_component_exists": published_count > 0,
            "production_generate_exists": published_count > 0,
            "production_manifest_exists": prod_info.get("v3_package_exists", False),
        }
        for row in tracker_rows:
            component_key = str(row.get("component_id") or "").strip()
            if not component_key:
                continue
            if (dryrun_root / skill_id / "components" / component_key / "generate.py").is_file():
                file_status["dryrun_component_exists"] = True
                file_status["dryrun_generate_exists"] = True
            if (production_root / skill_id / "components" / component_key / "generate.py").is_file():
                file_status["production_component_exists"] = True
                file_status["production_generate_exists"] = True

    teacher_status = _resolve_skill_level_teacher_status(
        total_examples=total_examples,
        verified_count=verified_count,
        failed_count=failed_count,
        published_count=published_count,
        generated_not_packaged_count=generated_not_packaged_count,
        tracker_rows=tracker_rows,
        prod_info=prod_info,
        file_status=file_status,
    )

    return {
        "status": status,
        "status_label": format_gencode_status_label(status),
        "component_id": component_id,
        "component_count": component_count,
        "has_payload": has_payload,
        "has_payload_label": "有" if has_payload else "無",
        "error_log": error_log,
        "updated_at": updated_at,
        "coverage": coverage,
        "coverage_summary": (
            f"V3: {coverage.get('verified_count', 0)}/{coverage.get('total_examples', 0)} verified"
        ),
        "total_examples": total_examples,
        "verified_count": verified_count,
        "available_count": verified_count,
        "published_count": published_count,
        "generated_not_packaged_count": generated_not_packaged_count,
        "failed_count": failed_count,
        "unsupported_count": int(coverage.get("unsupported_count") or 0),
        "missing_tracker_count": len(missing_tracker_ids),
        "coverage_missing_ids": missing_tracker_ids,
        "coverage_warnings": coverage_warnings,
        "publish_ready": bool(coverage.get("publish_ready")),
        "publish_eligible": bool(coverage.get("publish_ready")),
        "teacher_status": teacher_status,
        **file_status,
        **prod_info,
        "dryrun_generate_label": _bool_label(bool(file_status["dryrun_generate_exists"])),
        "production_generate_label": _bool_label(bool(file_status["production_generate_exists"])),
    }


def build_admin_skills_gencode_status_map(
    conn: sqlite3.Connection,
    skill_ids: list[str],
    *,
    project_root: str | Path | None = None,
    dryrun_base_dir: str = "reports/gencode_v3_dryrun",
    production_base_dir: str = "agent_skills_v3",
    audit_variation: bool = False,
) -> dict[str, dict[str, object]]:
    keys = [str(skill_id or "").strip() for skill_id in skill_ids if str(skill_id or "").strip()]
    if not keys:
        return {}
    if audit_variation:
        return {
            skill_key: build_admin_skill_gencode_status_view(
                conn,
                skill_id=skill_key,
                project_root=project_root,
                dryrun_base_dir=dryrun_base_dir,
                production_base_dir=production_base_dir,
                audit_variation=True,
            )
            for skill_key in keys
        }

    from core.gencode.services.v3_skill_coverage_service import get_v3_skills_component_coverage_batch

    root = Path(project_root) if project_root is not None and str(project_root).strip() else PROJECT_ROOT
    dryrun_root = _resolve_base_path(dryrun_base_dir, project_root)
    production_root = _resolve_base_path(production_base_dir, project_root)
    coverage_map = get_v3_skills_component_coverage_batch(conn, keys)
    tracker_map = _fetch_batch_tracker_rows_for_skills(conn, keys)
    prod_map = _batch_inspect_skill_production_files(
        keys,
        production_base_dir=production_base_dir,
        project_root=project_root,
    )
    return {
        skill_key: _build_skill_list_gencode_status_view(
            skill_id=skill_key,
            coverage=coverage_map.get(
                skill_key,
                {
                    "skill_id": skill_key,
                    "total_examples": 0,
                    "verified_count": 0,
                    "failed_count": 0,
                    "unsupported_count": 0,
                    "publish_ready": False,
                    "examples": [],
                },
            ),
            tracker_rows=tracker_map.get(skill_key, []),
            prod_info=prod_map.get(
                skill_key,
                {
                    "production_wrapper_exists": False,
                    "v3_package_exists": False,
                    "generator_specs_count": 0,
                    "production_component_count": 0,
                },
            ),
            production_root=production_root,
            dryrun_root=dryrun_root,
            project_root=project_root,
            dryrun_base_dir=dryrun_base_dir,
            production_base_dir=production_base_dir,
        )
        for skill_key in keys
    }


def resolve_admin_project_root(app_root_path: str | Path | None = None) -> Path:
    root_candidates = [
        Path(app_root_path) if app_root_path else PROJECT_ROOT,
        Path(app_root_path).parent if app_root_path else PROJECT_ROOT.parent,
        PROJECT_ROOT,
    ]
    for candidate in root_candidates:
        if (candidate / "skills").exists():
            return candidate
    return PROJECT_ROOT
