from implementation_candidate import build_collinear_trisection_coordinate_matrix


def test_trisection_operation() -> None:
    for seed in (7, 42, 101):
        matrix = build_collinear_trisection_coordinate_matrix(seed=seed)
        facts = matrix["validation_facts"]
        point_a, point_b = facts["point_a"], facts["point_b"]
        point_c, point_d = facts["point_c"], facts["point_d"]
        vector_ad = (point_d[0] - point_a[0], point_d[1] - point_a[1])
        assert point_b == (
            (2 * point_a[0] + point_d[0]) // 3,
            (2 * point_a[1] + point_d[1]) // 3,
        )
        assert point_c == (
            (point_a[0] + 2 * point_d[0]) // 3,
            (point_a[1] + 2 * point_d[1]) // 3,
        )
        for point in (point_b, point_c):
            vector_ap = (point[0] - point_a[0], point[1] - point_a[1])
            assert vector_ad[0] * vector_ap[1] == vector_ad[1] * vector_ap[0]
        assert (
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        ) == (
            point_d[0] - point_c[0],
            point_d[1] - point_c[1],
        )
        assert facts["ratios"] == {"AB:BD": "1:2", "AC:CD": "2:1"}
        midpoint = (
            (point_a[0] + point_d[0]) / 2,
            (point_a[1] + point_d[1]) / 2,
        )
        assert point_b != midpoint
        assert point_c != midpoint
        assert matrix["answer"]["point"] == f"({point_c[0]}, {point_c[1]})"
        assert str(point_a) in matrix["question"]
        assert str(point_d) in matrix["question"]
