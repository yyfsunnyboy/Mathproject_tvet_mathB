"""Teacher-review samples for 普高數學2 Unit 5: per component the textbook label, operation, checker, the source-parameter answer and one
generated variant (stem + answer).  Read-only (snapshot DB, in-memory candidate); writes review_samples.json next to this script."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.combinations import build_sandbox as B  # noqa: E402
from agent_domains_candidate.combinations.combinations_specs import COMPONENTS, FIXED_ROWS, SKILLS  # noqa: E402
from agent_domains_candidate.combinations.sandbox_harness import register_candidate_in_memory  # noqa: E402


def main() -> None:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    con = sqlite3.connect(f"file:{B.isolated_db().as_posix()}?mode=ro", uri=True)
    labels = {r[0]: r[1].split(" [")[0] for r in con.execute("select id, source_description from textbook_examples where id between 12812 and 12848")}
    con.close()
    rows = []
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        variants = B.collect_variants(cid, op, source, sampler)
        src = dispatch_registered_operation(B.DOMAIN_KEY, op, seed=0, constraints=dict(source))[1]
        other = next(v for v in variants if v != source) if len(variants) > 1 else source
        var = dispatch_registered_operation(B.DOMAIN_KEY, op, seed=0, constraints=dict(other))[1]
        contract = src["answer_contract"]
        rows.append({"id": cid, "label": labels[cid], "skill": SKILLS[skill_key], "operation": op, "variants": len(variants),
                     "answer_type": contract["answer_type"],
                     "checkers": sorted({contract["checker_key"], *(p["checker"] for p in contract.get("parts") or [])}),
                     "source_answer": src["correct_answer"], "variant_stem": var["question_text"], "variant_answer": var["correct_answer"]})
    out = {"components": rows, "fixed": {str(k): {"label": labels[k], "reason": v} for k, v in sorted(FIXED_ROWS.items())}}
    (HERE / "review_samples.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print(r["id"], r["label"], r["operation"], r["variants"], r["checkers"], json.dumps(r["source_answer"], ensure_ascii=False))


if __name__ == "__main__":
    main()
