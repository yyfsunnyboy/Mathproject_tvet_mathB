# -*- coding: utf-8 -*-
"""Read-only Cursor handoff artifacts for V3 capability gaps (no model, no core writes)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from core.gencode.services.v3_skill_capability_preflight_service import (
    evaluate_skill_v3_capability,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GAP_ROOT = PROJECT_ROOT / "reports" / "gencode_capability_gaps"


def _utc_stamp() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def compute_gap_fingerprint(preflight: dict[str, Any]) -> str:
    payload = {
        "skill_id": preflight.get("skill_id"),
        "capability_status": preflight.get("capability_status"),
        "domain_key": preflight.get("domain_key"),
        "missing_layers": list(preflight.get("missing_layers") or []),
        "unresolved_example_ids": list(preflight.get("unresolved_example_ids") or []),
        "supported_operations": list(preflight.get("supported_operations") or []),
        "domain_module": preflight.get("domain_module"),
        "entrypoint": preflight.get("entrypoint"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_example_briefs(conn: sqlite3.Connection, skill_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, problem_text, correct_answer, problem_type, source_description
        FROM textbook_examples
        WHERE skill_id = ?
        ORDER BY id ASC
        """,
        (str(skill_id).strip(),),
    ).fetchall()
    briefs = []
    for row in rows:
        if hasattr(row, "keys"):
            d = dict(row)
        else:
            d = {
                "id": row[0],
                "problem_text": row[1],
                "correct_answer": row[2],
                "problem_type": row[3],
                "source_description": row[4],
            }
        briefs.append(
            {
                "textbook_example_id": int(d.get("id") or 0),
                "source_id": f"src_{int(d.get('id') or 0)}",
                "problem_type": str(d.get("problem_type") or ""),
                "problem_text": str(d.get("problem_text") or "")[:500],
                "correct_answer": str(d.get("correct_answer") or "")[:200],
                "source_description": str(d.get("source_description") or ""),
            }
        )
    return briefs


