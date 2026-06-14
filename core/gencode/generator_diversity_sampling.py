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


def _coerce_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _metadata_plan_fields(meta: Any) -> dict[str, str]:
    md = _coerce_mapping(meta)
    givens = md.get("givens")
    givens_map = _coerce_mapping(givens)
    scenario_type = str(
        givens_map.get("scenario_type", "")
        or md.get("scenario_type", "")
        or md.get("scenario_id", "")
    ).strip()
    return {
        "template_variant": str(md.get("template_variant") or md.get("template_id") or "live"),
        "routing_track": str(md.get("routing_track", "")),
        "scenario_type": scenario_type,
        "ratio_form": str(md.get("ratio_form", "")),
        "ratio_values": str(md.get("ratio_values", "")),
        "coordinate_pattern": str(md.get("coordinate_pattern", "")),
    }


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
    plan_map = dict(plan) if isinstance(plan, dict) else {}
    fields_raw = signature_fields or list(DEFAULT_ANTI_REPETITION.get("signature_fields") or [])
    fields = [str(f).strip() for f in fields_raw if isinstance(f, str) and str(f).strip()]
    return {f: plan_map.get(f, "") for f in fields if f in plan_map or f == "problem_type_id"}


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


def _detect_payload_spec_contract_mismatch(
    spec: dict[str, Any],
    payloads: list[dict[str, Any]],
) -> list[str]:
    """Compare live payloads against spec answer_contract and answer_format_hint.

    Returns blocker tokens when the actual generator output contradicts the spec.
    Requires at least 3 payloads to make a reliable judgment.
    """
    if len(payloads) < 3:
        return []
    from core.gencode.problem_type_spec import get_answer_contract
    from core.gencode.answer_format_hint import (
        HINT_UNKNOWN,
        HINT_CHOICE,
        HINT_INTEGER,
        HINT_RATIONAL,
        HINT_COORDINATE,
        infer_answer_format_hint,
    )

    ac = get_answer_contract(spec)
    spec_answer_type = str(ac.get("answer_type", "")).strip().lower()
    spec_checker = str(ac.get("checker_key") or ac.get("checker") or "").strip().lower()
    spec_hint = str(spec.get("answer_format_hint") or "").strip()
    if not spec_hint:
        spec_hint = infer_answer_format_hint(spec)

    blockers: list[str] = []

    # Tally payload evidence
    choices_in_payload = 0
    text_short_in_payload = 0
    numeric_type_in_payload = 0
    rational_answer_in_payload = 0
    choice_answer_in_payload = 0
    coordinate_in_payload = 0
    structured_text_in_payload = 0

    for pl in payloads:
        if not isinstance(pl, dict):
            continue
        pl_answer_type = str(pl.get("answer_type", "")).strip().lower()
        pl_choices = pl.get("choices")
        pl_answer = str(pl.get("answer", pl.get("correct_answer", ""))).strip()
        pl_checker = str(pl.get("checker") or pl.get("checker_key") or "").strip().lower()

        if isinstance(pl_choices, list) and pl_choices:
            choices_in_payload += 1
        if pl_answer_type in {"single_choice", "choice", "choice_label"}:
            choice_answer_in_payload += 1
        if pl_answer_type in {"text_short", "short_answer"}:
            text_short_in_payload += 1
        if pl_answer_type in {"integer", "numeric", "rational"}:
            numeric_type_in_payload += 1
        if pl_answer_type == "rational" or "/" in pl_answer:
            rational_answer_in_payload += 1
        if pl_answer_type in {"coordinate_pair", "ordered_pair"}:
            coordinate_in_payload += 1
        # A/B/C/D single-char answers indicate choice
        if len(pl_answer) == 1 and pl_answer in {"A", "B", "C", "D"}:
            choice_answer_in_payload += 1
        # Bracket pattern for coordinate
        if pl_answer.startswith("(") and "," in pl_answer and pl_answer.endswith(")"):
            coordinate_in_payload += 1

    threshold = max(3, len(payloads) // 2)

    # ── Rule 1: spec numeric but payload produces choices ────────────────────
    if spec_answer_type in {"integer", "numeric", "rational"} or spec_checker in {
        "integer_checker", "numeric_checker", "rational_checker"
    }:
        if choices_in_payload >= threshold or choice_answer_in_payload >= threshold:
            blockers.append("checker_answer_mismatch:spec_numeric_but_payload_choices")
        if text_short_in_payload >= threshold:
            blockers.append("checker_answer_mismatch:spec_numeric_but_payload_text")
        if (spec_answer_type == "integer" or spec_checker == "integer_checker") and rational_answer_in_payload >= threshold:
            blockers.append("checker_answer_mismatch:spec_integer_but_payload_rational")

    # ── Rule 2: spec choice but payload is non-choice ─────────────────────────
    if spec_answer_type in {"single_choice", "choice"} or spec_checker in {"choice_label_checker"}:
        if numeric_type_in_payload >= threshold and choices_in_payload < threshold:
            blockers.append("checker_answer_mismatch:spec_choice_but_payload_numeric")
        if text_short_in_payload >= threshold and choices_in_payload < threshold:
            blockers.append("checker_answer_mismatch:spec_choice_but_payload_text_without_choices")

    # ── Rule 3: spec text_short but payload produces choices ──────────────────
    if spec_answer_type in {"text_short", "short_answer"} or "text_short_checker" in spec_checker:
        if choices_in_payload >= threshold or choice_answer_in_payload >= threshold:
            blockers.append("checker_answer_mismatch:spec_text_but_payload_choices")
        # Also detect text_short spec with integer/numeric payload (common wrong prefix inference)
        if numeric_type_in_payload >= threshold and choices_in_payload < threshold:
            blockers.append("checker_answer_mismatch:spec_text_but_payload_numeric")

    # ── Rule 4: spec coordinate_pair but payload produces scalar ──────────────
    if spec_answer_type in {"coordinate_pair", "ordered_pair"}:
        if numeric_type_in_payload >= threshold and coordinate_in_payload < threshold:
            blockers.append("checker_answer_mismatch:spec_coordinate_but_payload_scalar")

    # ── Rule 5: answer_format_hint mismatch ───────────────────────────────────
    if spec_hint == HINT_CHOICE:
        if choices_in_payload < threshold and choice_answer_in_payload < threshold:
            blockers.append("answer_format_mismatch:spec_hint_choice_but_payload_has_no_choices")
    elif spec_hint in {HINT_INTEGER, HINT_RATIONAL}:
        if choices_in_payload >= threshold or choice_answer_in_payload >= threshold:
            blockers.append("answer_format_mismatch:payload_not_following_answer_format_hint")
    elif spec_hint == HINT_COORDINATE:
        if coordinate_in_payload < threshold and choices_in_payload >= threshold:
            blockers.append("answer_format_mismatch:payload_not_following_answer_format_hint")

    # ── Rule 6: unknown hint warning (not a hard blocker) ─────────────────────
    # (Only flag when hint is truly absent AND no evidence from answer_type either)
    if not spec_hint or spec_hint == HINT_UNKNOWN:
        if not spec_answer_type and not spec_checker:
            blockers.append("contract_unknown:missing_answer_format_hint")

    return blockers


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
    from generators.base_generator import BaseGenerator
    
    # Resolve source examples count and initialize BaseGenerator
    matched_count = int(spec.get("matched_example_count") or spec.get("source_example_count") or spec.get("matched_examples_count") or 3)
    dummy_examples = [None] * matched_count
    base_generator = BaseGenerator(source_examples=dummy_examples)
    
    # Apply Low-Sample Adaptation by scaling seed variance and parameters
    spec_to_use = dict(spec)
    if base_generator.low_source_examples:
        gc = spec_to_use.get("generator_contract", {})
        if isinstance(gc, dict):
            spec_to_use["generator_contract"] = dict(gc)
            schema = gc.get("parameter_schema", {})
            if isinstance(schema, dict):
                spec_to_use["generator_contract"]["parameter_schema"] = base_generator.adapt_parameters(schema)

    gc = _gc(spec_to_use)
    anti = gc.get("anti_repetition_rules") if isinstance(gc.get("anti_repetition_rules"), dict) else {}
    sig_fields = list(anti.get("signature_fields") or DEFAULT_ANTI_REPETITION.get("signature_fields") or [])
    variant_ids = [str(v.get("id", "")) for v in _enabled_variants(gc)]

    live_payloads: list[dict[str, Any]] = []
    signatures: list[dict[str, Any]] = []
    question_texts: list[str] = []
    answers: list[str] = []
    history: list[dict[str, Any]] = []
    generation_errors: list[str] = []

    for i in range(sample_count):
        seed = base_seed + i * 17
        if base_generator.low_source_examples:
            seed = base_generator.adjust_variance(seed)
            
        payload = None
        try:
            from core.gencode.slot_generators import generate_from_problem_type_spec

            payload = generate_from_problem_type_spec(skill_id, spec_to_use, seed=seed)
        except Exception as ex:
            generation_errors.append(str(ex)[:120])

        if payload and isinstance(payload, dict):
            live_payloads.append(payload)
            qt = str(payload.get("question_text", "")).strip()
            ans = str(payload.get("answer", payload.get("correct_answer", ""))).strip()
            question_texts.append(qt)
            answers.append(ans)
            meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
            fields = _metadata_plan_fields(meta)
            plan = {
                "problem_type_id": str(spec_to_use.get("problem_type_id", "")),
                **fields,
                "answer": ans,
            }
        else:
            plan = sample_plan_from_contract(spec_to_use, seed, history=history)
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
    
    # Apply diversity blocking exemption if low source examples
    metrics = base_generator.exempt_diversity_warning(metrics)
    metrics["generation_errors"] = generation_errors[:5]
    err_count = len(generation_errors)
    if err_count >= sample_count // 2:
        metrics["sampling_mode"] = "contract_simulation"
    elif err_count:
        metrics["sampling_mode"] = "live_and_contract"
    else:
        metrics["sampling_mode"] = "live"

    # ── Payload/spec contract mismatch gate ─────────────────────────────────
    # Detect when live generator output contradicts spec answer_contract.
    # This catches issues Phase 3 smoke would otherwise catch.
    if live_payloads:
        mismatch_blockers = _detect_payload_spec_contract_mismatch(spec, live_payloads)
        if mismatch_blockers:
            existing_blockers = list(metrics.get("diversity_blockers") or [])
            existing_blockers.extend(mismatch_blockers)
            metrics["diversity_blockers"] = sorted(set(existing_blockers))
            # Upgrade to a hard blocker status
            if metrics.get("diversity_sampling_status") not in {"generator_diversity_blocked"}:
                metrics["diversity_sampling_status"] = "generator_diversity_blocked"
            metrics["contract_mismatch_blockers"] = mismatch_blockers

    return metrics
