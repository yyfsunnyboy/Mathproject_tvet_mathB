# -*- coding: utf-8 -*-
"""Phase 2 generator diversity sampling gate (contract-driven)."""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any

from core.gencode.generator_contract_schema import DEFAULT_ANTI_REPETITION
from core.gencode.problem_type_spec import get_generator_contract

DIVERSITY_SAMPLE_COUNT = 30
UNIQUE_SIGNATURE_MIN = 15
MIN_TEMPLATE_VARIANTS_USED = 2
MAX_CONSECUTIVE_SAME_TEMPLATE = 4
SEVERE_CONSECUTIVE_TEMPLATE_FACTOR = 2


def _gc(spec: dict[str, Any]) -> dict[str, Any]:
    return get_generator_contract(spec) if isinstance(spec, dict) else {}


def _enabled_variants(gc: dict[str, Any]) -> list[dict[str, Any]]:
    variants = gc.get("template_variants")
    if not isinstance(variants, list):
        return []
    return [v for v in variants if isinstance(v, dict) and v.get("enabled", True)]


def _weighted_choice(rng: random.Random, items: list[dict[str, Any]]) -> dict[str, Any]:
    weights = [float(x.get("weight", 1.0) or 1.0) for x in items]
    total = sum(weights) or 1.0
    r = rng.random() * total
    acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if r <= acc:
            return item
    return items[-1]


def _pick_point_names(rng: random.Random, schema: dict[str, Any]) -> list[str]:
    pn = schema.get("point_names") if isinstance(schema.get("point_names"), dict) else {}
    choices = pn.get("choices")
    if isinstance(choices, list) and choices:
        return list(rng.choice(choices))
    return ["A", "B", "P"]


def _pick_coords(rng: random.Random, schema: dict[str, Any]) -> tuple[int, int, int, int]:
    cr = schema.get("coordinate_range") if isinstance(schema.get("coordinate_range"), dict) else {}
    xmin = int(cr.get("x_min", -10))
    xmax = int(cr.get("x_max", 10))
    ymin = int(cr.get("y_min", -10))
    ymax = int(cr.get("y_max", 10))
    excl_p = float(cr.get("exclude_zero_probability", 0) or 0)

    def _one(lo: int, hi: int) -> int:
        for _ in range(40):
            v = rng.randint(lo, hi)
            if excl_p and v == 0 and rng.random() < excl_p:
                continue
            return v
        return rng.choice([i for i in range(lo, hi + 1) if i != 0] or [1])

    return _one(xmin, xmax), _one(ymin, ymax), _one(xmin, xmax), _one(ymin, ymax)


