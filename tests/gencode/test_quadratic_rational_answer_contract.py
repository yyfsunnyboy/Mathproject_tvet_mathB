from __future__ import annotations

from core.gencode.answer_contract_policy import infer_answer_contract_from_problem_context
from core.gencode.generator_diversity_sampling import _detect_payload_spec_contract_mismatch
from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization
from core.gencode.problem_type_induction import _build_problem_type_spec_draft
from core.gencode.slot_generators import SLOT_REGISTRY
from core.gencode.validators import validate_generator_payload


def _checker(ac: dict) -> str:
    return str(ac.get("checker_key") or ac.get("checker") or "")


def test_quadratic_vertex_contract_accepts_fractional_answer_payload() -> None:
    spec = enrich_spec_with_canonicalization(
        {
            "problem_type_id": "integer_quadratic_vertex_or_parameter_computation",
            "target_task": "quadratic_vertex_or_parameter_computation",
            "answer_contract": {
                "answer_type": "integer",
                "checker_key": "integer_checker",
                "equivalence_type": "numeric_exact",
            },
        }
    )
    ac = spec["answer_contract"]

    assert spec["problem_type_id"] == "quadratic_vertex_or_parameter_computation"
    assert ac["answer_type"] in {"rational", "numeric"}
    assert _checker(ac) != "integer_checker"
    assert ac["answer_shape"] == "scalar"
    assert ac["equivalence_type"] == "rational_equivalent"

    payloads = [
        {
            "answer_type": ac["answer_type"],
            "answer": "-9/8",
            "correct_answer": "-9/8",
            "checker": _checker(ac),
            "answer_contract": ac,
        }
        for _ in range(4)
    ]
    assert not _detect_payload_spec_contract_mismatch(spec, payloads)


def _rational_spec() -> dict:
    return {
        "problem_type_id": "quadratic_vertex_or_parameter_computation",
        "answer_contract": {
            "answer_type": "rational",
            "answer_shape": "scalar",
            "answer_equivalence": "rational_equivalent",
            "equivalence_type": "rational_equivalent",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
        },
        "stem_contract": {"stem_must_not_embed_choices": True},
        "dependency_contract": {},
        "semantic_contract": {},
    }


def test_rational_validator_accepts_integer_string_answer_and_correct_answer() -> None:
    payload = {
        "problem_type_id": "quadratic_vertex_or_parameter_computation",
        "question_text": "求頂點參數。",
        "answer_type": "rational",
        "answer": "5",
        "correct_answer": "5",
        "choices": [],
        "metadata": {},
    }

    assert validate_generator_payload(payload, problem_type_spec=_rational_spec()) == []


def test_rational_validator_accepts_fraction_string_answer_and_correct_answer() -> None:
    payload = {
        "problem_type_id": "quadratic_vertex_or_parameter_computation",
        "question_text": "求頂點參數。",
        "answer_type": "rational",
        "answer": "-9/8",
        "correct_answer": " -9 / 8 ",
        "choices": [],
        "metadata": {},
    }

    assert validate_generator_payload(payload, problem_type_spec=_rational_spec()) == []


def test_rational_validator_rejects_invalid_string_answer() -> None:
    payload = {
        "problem_type_id": "quadratic_vertex_or_parameter_computation",
        "question_text": "求頂點參數。",
        "answer_type": "rational",
        "answer": "A",
        "correct_answer": "1/0",
        "choices": [],
        "metadata": {},
    }

    errors = validate_generator_payload(payload, problem_type_spec=_rational_spec())
    assert any("invalid_answer_type" in err for err in errors)


def test_source_integer_example_does_not_make_quadratic_vertex_type_integer() -> None:
    spec, _legacy = _build_problem_type_spec_draft(
        "vh_數學B1_CompletingTheSquare",
        {
            "answer_type": "integer",
            "features": [
                {
                    "source_example_id": 1,
                    "answer": "-2",
                    "target_task": "quadratic_vertex_or_parameter_computation",
                    "math_objects": ["quadratic_equation", "axis_of_symmetry"],
                    "has_choices": False,
                }
            ],
        },
        set(),
    )

    ac = spec["answer_contract"]
    assert spec["problem_type_id"] == "quadratic_vertex_or_parameter_computation"
    assert ac["answer_type"] in {"rational", "numeric"}
    assert _checker(ac) != "integer_checker"


def test_proxy_integer_prefix_is_removed_for_quadratic_vertex_rational_capable_type() -> None:
    spec, _legacy = _build_problem_type_spec_draft(
        "vh_數學B1_CompletingTheSquare",
        {
            "answer_type": "integer",
            "features": [
                {
                    "source_example_id": 2,
                    "answer": "5",
                    "target_task": "quadratic_vertex_or_parameter_computation",
                    "proxy_problem_type_id": "integer_quadratic_vertex_or_parameter_computation",
                    "math_objects": ["quadratic_equation", "axis_of_symmetry"],
                    "has_choices": False,
                }
            ],
        },
        set(),
    )

    assert spec["problem_type_id"] == "quadratic_vertex_or_parameter_computation"


def test_proxy_integer_prefix_is_removed_for_quadratic_vertex_axis_choice_type() -> None:
    spec, _legacy = _build_problem_type_spec_draft(
        "vh_數學B1_CompletingTheSquare",
        {
            "answer_type": "single_choice",
            "features": [
                {
                    "source_example_id": 3,
                    "answer": "A",
                    "target_task": "quadratic_graph_vertex_axis_choice",
                    "proxy_problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
                    "math_objects": ["quadratic_equation", "axis_of_symmetry"],
                    "has_choices": True,
                }
            ],
        },
        set(),
    )

    assert spec["problem_type_id"] == "quadratic_graph_vertex_axis_choice"


def test_quadratic_vertex_slot_can_emit_fraction_under_rational_contract() -> None:
    spec = enrich_spec_with_canonicalization(
        {
            "problem_type_id": "quadratic_vertex_or_parameter_computation",
            "target_task": "quadratic_vertex_or_parameter_computation",
            "answer_contract": infer_answer_contract_from_problem_context(
                answer_type="numeric",
                target_task="quadratic_vertex_or_parameter_computation",
            ),
        }
    )
    payloads = [
        SLOT_REGISTRY["quadratic_vertex_or_parameter_computation"](
            "vh_數學B1_CompletingTheSquare",
            "quadratic_vertex_or_parameter_computation",
            spec,
            seed,
        )
        for seed in range(1, 20)
    ]

    assert any("/" in str(p.get("answer", "")) for p in payloads)
    assert not _detect_payload_spec_contract_mismatch(spec, payloads)


def test_integer_only_contract_fails_when_generator_emits_rational_payloads() -> None:
    spec = {
        "problem_type_id": "integer_only_quadratic_axis_value",
        "target_task": "integer_only_quadratic_axis_value",
        "answer_contract": {
            "answer_type": "integer",
            "checker_key": "integer_checker",
            "equivalence_type": "numeric_exact",
        },
    }
    payloads = [{"answer_type": "rational", "answer": "-9/8"} for _ in range(4)]

    blockers = _detect_payload_spec_contract_mismatch(spec, payloads)
    assert "checker_answer_mismatch:spec_integer_but_payload_rational" in blockers
