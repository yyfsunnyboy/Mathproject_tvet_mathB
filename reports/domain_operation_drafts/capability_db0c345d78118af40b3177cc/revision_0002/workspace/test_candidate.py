from implementation_candidate import build_linear_equation_from_two_points_choice_matrix


def _point_on_line(point: tuple[int, int], facts: dict) -> bool:
    x, y = point
    if facts["line_kind"] == "vertical":
        return x == int(facts["equation"].split("=")[1])
    return y == (facts["slope"] or 0) * x + int(
        facts["equation"].split("=")[1].split("x")[-1] or 0
    )


def test_seeded_choice_generation() -> None:
    for seed in (7, 42, 101):
        matrix = build_linear_equation_from_two_points_choice_matrix(seed=seed)
        facts = matrix["validation_facts"]
        assert len(matrix["choices"]) == len({item["value"] for item in matrix["choices"]}) == 4
        assert facts["choice_value_to_label"][facts["equation"]] == facts["correct_label"]
        assert matrix["answer"]["correct_label"] == facts["correct_label"]
        assert matrix["semantic_answer"] == facts["equation"]
        assert str(facts["point_1"]) in matrix["question"]
        assert str(facts["point_2"]) in matrix["question"]


def test_vertical_horizontal_and_oblique_boundaries() -> None:
    for line_kind in ("vertical", "horizontal", "oblique"):
        matrix = build_linear_equation_from_two_points_choice_matrix(
            seed=7,
            constraints={"line_kind": line_kind, "offset": 2, "slope": -2},
        )
        facts = matrix["validation_facts"]
        point_1, point_2 = facts["point_1"], facts["point_2"]
        if line_kind == "vertical":
            assert point_1[0] == point_2[0]
        elif line_kind == "horizontal":
            assert point_1[1] == point_2[1]
        else:
            assert (point_2[1] - point_1[1]) / (point_2[0] - point_1[0]) == -2
