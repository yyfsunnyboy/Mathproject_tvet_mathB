# -*- coding: utf-8 -*-
"""Phase 1 induction source tiers: core vs enrichment (literacy, SDGS, math files, long context)."""

from __future__ import annotations

import re
from typing import Any

# Minimum core examples recommended for stable problem_type induction.
MIN_CORE_EXAMPLES_FOR_INDUCTION = 2

# Stem longer than this is treated as enrichment (literacy / reading load).
LONG_STEM_CHAR_THRESHOLD = 380

_ENRICHMENT_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("sdgs", re.compile(r"\bSDG[S]?\s*\d", re.I)),
    ("sdgs", re.compile(r"SDG[S]?\s*7", re.I)),
    ("math_file", re.compile(r"數學\s*檔案|数学\s*档案")),
    ("literacy_reading", re.compile(r"閱讀素養|阅读素养|素養題|素養題")),
    ("figure_mixed", re.compile(r"▲\s*圖|▲图")),
    ("historical_narrative", re.compile(r"\d{3,4}\s*[−\-–]\s*\d{3,4}")),
    ("historical_narrative", re.compile(r"(?:科學家|科学家|數學家|数学家).{0,24}[（(]\s*[A-Za-z]")),
    ("piecewise_application", re.compile(r"\\begin\s*\{\s*align|分段函數|分段函数|夏季電費|夏季电费|非夏季電費")),
    ("applied_context", re.compile(r"虎克定律|虎克|Hooke|自由落體|自由落体|Galileo|伽利略")),
)

_CONTEXT_TOPIC_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"電費|电费|SDG", re.I),
    re.compile(r"虎克|Hooke|彈簧|弹簧", re.I),
    re.compile(r"尤拉|Euler|數學檔案|数学档案", re.I),
    re.compile(r"自由落體|自由落体|Galileo|伽利略", re.I),
    re.compile(r"閱讀|阅读素養", re.I),
)


def _source_text(ex: dict[str, Any] | None, feat: dict[str, Any] | None) -> str:
    if isinstance(feat, dict):
        text = str(feat.get("question_text", "")).strip()
        if text:
            return text
    if isinstance(ex, dict):
        for key in ("problem_text", "problem", "question", "stem", "content"):
            text = str(ex.get(key, "")).strip()
            if text:
                return text
    return ""


def _metadata_hints(ex: dict[str, Any] | None) -> list[str]:
    if not isinstance(ex, dict):
        return []
    hints: list[str] = []
    for key in ("example_label", "practice_label", "problem_type", "source_type", "title"):
        val = str(ex.get(key, "") or "").strip()
        if val:
            hints.append(val)
    return hints


def detect_enrichment_reasons(
    *,
    example: dict[str, Any] | None = None,
    feature: dict[str, Any] | None = None,
) -> list[str]:
    text = _source_text(example, feature)
    meta_blob = " ".join(_metadata_hints(example))
    combined = f"{text}\n{meta_blob}"
    reasons: list[str] = []
    if not combined.strip():
        return reasons

    seen: set[str] = set()
    for reason, pattern in _ENRICHMENT_MARKERS:
        if reason in seen:
            continue
        if pattern.search(combined):
            seen.add(reason)
            reasons.append(reason)

    if len(text) >= LONG_STEM_CHAR_THRESHOLD:
        reasons.append("long_stem")

    topic_hits = sum(1 for p in _CONTEXT_TOPIC_PATTERNS if p.search(combined))
    if topic_hits >= 2:
        reasons.append("mixed_unrelated_context")

    if re.search(r"素養|素養題|閱讀", meta_blob):
        if "literacy_reading" not in reasons:
            reasons.append("literacy_reading")

    return sorted(set(reasons))


