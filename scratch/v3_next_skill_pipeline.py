# -*- coding: utf-8 -*-
"""One-off: discover next V3 skill and run pipeline diagnostics."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from core.gencode.schema.gencode_component_tracker_inspection import ensure_gencode_component_tracker_table
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_skill,
    run_admin_v3_publish_for_skill,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.v3_presentation_inference import has_abcd_choice_group, infer_presentation_mode_from_textbook_row
from core.gencode.v3_production_publish_service import V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS
from core.gencode.answer_payload import refresh_runtime_question_session
from core.gencode.runtime_skill_wrapper import check_answer

DB = PROJECT_ROOT / "instance" / "kumon_math.db"
HV_SKILL = "vh_數學B1_HorizontalAndVerticalLineEquations"


def load_mvp_skills() -> list[str]:
    data = yaml.safe_load(
        (PROJECT_ROOT / "configs/gencode_taxonomy/k12_component_taxonomy.yaml").read_text(encoding="utf-8")
    )
    return [str(x) for x in data.get("mvp_scope", {}).get("v1", [])]


def pick_next_skill(conn: sqlite3.Connection) -> str:
    mvp = load_mvp_skills()
    candidates: list[tuple[str, int, int, int]] = []
    for skill in mvp:
        if skill == HV_SKILL:
            continue
        total = conn.execute(
            "SELECT COUNT(*) FROM textbook_examples WHERE skill_id = ?", (skill,)
        ).fetchone()[0]
        verified = conn.execute(
            """
            SELECT COUNT(*) FROM gencode_component_tracker
            WHERE skill_id = ? AND gencode_status = 'verified'
            """,
            (skill,),
        ).fetchone()[0]
        published = 1 if (PROJECT_ROOT / "skills" / f"{skill}.py").is_file() else 0
        candidates.append((skill, total, verified, published))
    if not candidates:
        raise RuntimeError("no_next_mvp_skill_after_hv")
    # Prefer skill with incomplete verified coverage; tie-break by MVP order.
    incomplete = [c for c in candidates if c[2] < c[1] or c[3] == 0]
    pool = incomplete or candidates
    pool.sort(key=lambda row: (row[2] / max(row[1], 1), row[0]))
    return pool[0][0]


def list_textbook_examples(conn: sqlite3.Connection, skill_id: str) -> list[dict]:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)")}
    fields = [
        f
        for f in (
            "id",
            "source_description",
            "problem_type",
            "problem_text",
            "correct_answer",
        )
        if f in cols
    ]
    rows = conn.execute(
        f"SELECT {', '.join(fields)} FROM textbook_examples WHERE skill_id = ? ORDER BY id",
        (skill_id,),
    ).fetchall()
    out = []
    for row in rows:
        d = dict(row)
        text = str(d.get("problem_text") or "")
        inferred = infer_presentation_mode_from_textbook_row(d)
        out.append(
            {
                "id": d.get("id"),
                "source_description": d.get("source_description"),
                "problem_type": d.get("problem_type"),
                "has_abcd_choices": has_abcd_choice_group(text),
                "expected_presentation_mode": inferred["presentation_mode"],
            }
        )
    return out


def component_contract_report(conn: sqlite3.Connection, skill_id: str) -> list[dict]:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "facade", PROJECT_ROOT / "skills" / f"{skill_id}.py"
    )
    mod = None
    if spec and spec.loader and (PROJECT_ROOT / "skills" / f"{skill_id}.py").is_file():
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    rows = conn.execute(
        """
        SELECT textbook_example_id, component_id, induced_spec_payload
        FROM gencode_component_tracker
        WHERE skill_id = ?
        ORDER BY textbook_example_id
        """,
        (skill_id,),
    ).fetchall()

    reports = []
    for row in rows:
        tid = int(row["textbook_example_id"])
        cid = str(row["component_id"])
        induced = json.loads(row["induced_spec_payload"] or "{}")
        payload = None
        if mod is not None:
            try:
                payload = mod.generate(seed=tid, component_id=cid)
            except Exception:
                payload = None
        if payload is None:
            # load component directly from agent_skills_v3
            gen_path = PROJECT_ROOT / "agent_skills_v3" / skill_id / "components" / cid / "generate.py"
            if gen_path.is_file():
                s = importlib.util.spec_from_file_location(f"gen_{cid}", gen_path)
                if s and s.loader:
                    m = importlib.util.module_from_spec(s)
                    s.loader.exec_module(m)
                    payload = m.generate(seed=tid, component_id=cid)
        if isinstance(payload, dict) and mod is not None and hasattr(mod, "GENERATOR_SPECS"):
            # merge like house __init__
            for spec_row in mod.GENERATOR_SPECS:
                if str(spec_row.get("component_id")) == cid:
                    from core.gencode.skill_wrapper_compiler import _render_new_house_init_py  # noqa: F401

                    break
        norm = refresh_runtime_question_session(dict(payload or {}), skill_id=skill_id)
        meta = (payload or {}).get("metadata") or {}
        reports.append(
            {
                "textbook_example_id": tid,
                "component_id": cid,
                "induced_presentation_mode": induced.get("presentation_mode"),
                "presentation_mode": (payload or {}).get("presentation_mode"),
                "answer_type": (payload or {}).get("answer_type"),
                "answer": (payload or {}).get("answer"),
                "correct_answer": (payload or {}).get("correct_answer"),
                "choices_count": len((payload or {}).get("choices") or []),
                "semantic_answer": (payload or {}).get("semantic_answer"),
                "metadata_presentation_mode": meta.get("presentation_mode"),
                "problem_type_id": (payload or {}).get("problem_type_id"),
                "answer_contract_nonempty": bool(norm.get("answer_contract")),
                "answer_contract": norm.get("answer_contract"),
            }
        )
    return reports


def practice_runtime_samples(skill_id: str, seeds: range) -> list[dict]:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "facade", PROJECT_ROOT / "skills" / f"{skill_id}.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = []
    for seed in seeds:
        raw = mod.generate(seed=seed)
        norm = refresh_runtime_question_session(dict(raw), skill_id=skill_id)
        correct = raw.get("correct_answer")
        user = raw.get("answer")
        ok = check_answer(user, correct, payload=norm, skill_id=skill_id)
        out.append(
            {
                "seed": seed,
                "component_id": raw.get("component_id"),
                "presentation_mode": raw.get("presentation_mode"),
                "question_text": str(raw.get("question_text") or "")[:80],
                "answer": raw.get("answer"),
                "correct_answer": correct,
                "choices_count": len(raw.get("choices") or []),
                "semantic_answer": raw.get("semantic_answer"),
                "check_passed": ok,
            }
        )
    return out


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    ensure_gencode_component_tracker_table(conn)

    skill_id = pick_next_skill(conn)
    print("NEXT_SKILL", skill_id)
    print("ALLOWLIST", skill_id in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS)

    print("\n=== TEXTBOOK EXAMPLES ===")
    for row in list_textbook_examples(conn, skill_id):
        print(json.dumps(row, ensure_ascii=False))

    print("\n=== DRYRUN ===")
    dry = run_admin_v3_dryrun_for_skill(
        conn, skill_id, smoke=True, verify=True, force=True
    )
    print(
        json.dumps(
            {
                "success": dry.get("success"),
                "success_count": dry.get("success_count"),
                "failed_count": dry.get("failed_count"),
                "results": dry.get("results"),
            },
            ensure_ascii=False,
        )
    )

    coverage = get_v3_skill_component_coverage(conn, skill_id)
    print("\n=== COVERAGE ===")
    print(json.dumps(coverage, ensure_ascii=False, indent=2))

    print("\n=== CONTRACT (from dryrun components) ===")
    # load from v3 house after dryrun
    for cid_dir in sorted(
        (PROJECT_ROOT / "reports/gencode_v3_dryrun" / skill_id / "components").glob("src_*")
    ):
        import importlib.util

        cid = cid_dir.name
        tid = int(cid.replace("src_", ""))
        gen = importlib.util.spec_from_file_location("g", cid_dir / "generate.py")
        assert gen and gen.loader
        m = importlib.util.module_from_spec(gen)
        gen.loader.exec_module(m)
        payload = m.generate(seed=tid, component_id=cid)
        norm = refresh_runtime_question_session(dict(payload), skill_id=skill_id)
        meta = payload.get("metadata") or {}
        induced = json.loads(
            conn.execute(
                "SELECT induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id=?",
                (tid,),
            ).fetchone()["induced_spec_payload"]
        )
        print(
            json.dumps(
                {
                    "textbook_example_id": tid,
                    "component_id": cid,
                    "induced_presentation_mode": induced.get("presentation_mode"),
                    "presentation_mode": payload.get("presentation_mode"),
                    "answer_type": payload.get("answer_type"),
                    "answer": payload.get("answer"),
                    "correct_answer": payload.get("correct_answer"),
                    "choices_count": len(payload.get("choices") or []),
                    "semantic_answer": payload.get("semantic_answer"),
                    "metadata_presentation_mode": meta.get("presentation_mode"),
                    "problem_type_id": payload.get("problem_type_id"),
                    "answer_contract_nonempty": bool(norm.get("answer_contract")),
                },
                ensure_ascii=False,
            )
        )

    if coverage.get("publish_ready"):
        staging = PROJECT_ROOT / "reports" / "gencode_v3_publish_staging" / f"auto_{skill_id}"
        dryrun_skill = PROJECT_ROOT / "reports" / "gencode_v3_dryrun" / skill_id
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        shutil.copytree(dryrun_skill, staging / skill_id)
        (staging / "agent_skills_v3").mkdir(parents=True)
        shutil.copytree(dryrun_skill, staging / "agent_skills_v3" / skill_id)
        print("\n=== PUBLISH ===")
        pub = run_admin_v3_publish_for_skill(
            conn=conn,
            skill_id=skill_id,
            project_root=str(PROJECT_ROOT),
            staging_root=str(staging),
            force_publish=True,
            strict_coverage=True,
        )
        print(json.dumps({"status": pub.get("status"), "component_count": pub.get("component_count")}, ensure_ascii=False))

        print("\n=== GENERATOR_SPECS ===")
        import importlib.util

        spec = importlib.util.spec_from_file_location("f", PROJECT_ROOT / "skills" / f"{skill_id}.py")
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for row in mod.GENERATOR_SPECS:
            print(json.dumps(row, ensure_ascii=False))

        print("\n=== PRACTICE RUNTIME (8 seeds) ===")
        for row in practice_runtime_samples(skill_id, range(1, 9)):
            print(json.dumps(row, ensure_ascii=False))
    else:
        print("\nSKIP PUBLISH: publish_ready=false")

    conn.close()


if __name__ == "__main__":
    main()
