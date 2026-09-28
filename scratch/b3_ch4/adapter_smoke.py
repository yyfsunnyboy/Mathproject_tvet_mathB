import json
import sys
import traceback
from collections import Counter

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix
from core.gencode.runtime_skill_wrapper import check_answer

seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
problems = Counter()
shown = 0
for eid, spec in sorted(SOURCE_SPECS.items()):
    for seed in range(seeds):
        try:
            mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
            payload = adapt_exponential_logarithmic_matrix(
                mat, domain_operation=spec["op"], presentation_mode=spec["presentation"],
                component_id=f"src_{eid}", textbook_example_id=eid, seed=seed,
            )
            ac = payload["answer_contract"]
            correct = payload.get("correct_answer")
            if spec["presentation"] == "single_choice":
                label = mat["correct_label"]
                ok = check_answer(label, correct, payload=payload)
                bad = any(check_answer(c["label"], correct, payload=payload) for c in mat["choices"] if c["label"] != label)
            elif isinstance(mat["answer"]["value"], dict):
                parts = mat["answer"]["value"]
                ok = check_answer(dict(parts), correct, payload=payload)
                broken = dict(parts)
                k0 = next(iter(broken))
                broken[k0] = "999999"
                bad = check_answer(broken, correct, payload=payload)
                keys = [row.get("key") for row in ac.get("parts") or []]
                if sorted(keys) != sorted(parts):
                    problems[f"{eid}:part_keys:{keys}"] += 1
            else:
                ans = mat["answer"]["value"]
                ok = check_answer(ans, correct, payload=payload)
                bad = check_answer("999999", correct, payload=payload)
            if not ok:
                problems[f"{eid}:{spec['op']}:correct_rejected"] += 1
                if shown < 8:
                    shown += 1
                    print("REJECT", eid, json.dumps(mat["answer"]["value"], ensure_ascii=False), json.dumps(correct, ensure_ascii=False)[:300])
                    print("   parts:", json.dumps(ac.get("parts"), ensure_ascii=False)[:600])
            if bad:
                problems[f"{eid}:{spec['op']}:wrong_accepted"] += 1
        except Exception as exc:  # noqa: BLE001
            problems[f"{eid}:{spec['op']}:{type(exc).__name__}:{str(exc)[:100]}"] += 1
            if shown < 8:
                shown += 1
                traceback.print_exc()
for k, v in sorted(problems.items()):
    print(k, v)
print("problem keys:", len(problems))