def _find_reusable_handoff(skill_dir: Path, fingerprint: str) -> Path | None:
    if not skill_dir.is_dir():
        return None
    candidates = sorted(
        [p for p in skill_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    for folder in candidates:
        fp_file = folder / "gap_fingerprint.txt"
        if fp_file.is_file() and fp_file.read_text(encoding="utf-8").strip() == fingerprint:
            if (folder / "cursor_handoff.md").is_file():
                return folder
    return None


def _suggest_isomorphism_groups(briefs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[int]] = {}
    for b in briefs:
        key = str(b.get("problem_type") or "unknown").strip() or "unknown"
        groups.setdefault(key, []).append(int(b["textbook_example_id"]))
    return [{"group_key": k, "textbook_example_ids": v} for k, v in sorted(groups.items())]


def build_cursor_handoff_markdown(
    *,
    preflight: dict[str, Any],
    example_briefs: list[dict[str, Any]],
    fingerprint: str,
) -> str:
    skill_id = str(preflight.get("skill_id") or "")
    status = str(preflight.get("capability_status") or "")
    unresolved = list(preflight.get("unresolved_example_ids") or [])
    lines = [
        f"# Cursor 交接包：{skill_id}",
        "",
        f"- generated_at: `{_utc_stamp()}`",
        f"- capability_status: `{status}`",
        f"- gap_fingerprint: `{fingerprint}`",
        f"- domain_key: `{preflight.get('domain_key') or ''}`",
        f"- domain_module: `{preflight.get('domain_module') or ''}`",
        f"- entrypoint: `{preflight.get('entrypoint') or ''}`",
        "",
        "## 目標與硬限制",
        "",
        "- 目標：補齊 Gencode V3 所需 domain capability／operation／registry／schema／checker 接線。",
        "- **不得**自動呼叫 Qwen／Gemini 修改正式 core。",
        "- **不得**覆寫既有 verified／published production components。",
        "- **不得**寫入學生端 production 或變更正式 tracker verified／published。",
        "- Gencode V3 只會使用既有 domain 能力重新建置，不會自行發明 API。",
        "",
        "## Domain resolver 結果",
        "",
        "```json",
        json.dumps(
            {
                "capability_status": status,
                "registry_entry": preflight.get("registry_entry"),
                "supported_operations": preflight.get("supported_operations"),
                "missing_layers": preflight.get("missing_layers"),
                "wiring_error": preflight.get("wiring_error"),
                "resolvable_example_count": preflight.get("resolvable_example_count"),
                "unresolved_example_count": preflight.get("unresolved_example_count"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "## 缺少層級",
        "",
    ]
    for layer in preflight.get("missing_layers") or []:
        lines.append(f"- `{layer}`")
    if not preflight.get("missing_layers"):
        lines.append("- （無明確 missing_layers；請依 unresolved 題目診斷）")

    lines.extend(
        [
            "",
            "## 教材題目清單",
            "",
            f"- total: {preflight.get('textbook_example_count')}",
            f"- resolvable: {preflight.get('resolvable_example_count')}",
            f"- unresolved: {preflight.get('unresolved_example_count')}",
            "",
        ]
    )
    for b in example_briefs:
        mark = "UNRESOLVED" if int(b["textbook_example_id"]) in set(unresolved) else "ok"
        lines.append(
            f"- `{b['source_id']}` ({mark}) type=`{b.get('problem_type')}` "
            f"Q=`{(b.get('problem_text') or '')[:120]}` A=`{(b.get('correct_answer') or '')[:60]}`"
        )

    groups = _suggest_isomorphism_groups(example_briefs)
    lines.extend(["", "## 同構分群建議", ""])
    for g in groups:
        lines.append(f"- `{g['group_key']}`: {g['textbook_example_ids']}")

    lines.extend(
        [
            "",
            "## 既有相近 API／可重用方向",
            "",
            "- 先查 `core/registry/taxonomy_registry.py` 與同章已 ready 的 skill binding。",
            "- 優先擴充既有 `domain_module` 的 allowed_operations，而不是新建獨立 skill runtime。",
            "- checker／answer schema 必須落在既有 registry（`answer_schema_registry`、`_ALLOWED_CHECKERS`）。",
            "",
            "## 必須執行的 focused tests",
            "",
            "- domain resolver：`resolve_domain_for_skill(skill_id)` 成功且 wiring_ok",
            "- capability preflight：`capability_status == ready`",
            "- 單題 no-LLM phase1：unresolved_example_count == 0",
            "- 既有 verified skill 回歸：不得被本改動破壞",
            "",
            "## 不可修改的 verified 成果",
            "",
            "- `agent_skills_v3/<other_ready_skills>/...` production components",
            "- 既有 tracker `verified`／`published` 列",
            "- 正式 publish manifest（除非另開受控 publish 任務）",
            "",
            "## 完成條件",
            "",
            "1. `evaluate_skill_v3_capability` 回傳 `ready`",
            "2. `/skills` 顯示「重新建置與驗證」",
            "3. `POST .../gencode_v3_dryrun` 不再因 capability 回 409",
            "4. 不自動 publish；由教師另按「更新到學生端」",
            "",
            "## 建議 Cursor 執行 prompt",
            "",
            "```text",
            f"請為 skill `{skill_id}` 補齊 Gencode V3 domain capability。",
            f"目前 capability_status=`{status}`，missing_layers={preflight.get('missing_layers')}。",
            "只允許最小接線修改（registry / domain operation / schema / checker）。",
            "禁止呼叫模型自動改 core，禁止覆寫其他 skill 的 verified/production。",
            "完成後執行 focused tests，並確認 evaluate_skill_v3_capability == ready。",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def create_or_reuse_capability_handoff(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    gap_root: str | Path | None = None,
) -> dict[str, Any]:
    """Create or reuse a handoff folder for the skill's current gap fingerprint."""
    preflight = evaluate_skill_v3_capability(conn, skill_id, probe_examples=True)
    fingerprint = compute_gap_fingerprint(preflight)
    root = Path(gap_root) if gap_root else DEFAULT_GAP_ROOT
    skill_dir = root / str(preflight.get("skill_id") or skill_id)
    skill_dir.mkdir(parents=True, exist_ok=True)

    reused = _find_reusable_handoff(skill_dir, fingerprint)
    if reused is not None:
        return {
            "ok": True,
            "reused": True,
            "skill_id": preflight.get("skill_id"),
            "capability_status": preflight.get("capability_status"),
            "gap_fingerprint": fingerprint,
            "handoff_dir": str(reused),
            "handoff_md": str(reused / "cursor_handoff.md"),
            "preflight": preflight,
        }

    stamp = _utc_stamp()
    out_dir = skill_dir / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    briefs = _load_example_briefs(conn, str(preflight.get("skill_id") or skill_id))
    md = build_cursor_handoff_markdown(
        preflight=preflight,
        example_briefs=briefs,
        fingerprint=fingerprint,
    )
    (out_dir / "gap_fingerprint.txt").write_text(fingerprint + "\n", encoding="utf-8")
    (out_dir / "preflight.json").write_text(
        json.dumps(preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "examples.json").write_text(
        json.dumps(briefs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "cursor_handoff.md").write_text(md, encoding="utf-8")
    return {
        "ok": True,
        "reused": False,
        "skill_id": preflight.get("skill_id"),
        "capability_status": preflight.get("capability_status"),
        "gap_fingerprint": fingerprint,
        "handoff_dir": str(out_dir),
        "handoff_md": str(out_dir / "cursor_handoff.md"),
        "preflight": preflight,
    }
