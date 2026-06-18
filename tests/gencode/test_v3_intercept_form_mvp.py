from __future__ import annotations

from core.domain.coordinate_geometry.line_equation_domain import (
    build_intercept_form_equation_and_area,
    build_intercept_form_from_intercept_sum_and_slope,
    build_parabola_secant_parallel_line_choice,
    build_triangle_area_bisector_line,
    build_intercept_form_from_intercepts,
    build_intercept_triangle_area,
    build_line_equation_matrix,
    get_coordinate_midpoint,
)
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.pipeline_orchestrator import build_v3_component_draft_from_skill
from core.gencode.runtime_skill_wrapper import check_answer

SKILL_ID = "vh_數學B1_InterceptForm"


def test_intercept_form_domain_equation_and_area() -> None:
    equation = build_intercept_form_from_intercepts(2, -3)
    assert equation["general_form"] == "3x - 2y - 6 = 0"
    assert equation["x_intercept"] == "2"
    assert equation["y_intercept"] == "-3"
    assert build_intercept_triangle_area(2, -3) == 3
    assert build_intercept_form_equation_and_area(2, -3) == {
        "equation": "3x - 2y - 6 = 0",
        "area": "3",
    }
    assert build_intercept_form_from_intercept_sum_and_slope(6, r"\frac{3}{2}")["general_form"] == (
        "3x - 2y + 36 = 0"
    )
    secant = build_parabola_secant_parallel_line_choice(
        -3,
        1,
        [
            {"label": "A", "text": "y=-2x"},
            {"label": "B", "text": r"y=\frac{-1}{2}x"},
            {"label": "C", "text": r"y=\frac{1}{2}x"},
            {"label": "D", "text": "y=2x"},
        ],
    )
    assert secant["slope"] == "-2"
    assert secant["correct_answer"] == "A"
    assert secant["semantic_answer"] == "y = -2x"
    assert get_coordinate_midpoint((4, 2), (2, -2)) == ("3", "0")
    bisector = build_triangle_area_bisector_line(
        {"x": 7, "y": -3},
        {"x": 4, "y": 2},
        {"x": 2, "y": -2},
    )
    assert bisector["midpoint"] == {"x": "3", "y": "0"}
    assert bisector["general_form"] == "3x + 4y - 9 = 0"


def test_intercept_form_equation_and_area_payload_uses_multi_part_checker() -> None:
    matrix = build_line_equation_matrix(
        seed=1,
        line_type="intercept_form_equation_and_triangle_area",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"x_intercept": "2", "y_intercept": "-3"},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="intercept_form_equation_and_triangle_area",
    )

    assert payload["answer_type"] == "multi_part"
    assert payload["choices"] == []
    assert payload["answer_contract"]["checker"] == "multi_part_answer_checker"
    assert payload["answer"] == {"equation": "3x - 2y - 6 = 0", "area": "3"}
    assert check_answer(
        {"equation": "x/2 - y/3 = 1", "area": "3"},
        payload["correct_answer"],
        payload=payload,
    )
    assert not check_answer(
        {"equation": "x/2 - y/3 = 1", "area": "4"},
        payload["correct_answer"],
        payload=payload,
    )

    fractional_area_matrix = build_line_equation_matrix(
        seed=1,
        line_type="intercept_form_equation_and_triangle_area",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"x_intercept": "-1", "y_intercept": "5"},
    )
    fractional_area_payload = convert_line_equation_matrix_to_question_payload(
        fractional_area_matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="intercept_form_equation_and_triangle_area",
    )

    assert fractional_area_payload["correct_answer"]["area"] == "5/2"
    assert fractional_area_payload["display_answer"]["area"] == r"\frac{5}{2}"
    assert "5/2" not in str(fractional_area_payload["display_answer"])
    assert check_answer(
        {"equation": "5x - y + 5 = 0", "area": "5/2"},
        fractional_area_payload["correct_answer"],
        payload=fractional_area_payload,
    )


def test_intercept_form_triangle_area_single_choice_uses_numeric_choices() -> None:
    matrix = build_line_equation_matrix(
        seed=1,
        line_type="intercept_form_triangle_area",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"equation_coefficients": {"A": 4, "B": -3, "C": 12}},
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="intercept_form_triangle_area",
    )

    assert payload["answer_type"] == "single_choice"
    assert payload["answer"] in {"A", "B", "C", "D"}
    assert payload["semantic_answer"] == "6"
    assert len(payload["choices"]) == 4
    assert len({choice["text"] for choice in payload["choices"]}) == 4
    assert all("x" not in choice["text"] and "y" not in choice["text"] for choice in payload["choices"])
    assert check_answer(payload["answer"], payload["correct_answer"], payload=payload)


