from __future__ import annotations

import hashlib
import json
from typing import Any

from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"missing skill suffix={suffix}")


def _is_chinese_text(s: str) -> bool:
    if not s:
        return False
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def _hash_dict(data: Any) -> str:
    return hashlib.sha1(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def test_cumulative_frequency_table_diversity() -> None:
    skill = _resolve_skill_id("CumulativeFrequencyTablesAndGraphs")
    payloads = [generate_for_chap3_skill(skill_id=skill, seed=i + 1, level=1) for i in range(30)]

    signatures = [str(p.get("parameter_signature", "")) for p in payloads]
    table_hashes = [str(p.get("table_spec_hash") or _hash_dict(p.get("table") or {})) for p in payloads]
    unique_signature_count = len(set(signatures))
    unique_table_hash_count = len(set(table_hashes))
    consecutive_same_table = sum(1 for i in range(1, len(table_hashes)) if table_hashes[i] == table_hashes[i - 1])

    assert unique_signature_count >= 10
    assert unique_table_hash_count >= 8
    assert consecutive_same_table == 0

    for p in payloads:
        assert p.get("runtime_mode") == "visual_or_handwriting_ai_checked"
        assert p.get("check_mode") in {"review_mode", "handwriting_ai_checked"}
        assert p.get("grading_mode") in {"teacher_review", "ai_assisted_review"}
        assert p.get("visual_backed") is True
        assert p.get("visual_asset_type") == "table"
        assert p.get("table") or p.get("visual_aids") or p.get("image_base64")
        schema = p.get("expected_answer_schema") or {}
        freqs = ((p.get("parameters") or {}).get("frequencies")) or schema.get("frequency_values") or []
        cum = schema.get("cumulative_values") or []
        if freqs and cum:
            running = 0
            expected = []
            for f in freqs:
                running += int(f)
                expected.append(running)
            assert expected == [int(x) for x in cum]


def test_frequency_distribution_table_construction_diversity() -> None:
    skill = _resolve_skill_id("FrequencyDistributionTableConstruction")
    payloads = [generate_for_chap3_skill(skill_id=skill, seed=i + 1, level=1) for i in range(30)]

    signatures = [str(p.get("parameter_signature", "")) for p in payloads]
    raw_or_table_hash = []
    for p in payloads:
        raw = p.get("raw_data") or ((p.get("parameters") or {}).get("raw_data")) or []
        schema = p.get("table_schema") or p.get("table") or {}
        raw_or_table_hash.append(_hash_dict({"raw": raw, "schema": schema}))
    assert len(set(signatures)) >= 10
    assert len(set(raw_or_table_hash)) >= 8

    for p in payloads:
        assert p.get("runtime_mode") == "visual_or_handwriting_ai_checked"
        assert p.get("check_mode") in {"review_mode", "handwriting_ai_checked"}
        assert p.get("grading_mode") in {"teacher_review", "ai_assisted_review"}
        assert p.get("visual_backed") is True
        assert p.get("visual_asset_type") == "table"
        schema = p.get("expected_answer_schema") or {}
        freq_map = schema.get("frequency_map") or ((p.get("parameters") or {}).get("frequency_map")) or {}
        raw_data = p.get("raw_data") or ((p.get("parameters") or {}).get("raw_data")) or []
        if freq_map and raw_data:
            for label, cnt in freq_map.items():
                lo, hi = [int(x) for x in str(label).split("-")]
                got = sum(1 for v in raw_data if lo <= int(v) <= hi)
                assert got == int(cnt)


def test_histogram_reading_diversity_and_consistency() -> None:
    skill = _resolve_skill_id("HistogramsAndFrequencyPolygons")
    payloads = [generate_for_chap3_skill(skill_id=skill, seed=i + 1, level=1) for i in range(30)]

    signatures = [str(p.get("parameter_signature", "")) for p in payloads]
    chart_hashes = [str(p.get("chart_spec_hash") or _hash_dict(p.get("chart_spec") or {})) for p in payloads]
    unique_question_types = set()
    for p in payloads:
        q = str(p.get("question_text", ""))
        if "總次數" in q:
            unique_question_types.add("total")
        elif "哪一組" in q and "最多" in q:
            unique_question_types.add("max_group")
        else:
            unique_question_types.add("group_frequency")

    assert len(set(signatures)) >= 10
    assert len(set(chart_hashes)) >= 8
    assert len(unique_question_types) >= 3

    for p in payloads:
        assert p.get("runtime_mode") == "visual_reading_with_short_answer"
        assert p.get("check_mode") == "deterministic_auto_checked"
        assert p.get("grading_mode") == "deterministic"
        assert p.get("image_base64") or p.get("visual_aids") or p.get("chart_spec")
        bins = ((p.get("parameters") or {}).get("bins")) or []
        freqs = ((p.get("parameters") or {}).get("frequencies")) or []
        q = str(p.get("question_text", ""))
        ans = str(p.get("answer", ""))
        if bins and freqs:
            if "總次數" in q:
                assert ans == str(sum(int(v) for v in freqs))
            elif "哪一組" in q and "最多" in q:
                idx = max(range(len(freqs)), key=lambda i: int(freqs[i]))
                assert ans == str(bins[idx])
            else:
                hit = None
                for b, f in zip(bins, freqs):
                    if str(b) in q:
                        hit = str(f)
                        break
                assert hit is not None
                assert ans == hit


def test_blocked_fidelity_regression() -> None:
    skill_h = _resolve_skill_id("HistogramsAndFrequencyPolygons")
    skill_c = _resolve_skill_id("CumulativeFrequencyTablesAndGraphs")
    hp = generate_for_chap3_skill(skill_id=skill_h, seed=1, level=1)
    cp = generate_for_chap3_skill(skill_id=skill_c, seed=1, level=1)

    assert hp.get("problem_type_id") != "frequency_polygon_reading"
    assert hp.get("runtime_mode") == "visual_reading_with_short_answer"
    assert cp.get("problem_type_id") == "cumulative_frequency_table_completion_review"
    assert cp.get("runtime_mode") != "deterministic_short_answer"


def test_localization_and_payload_contract() -> None:
    targets = [
        _resolve_skill_id("CumulativeFrequencyTablesAndGraphs"),
        _resolve_skill_id("FrequencyDistributionTableConstruction"),
        _resolve_skill_id("HistogramsAndFrequencyPolygons"),
    ]
    bad_tokens = ["Read the", "Frequency Table", "Histogram", "Value", "Frequency", "interval", "count"]
    for skill in targets:
        for i in range(10):
            p = generate_for_chap3_skill(skill_id=skill, seed=i + 1, level=1)
            q = str(p.get("question_text", ""))
            exp = str(p.get("explanation", ""))
            assert _is_chinese_text(q)
            assert _is_chinese_text(exp)
            for t in bad_tokens:
                assert t not in q
                assert t not in exp
            if "下表" in q:
                assert p.get("table") or p.get("visual_aids") or p.get("image_base64")
            if "附圖" in q or "直方圖" in q or "下圖" in q:
                assert p.get("image_base64") or p.get("visual_aids") or p.get("chart_spec")

