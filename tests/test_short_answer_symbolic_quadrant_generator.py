from __future__ import annotations

import re

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT = "short_answer_classify_quadrant_symbolic_condition_coordinate_point"
_NUMERIC_POINT = re.compile(r"[PQ]\s*\(\s*-?\d+\s*,\s*-?\d+\s*\)", re.I)


def _spec() -> dict:
    spec = load_problem_type_spec(SKILL_ID, PT, prefer="auto")
    if spec:
        return spec
    raise AssertionError("induced spec missing")


def test_generate_50_symbolic_quadrant_items():
    spec = _spec()
    for seed in range(50):
        payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
        qt = str(payload.get("question_text", ""))
        assert not _NUMERIC_POINT.search(qt), qt
        if re.search(r"a\s*<\s*b|0<a<b", qt, re.I):
            assert re.search(r"\bab\b|\ba-b\b|\ba\^2b\b|\ba\+b\b", qt), qt
        meta = payload.get("metadata", {})
        assert isinstance(meta.get("givens"), list) and meta["givens"]
        assert isinstance(meta.get("target"), dict) and meta["target"]
        assert isinstance(meta.get("derivation"), list) and meta["derivation"]
        target = meta["target"]
        assert target.get("variables"), meta
        errors = validate_generator_payload(payload, problem_type_spec=spec)
        assert not errors, errors
