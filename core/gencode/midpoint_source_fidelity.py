"""Source-topology contracts and generators for MidpointCoordinates components."""

from __future__ import annotations

import math
import random
from typing import Any

SKILL_ID = "vh_數學B1_MidpointCoordinates"

SOURCE_SPECS: dict[int, dict[str, Any]] = {
    4418: {
        "problem_type_id": "multi_part_midpoint_application",
        "required_givens": ["endpoint_a", "endpoint_b", "midpoint_relation", "third_point"],
        "requested_quantity": ["segment_length", "midpoint_to_third_point_distance"],
        "topology_tags": ["two_endpoints", "declared_midpoint", "two_part_distance"],
        "answer_schema": "multi_part_scalar",
        "presentation_mode": "short_answer",
    },
    4422: {
        "problem_type_id": "parallelogram_fourth_vertex",
        "required_givens": ["three_consecutive_vertices", "parallelogram_relation"],
        "requested_quantity": ["fourth_vertex_coordinate"],
        "topology_tags": ["parallelogram", "diagonals_bisect", "inverse_midpoint"],
        "answer_schema": "coordinate_pair",
        "presentation_mode": "short_answer",
    },
    4428: {
        "problem_type_id": "midpoint_distance_from_origin",
        "required_givens": ["endpoint_a", "endpoint_b", "midpoint_relation", "origin"],
        "requested_quantity": ["midpoint_distance_from_origin"],
        "topology_tags": ["two_endpoints", "midpoint_then_distance", "origin_distance"],
        "answer_schema": "radical_scalar",
        "presentation_mode": "short_answer",
    },
    4429: {
        "problem_type_id": "parallelogram_fourth_vertex",
        "required_givens": ["three_consecutive_vertices", "parallelogram_relation"],
        "requested_quantity": ["fourth_vertex_coordinate"],
        "topology_tags": ["parallelogram", "diagonals_bisect", "inverse_midpoint"],
        "answer_schema": "coordinate_pair",
        "presentation_mode": "short_answer",
    },
    4439: {
        "problem_type_id": "midpoint_distance_from_origin",
        "required_givens": ["endpoint_a", "endpoint_b", "midpoint_relation", "origin"],
        "requested_quantity": ["midpoint_distance_from_origin"],
        "topology_tags": ["two_endpoints", "midpoint_then_distance", "origin_distance"],
        "answer_schema": "radical_scalar",
        "presentation_mode": "short_answer",
    },
    4440: {
        "problem_type_id": "parallelogram_fourth_vertex",
        "required_givens": ["three_consecutive_vertices", "parallelogram_relation"],
        "requested_quantity": ["fourth_vertex_coordinate"],
        "topology_tags": ["parallelogram", "diagonals_bisect", "inverse_midpoint"],
        "answer_schema": "coordinate_pair",
        "presentation_mode": "short_answer",
    },
    4443: {
        "problem_type_id": "centroid_coordinate",
        "required_givens": ["triangle_three_vertices"],
        "requested_quantity": ["centroid_coordinate"],
        "topology_tags": ["triangle", "three_vertices", "centroid_formula"],
        "answer_schema": "coordinate_pair",
        "presentation_mode": "short_answer",
    },
    4447: {
        "problem_type_id": "inverse_centroid_vertex",
        "required_givens": ["two_triangle_vertices", "centroid_coordinate"],
        "requested_quantity": ["missing_vertex_coordinate"],
        "topology_tags": ["triangle", "known_centroid", "inverse_centroid_formula"],
        "answer_schema": "coordinate_pair",
        "presentation_mode": "short_answer",
    },
    4511: {
        "problem_type_id": "triangle_median_length",
        "required_givens": ["triangle_three_vertices", "specified_side"],
        "requested_quantity": ["median_length_to_specified_side"],
        "topology_tags": ["triangle", "side_midpoint", "opposite_vertex_distance", "median"],
        "answer_schema": "choice_label_with_radical_scalar",
        "presentation_mode": "single_choice",
    },
    4514: {
        "problem_type_id": "multi_part_midpoint_application",
        "required_givens": ["triangle_three_vertices", "three_side_midpoints"],
        "requested_quantity": ["medial_triangle_centroid_coordinate"],
        "topology_tags": ["triangle", "three_midpoints", "medial_triangle", "centroid"],
        "answer_schema": "choice_label_with_coordinate_pair",
        "presentation_mode": "single_choice",
    },
}

