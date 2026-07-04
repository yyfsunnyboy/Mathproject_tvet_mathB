from __future__ import annotations

import math

from core.gencode.midpoint_source_fidelity import (
    PROBLEM_TYPES,
    SOURCE_SPECS,
    generate_source_faithful_payload,
    validate_source_fidelity,
)


def test_source_specs_cover_ten_examples_and_required_problem_types() -> None:
    assert len(SOURCE_SPECS) == 10
    assert {
        "midpoint_coordinate",
        "midpoint_distance_from_origin",
        "parallelogram_fourth_vertex",
        "centroid_coordinate",
        "inverse_centroid_vertex",
        "triangle_median_length",
        "multi_part_midpoint_application",
    } <= PROBLEM_TYPES


def test_all_components_pass_ten_seed_source_fidelity() -> None:
    for source_id in SOURCE_SPECS:
        for seed in range(10):
            payload = generate_source_faithful_payload(source_id, seed)
            result = validate_source_fidelity(source_id, payload)
            assert result["passed"], (source_id, seed, result["errors"])


def test_src_4511_is_always_triangle_median_length() -> None:
    for seed in range(10):
        payload = generate_source_faithful_payload(4511, seed)
        assert payload["problem_type_id"] == "triangle_median_length"
        assert payload["presentation_mode"] == "single_choice"
        assert "三角形 ABC" in payload["question_text"]
        assert "AB 邊上的中線長" in payload["question_text"]
        assert "AP:PB" not in payload["question_text"]
        coords = payload["metadata"]["generation_coords"]
        midpoint = (
            (coords["A"][0] + coords["B"][0]) / 2,
            (coords["A"][1] + coords["B"][1]) / 2,
        )
        expected_squared = (
            (coords["C"][0] - midpoint[0]) ** 2
            + (coords["C"][1] - midpoint[1]) ** 2
        )
        semantic = payload["semantic_answer"]
        assert semantic
        correct_choice = next(
            choice for choice in payload["choices"]
            if choice["label"] == payload["correct_answer"]
        )
        assert correct_choice["text"] == semantic
        assert expected_squared > 0


def test_choice_semantics_and_visual_points_are_preserved() -> None:
    for source_id in (4511, 4514):
        for seed in range(10):
            payload = generate_source_faithful_payload(source_id, seed)
            assert payload["semantic_answer"] == payload["metadata"]["semantic_answer"]
            assert payload["answer_contract"]["semantic_answer"] == payload["semantic_answer"]
            assert payload["visual_spec"]["points"]
            labels = {point["label"] for point in payload["visual_spec"]["points"]}
            assert {"A", "B", "C"} <= labels
            assert len(payload["choices"]) == 4
            assert len({choice["text"] for choice in payload["choices"]}) == 4


def test_medial_triangle_centroid_matches_original_triangle_centroid() -> None:
    for seed in range(10):
        payload = generate_source_faithful_payload(4514, seed)
        coords = payload["metadata"]["generation_coords"]
        triangle_centroid = (
            sum(coords[name][0] for name in "ABC") / 3,
            sum(coords[name][1] for name in "ABC") / 3,
        )
        medial_centroid = (
            sum(coords[name][0] for name in "DEF") / 3,
            sum(coords[name][1] for name in "DEF") / 3,
        )
        assert math.isclose(triangle_centroid[0], medial_centroid[0])
        assert math.isclose(triangle_centroid[1], medial_centroid[1])
        assert payload["semantic_answer"] == f"({int(medial_centroid[0])},{int(medial_centroid[1])})"