def _pick_ratio(rng: random.Random, schema: dict[str, Any]) -> tuple[int, int, str]:
    ratio = schema.get("ratio") if isinstance(schema.get("ratio"), dict) else {}
    m = rng.randint(int(ratio.get("m_min", 1)), int(ratio.get("m_max", 5)))
    n = rng.randint(int(ratio.get("n_min", 1)), int(ratio.get("n_max", 5)))
    if ratio.get("require_coprime"):
        g = math.gcd(m, n)
        m, n = max(1, m // g), max(1, n // g)
    if not ratio.get("allow_equal_ratio", False) and m == n:
        n = min(int(ratio.get("n_max", 5)), m + 1)
    forms = ["AP:PB=m:n", "AP=mPB", "mAP=nPB"]
    return m, n, rng.choice(forms)


def _answer_mode(rng: random.Random, schema: dict[str, Any]) -> str:
    atm = schema.get("answer_type_mode") if isinstance(schema.get("answer_type_mode"), dict) else {}
    choices = atm.get("choices")
    weights = atm.get("weights")
    if isinstance(choices, list) and choices:
        if isinstance(weights, list) and len(weights) == len(choices):
            total = sum(float(w) for w in weights) or 1.0
            r = rng.random() * total
            acc = 0.0
            for c, w in zip(choices, weights):
                acc += float(w)
                if r <= acc:
                    return str(c)
        return str(rng.choice(choices))
    return "integer_coordinate"


def sample_plan_from_contract(
    spec: dict[str, Any],
    seed: int | None,
    *,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Sample a generation plan from generator_contract (no LLM)."""
    gc = _gc(spec)
    rng = random.Random(seed)
    schema = gc.get("parameter_schema") if isinstance(gc.get("parameter_schema"), dict) else {}
    variants = _enabled_variants(gc)
    if not variants:
        variants = [{"id": "default", "stem_pattern": "", "weight": 1.0}]
    anti = gc.get("anti_repetition_rules") if isinstance(gc.get("anti_repetition_rules"), dict) else DEFAULT_ANTI_REPETITION
    hist = list(history or [])

    def _ok_variant(vid: str) -> bool:
        if not anti.get("avoid_same_template_consecutive") or not hist:
            return True
        window = int(anti.get("recent_history_window", 5) or 5)
        recent = [h.get("template_variant") for h in hist[-window:]]
        return not (len(recent) >= 1 and recent[-1] == vid)

    picked = None
    for _ in range(12):
        cand = _weighted_choice(rng, variants)
        vid = str(cand.get("id", "default"))
        if _ok_variant(vid):
            picked = cand
            break
    if picked is None:
        picked = _weighted_choice(rng, variants)

    names = _pick_point_names(rng, schema)
    ax, ay, bx, by = _pick_coords(rng, schema)
    m, n, ratio_form = _pick_ratio(rng, schema)
    answer_mode = _answer_mode(rng, schema)
    sign_pattern = rng.choice(["++", "+-", "-+", "--", "mixed"])
    pt = str(spec.get("problem_type_id", "")).strip()
    target = str(spec.get("target_task", "")).strip()

    answer = f"({ax + 1},{by + 1})"
    if answer_mode == "rational_coordinate":
        answer = f"({ax}/2,{by}/2)"
    elif "integer" in answer_mode or "integer" in str(gc.get("answer_shape", "")):
        answer = f"({ax + m},{by + n})"

    plan = {
        "problem_type_id": pt,
        "target_task": target,
        "template_variant": str(picked.get("id", "default")),
        "point_names": names,
        "ratio_form": ratio_form,
        "ratio_values": f"{m}:{n}",
        "coordinate_pattern": sign_pattern,
        "answer_type_mode": answer_mode,
        "answer": answer,
        "context_style": rng.choice(["pure_symbolic", "word_context"]),
    }
    return plan


def plan_to_signature(plan: dict[str, Any], signature_fields: list[str] | None = None) -> dict[str, Any]:
    fields = signature_fields or list(DEFAULT_ANTI_REPETITION.get("signature_fields") or [])
    return {f: plan.get(f, "") for f in fields if f in plan or f == "problem_type_id"}


def signature_key(sig: dict[str, Any]) -> str:
    return "|".join(f"{k}={sig.get(k, '')}" for k in sorted(sig.keys()))


def _max_consecutive_same(values: list[str]) -> int:
    if not values:
        return 0
    best = cur = 1
    for i in range(1, len(values)):
        if values[i] == values[i - 1]:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best


def evaluate_diversity_metrics(
    signatures: list[dict[str, Any]],
    *,
    template_variant_ids: list[str],
    question_texts: list[str] | None = None,
    answers: list[str] | None = None,
    sample_count: int = DIVERSITY_SAMPLE_COUNT,
) -> dict[str, Any]:
    keys = [signature_key(s) for s in signatures]
    unique_sig = len(set(keys))
    qt = question_texts or []
    unique_q = len(set(qt)) if qt else unique_sig
    tmpl_counts = Counter(str(s.get("template_variant", "")) for s in signatures)
    ans = answers or [str(s.get("answer", "")) for s in signatures]
    ans_counts = Counter(ans)
    tmpl_seq = [str(s.get("template_variant", "")) for s in signatures]
    max_consec = _max_consecutive_same(tmpl_seq)

    enabled_variant_count = len([v for v in template_variant_ids if v])
    warnings: list[str] = []
    blockers: list[str] = []

    template_variant_count = len([k for k in tmpl_counts if k])
    diversity_healthy = unique_sig >= UNIQUE_SIGNATURE_MIN and (
        enabled_variant_count < MIN_TEMPLATE_VARIANTS_USED
        or template_variant_count >= MIN_TEMPLATE_VARIANTS_USED
    )
    severe_consecutive = max(
        MAX_CONSECUTIVE_SAME_TEMPLATE * SEVERE_CONSECUTIVE_TEMPLATE_FACTOR,
        max(1, sample_count - 2),
    )

    if unique_sig < min(UNIQUE_SIGNATURE_MIN, max(1, sample_count // 2)):
        warnings.append("low_unique_signature_count")
    if enabled_variant_count >= MIN_TEMPLATE_VARIANTS_USED and template_variant_count < MIN_TEMPLATE_VARIANTS_USED:
        warnings.append("insufficient_template_variant_coverage")
    if max_consec > MAX_CONSECUTIVE_SAME_TEMPLATE:
        warnings.append("consecutive_same_template_variant")
    if len(ans_counts) == 1 and sample_count >= 10:
        integer_only = all(
            isinstance(a, str) and a.startswith("(") and "," in a and "/" not in a for a in ans_counts.keys()
        )
        if integer_only:
            warnings.append("answer_distribution_too_uniform")

    if not diversity_healthy:
        if unique_sig < max(5, sample_count // 6):
            blockers.append("generator_diversity_blocked")
        if enabled_variant_count >= MIN_TEMPLATE_VARIANTS_USED and template_variant_count < 1:
            blockers.append("no_template_variant_used")
        if max_consec >= severe_consecutive and template_variant_count < MIN_TEMPLATE_VARIANTS_USED:
            blockers.append("consecutive_template_diversity_blocked")

    status = "passed"
    if blockers:
        status = "generator_diversity_blocked"
    elif warnings:
        status = "runtime_ready_with_diversity_warning"

    return {
        "diversity_sampling_status": status,
        "diversity_healthy": diversity_healthy,
        "sample_count": sample_count,
        "unique_signature_count": unique_sig,
        "unique_question_text_count": unique_q,
        "template_variant_distribution": dict(tmpl_counts),
        "answer_shape_distribution": dict(ans_counts),
        "variable_coverage_report": {
            "ratio_forms": sorted({str(s.get("ratio_form", "")) for s in signatures if s.get("ratio_form")}),
            "coordinate_patterns": sorted({str(s.get("coordinate_pattern", "")) for s in signatures}),
            "answer_type_modes": sorted({str(s.get("answer_type_mode", "")) for s in signatures}),
        },
        "repetition_warnings": warnings,
        "diversity_blockers": blockers,
        "max_consecutive_same_template": max_consec,
    }


def run_diversity_sampling(
    skill_id: str,
    spec: dict[str, Any],
    *,
    sample_count: int = DIVERSITY_SAMPLE_COUNT,
    base_seed: int = 42,
) -> dict[str, Any]:
    """
    Sample N plans (live generator when registered, else contract simulation).
    Returns diversity metrics for Phase 2 report.
    """
    gc = _gc(spec)
    anti = gc.get("anti_repetition_rules") if isinstance(gc.get("anti_repetition_rules"), dict) else {}
    sig_fields = list(anti.get("signature_fields") or DEFAULT_ANTI_REPETITION.get("signature_fields") or [])
    variant_ids = [str(v.get("id", "")) for v in _enabled_variants(gc)]

    signatures: list[dict[str, Any]] = []
    question_texts: list[str] = []
    answers: list[str] = []
    history: list[dict[str, Any]] = []
    generation_errors: list[str] = []

    for i in range(sample_count):
        seed = base_seed + i * 17
        payload = None
        try:
            from core.gencode.slot_generators import generate_from_problem_type_spec

            payload = generate_from_problem_type_spec(skill_id, spec, seed=seed)
        except Exception as ex:
            generation_errors.append(str(ex)[:120])

        if payload and isinstance(payload, dict):
            qt = str(payload.get("question_text", "")).strip()
            ans = str(payload.get("answer", payload.get("correct_answer", ""))).strip()
            question_texts.append(qt)
            answers.append(ans)
            meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
            plan = {
                "problem_type_id": str(spec.get("problem_type_id", "")),
                "template_variant": str((meta.get("template_variant") or meta.get("template_id") or "live")),
                "ratio_form": str(meta.get("ratio_form", "")),
                "ratio_values": str(meta.get("ratio_values", "")),
                "coordinate_pattern": str(meta.get("coordinate_pattern", "")),
                "answer": ans,
            }
        else:
            plan = sample_plan_from_contract(spec, seed, history=history)
            answers.append(str(plan.get("answer", "")))
            question_texts.append(
                f"{plan.get('template_variant')}|{plan.get('ratio_form')}|{plan.get('coordinate_pattern')}"
            )

        sig = plan_to_signature(plan, sig_fields)
        signatures.append(sig)
        history.append(plan)

    metrics = evaluate_diversity_metrics(
        signatures,
        template_variant_ids=variant_ids,
        question_texts=question_texts,
        answers=answers,
        sample_count=sample_count,
    )
    metrics["generation_errors"] = generation_errors[:5]
    err_count = len(generation_errors)
    if err_count >= sample_count // 2:
        metrics["sampling_mode"] = "contract_simulation"
    elif err_count:
        metrics["sampling_mode"] = "live_and_contract"
    else:
        metrics["sampling_mode"] = "live"
    return metrics
