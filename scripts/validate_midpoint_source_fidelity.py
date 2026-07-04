from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.midpoint_source_fidelity import (
    SKILL_ID,
    SOURCE_SPECS,
    generate_source_faithful_payload,
    validate_source_fidelity,
)


def main() -> int:
    components = []
    src_4511 = []
    for source_id, spec in SOURCE_SPECS.items():
        passed = 0
        for seed in range(10):
            payload = generate_source_faithful_payload(source_id, seed)
            validation = validate_source_fidelity(source_id, payload)
            if not validation["passed"]:
                raise AssertionError(
                    f"source fidelity failed: source={source_id} seed={seed} "
                    f"errors={validation['errors']}"
                )
            passed += 1
            if source_id == 4511:
                src_4511.append(
                    {
                        "seed": seed,
                        "question": payload["question_text"],
                        "correct_label": payload["correct_answer"],
                        "semantic_answer": payload["semantic_answer"],
                    }
                )
        components.append(
            {
                "component_id": f"src_{source_id}",
                "problem_type_id": spec["problem_type_id"],
                "seeds": 10,
                "passed": passed,
            }
        )
    print(
        json.dumps(
            {
                "skill_id": SKILL_ID,
                "validator": "PASS",
                "components": components,
                "src_4511_seeds": src_4511,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
