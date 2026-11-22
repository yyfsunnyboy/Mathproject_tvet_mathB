# -*- coding: utf-8 -*-
"""Regression: cable multipart labels, blank submit, OCR map, checker, AI oracle."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _ok(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        raise AssertionError(f"{name}: {detail}")


def main() -> None:
    from agent_skills_v3.vh_數學B2_TrigonometricFunctionsOfAcuteAngles.components.src_11584.generate import (
        generate,
    )
    from skills.vh_數學B2_TrigonometricFunctionsOfAcuteAngles import check
    from core.gencode.answer_grading import grade_answer_for_current_question
    from core.handwriting_ai_check import (
        HandwritingCheckContext,
        deterministic_final_answer_check,
        normalize_multi_part_handwriting_answer,
    )
    from core.routes.analysis import (
        _handwriting_expected_answer,
        _handwriting_multipart_oracle_match,
        _handwriting_structured_analysis,
    )

    p = generate(seed=1)
    parts = (p.get("answer_contract") or {}).get("parts") or []
    _ok("two_parts", len(parts) == 2, str(parts))
    labels = [str(x.get("display_label") or x.get("label") or "") for x in parts]
    _ok("label0", "海拔" in labels[0] and "elevation" not in labels[0].lower(), labels[0])
    _ok("label1", "水平" in labels[1] and "horizontal" not in labels[1].lower(), labels[1])
    _ok("keys_stable", [x.get("key") for x in parts] == ["elevation", "horizontal_projection"])

    good = {
        "elevation": "500+450sqrt(2)",
        "horizontal_projection": "450sqrt(2)",
    }
    _ok("checker_good", check(good, None, question_payload=p) is True)
    _ok(
        "checker_unicode",
        check(
            {"elevation": "500+450√2", "horizontal_projection": "450√2"},
            None,
            question_payload=p,
        )
        is True,
    )
    _ok(
        "checker_wrong",
        check({"elevation": "500", "horizontal_projection": "450"}, None, question_payload=p)
        is False,
    )

    graded_blank = grade_answer_for_current_question(
        {"elevation": "", "horizontal_projection": ""},
        p,
        str(p.get("skill_id") or ""),
    ) or {}
    msg = str(graded_blank.get("result") or graded_blank.get("message") or "")
    _ok("blank_message", "尚未填寫" in msg and "部分小題答錯" not in msg, msg)

    graded_partial = grade_answer_for_current_question(
        {"elevation": "500+450sqrt(2)", "horizontal_projection": ""},
        p,
        str(p.get("skill_id") or ""),
    ) or {}
    msg2 = str(graded_partial.get("result") or graded_partial.get("message") or "")
    _ok("partial_has_unfilled", "未填寫" in msg2, msg2)

    ctx = HandwritingCheckContext(
        skill_id=str(p.get("skill_id") or ""),
        answer_type="multi_part",
        correct_answer=p.get("correct_answer"),
        answer_contract=p.get("answer_contract"),
        question_text=p.get("question_text"),
        checker="multi_part_answer_checker",
        equivalence="multi_part_answer",
    )
    for raw in (
        "500+450√2; 450√2",
        "500+450sqrt(2)\n450sqrt(2)",
        "(1) 500+450√2 (2) 450√2",
    ):
        mapped = normalize_multi_part_handwriting_answer(raw, ctx)
        _ok(f"ocr_map_{raw[:12]}", isinstance(mapped, dict), str(mapped))
        _ok(f"ocr_det_{raw[:12]}", deterministic_final_answer_check(mapped, ctx) is True, str(mapped))

    exp = _handwriting_expected_answer(p)
    _ok("expected_not_str_dict", "elevation" not in exp or "海拔" in exp or "(1)" in exp, exp)
    _ok("expected_no_brace_dict", not exp.startswith("{"), exp)

    oracle = _handwriting_multipart_oracle_match("500+450√2; 450√2", p)
    _ok("multipart_oracle", oracle is True, str(oracle))
    analysis = _handwriting_structured_analysis(
        "500+450√2; 450√2",
        exp,
        p.get("question_text"),
        "",
        trusted_question=p,
    )
    _ok("analysis_correct", analysis.get("status") == "correct", str(analysis.get("status")))
    _ok(
        "analysis_source_oracle",
        analysis.get("analysis_source") == "multipart_oracle_checker",
        str(analysis.get("analysis_source")),
    )

    # Other acute types still generate
    from skills.vh_數學B2_TrigonometricFunctionsOfAcuteAngles import generate as gen_skill

    for seed in range(8):
        q = gen_skill(level=1, seed=seed)
        _ok(f"acute_seed_{seed}", bool(q.get("question_text") or q.get("question")))

    print("ALL_PASS")


if __name__ == "__main__":
    main()
