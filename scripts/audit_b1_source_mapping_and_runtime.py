# -*- coding: utf-8 -*-
"""B1-only textbook mapping + static fidelity + offline runtime smoke (read-mostly).

Does not rebuild generators or mutate student history.
Writes reports under reports/gencode_closed_loop/.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.generator_problem_type_inventory import (
    inventory_skill_generator_problem_types,
)
from core.gencode.services.gencode_status_query_service import load_v3_skill_generator_specs
from core.gencode.skill_wrapper_compiler import (
    _fetch_publish_eligible_components,
    _fetch_verified_components,
)
from core.gencode.services.v3_publish_eligibility import component_publish_blockers

VOLUME = "數學B1"
SRC_RE = re.compile(r"^src_(\d+)$")


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    con.row_factory = sqlite3.Row
    return con


def _skills(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT si.skill_id, si.skill_ch_name, si.category, si.is_active,
               sc.volume, sc.chapter, sc.section, sc.display_order
        FROM skills_info si
        LEFT JOIN skill_curriculum sc ON sc.skill_id = si.skill_id
        WHERE si.skill_id LIKE 'vh_數學B1_%'
           OR si.skill_id LIKE 'outline_vocational_數學B1%'
           OR sc.volume = ?
        ORDER BY sc.display_order, si.skill_id
        """,
        (VOLUME,),
    ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        sid = str(r["skill_id"])
        if sid in out:
            continue
        if not (sid.startswith("vh_數學B1_") or sid.startswith("outline_vocational_數學B1")):
            continue
        out[sid] = dict(r)
    return list(out.values())


