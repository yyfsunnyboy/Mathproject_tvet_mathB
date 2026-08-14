#!/usr/bin/env python3
"""Inventory production visual kinds from runtime generate() outputs."""

from __future__ import annotations

import importlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.domain_matrix_adapter import _apply_line_equation_practice_surface
from core.routes.practice import _finalize_practice_question_api_fields


def _visual_kind(payload: dict) -> str:
    vs = payload.get("visual_spec") or {}
    if not isinstance(vs, dict):
        return "(no_visual_spec)"
    kind = str(vs.get("kind") or vs.get("type") or "").strip()
    if kind:
        return kind
    if vs.get("image_base64"):
        return "visual_spec.image_base64"
    if payload.get("image_base64"):
        return "payload.image_base64"
    if vs:
        return "(visual_spec_empty_kind)"
    return "(empty)"


def _media_flags(payload: dict) -> dict:
    vs = payload.get("visual_spec") or {}
    td = payload.get("table_data") or {}
    return {
        "payload_image": bool(str(payload.get("image_base64") or "").strip()),
        "vs_image": bool(isinstance(vs, dict) and str(vs.get("image_base64") or "").strip()),
        "table_image": bool(isinstance(td, dict) and str(td.get("image_base64") or "").strip()),
        "visual_aids": bool(payload.get("visual_aids")),
        "image_url": bool(str(payload.get("image_url") or "").strip()),
    }


def _try_generate(skill_id: str, component_id: str) -> dict | None:
    mod_path = f"agent_skills_v3.{skill_id}.components.{component_id}.generate"
    try:
        mod = importlib.import_module(mod_path)
    except Exception:
        return None
    try:
        raw = mod.generate(seed=1, component_id=component_id)
    except TypeError:
        try:
            raw = mod.generate(seed=1)
        except Exception:
            return None
    except Exception:
        return None
    if skill_id.startswith("vh_數學B1_") and hasattr(raw, "get"):
        try:
            raw = _apply_line_equation_practice_surface(raw)
        except Exception:
            pass
    try:
        return _finalize_practice_question_api_fields(raw, skill_id=skill_id)
    except Exception:
        return raw if isinstance(raw, dict) else None


def main() -> int:
    root = PROJECT_ROOT / "agent_skills_v3"
    entries: list[tuple[str, str, str, dict]] = []
    kind_counter: Counter[str] = Counter()
    kind_skills: defaultdict[str, set[str]] = defaultdict(set)
    media_counter: Counter[str] = Counter()

    for skill_dir in sorted(root.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_id = skill_dir.name
        components = skill_dir / "components"
        if not components.is_dir():
            continue
        for comp_dir in sorted(components.iterdir()):
            if not comp_dir.is_dir():
                continue
            component_id = comp_dir.name
            payload = _try_generate(skill_id, component_id)
            if not payload:
                continue
            kind = _visual_kind(payload)
            flags = _media_flags(payload)
            kind_counter[kind] += 1
            kind_skills[kind].add(skill_id)
            for key, val in flags.items():
                if val:
                    media_counter[key] += 1
            entries.append((skill_id, component_id, kind, flags))

    print("=== Production visual kind inventory (runtime generate) ===")
    for kind, count in kind_counter.most_common():
        skills = sorted(kind_skills[kind])
        print(f"{count:4d}  {kind}")
        print(f"       skills: {', '.join(skills[:5])}{'...' if len(skills)>5 else ''}")

    print("\n=== Media flags (components with flag) ===")
    for key, count in media_counter.most_common():
        print(f"{count:4d}  {key}")

    sample_path = PROJECT_ROOT / "reports" / "_inventory_visual_kinds.json"
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path.write_text(
        json.dumps(
            {
                "kind_counts": dict(kind_counter),
                "media_counts": dict(media_counter),
                "samples": [
                    {"skill_id": s, "component_id": c, "kind": k, "media": f}
                    for s, c, k, f in entries
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {sample_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