PROBLEM_TYPES = frozenset(
    {
        "midpoint_coordinate",
        "midpoint_distance_from_origin",
        "parallelogram_fourth_vertex",
        "centroid_coordinate",
        "inverse_centroid_vertex",
        "triangle_median_length",
        "multi_part_midpoint_application",
    }
)


def get_source_spec(source_example_id: int) -> dict[str, Any]:
    try:
        return dict(SOURCE_SPECS[int(source_example_id)])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"unsupported_midpoint_source_example:{source_example_id}") from exc


def _rng(seed: int | None, source_example_id: int) -> random.Random:
    return random.Random(f"{seed}|{SKILL_ID}|{source_example_id}")


def _point(rng: random.Random) -> tuple[int, int]:
    return rng.randint(-7, 7), rng.randint(-7, 7)


def _distinct_points(rng: random.Random, count: int) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    while len(points) < count:
        point = _point(rng)
        if point not in points:
            points.append(point)
    return points


def _pair(point: tuple[int, int]) -> str:
    return f"({point[0]},{point[1]})"


def _radical(square: int) -> str:
    root = math.isqrt(square)
    if root * root == square:
        return str(root)
    factor = 1
    for candidate in range(2, root + 1):
        if square % (candidate * candidate) == 0:
            factor = candidate
    remainder = square // (factor * factor)
    return f"sqrt({remainder})" if factor == 1 else f"{factor}*sqrt({remainder})"


