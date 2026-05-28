from __future__ import annotations

import re

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT = "single_choice_choose_correct_statement_axis_distance_coordinate_point"


def test_merged_single_choice_rotates_axis_distance_and_statement():
    spec = load_problem_type_spec(SKILL_ID, PT, prefer="auto")
    assert spec is not None
    axis = 0
    statement = 0
    for seed in range(40):
        payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
        qt = str(payload.get("question_text", ""))
        if "到 x 軸" in qt or "到 y 軸" in qt or re.search(r"P\s*\(\s*-?\d+", qt):
            axis += 1
        elif "敘述" in qt or "下列" in qt:
            statement += 1
    assert axis >= 1, "expected axis_distance_choice samples"
    assert statement >= 1, "expected symbolic_quadrant_statement_choice samples"
