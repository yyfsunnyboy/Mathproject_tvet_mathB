"""Cross-validate sequence.series_sums answers against the existing static ``sequence.series`` domain functions (vocational B3), over every
sampled variant of the components whose primitives it also has.  Pure computation: no DB, no files written."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import sympy as sp  # noqa: E402

from agent_domains_candidate.series_summation import build_sandbox as B  # noqa: E402
from agent_domains_candidate.series_summation import series_summation_domain as D  # noqa: E402
from agent_domains_candidate.series_summation.series_summation_specs import COMPONENTS  # noqa: E402
from agent_domains_candidate.series_summation.sandbox_harness import register_candidate_in_memory  # noqa: E402
from core.domain import sequence_series_domain as S  # noqa: E402

register_candidate_in_memory()

checked: dict[str, list[int]] = {}


def tally(name: str, ok: bool) -> None:
    checked.setdefault(name, [0, 0])
    checked[name][0 if ok else 1] += 1


for cid, (_skill, op, source, sampler) in COMPONENTS.items():
    for variant in B.collect_variants(cid, op, source, sampler):
        answer = D.build_series_summation_matrix(domain_operation=op, constraints=dict(variant))["answer"]
        if op == "arithmetic_series_items":
            for item, got in zip(variant["items"], answer["items"]):
                if item["kind"] == "d_from_sum":
                    tally("arithmetic d from S_n", S.arithmetic_recover_d_from_sum(item["S"], item["a1"], int(item["n"])) == D.num(got["value"]))
                else:
                    tally("arithmetic S_n of listed terms", S.arithmetic_partial_sum(item["first"], item["d"], got["n"]) == D.num(got["value"]))
        elif op == "geometric_series_items":
            for item, got in zip(variant["items"], answer["items"]):
                if item["kind"] == "ratio_sum":
                    tally("geometric S_n", sp.simplify(S.geometric_partial_sum(item["a1"], item["r"], int(item["n"])) - D.num(got["value"])) == 0)
                else:
                    r = D.num(got["ratio"])
                    tally("geometric S_n of listed terms", sp.simplify(S.geometric_partial_sum(item["terms"][0], r, got["n"]) - D.num(got["value"])) == 0)
        elif op == "arithmetic_series_relation" and variant["kind"] == "mid_total":
            tally("odd-length total = mid x count", S.arithmetic_total_from_odd_mid(variant["mid"], int(variant["n"])) == D.num(answer["total"]))
        elif op == "geometric_series_relation" and variant["kind"] == "first_last_sum":
            n = S.geometric_recover_n_from_sum(variant["S"], variant["a1"], D.num(answer["ratio"]))
            tally("geometric n from S_n", n == answer["n"])
        elif op == "geometric_series_relation" and variant["kind"] == "layers":
            tally("geometric S_n (layers)", sp.simplify(S.geometric_partial_sum(variant["W"], D.num(answer["ratio"]), int(variant["layers"])) - D.num(answer["total"])) == 0)
print({k: f"{v[0]} agree / {v[1]} differ" for k, v in checked.items()})
sys.exit(1 if any(v[1] for v in checked.values()) else 0)
