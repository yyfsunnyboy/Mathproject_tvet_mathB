from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_generator_payload


def _ensure_metadata_supports_answer(payload: dict[str, Any]) -> bool:
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    derivation = metadata.get("derivation") if isinstance(metadata.get("derivation"), list) else []
    answer = str(payload.get("answer", "")).strip()
    if not answer:
        return False
    blob = " ".join(str(x) for x in derivation)
    return answer in blob or bool(derivation)


def run_smoke(skill_id: str, sample_count: int) -> dict[str, Any]:
    mod = importlib.import_module(f"skills.{skill_id}")
    errors: list[dict[str, Any]] = []
    generated = 0
    by_pt: dict[str, int] = {}
    for i in range(sample_count):
        payload = mod.generate(level=1, seed=i)
        generated += 1
        pt = str(payload.get("problem_type_id", "")).strip()
        by_pt[pt] = by_pt.get(pt, 0) + 1
        spec = load_problem_type_spec(skill_id, pt)
        if not spec:
            errors.append({"seed": i, "problem_type_id": pt, "error": "problem_type_spec_missing"})
            continue
        contract_errors = validate_generator_payload(payload, problem_type_spec=spec)
        if contract_errors:
            errors.append({"seed": i, "problem_type_id": pt, "error": "contract_validation_failed", "detail": contract_errors})
        if not _ensure_metadata_supports_answer(payload):
            errors.append({"seed": i, "problem_type_id": pt, "error": "metadata_derivation_not_support_answer"})
    return {
        "skill_id": skill_id,
        "sample_count": sample_count,
        "generated_count": generated,
        "problem_type_distribution": by_pt,
        "errors": errors,
        "passed": len(errors) == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--sample-count", type=int, default=30)
    args = parser.parse_args()
    report = run_smoke(skill_id=args.skill_id, sample_count=args.sample_count)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