def classify_induction_source_tier(
    *,
    example: dict[str, Any] | None = None,
    feature: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reasons = detect_enrichment_reasons(example=example, feature=feature)
    tier = "enrichment" if reasons else "core"
    future_ai = False
    contextual = False
    if tier == "enrichment":
        contextual = any(
            r in reasons
            for r in (
                "applied_context",
                "piecewise_application",
                "sdgs",
                "historical_narrative",
                "long_stem",
                "mixed_unrelated_context",
            )
        )
        future_ai = any(
            r in reasons
            for r in ("sdgs", "piecewise_application", "math_file", "literacy_reading", "mixed_unrelated_context")
        )
        sc = {}
        if isinstance(feature, dict):
            sc = feature.get("semantic_classification") if isinstance(feature.get("semantic_classification"), dict) else {}
        if str(sc.get("candidate_source", "")).strip() == "needs_review" or str(
            sc.get("ai_best_candidate_id", "")
        ).strip() == "needs_review":
            future_ai = True
    return {
        "induction_tier": tier,
        "enrichment_reasons": reasons,
        "future_ai_judged": future_ai,
        "contextual_application": contextual,
    }


def filter_core_induction_examples(
    features: list[dict[str, Any]],
    examples: list[dict[str, Any]] | None = None,
) -> None:
    """
    SOP v0.2 Smart Degraded Salvage Mechanism:
    Intercepts core examples belonging to the main skill. If they have physical damage (missing_answer, broken_latex),
    fills placeholder answers, clears source_quality_reject, and marks them as FORCE_ALLOWED_FOR_INDUCTION.
    """
    if not features:
        return

    ex_by_id = {}
    for ex in examples or []:
        if isinstance(ex, dict):
            eid = ex.get("id") or ex.get("example_id")
            if eid is not None:
                ex_by_id[eid] = ex

    for feat in features:
        if not isinstance(feat, dict):
            continue
        ex_id = feat.get("source_example_id")
        ex_row = ex_by_id.get(ex_id, {})

        tier_info = classify_induction_source_tier(example=ex_row, feature=feat)
        is_core = tier_info.get("induction_tier") == "core"

        if is_core and (feat.get("source_quality_reject") or feat.get("source_quality_issues")):
            # Fill placeholder if answer is missing
            if not feat.get("answer") and not feat.get("correct_answer"):
                is_choice = feat.get("answer_type") == "single_choice" or len(feat.get("choices") or []) >= 2
                placeholder = "A" if is_choice else "0"
                feat["answer"] = placeholder
                feat["correct_answer"] = placeholder
                if isinstance(ex_row, dict):
                    ex_row["correct_answer"] = placeholder
                    ex_row["answer"] = placeholder

            # Reset physical quality damage flags/issues
            feat["source_quality_reject"] = False
            feat["source_quality_status"] = "FORCE_ALLOWED_FOR_INDUCTION"
            if "source_quality_issues" in feat:
                feat["source_quality_issues"] = []

            # Update trace inside semantic classification if present
            if isinstance(feat.get("semantic_classification"), dict):
                sc = feat["semantic_classification"]
                sc["source_quality_reject"] = False
                sc["source_quality_status"] = "FORCE_ALLOWED_FOR_INDUCTION"
                if "source_quality_issues" in sc:
                    sc["source_quality_issues"] = []


def validate_source_quality(
    features: list[dict[str, Any]],
    examples: list[dict[str, Any]] | None = None,
) -> None:
    filter_core_induction_examples(features, examples)


def split_induction_source_features(
    features: list[dict[str, Any]],
    *,
    examples: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    filter_core_induction_examples(features, examples)
    ex_by_id: dict[int, dict[str, Any]] = {}
    for ex in examples or []:
        if not isinstance(ex, dict):
            continue
        raw = ex.get("id") if ex.get("id") is not None else ex.get("example_id")
        try:
            ex_by_id[int(raw)] = ex
        except (TypeError, ValueError):
            continue

    core: list[dict[str, Any]] = []
    skipped_enrichment: list[dict[str, Any]] = []
    future_ai_judged: list[dict[str, Any]] = []
    contextual_application: list[dict[str, Any]] = []

    for feat in features:
        if not isinstance(feat, dict):
            continue
        ex_id = feat.get("source_example_id")
        ex_row = ex_by_id.get(ex_id, {}) or {}
        tier_info = classify_induction_source_tier(example=ex_row, feature=feat)
        enriched_feat = dict(feat)
        enriched_feat["induction_tier"] = tier_info["induction_tier"]
        enriched_feat["enrichment_reasons"] = tier_info["enrichment_reasons"]
        enriched_feat["included_in_core_induction"] = tier_info["induction_tier"] == "core"

        row = {
            "example_id": ex_id,
            "induction_tier": tier_info["induction_tier"],
            "enrichment_reasons": tier_info["enrichment_reasons"],
            "stem_length": len(_source_text(ex_row, feat)),
        }
        if tier_info["induction_tier"] == "core":
            core.append(enriched_feat)
        else:
            skipped_enrichment.append(row)
            if tier_info["future_ai_judged"]:
                future_ai_judged.append(row)
            if tier_info["contextual_application"]:
                contextual_application.append(row)

    report = {
        "core_example_count": len(core),
        "enrichment_example_count": len(skipped_enrichment),
        "skipped_enrichment_examples": skipped_enrichment,
        "future_ai_judged_candidates": future_ai_judged,
        "contextual_application_sources": contextual_application,
        "min_core_examples_for_induction": MIN_CORE_EXAMPLES_FOR_INDUCTION,
        "core_sufficient_for_induction": len(core) >= MIN_CORE_EXAMPLES_FOR_INDUCTION,
    }
    return core, report


def annotate_features_with_induction_tier(
    features: list[dict[str, Any]],
    *,
    examples: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    filter_core_induction_examples(features, examples)
    core, _report = split_induction_source_features(features, examples=examples)
    del core
    ex_by_id: dict[int, dict[str, Any]] = {}
    for ex in examples or []:
        if not isinstance(ex, dict):
            continue
        raw = ex.get("id") if ex.get("id") is not None else ex.get("example_id")
        try:
            ex_by_id[int(raw)] = ex
        except (TypeError, ValueError):
            continue
    out: list[dict[str, Any]] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        ex_id = feat.get("source_example_id")
        ex_row = ex_by_id.get(ex_id, {}) or {}
        tier_info = classify_induction_source_tier(example=ex_row, feature=feat)
        row = dict(feat)
        row["induction_tier"] = tier_info["induction_tier"]
        row["enrichment_reasons"] = tier_info["enrichment_reasons"]
        row["included_in_core_induction"] = tier_info["induction_tier"] == "core"
        out.append(row)
    return out
