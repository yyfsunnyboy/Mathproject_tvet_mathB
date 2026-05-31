from __future__ import annotations

import importlib

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_generator_payload
from core.gencode.validators.answer_contract_validator import CHOICE_EMBEDDED_PATTERN

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"


def test_thin_wrapper_generate_30_samples_contract_safe():
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    for i in range(30):
        payload = mod.generate(level=1, seed=i)
        assert isinstance(payload, dict)
        assert str(payload.get("question_text", "")).strip()
        assert str(payload.get("answer", "")).strip()
        assert payload.get("answer_type")
        assert "choices" in payload
        assert "metadata" in payload
        meta = payload["metadata"]
        assert isinstance(meta, dict)
        assert "givens" in meta and "target" in meta and "derivation" in meta
        pt = str(payload.get("problem_type_id", "")).strip()
        spec = load_problem_type_spec(SKILL_ID, pt, prefer="auto")
        assert spec is not None
        errors = validate_generator_payload(payload, problem_type_spec=spec)
        assert not errors, errors
        if str(payload.get("answer_type")) == "short_answer":
            assert not payload.get("choices")
        if str(payload.get("answer_type")) == "single_choice":
            texts = [str(c.get("text", c) if isinstance(c, dict) else c) for c in (payload.get("choices") or [])]
            assert len(texts) == len(set(texts))
            assert not CHOICE_EMBEDDED_PATTERN.search(str(payload.get("question_text", "")))