def _examples(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT id, skill_id, source_volume, source_chapter, source_section,
               source_description, source_paragraph, problem_text, problem_type,
               correct_answer
        FROM textbook_examples
        WHERE source_volume = ? OR skill_id LIKE 'vh_數學B1_%'
        ORDER BY id
        """,
        (VOLUME,),
    ).fetchall()
    return [dict(r) for r in rows]


def _stem_preview(text: Any, n: int = 80) -> str:
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    return s[:n]


def _mapping_row(
    *,
    example: dict[str, Any] | None,
    skill_id: str,
    component_id: str | None,
    problem_type_id: str | None,
    family: str | None,
    generator_exists: bool,
    in_facade: bool,
    tracker_status: str | None,
    blockers: list[str],
    fidelity: str,
    fidelity_note: str,
) -> dict[str, Any]:
    eid = int(example["id"]) if example else None
    source_id = f"src_{eid}" if eid is not None else component_id
    mapping = "PASS"
    if example is None and component_id:
        mapping = "FAIL"
    elif component_id and example and f"src_{example['id']}" != component_id:
        mapping = "FAIL"
    elif component_id and not generator_exists:
        mapping = "WARN"
    elif component_id and not in_facade:
        mapping = "WARN"
    elif example and not component_id:
        mapping = "WARN"
    return {
        "source_id": source_id,
        "textbook_example_id": eid,
        "skill_id": skill_id,
        "family": family or "",
        "problem_type_id": problem_type_id or "",
        "generator": component_id or "",
        "generator_exists": generator_exists,
        "in_runtime_registry": in_facade,
        "tracker_status": tracker_status,
        "publish_blockers": blockers,
        "mapping": mapping,
        "fidelity": fidelity,
        "fidelity_note": fidelity_note,
        "source_stem_preview": _stem_preview(example.get("problem_text") if example else ""),
        "source_chapter": (example or {}).get("source_chapter"),
        "source_section": (example or {}).get("source_section"),
        "db_problem_type": (example or {}).get("problem_type"),
        "evidence": {
            "db_table": "textbook_examples" if example else None,
            "component_path": (
                str(ROOT / "agent_skills_v3" / skill_id / "components" / component_id / "generate.py")
                if component_id
                else None
            ),
        },
    }


def _static_fidelity(
    example: dict[str, Any] | None,
    problem_type_id: str,
    meta_line_type: str,
) -> tuple[str, str]:
    """Structural fidelity only.

    DB ``problem_type`` is often a coarse legacy label and must NOT be equated to
    ``problem_type_id``. Deep math-structure equivalence remains HUMAN_REVIEW when
    automated evidence is insufficient — never force PASS on semantics.
    """
    if not example:
        return "WARN", "no_textbook_row_for_component"
    stem = str(example.get("problem_text") or "")
    if not stem.strip():
        return "HUMAN_REVIEW", "empty_source_stem"
    pt = str(problem_type_id or "")
    line = str(meta_line_type or "")
    notes: list[str] = []
    # Soft keyword checks by family hints — never invent mappings.
    if "inequality" in pt or "inequality" in line:
        if (
            "不等式" not in stem
            and "≤" not in stem
            and "≥" not in stem
            and "<" not in stem
            and ">" not in stem
            and "le" not in stem
            and "ge" not in stem
        ):
            notes.append("inequality_token_missing_in_stem")
    if "quadratic" in pt and "x" not in stem and "二次" not in stem:
        notes.append("quadratic_stem_weak")
    if notes:
        return "HUMAN_REVIEW", ";".join(notes)
    # Automated structural mapping OK; full mathematical fidelity still needs
    # sampled human review for complex stems (reported separately, not FAIL).
    return "PASS", "source_exists_skill_bound_structural_ok"


def main() -> int:
    con = _conn()
    skills = _skills(con)
    examples = _examples(con)
    by_skill_ex: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_id: dict[int, dict[str, Any]] = {}
    for ex in examples:
        by_skill_ex[str(ex["skill_id"])].append(ex)
        by_id[int(ex["id"])] = ex

    mapping_rows: list[dict[str, Any]] = []
    skill_summaries: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []

    for meta in skills:
        sid = str(meta["skill_id"])
        inv = inventory_skill_generator_problem_types(sid, project_root=ROOT, category=meta.get("category"))
        specs = load_v3_skill_generator_specs(skill_id=sid, project_root=ROOT)
        facade_keys = set()
        facade_path = ROOT / "skills" / f"{sid}.py"
        if facade_path.is_file():
            # keys already reflected via inventory/specs; load keys from package/facade via specs component ids
            facade_keys = {str(r.get("component_id") or "") for r in specs if r.get("component_id")}

        # Also read facade keys from inventory evidence by scanning SPECS already loaded.
        package_components_dir = ROOT / "agent_skills_v3" / sid / "components"
        disk_components = set()
        if package_components_dir.is_dir():
            disk_components = {
                p.name
                for p in package_components_dir.iterdir()
                if p.is_dir() and (p / "generate.py").is_file()
            }

        verified = _fetch_verified_components(con, sid)
        verified_by_cid = {str(r["component_id"]): r for r in verified}
        eligible = _fetch_publish_eligible_components(con, sid)

        covered_example_ids: set[int] = set()
        for row in specs:
            cid = str(row.get("component_id") or "").strip()
            pt = str(row.get("problem_type_id") or "").strip()
            family = str(row.get("line_type") or "").strip()
            m = SRC_RE.match(cid)
            eid = int(m.group(1)) if m else None
            example = by_id.get(eid) if eid is not None else None
            if example:
                covered_example_ids.add(int(example["id"]))
            gen_exists = cid in disk_components
            tracker = verified_by_cid.get(cid)
            blockers: list[str] = []
            if tracker:
                blockers = list(
                    component_publish_blockers(
                        skill_id=sid,
                        component_skill_id=sid,
                        component_status="verified",
                        spec=tracker.get("induced_spec_payload") or {},
                    )
                    or []
                )
            # skill binding check
            fidelity, fnote = _static_fidelity(example, pt, family)
            if example and str(example.get("skill_id")) != sid:
                anomalies.append(
                    {
                        "severity": "P0",
                        "code": "source_skill_mismatch",
                        "skill_id": sid,
                        "source_id": f"src_{example['id']}",
                        "detail": f"example.skill_id={example['skill_id']} but registered under {sid}",
                    }
                )
                fidelity = "FAIL"
                fnote = "source_bound_to_different_skill"
            mapping_rows.append(
                _mapping_row(
                    example=example,
                    skill_id=sid,
                    component_id=cid or None,
                    problem_type_id=pt or None,
                    family=family or None,
                    generator_exists=gen_exists,
                    in_facade=bool(cid and cid in facade_keys),
                    tracker_status=("verified" if tracker else None),
                    blockers=blockers,
                    fidelity=fidelity,
                    fidelity_note=fnote,
                )
            )

        # Examples without generator registry coverage
        for ex in by_skill_ex.get(sid, []):
            if int(ex["id"]) in covered_example_ids:
                continue
            mapping_rows.append(
                _mapping_row(
                    example=ex,
                    skill_id=sid,
                    component_id=None,
                    problem_type_id=None,
                    family=None,
                    generator_exists=False,
                    in_facade=False,
                    tracker_status=None,
                    blockers=[],
                    fidelity="WARN",
                    fidelity_note="textbook_example_without_runtime_generator_registry",
                )
            )

        # Orphan generate.py not in SPECS
        for cid in sorted(disk_components - facade_keys):
            m = SRC_RE.match(cid)
            example = by_id.get(int(m.group(1))) if m else None
            anomalies.append(
                {
                    "severity": "P1",
                    "code": "orphan_generate_py",
                    "skill_id": sid,
                    "source_id": cid,
                    "detail": "generate.py exists but not in runtime GENERATOR_SPECS",
                }
            )
            mapping_rows.append(
                _mapping_row(
                    example=example,
                    skill_id=sid,
                    component_id=cid,
                    problem_type_id=None,
                    family=None,
                    generator_exists=True,
                    in_facade=False,
                    tracker_status=("verified" if cid in verified_by_cid else None),
                    blockers=[],
                    fidelity="WARN",
                    fidelity_note="orphan_component_not_in_facade",
                )
            )

        skill_summaries.append(
            {
                "skill_id": sid,
                "skill_ch_name": meta.get("skill_ch_name"),
                "category": meta.get("category"),
                "is_outline": inv["is_outline"],
                "is_active": bool(meta.get("is_active")),
                "textbook_example_count": len(by_skill_ex.get(sid, [])),
                "generator_impl_count": inv["generator_impl_count"],
                "usable_problem_type_count": inv["usable_problem_type_count"],
                "usable_problem_type_ids": inv["usable_problem_type_ids"],
                "static_health": inv["health"],
                "verified_tracker_count": len(verified),
                "publish_eligible_count": len(eligible),
                "promotion_gate": "PASS" if eligible and len(eligible) == len(verified) and verified else (
                    "PARTIAL" if eligible else ("N/A_OUTLINE" if inv["is_outline"] else "FAIL_OR_BLOCKED")
                ),
                "domain_evidence_complete": bool(eligible) and len(eligible) == len(verified) and bool(verified),
            }
        )

    # Special regressions
    point_specs = load_v3_skill_generator_specs(skill_id="vh_數學B1_DistanceBetweenPointAndLine", project_root=ROOT)
    parallel_specs = load_v3_skill_generator_specs(
        skill_id="vh_數學B1_DistanceBetweenTwoParallelLines", project_root=ROOT
    )
    src_4584 = {
        "in_point": any(str(r.get("component_id")) == "src_4584" for r in point_specs),
        "in_parallel": any(str(r.get("component_id")) == "src_4584" for r in parallel_specs),
        "db_skill": (by_id.get(4584) or {}).get("skill_id"),
        "db_stem_preview": _stem_preview((by_id.get(4584) or {}).get("problem_text")),
    }
    if not (src_4584["in_point"] and not src_4584["in_parallel"] and src_4584["db_skill"] == "vh_數學B1_DistanceBetweenPointAndLine"):
        anomalies.append(
            {
                "severity": "P0",
                "code": "src_4584_mapping_regression",
                "skill_id": "vh_數學B1_DistanceBetweenPointAndLine",
                "source_id": "src_4584",
                "detail": src_4584,
            }
        )

    # Cross-skill duplicate component ids
    cid_owners: dict[str, set[str]] = defaultdict(set)
    for row in mapping_rows:
        if row.get("generator"):
            cid_owners[str(row["generator"])].add(str(row["skill_id"]))
    for cid, owners in cid_owners.items():
        if len(owners) > 1:
            anomalies.append(
                {
                    "severity": "P0",
                    "code": "duplicate_component_across_skills",
                    "source_id": cid,
                    "detail": sorted(owners),
                }
            )

    mapping_counts = Counter(r["mapping"] for r in mapping_rows)
    fidelity_counts = Counter(r["fidelity"] for r in mapping_rows)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scope": "B1_only",
        "sop_applied": [
            "AGENTS.md",
            "docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md (§0.2, §1, §2, §3, §4, §5)",
            "docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md (§6–§8)",
            "docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md (package/publish)",
            "docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md",
            "docs/系統SOP/數學答案檢核原則_v1.12_20260908.md",
        ],
        "counts": {
            "skills_total": len(skills),
            "executable_skills": sum(1 for s in skill_summaries if not s["is_outline"]),
            "outline_skills": sum(1 for s in skill_summaries if s["is_outline"]),
            "textbook_examples": len(examples),
            "mapping_rows": len(mapping_rows),
            "mapping": dict(mapping_counts),
            "fidelity": dict(fidelity_counts),
        },
        "src_4584": src_4584,
        "skill_summaries": skill_summaries,
        "mapping_rows": mapping_rows,
        "anomalies": anomalies,
        "number_line": next((s for s in skill_summaries if s["skill_id"] == "vh_數學B1_NumberLine"), None),
        "subsection332": next((s for s in skill_summaries if s["skill_id"] == "vh_數學B1_SubSection332"), None),
    }

    out_dir = ROOT / "reports" / "gencode_closed_loop"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"b1_source_mapping_audit_{stamp}.json"
    latest_json = out_dir / "b1_source_mapping_audit_latest.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", json_path)
    print("skills", payload["counts"])
    print("src_4584", src_4584)
    print("anomalies", len(anomalies))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
