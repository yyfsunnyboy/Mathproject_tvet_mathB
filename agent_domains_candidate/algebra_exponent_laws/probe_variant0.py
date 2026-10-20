"""Run every source-faithful variant through registry dispatch and print a short verdict."""

from __future__ import annotations

import sys

from agent_domains_candidate.algebra_exponent_laws.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.algebra_exponent_laws.unit3_specs import COMPONENTS, OP, SKILLS

DOMAIN_KEY = "algebra.exponent_laws"


def main() -> int:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    bad = 0
    only = {int(x) for x in sys.argv[1:]}
    for cid, (skill, op, variant, _sampler) in COMPONENTS.items():
        if only and cid not in only:
            continue
        try:
            matrix, payload = dispatch_registered_operation(DOMAIN_KEY, OP[op], seed=0, constraints=dict(variant))
            vals = payload["answer"]
            print(cid, "OK", str(vals)[:90].replace("\n", " "))
        except Exception as exc:  # noqa: BLE001
            bad += 1
            print(cid, "FAIL", type(exc).__name__, str(exc)[:160])
    print("bad:", bad)
    return bad


if __name__ == "__main__":
    raise SystemExit(main())
