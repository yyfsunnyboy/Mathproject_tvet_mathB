from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from urllib.parse import quote

from app import create_app
from core.gencode.services.v3_question_integrity_validator import validate_component_payload


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "vh_數學B4_FrequencyDistributionTableConstruction"


def _load_component_module(component_id: str):
    path = (
        PROJECT_ROOT
        / "agent_skills_v3"
        / SKILL_ID
        / "components"
        / component_id
        / "generate.py"
    )
    spec = importlib.util.spec_from_file_location(f"freq_{component_id}_generate_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_src3822_evidence_and_integrity() -> None:
    module = _load_component_module("src_3822")
    payload = module.generate(seed=42, component_id="src_3822")
    
    # 1. 題面中顯示的資料筆數等於 metadata 筆數
    match = re.search(r"成績如下：([^。]+)。", payload["question_text"])
    assert match, payload["question_text"]
    scores = [int(x) for x in match.group(1).split("、")]
    assert len(scores) == 40
    assert len(scores) == len(payload["metadata"]["raw_scores"])
    
    # 2. 題面資料與 metadata 完全一致
    assert scores == payload["metadata"]["raw_scores"]
    
    # 3. 正確答案可只根據學生可見題面重新計算
    match_interval = re.search(r"其中一組為(\d+)～(\d+)分", payload["question_text"])
    assert match_interval
    lo, hi = int(match_interval.group(1)), int(match_interval.group(2))
    expected_ans = sum(1 for s in scores if lo <= s <= hi)
    assert int(payload["correct_answer"]) == expected_ans

    # 4. 移除必要資料時，validator 回傳 REQUIRED_EVIDENCE_NOT_RENDERED
    payload_bad = dict(payload)
    payload_bad["question_text"] = "國貿科三年甲班40人英文模擬考成績。將成績分成7組，其中一組為32～41分，請問此組的次數是多少？"
    result = validate_component_payload(payload_bad, component_id="src_3822")
    assert not result["passed"]
    assert "REQUIRED_EVIDENCE_NOT_RENDERED:raw_scores" in result["blockers"]


def test_src3823_evidence_and_integrity() -> None:
    module = _load_component_module("src_3823")
    payload = module.generate(seed=42, component_id="src_3823")
    
    # 1. Check consistency of known frequencies and total
    match_total = re.search(r"會計科三年甲班(\d+)人", payload["question_text"])
    assert match_total
    total = int(match_total.group(1))
    assert total == payload["metadata"]["total_frequency"]
    
    match_table = re.search(r"已知前四組次數為：([^。]+)。", payload["question_text"])
    assert match_table
    table_parts = match_table.group(1).split("、")
    known_freqs = []
    for part in table_parts:
        m = re.search(r"：(\d+)人", part)
        assert m
        known_freqs.append(int(m.group(1)))
        
    assert len(known_freqs) == 4
    assert known_freqs == payload["metadata"]["known_frequencies"]
    
    # 2. 正確答案可只根據學生可見題面重新計算
    expected_ans = total - sum(known_freqs)
    assert int(payload["correct_answer"]) == expected_ans

    # 3. 移除必要資料時，validator 回傳 REQUIRED_EVIDENCE_NOT_RENDERED
    payload_bad = dict(payload)
    payload_bad["question_text"] = f"會計科三年甲班{total}人數學模擬考分成5組。請問最後一組 80～89 分的次數是多少？"
    result = validate_component_payload(payload_bad, component_id="src_3823")
    assert not result["passed"]
    assert "REQUIRED_EVIDENCE_NOT_RENDERED:frequency_table" in result["blockers"]


def test_src3824_evidence_and_integrity() -> None:
    module = _load_component_module("src_3824")
    payload = module.generate(seed=42, component_id="src_3824")
    
    # 1. 題面中顯示的資料筆數等於 metadata 筆數
    match = re.search(r"有一組數值資料為 ([^。]+)。", payload["question_text"])
    assert match, payload["question_text"]
    values = [int(x) for x in match.group(1).split("、")]
    assert len(values) == 8
    assert len(values) == len(payload["metadata"]["values"])
    
    # 2. 題面資料與 metadata 完全一致
    assert values == payload["metadata"]["values"]
    
    # 3. 正確答案可只根據學生可見題面重新計算
    expected_ans = max(values) - min(values)
    assert int(payload["correct_answer"]) == expected_ans

    # 4. 移除必要資料時，validator 回傳 REQUIRED_EVIDENCE_NOT_RENDERED
    payload_bad = dict(payload)
    payload_bad["question_text"] = "有一組數值資料。請問這組資料的全距是多少？"
    result = validate_component_payload(payload_bad, component_id="src_3824")
    assert not result["passed"]
    assert "REQUIRED_EVIDENCE_NOT_RENDERED:values" in result["blockers"]


def test_src3825_evidence_and_integrity() -> None:
    module = _load_component_module("src_3825")
    payload = module.generate(seed=42, component_id="src_3825")
    
    # 1. 題面中顯示的資料筆數等於 metadata 筆數
    match = re.search(r"20位員工年齡資料如下：\s*([^。]+)。", payload["question_text"])
    assert match, payload["question_text"]
    # Clean up whitespace or newlines if any
    clean_scores_str = match.group(1).replace("\n", "").replace("\r", "").strip()
    ages = [int(x) for x in clean_scores_str.split("、")]
    assert len(ages) == 20
    assert len(ages) == len(payload["metadata"]["values"])
    
    # 2. 題面資料與 metadata 完全一致
    assert ages == payload["metadata"]["values"]
    
    # 3. 正確答案可只根據學生可見題面重新計算
    match_interval = re.search(r"請問(\d+)～(\d+)歲這一組的次數是多少？", payload["question_text"])
    assert match_interval
    lo, hi = int(match_interval.group(1)), int(match_interval.group(2))
    expected_ans = sum(1 for a in ages if lo <= a <= hi)
    assert int(payload["correct_answer"]) == expected_ans

    # 4. 移除必要資料時，validator 回傳 REQUIRED_EVIDENCE_NOT_RENDERED
    payload_bad = dict(payload)
    payload_bad["question_text"] = "某公司企劃部20位員工年齡資料將資料依組距5分成4組，最小一組為25～29歲。請問30～34歲這一組的次數是多少？"
    result = validate_component_payload(payload_bad, component_id="src_3825")
    assert not result["passed"]
    assert "REQUIRED_EVIDENCE_NOT_RENDERED:values" in result["blockers"]


def test_flask_get_next_question_all_four_components() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()
    
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True

    expected_ids = ["src_3822", "src_3823", "src_3824", "src_3825"]
    
    for expected_id in expected_ids:
        response = client.get(f"/get_next_question?skill={quote(SKILL_ID)}&level=1")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["component_id"] == expected_id
        assert payload["route_source"] == "gencode_wrapper"
        
        # Verify the student visible info is sufficient to determine the answer uniquely
        if expected_id == "src_3822":
            match = re.search(r"成績如下：([^。]+)。", payload["question_text"])
            assert match
            scores = [int(x) for x in match.group(1).split("、")]
            assert len(scores) == 40
            match_interval = re.search(r"其中一組為(\d+)～(\d+)分", payload["question_text"])
            assert match_interval
            lo, hi = int(match_interval.group(1)), int(match_interval.group(2))
            assert int(payload["correct_answer"]) == sum(1 for s in scores if lo <= s <= hi)
            
        elif expected_id == "src_3823":
            match_total = re.search(r"會計科三年甲班(\d+)人", payload["question_text"])
            assert match_total
            total = int(match_total.group(1))
            match_table = re.search(r"已知前四組次數為：([^。]+)。", payload["question_text"])
            assert match_table
            known_freqs = [int(re.search(r"：(\d+)人", part).group(1)) for part in match_table.group(1).split("、")]
            assert int(payload["correct_answer"]) == total - sum(known_freqs)
            
        elif expected_id == "src_3824":
            match = re.search(r"有一組數值資料為 ([^。]+)。", payload["question_text"])
            assert match
            values = [int(x) for x in match.group(1).split("、")]
            assert len(values) == 8
            assert int(payload["correct_answer"]) == max(values) - min(values)
            
        elif expected_id == "src_3825":
            match = re.search(r"20位員工年齡資料如下：\s*([^。]+)。", payload["question_text"])
            assert match
            clean_scores_str = match.group(1).replace("\n", "").replace("\r", "").strip()
            ages = [int(x) for x in clean_scores_str.split("、")]
            assert len(ages) == 20
            match_interval = re.search(r"請問(\d+)～(\d+)歲這一組的次數是多少？", payload["question_text"])
            assert match_interval
            lo, hi = int(match_interval.group(1)), int(match_interval.group(2))
            assert int(payload["correct_answer"]) == sum(1 for a in ages if lo <= a <= hi)
