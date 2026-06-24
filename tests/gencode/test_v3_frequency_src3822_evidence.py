from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from urllib.parse import quote

from app import create_app
from core.gencode.services.v3_question_integrity_validator import validate_component_payload


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "vh_數學B4_FrequencyDistributionTableConstruction"
COMPONENT_ID = "src_3822"


def _load_src3822_module():
    path = (
        PROJECT_ROOT
        / "agent_skills_v3"
        / SKILL_ID
        / "components"
        / COMPONENT_ID
        / "generate.py"
    )
    spec = importlib.util.spec_from_file_location("freq_src3822_generate_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scores_from_question(question_text: str) -> list[int]:
    match = re.search(r"成績如下：([^。]+)。", question_text)
    assert match, question_text
    return [int(part) for part in match.group(1).split("、")]


def _interval_from_question(question_text: str) -> tuple[int, int]:
    match = re.search(r"其中一組為(\d+)～(\d+)分", question_text)
    assert match, question_text
    return int(match.group(1)), int(match.group(2))


def test_src3822_question_renders_same_40_scores_as_metadata() -> None:
    module = _load_src3822_module()
    payload = module.generate(seed=7, component_id=COMPONENT_ID)
    metadata = payload["metadata"]

    question_scores = _scores_from_question(payload["question_text"])
    assert len(question_scores) == 40
    assert question_scores == metadata["raw_scores"]
    assert f"{len(question_scores)}人" in payload["question_text"]
    assert metadata["group_count"] == 7
    assert f"分成{metadata['group_count']}組" in payload["question_text"]


def test_src3822_answer_matches_rendered_scores_and_inclusive_interval() -> None:
    module = _load_src3822_module()
    payload = module.generate(seed=11, component_id=COMPONENT_ID)

    scores = _scores_from_question(payload["question_text"])
    lower, upper = _interval_from_question(payload["question_text"])
    answer = sum(1 for score in scores if lower <= score <= upper)

    assert payload["metadata"]["target_interval"] == {
        "lower": lower,
        "upper": upper,
        "inclusive": True,
    }
    assert payload["metadata"]["target_frequency"] == answer
    assert int(payload["correct_answer"]) == answer
    assert int(payload["answer"]) == answer


def test_src3822_seed_variation_and_reproducibility() -> None:
    module = _load_src3822_module()
    first = module.generate(seed=21, component_id=COMPONENT_ID)
    second = module.generate(seed=21, component_id=COMPONENT_ID)
    other = module.generate(seed=22, component_id=COMPONENT_ID)

    assert first["metadata"]["raw_scores"] == second["metadata"]["raw_scores"]
    assert first["correct_answer"] == second["correct_answer"]
    assert first["metadata"]["raw_scores"] != other["metadata"]["raw_scores"]


def test_required_evidence_visibility_gate_blocks_hidden_raw_scores() -> None:
    module = _load_src3822_module()
    payload = module.generate(seed=7, component_id=COMPONENT_ID)
    payload["question_text"] = (
        "國貿科三年甲班40人英文模擬考成績分成7組。"
        "若其中一組為72～81分，請問此組次數是多少？"
    )
    result = validate_component_payload(payload, component_id=COMPONENT_ID)

    assert not result["passed"]
    assert "REQUIRED_EVIDENCE_NOT_RENDERED:raw_scores" in result["blockers"]


def test_src3822_integrity_gate_passes_with_rendered_raw_scores() -> None:
    module = _load_src3822_module()
    payload = module.generate(seed=7, component_id=COMPONENT_ID)
    result = validate_component_payload(payload, component_id=COMPONENT_ID)
    assert result["passed"], result["blockers"]


def test_flask_get_next_question_src3822_renders_all_scores() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True

    response = client.get(f"/get_next_question?skill={quote(SKILL_ID)}&level=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["component_id"] == COMPONENT_ID
    assert payload["route_source"] == "gencode_wrapper"

    question_scores = _scores_from_question(payload["question_text"])
    assert len(question_scores) == 40
    assert question_scores == payload["metadata"]["raw_scores"]
    lower, upper = _interval_from_question(payload["question_text"])
    assert int(payload["correct_answer"]) == sum(1 for score in question_scores if lower <= score <= upper)
