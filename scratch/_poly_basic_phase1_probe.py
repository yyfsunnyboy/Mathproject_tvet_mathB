# -*- coding: utf-8 -*-
"""Read-only Phase 1 probe for vh_數學B1_PolynomialBasicConcepts."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from core.gencode.pipeline_orchestrator import (
    _infer_generic_capabilities_from_text,
    run_v3_no_llm_phase1_for_example,
)
from core.registry.taxonomy_registry import SkillDomainNotRegisteredError, resolve_domain_for_skill

SKILL_ID = "vh_數學B1_PolynomialBasicConcepts"
OUT = PROJECT_ROOT / "scratch" / "_poly_basic_phase1_probe.json"


def main() -> None:
    conn = sqlite3.connect(Config.db_path)
    conn.row_factory = sqlite3.Row
    cols = [r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)")]
    preferred = [
        "id",
        "skill_id",
        "problem_text",
        "correct_answer",
        "problem_type",
        "question_type",
        "source_description",
        "choices",
        "detailed_solution",
        "explanation",
        "answer_type",
    ]
    fields = [c for c in preferred if c in cols]
    rows = conn.execute(
        f"SELECT {', '.join(fields)} FROM textbook_examples WHERE skill_id = ? ORDER BY id",
        (SKILL_ID,),
    ).fetchall()

    domain_status = "ok"
    domain_error = ""
    try:
        domain = resolve_domain_for_skill(SKILL_ID)
    except SkillDomainNotRegisteredError as exc:
        domain = {}
        domain_status = "SkillDomainNotRegisteredError"
        domain_error = str(exc)
    except Exception as exc:
        domain = {}
        domain_status = type(exc).__name__
        domain_error = str(exc)

    examples = []
    for row in rows:
        d = {k: row[k] for k in row.keys()}
        text = " ".join(
            str(d.get(k) or "")
            for k in ("problem_text", "correct_answer", "source_description", "problem_type")
        )
        induced = run_v3_no_llm_phase1_for_example(SKILL_ID, dict(d), conn=conn)
        examples.append(
            {
                "id": d.get("id"),
                "source_description": d.get("source_description"),
                "problem_type": d.get("problem_type"),
                "question_type": d.get("question_type"),
                "problem_text": d.get("problem_text"),
                "correct_answer": d.get("correct_answer"),
                "inferred_caps_from_text": _infer_generic_capabilities_from_text(text),
                "phase1": induced,
            }
        )

    payload = {
        "skill_id": SKILL_ID,
        "example_count": len(examples),
        "domain_status": domain_status,
        "domain_error": domain_error,
        "domain": domain,
        "examples": examples,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(OUT))
    print("examples", len(examples), "domain", domain_status)
    conn.close()


if __name__ == "__main__":
    main()