def test_intercept_form_v3_bridge_classifies_supported_rows() -> None:
    rows = {
        4548: {
            "id": 4548,
            "skill_id": SKILL_ID,
            "problem_type": "advanced_exercise",
            "problem_text": r"若直線L在兩坐標軸上的截距和為6，且L之斜率為$\frac{3}{2}$，則L之方程式為何？",
            "correct_answer": "",
        },
        4547: {
            "id": 4547,
            "skill_id": SKILL_ID,
            "problem_type": "textbook_exercise",
            "problem_text": "設直線L : 2x − 7y − 14 = 0，試求：(1) 直線L化成截距式。(2) 面積。",
            "correct_answer": "",
        },
        4555: {
            "id": 4555,
            "skill_id": SKILL_ID,
            "problem_type": "textbook_example",
            "problem_text": "已知一直線L的x截距為2，y截距為−3，試求：(1)直線L的方程式。(2)面積。",
            "correct_answer": "",
        },
        4604: {
            "id": 4604,
            "skill_id": SKILL_ID,
            "problem_type": "self_assessment",
            "problem_text": "坐標平面上的直線4x − 3y + 12 = 0，它與x軸及y軸所圍成之三角形的面積為多少平方單位？ (A) 6 (B) 7 (C) 12 (D) 24。",
            "correct_answer": "",
        },
        4559: {
            "id": 4559,
            "skill_id": SKILL_ID,
            "problem_type": "exam_practice",
            "problem_text": r"若A、B兩點分別是拋物線 y={{x}^{2}} 與直線 x=-3、x=1 的交點，則直線AB與哪一條直線平行？ (A)$y=-2x$ (B)$y=\frac{-1}{2}x$ (C)$y=\frac{1}{2}x$ (D)$y=2x$",
            "correct_answer": "",
        },
        4558: {
            "id": 4558,
            "skill_id": SKILL_ID,
            "problem_type": "advanced_exercise",
            "problem_text": r"三角形農地 A\left( 4,2 \right)、B\left( 7,-3 \right)、C\left( 2,-2 \right)，點D在AC上，試求平分農地面積的直線BD之方程式。",
            "correct_answer": "",
        },
    }

    expected = {
        4548: ("intercept_form_from_intercept_sum_and_slope", "expression"),
        4547: ("intercept_form_equation_and_triangle_area", "multi_part"),
        4555: ("intercept_form_equation_and_triangle_area", "multi_part"),
        4604: ("intercept_form_triangle_area", "single_choice"),
        4559: ("parabola_secant_parallel_line_choice", "single_choice"),
        4558: ("triangle_area_bisector_line_equation", "linear_equation"),
    }
    for example_id, row in rows.items():
        draft = build_v3_component_draft_from_skill(
            SKILL_ID,
            textbook_example_id=example_id,
            source_kind=f"ex_{example_id}",
            seed=42,
            textbook_row=row,
        )
        assert (draft["line_type"], draft["answer_type"]) == expected[example_id]

def test_intercept_form_triangle_area_bisector_payload_uses_linear_checker() -> None:
    draft = build_v3_component_draft_from_skill(
        SKILL_ID,
        textbook_example_id=4558,
        source_kind="ex_4558",
        seed=42,
        textbook_row={
            "id": 4558,
            "skill_id": SKILL_ID,
            "problem_type": "advanced_exercise",
            "problem_text": r"三角形農地 A\left( 4,2 \right)、B\left( 7,-3 \right)、C\left( 2,-2 \right)，點D在AC上，試求平分農地面積的直線BD之方程式。",
            "correct_answer": "",
        },
    )

    assert draft["line_type"] == "triangle_area_bisector_line_equation"
    namespace: dict[str, object] = {}
    exec(draft["files"]["generate.py"], namespace)
    payload = namespace["generate"](seed=42)
    assert payload["answer_contract"]["checker"] == "linear_equation_equivalent_checker"
    assert payload["correct_answer"] == "3x + 4y - 9 = 0"
    assert check_answer("6x + 8y - 18 = 0", payload["correct_answer"], payload=payload)


def test_intercept_form_production_components_variation() -> None:
    import importlib.util
    from pathlib import Path
    from core.gencode.services.v3_variation_audit_service import extract_parameter_signature
    
    base = Path(__file__).resolve().parents[2] / "agent_skills_v3" / "vh_數學B1_InterceptForm" / "components"
    components = sorted([p.name for p in base.glob("src_*") if p.is_dir()])
    
    for comp_id in components:
        gen_path = base / comp_id / "generate.py"
        spec = importlib.util.spec_from_file_location(f"prod_mod_{comp_id}", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        payloads = []
        for seed in range(1, 21):
            payload = mod.generate(seed=seed, component_id=comp_id)
            payloads.append(payload)
            
            # Check necessary fields
            assert "question_text" in payload or "new_question_text" in payload
            assert "correct_answer" in payload
            assert payload.get("problem_type_id") is not None
            assert payload.get("answer_type") is not None
            
            # Single choice checks
            if payload.get("presentation_mode") == "single_choice":
                choices = payload.get("choices") or []
                assert len(choices) == 4
                texts = [c["text"] for c in choices]
                assert len(set(texts)) == 4  # choices不重複
                ans_label = payload["correct_answer"]
                assert ans_label in ("A", "B", "C", "D")  # answer存在於choices
                
            # Multi-part checks
            if payload.get("answer_type") == "multi_part":
                c_ans = payload["correct_answer"]
                assert isinstance(c_ans, dict)
                assert "equation" in c_ans or "canonical_form" in c_ans
                assert "area" in c_ans
                
        # Unique count checks
        unique_q = len(set(p["question_text"] for p in payloads))
        unique_sigs = len(set(extract_parameter_signature(p) for p in payloads))
        
        assert unique_q > 1, f"Component {comp_id} has static question text"
        assert unique_sigs > 1, f"Component {comp_id} has static parameters"