def _distance_answer(first: tuple[int, int], second: tuple[int, int]) -> str:
    return _radical((first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2)


def _coordinate_choices(
    rng: random.Random, correct: tuple[int, int]
) -> tuple[list[dict[str, str]], str]:
    candidates = [
        correct,
        (correct[1], correct[0]),
        (correct[0] + 1, correct[1]),
        (correct[0], correct[1] - 1),
    ]
    unique: list[tuple[int, int]] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    while len(unique) < 4:
        candidate = (correct[0] + rng.randint(-4, 4), correct[1] + rng.randint(-4, 4))
        if candidate not in unique:
            unique.append(candidate)
    rng.shuffle(unique)
    labels = "ABCD"
    choices = [
        {"label": label, "text": _pair(value), "value": _pair(value)}
        for label, value in zip(labels, unique)
    ]
    return choices, labels[unique.index(correct)]


def _scalar_choices(rng: random.Random, correct: str, square: int) -> tuple[list[dict[str, str]], str]:
    values = [
        correct,
        _radical(square + 1),
        _radical(max(1, square - 1)),
        _radical(square * 4),
    ]
    values = list(dict.fromkeys(values))
    while len(values) < 4:
        values.append(str(math.isqrt(square) + len(values) + 1))
        values = list(dict.fromkeys(values))
    rng.shuffle(values)
    labels = "ABCD"
    choices = [
        {"label": label, "text": value, "value": value}
        for label, value in zip(labels, values)
    ]
    return choices, labels[values.index(correct)]


def _base_payload(
    source_example_id: int,
    seed: int | None,
    question: str,
    semantic_answer: Any,
    explanation: str,
    points: dict[str, tuple[int, int]],
    *,
    choices: list[dict[str, str]] | None = None,
    correct_label: str | None = None,
) -> dict[str, Any]:
    spec = get_source_spec(source_example_id)
    mode = spec["presentation_mode"]
    if mode == "single_choice":
        answer = correct_label
    elif isinstance(semantic_answer, dict):
        answer = "; ".join(f"({key}) {value}" for key, value in semantic_answer.items())
    else:
        answer = semantic_answer
    answer_type = "single_choice" if mode == "single_choice" else spec["answer_schema"]
    source_trace = {
        "skill_id": SKILL_ID,
        "source_id": source_example_id,
        "component_id": f"src_{source_example_id}",
    }
    metadata = {
        "source_trace": source_trace,
        "source_topology": spec,
        "required_givens": list(spec["required_givens"]),
        "requested_quantity": list(spec["requested_quantity"]),
        "topology_tags": list(spec["topology_tags"]),
        "answer_schema": spec["answer_schema"],
        "presentation_mode": mode,
        "semantic_answer": semantic_answer,
        "generation_coords": {name: list(point) for name, point in points.items()},
    }
    visual_spec = {
        "kind": "coordinate_plane_spec",
        "points": [
            {"label": name, "x": point[0], "y": point[1]}
            for name, point in points.items()
        ],
        "lines": [],
        "x_range": [-10, 10],
        "y_range": [-10, 10],
    }
    return {
        "skill_id": SKILL_ID,
        "component_id": f"src_{source_example_id}",
        "source_id": source_example_id,
        "textbook_example_id": source_example_id,
        "generator_key": f"src_{source_example_id}",
        "problem_type_id": spec["problem_type_id"],
        "operation": spec["problem_type_id"],
        "question_text": question,
        "question": question,
        "answer": answer,
        "correct_answer": answer,
        "correct_value": semantic_answer,
        "semantic_answer": semantic_answer,
        "display_answer": answer,
        "choices": choices or [],
        "options": [choice["text"] for choice in choices or []],
        "presentation_mode": mode,
        "answer_type": answer_type,
        "checker": "choice_label_checker" if mode == "single_choice" else "exact_string_checker",
        "checker_type": "choice_label_checker" if mode == "single_choice" else "exact_string_checker",
        "equivalence": "choice_label" if mode == "single_choice" else "exact",
        "explanation": explanation,
        "metadata": metadata,
        "math_core": {
            "semantic_answer": semantic_answer,
            "generation_coords": metadata["generation_coords"],
            "topology_tags": spec["topology_tags"],
        },
        "visual_spec": visual_spec,
        "answer_contract": {
            "presentation_mode": mode,
            "answer_type": answer_type,
            "answer_schema": spec["answer_schema"],
            "checker": "choice_label_checker" if mode == "single_choice" else "exact_string_checker",
            "semantic_answer": semantic_answer,
        },
        "seed": seed,
        "source": "midpoint_source_topology_generator",
    }


def generate_source_faithful_payload(
    source_example_id: int, seed: int | None = None
) -> dict[str, Any]:
    spec = get_source_spec(source_example_id)
    rng = _rng(seed, source_example_id)
    problem_type = spec["problem_type_id"]

    if source_example_id == 4418:
        a, b, c = _distinct_points(rng, 3)
        p = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        a = (2 * p[0] - b[0], 2 * p[1] - b[1])
        answers = {"1": _distance_answer(a, b), "2": _distance_answer(p, c)}
        question = (
            f"若 P 為 A{_pair(a)} 與 B{_pair(b)} 兩點之中點，C{_pair(c)}，試求："
            "(1) 線段 AB 的長度；(2) P 點與 C 點的距離。"
        )
        return _base_payload(
            source_example_id, seed, question, answers,
            f"先由 A、B 求中點 P，再分別使用距離公式求 AB 與 PC，答案為 {answers}。",
            {"A": a, "B": b, "P": p, "C": c},
        )

    if problem_type == "parallelogram_fourth_vertex":
        a, b, c = _distinct_points(rng, 3)
        d = (a[0] + c[0] - b[0], a[1] + c[1] - b[1])
        question = (
            f"設 A{_pair(a)}、B{_pair(b)}、C{_pair(c)} 依序為平行四邊形 ABCD "
            "之三頂點，求 D 點坐標。"
        )
        return _base_payload(
            source_example_id, seed, question, _pair(d),
            f"平行四邊形對角線互相平分，故 D=A+C-B={_pair(d)}。",
            {"A": a, "B": b, "C": c, "D": d},
        )

    if problem_type == "midpoint_distance_from_origin":
        p = _point(rng)
        delta = _point(rng)
        if delta == (0, 0):
            delta = (1, 2)
        a, b = (p[0] - delta[0], p[1] - delta[1]), (p[0] + delta[0], p[1] + delta[1])
        answer = _distance_answer(p, (0, 0))
        question = f"若 P 為 A{_pair(a)} 與 B{_pair(b)} 兩點之中點，求 P 點與原點 O 的距離。"
        return _base_payload(
            source_example_id, seed, question, answer,
            f"先求 P={_pair(p)}，再用距離公式得 OP={answer}。",
            {"A": a, "B": b, "P": p, "O": (0, 0)},
        )

    if problem_type == "centroid_coordinate":
        g = _point(rng)
        a, b = _distinct_points(rng, 2)
        c = (3 * g[0] - a[0] - b[0], 3 * g[1] - a[1] - b[1])
        question = f"設三角形 ABC 的三頂點為 A{_pair(a)}、B{_pair(b)}、C{_pair(c)}，求其重心坐標。"
        return _base_payload(
            source_example_id, seed, question, _pair(g),
            f"重心為三頂點坐標平均，G={_pair(g)}。",
            {"A": a, "B": b, "C": c, "G": g},
        )

    if problem_type == "inverse_centroid_vertex":
        a, b, g = _distinct_points(rng, 3)
        c = (3 * g[0] - a[0] - b[0], 3 * g[1] - a[1] - b[1])
        question = (
            f"已知 A{_pair(a)}、B{_pair(b)}，且 G{_pair(g)} 為三角形 ABC 的重心，"
            "求 C 點坐標。"
        )
        return _base_payload(
            source_example_id, seed, question, _pair(c),
            f"由 G=(A+B+C)/3，得 C=3G-A-B={_pair(c)}。",
            {"A": a, "B": b, "C": c, "G": g},
        )

    if problem_type == "triangle_median_length":
        a, b, c = _distinct_points(rng, 3)
        midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        square_times_four = (
            (2 * c[0] - a[0] - b[0]) ** 2
            + (2 * c[1] - a[1] - b[1]) ** 2
        )
        semantic = (
            _radical(square_times_four // 4)
            if square_times_four % 4 == 0
            else f"{_radical(square_times_four)}/2"
        )
        choices, label = _scalar_choices(rng, semantic, max(1, square_times_four // 4))
        question = (
            f"已知三角形 ABC 的三頂點為 A{_pair(a)}、B{_pair(b)}、C{_pair(c)}，"
            "則 AB 邊上的中線長為何？"
        )
        return _base_payload(
            source_example_id, seed, question, semantic,
            f"先求 AB 中點 M=({midpoint[0]:g},{midpoint[1]:g})，再求 CM={semantic}。",
            {"A": a, "B": b, "C": c},
            choices=choices, correct_label=label,
        )

    if source_example_id == 4514:
        g = _point(rng)
        u, v = _distinct_points(rng, 2)
        a = (g[0] + 2 * u[0], g[1] + 2 * u[1])
        b = (g[0] + 2 * v[0], g[1] + 2 * v[1])
        c = (g[0] - 2 * u[0] - 2 * v[0], g[1] - 2 * u[1] - 2 * v[1])
        d = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        e = ((b[0] + c[0]) // 2, (b[1] + c[1]) // 2)
        f = ((c[0] + a[0]) // 2, (c[1] + a[1]) // 2)
        centroid = g
        choices, label = _coordinate_choices(rng, centroid)
        question = (
            f"設 A{_pair(a)}、B{_pair(b)}、C{_pair(c)} 是三角形 ABC 的三頂點，"
            "D、E、F 分別為 AB、BC、CA 的中點，則三角形 DEF 的重心坐標為何？"
        )
        return _base_payload(
            source_example_id, seed, question, _pair(centroid),
            f"先求三邊中點 D、E、F，再取三點坐標平均，得 {_pair(centroid)}。",
            {"A": a, "B": b, "C": c, "D": d, "E": e, "F": f},
            choices=choices, correct_label=label,
        )

    raise ValueError(f"unimplemented_midpoint_source_topology:{source_example_id}")


def validate_source_fidelity(
    source_example_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    expected = get_source_spec(source_example_id)
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    actual = {
        "required_givens": metadata.get("required_givens"),
        "requested_quantity": metadata.get("requested_quantity"),
        "topology_tags": metadata.get("topology_tags"),
        "answer_schema": metadata.get("answer_schema"),
        "presentation_mode": payload.get("presentation_mode"),
    }
    errors = [
        f"{field}: expected {expected[field]!r}, got {actual[field]!r}"
        for field in actual
        if actual[field] != expected[field]
    ]
    if payload.get("problem_type_id") != expected["problem_type_id"]:
        errors.append(
            f"problem_type_id: expected {expected['problem_type_id']!r}, "
            f"got {payload.get('problem_type_id')!r}"
        )
    if payload.get("semantic_answer") != metadata.get("semantic_answer"):
        errors.append("semantic_answer is not preserved in metadata")
    if not (payload.get("visual_spec") or {}).get("points"):
        errors.append("visual_spec.points is empty")
    if expected["presentation_mode"] == "single_choice":
        choices = payload.get("choices") or []
        correct_label = payload.get("correct_answer")
        correct = [choice for choice in choices if choice.get("label") == correct_label]
        if len(choices) != 4 or len(correct) != 1:
            errors.append("choice topology must contain four choices and one correct label")
        elif correct[0].get("text") != str(payload.get("semantic_answer")):
            errors.append("correct choice text does not equal semantic_answer")
    return {"passed": not errors, "errors": errors, "source_example_id": source_example_id}
