# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer

SKILL = "vh_數學B1_FactorTheorem"


def _load_facade():
    path = ROOT / "skills" / f"{SKILL}.py"
    spec = importlib.util.spec_from_file_location("ft_facade", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _convert(matrix, seed):
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="factor_theorem_root_factor",
        domain_operation="factor_theorem_root_factor",
        seed=seed,
    )


print("=== seed 677 payload ===")
matrix = build_polynomial_matrix(seed=677, domain_operation="factor_theorem_root_factor", constraints={})
payload = _convert(matrix, 677)
print("Q", payload.get("question_text"))
print("answer_type", payload.get("answer_type"))
print("answer", payload.get("answer"))
print("checker", payload.get("checker"), payload.get("checker_key"))
print("canonical/display", payload.get("display_answer"))
ac = payload.get("answer_contract") or {}
print("contract.answer_type", ac.get("answer_type"))
print("contract.checker", ac.get("checker"))
print("contract.parts", ac.get("parts"))

print("=== requested dict checks on NEW payload ===")
for name, ua in [
    ("correct_dict", {"part_1": "x-3", "part_2": "x-3"}),
    ("wrong_p1", {"part_1": "x+3", "part_2": "x-3"}),
    ("wrong_p2", {"part_1": "x-3", "part_2": "x+3"}),
    ("correct_str", "x-3"),
    ("correct_paren", "(x-3)"),
    ("wrong_str", "x+3"),
]:
    print(name, check_answer(ua, payload.get("answer"), payload=payload))

print("=== 100 root_to_factor seeds ===")
passed = failed = 0
errors = []
for seed in range(0, 2500):
    matrix = build_polynomial_matrix(seed=seed, domain_operation="factor_theorem_root_factor", constraints={})
    q = str(matrix.get("question_text") or "")
    if "一次因式" not in q or "一根" not in q:
        continue
    try:
        pl = _convert(matrix, seed)
        ans = pl.get("answer")
        if isinstance(ans, dict):
            raise AssertionError(f"still_dict:{ans}")
        if not check_answer(str(ans), ans, payload=pl):
            raise AssertionError("self_fail")
        if check_answer("x+99", ans, payload=pl):
            raise AssertionError("wrong_pass")
        replay = _convert(
            build_polynomial_matrix(seed=seed, domain_operation="factor_theorem_root_factor", constraints={}),
            seed,
        )
        if replay.get("answer") != ans:
            raise AssertionError("not_reproducible")
        ac = pl.get("answer_contract") or {}
        parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
        keys = [str(r.get("key") or "") for r in parts if isinstance(r, dict)]
        if len(keys) != len(set(keys)):
            raise AssertionError("dup_keys")
        passed += 1
    except Exception as exc:
        failed += 1
        errors.append(f"seed{seed}:{exc}")
    if passed + failed >= 100:
        break
print("sampling", passed, "passed", failed, "failed", "errors", errors[:5])

print("=== FactorTheorem smoke 40 ===")
mod = _load_facade()
ok = bad = 0
hits = Counter()
errs = []
keys = list(mod.GENERATOR_KEYS)
for i in range(40):
    try:
        pl = mod.generate(seed=3000 + i)
        cid = str(pl.get("component_id") or "")
        hits[cid] += 1
        if not (pl.get("question_text") or pl.get("question")) or pl.get("answer") is None:
            raise AssertionError("empty")
        if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
            raise AssertionError("checker")
        ok += 1
    except Exception as exc:
        bad += 1
        errs.append(str(exc))
print("SMOKE", ok, "/", 40, "failed", bad, "keys", len(keys))
print("HITS", dict(hits))
print("ERR", errs[:5])

out = {
    "seed_677": {
        "answer_type": payload.get("answer_type"),
        "answer": payload.get("answer"),
        "checker": payload.get("checker"),
        "parts": ac.get("parts"),
        "question": payload.get("question_text"),
    },
    "sampling": {"passed": passed, "failed": failed, "errors": errors[:10]},
    "smoke": {"passed": ok, "failed": bad, "wrapper_keys": len(keys), "hits": dict(hits), "errors": errs[:10]},
}
(ROOT / "scratch" / "_verify_factor_multipart_fix.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
print("DONE")
