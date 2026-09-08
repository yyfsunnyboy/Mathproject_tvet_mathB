# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.polynomial_domain import _eval, build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer

TECH = re.compile(r"_(?:[123]|duplicate|copy)\b")
SKILL = "vh_數學B1_FactorTheorem"
SC_KEYS = ["src_4655", "src_4710", "src_4711", "src_4712"]


def _load_facade():
    path = ROOT / "skills" / f"{SKILL}.py"
    spec = importlib.util.spec_from_file_location("ft_facade", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _texts(payload: dict) -> list[str]:
    out = []
    for item in payload.get("choices") or []:
        if isinstance(item, dict):
            out.append(str(item.get("text") or "").strip())
        else:
            out.append(str(item).strip())
    return out


def _convert(matrix: dict, seed: int) -> dict:
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="factor_theorem_root_factor",
        domain_operation="factor_theorem_root_factor",
        seed=seed,
    )


def _is_verify(matrix: dict) -> bool:
    q = str(matrix.get("question_text") or "")
    return "驗證" in q and "因式分解" in q


print("=== locate exact student poly ===")
exact = None
for seed in range(0, 2000):
    matrix = build_polynomial_matrix(
        seed=seed,
        domain_operation="factor_theorem_root_factor",
        constraints={},
    )
    if not _is_verify(matrix):
        continue
    q = str(matrix.get("question_text") or "")
    compact = q.replace(" ", "").replace("{", "").replace("}", "")
    if "2x^2-2x-12" in compact and "x=3" in compact:
        exact = {"seed": seed, "question": q, "answer": matrix["answer"]["canonical_form"],
                 "distractors": list(matrix.get("distractors") or [])}
        print("EXACT_SEED", seed)
        print("Q", q)
        print("A", exact["answer"])
        print("D", exact["distractors"])
        pl = _convert(matrix, seed)
        print("CHOICES", _texts(pl))
        break
if exact is None:
    print("NO_EXACT_POLY_IN_2000")

print("=== 100 verify_and_factor seeds ===")
stats = {
    "passed": 0,
    "failed": 0,
    "duplicate_choices": 0,
    "suffix_choices": 0,
    "multiple_correct": 0,
    "errors": [],
    "after_samples": [],
}
found_seeds: list[int] = []
for seed in range(0, 2000):
    matrix = build_polynomial_matrix(
        seed=seed,
        domain_operation="factor_theorem_root_factor",
        constraints={},
    )
    if not _is_verify(matrix):
        continue
    found_seeds.append(seed)
    try:
        givens = matrix.get("givens") or {}
        root = int(givens["root"])
        other = int(givens["other_root"])
        f = {int(k): Fraction(str(v)) for k, v in (givens.get("f") or {}).items()}
        if _eval(f, root) != 0 or _eval(f, other) != 0:
            raise AssertionError("factorization_invariant")
        payload = _convert(matrix, seed)
        texts = _texts(payload)
        if len(texts) != 4:
            raise AssertionError(f"choice_count:{len(texts)}")
        if len(set(texts)) != 4:
            stats["duplicate_choices"] += 1
            raise AssertionError("duplicate_choices")
        if any(TECH.search(t) for t in texts):
            stats["suffix_choices"] += 1
            raise AssertionError(f"suffix:{texts}")
        label = str(payload.get("answer") or "").strip().upper()
        if not check_answer(label, label, payload=payload):
            raise AssertionError("correct_fail")
        wrong_pass = 0
        for item in payload.get("choices") or []:
            other_label = str(item.get("label") or "").strip().upper()
            if other_label == label:
                continue
            if check_answer(other_label, label, payload=payload):
                wrong_pass += 1
        if wrong_pass:
            stats["multiple_correct"] += 1
            raise AssertionError("multiple_correct")
        replay = _texts(_convert(build_polynomial_matrix(
            seed=seed,
            domain_operation="factor_theorem_root_factor",
            constraints={},
        ), seed))
        if replay != texts:
            raise AssertionError("not_reproducible")
        stats["passed"] += 1
        if len(stats["after_samples"]) < 3:
            stats["after_samples"].append({"seed": seed, "question": matrix.get("question_text"), "choices": texts})
    except Exception as exc:
        stats["failed"] += 1
        stats["errors"].append(f"seed{seed}:{exc}")
    if len(found_seeds) >= 100:
        break
print("VERIFY_SEEDS", len(found_seeds), "passed", stats["passed"], "failed", stats["failed"])
if stats["errors"][:5]:
    print("ERR", stats["errors"][:5])

print("=== 100 seeds each published single_choice component ===")
mod = _load_facade()
comp_stats = {}
for key in SC_KEYS:
    ok = 0
    bad = 0
    suffix = 0
    dup = 0
    for seed in range(100):
        pl = mod.generate(seed=seed, component_id=key)
        texts = _texts(pl)
        if texts:
            if len(texts) != 4 or len(set(texts)) != 4:
                dup += 1
                bad += 1
                continue
            if any(TECH.search(t) for t in texts):
                suffix += 1
                bad += 1
                continue
        if pl.get("answer") is None:
            bad += 1
            continue
        ok += 1
    comp_stats[key] = {"passed": ok, "failed": bad, "suffix": suffix, "duplicate": dup}
    print(key, comp_stats[key])

print("=== FactorTheorem runtime smoke 40 ===")
hits = Counter()
smoke_ok = 0
smoke_bad = 0
smoke_suffix = 0
smoke_err = []
keys_before = list(mod.GENERATOR_KEYS)
for i in range(40):
    try:
        pl = mod.generate(seed=2000 + i)
        cid = str(pl.get("component_id") or "")
        hits[cid] += 1
        texts = _texts(pl)
        if any(TECH.search(t) for t in texts):
            smoke_suffix += 1
            raise AssertionError(f"suffix:{cid}:{texts}")
        if pl.get("answer_type") == "single_choice" and (len(texts) != 4 or len(set(texts)) != 4):
            raise AssertionError(f"choices:{cid}:{texts}")
        if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
            raise AssertionError("checker")
        smoke_ok += 1
    except Exception as exc:
        smoke_bad += 1
        smoke_err.append(str(exc))
print("SMOKE", smoke_ok, "/", 40, "failed", smoke_bad, "suffix", smoke_suffix)
print("HITS", dict(hits))
print("KEYS", keys_before, "count", len(keys_before))

out = {
    "exact": exact,
    "sampling_100": {
        "seeds": found_seeds,
        "passed": stats["passed"],
        "failed": stats["failed"],
        "duplicate_choices": stats["duplicate_choices"],
        "suffix_choices": stats["suffix_choices"],
        "multiple_correct": stats["multiple_correct"],
        "after_samples": stats["after_samples"],
        "errors": stats["errors"][:10],
    },
    "published_single_choice": comp_stats,
    "smoke": {
        "samples": 40,
        "passed": smoke_ok,
        "failed": smoke_bad,
        "suffix": smoke_suffix,
        "hits": dict(hits),
        "errors": smoke_err[:10],
        "wrapper_keys": keys_before,
    },
}
(ROOT / "scratch" / "_verify_factor_choice_suffix_fix.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("DONE")
