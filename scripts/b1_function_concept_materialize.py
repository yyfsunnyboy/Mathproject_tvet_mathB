# -*- coding: utf-8 -*-
"""Materialize FunctionConcept 4430/4431 and reconcile."""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.function_concept_domain import generate_function_concept_payload
from core.gencode.services.v3_artifact_reconciliation_service import reconcile_existing_artifacts

DRY = ROOT / "reports" / "gencode_v3_dryrun"
PROD = ROOT / "agent_skills_v3"
SKILL = "vh_數學B1_FunctionConcept"
TARGETS = {
    4430: "free_fall_function_value_choice",
    4431: "piecewise_utility_bill_savings_choice",
}

HINT = '''from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    meta = (question_payload or {}).get("metadata") or {}
    if step == 1:
        return "先辨識自變數與應變數，確認這是函數求值題。"
    if step == 2:
        return "依定義域選對應公式，再代入數值。"
    if step == 3:
        der = meta.get("derivation") or []
        return " → ".join(str(x) for x in der) if der else "代入後計算差額或函數值。"
    return ""
'''


def write_one(eid: int, pt: str) -> None:
    # smoke
    sample = generate_function_concept_payload(
        skill_id=SKILL, problem_type_id=pt, seed=42, component_id=f"src_{eid}", textbook_example_id=eid
    )
    assert sample.get("correct_answer")
    cid = f"src_{eid}"
    gen = textwrap.dedent(
        f"""\
        from __future__ import annotations
        from typing import Any
        from core.domain.function_concept_domain import generate_function_concept_payload

        SKILL_ID = {SKILL!r}
        PROBLEM_TYPE_ID = {pt!r}
        TEXTBOOK_EXAMPLE_ID = {eid}
        DEFAULT_COMPONENT_ID = {cid!r}
        PRESENTATION_MODE = "single_choice"
        ANSWER_TYPE = "single_choice"

        def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
            component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
            return generate_function_concept_payload(
                skill_id=SKILL_ID,
                problem_type_id=PROBLEM_TYPE_ID,
                seed=seed,
                component_id=component_id,
                textbook_example_id=TEXTBOOK_EXAMPLE_ID,
            )
        """
    )
    meta = textwrap.dedent(
        f"""\
        from __future__ import annotations
        from typing import Final
        COMPONENT_ID: Final[str] = {cid!r}
        SKILL_ID: Final[str] = {SKILL!r}
        TEXTBOOK_EXAMPLE_ID: Final[int] = {eid}
        PROBLEM_TYPE_ID: Final[str] = {pt!r}
        DOMAIN_OPERATION: Final[str] = {pt!r}
        TARGET_TASK: Final[str] = {pt!r}
        TEMPLATE_SLOT: Final[str] = {pt!r}
        PRESENTATION_MODE: Final[str] = "single_choice"
        ANSWER_TYPE: Final[str] = "single_choice"
        ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {{
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
            "answer_type": "single_choice",
        }}
        GENERATOR_READINESS: Final[str] = "runtime_ready"
        """
    )
    for base in (DRY, PROD):
        d = base / SKILL / "components" / cid
        d.mkdir(parents=True, exist_ok=True)
        (base / SKILL / "__init__.py").write_text("# package\n", encoding="utf-8")
        (d / "generate.py").write_text(gen, encoding="utf-8")
        (d / "metadata.py").write_text(meta, encoding="utf-8")
        (d / "get_hint.py").write_text(HINT, encoding="utf-8")
    return sample


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    samples = {}
    for eid, pt in TARGETS.items():
        samples[eid] = write_one(eid, pt)["correct_answer"]
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    result = reconcile_existing_artifacts(
        conn=conn,
        targets={SKILL: tuple(TARGETS.keys())},
        project_root=ROOT,
        commit=bool(args.commit),
    )
    try:
        conn.commit()
    except Exception:
        pass
    conn.close()
    out = {
        "samples": samples,
        "passed_count": result.get("passed_count"),
        "failed_count": result.get("failed_count"),
        "failed": [c.get("textbook_example_id") for c in result.get("components") or [] if not c.get("passed")],
        "blockers": {
            str(c.get("textbook_example_id")): c.get("blockers")
            for c in (result.get("components") or [])
            if not c.get("passed")
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not out["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
