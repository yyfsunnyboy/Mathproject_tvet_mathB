# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.runtime_skill_wrapper import check_answer

FAILED = {
    "vh_數學B1_SlopeOfALine": [4534],
    "vh_數學B1_PropertiesOfParallelLines": [4530, 4535],
    "vh_數學B1_PropertiesOfPerpendicularLines": [4531, 4536, 4537],
}
PROD = ROOT / "agent_skills_v3"
OUT = ROOT / "scratch" / "_b1_21_checker_fail.json"


def load_generate(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    rows = []
    for skill, ids in FAILED.items():
        for eid in ids:
            cid = f"src_{eid}"
            path = PROD / skill / "components" / cid / "generate.py"
            mod = load_generate(path, f"g_{eid}")
            payload = mod.generate(seed=eid, component_id=cid)
            correct = payload.get("correct_answer", payload.get("answer"))
            contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
            try:
                ok = check_answer(correct, correct, payload=payload, skill_id=skill)
            except Exception as exc:
                ok = f"EXC:{type(exc).__name__}:{exc}"
            rows.append(
                {
                    "id": eid,
                    "skill_id": skill,
                    "problem_type_id": payload.get("problem_type_id"),
                    "answer_type": payload.get("answer_type"),
                    "presentation_mode": payload.get("presentation_mode"),
                    "answer": payload.get("answer"),
                    "correct_answer": payload.get("correct_answer"),
                    "semantic_answer": payload.get("semantic_answer"),
                    "checker_key": payload.get("checker_key") or contract.get("checker_key"),
                    "equivalence_type": payload.get("equivalence_type") or contract.get("equivalence_type"),
                    "answer_contract": contract,
                    "self_check": ok,
                    "question_text": str(payload.get("question_text") or "")[:180],
                }
            )
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
