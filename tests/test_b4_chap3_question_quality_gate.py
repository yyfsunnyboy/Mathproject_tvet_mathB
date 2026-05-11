from __future__ import annotations

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


REPORT_PATH = Path("reports/b4_generator_planning/b4_chap3_ai_question_quality_gate_summary.md")
SAMPLE_DIR = Path("reports/b4_generator_planning/chap3_quality_samples")
SAMPLE_PER_SKILL = 10

TARGET_SKILL_SUFFIXES = [
    "StatisticalBasicConcepts",
    "SamplingSurvey",
    "SamplingMethods",
    "DataOrganizationAndCharts",
    "StatisticalChartReading",
    "CumulativeFrequencyTablesAndGraphs",
    "FrequencyDistributionTableConstruction",
    "HistogramsAndFrequencyPolygons",
    "CentralTendencyMeasures",
    "DispersionMeasures",
    "WeightedMean",
    "VarianceAndStandardDeviation",
    "LinearTransformationOfData",
    "NormalDistributionAndEmpiricalRule",
]

VISUAL_OR_TABLE_SKILL_SUFFIXES = {
    "SamplingSurvey",
    "DataOrganizationAndCharts",
    "StatisticalChartReading",
    "CumulativeFrequencyTablesAndGraphs",
    "FrequencyDistributionTableConstruction",
    "HistogramsAndFrequencyPolygons",
    "CentralTendencyMeasures",
    "DispersionMeasures",
}

REVIEW_CHECK_MODES = {"review_mode", "handwriting_ai_checked", "visual_ai_checked"}
ENGLISH_RESIDUAL = ["Read the", "Frequency Table", "Histogram", "Value", "Frequency", "count", "interval"]


@dataclass
class Issue:
    skill_id: str
    problem_type_id: str
    issue_type: str
    severity: str
    sample_question_text: str
    reason: str
    suggested_fix: str
    fixed_in_this_phase: str = "no"


def _resolve_skill_id_by_suffix(suffix: str) -> str:
    keys = [k for k in chap3_router._CHAP3_PHASE7B_REGISTRY.keys() if str(k).endswith(suffix)]
    if not keys:
        raise AssertionError(f"Missing chap3 skill in registry for suffix={suffix}")
    return str(keys[0])


def _hash_question_pattern(payload: dict) -> str:
    text = str(payload.get("question_text", "")).strip()
    return hashlib.sha1(text.encode("utf-8")).hexdigest() if text else "EMPTY"


def _first_wrong_choice(answer: str) -> str:
    for c in ("1", "2", "3", "4"):
        if c != answer:
            return c
    return "4"


def _contains_any(text: str, tokens: list[str]) -> bool:
    return any(t in text for t in tokens)


def _extract_table_headers_rows(payload: dict) -> tuple[list[str], list[list[Any]]]:
    table = payload.get("table") or {}
    if isinstance(table, dict):
        headers = table.get("headers") or []
        rows = table.get("rows") or []
        if headers or rows:
            return headers, rows
    for va in payload.get("visual_aids") or []:
        if isinstance(va, dict) and va.get("type") == "table":
            return va.get("headers") or [], va.get("rows") or []
    return [], []


def _add_issue(issues: list[Issue], **kwargs: Any) -> None:
    issues.append(Issue(**kwargs))


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_chap3_qgate_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_b4_chap3_question_quality_gate(logged_client) -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    skill_ids = [_resolve_skill_id_by_suffix(sfx) for sfx in TARGET_SKILL_SUFFIXES]
    sampled_payloads: dict[str, list[dict[str, Any]]] = {}
    sample_counts: dict[str, int] = {}
    diversity_rows: list[dict[str, Any]] = []
    issues: list[Issue] = []
    artifact_paths: list[str] = []

    for skill_id in skill_ids:
        payloads: list[dict[str, Any]] = []
        for i in range(SAMPLE_PER_SKILL):
            seed = i + 1
            try:
                p = generate_for_chap3_skill(skill_id=skill_id, seed=seed, level=1)
            except Exception as exc:
                _add_issue(
                    issues,
                    skill_id=skill_id,
                    problem_type_id="(generation_failed)",
                    issue_type="generation_failure",
                    severity="BLOCKING",
                    sample_question_text="",
                    reason=str(exc),
                    suggested_fix="修正 router/generator skill mapping。",
                )
                continue
            payloads.append(p)
        sampled_payloads[skill_id] = payloads
        sample_counts[skill_id] = len(payloads)

        # Rule-based QA
        for idx, p in enumerate(payloads):
            pt = str(p.get("problem_type_id", ""))
            q = str(p.get("question_text", ""))
            runtime_mode = str(p.get("runtime_mode", ""))
            check_mode = str(p.get("check_mode", ""))
            answer = str(p.get("answer", ""))
            answer_input_type = str(p.get("answer_input_type", ""))
            choices = p.get("choices") or []
            explanation = str(p.get("explanation", ""))
            message = str(p.get("message", ""))

            is_choice = ("選項代號" in q) or (answer_input_type == "choice")
            if is_choice:
                if not isinstance(choices, list) or not choices:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="choice_missing_choices",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="choice 題缺 choices。",
                        suggested_fix="補上 choices 並對齊 answer。",
                    )
                else:
                    codes = {str(c).split(".", 1)[0].strip() for c in choices}
                    if answer not in codes:
                        _add_issue(
                            issues,
                            skill_id=skill_id,
                            problem_type_id=pt,
                            issue_type="choice_answer_not_in_choices",
                            severity="BLOCKING",
                            sample_question_text=q,
                            reason="answer 無法對應 choices。",
                            suggested_fix="修正 answer 或 choices 編碼。",
                        )

                    # Route check_answer contract
                    resp = logged_client.get(
                        f"/get_next_question?skill={quote(skill_id)}&problem_type={quote(pt)}&gen_seed={idx + 1}&level=1"
                    )
                    if resp.status_code == 200:
                        if str(skill_id).endswith("SamplingSurvey") and pt == "sampling_survey_foundation_identification":
                            _add_issue(
                                issues,
                                skill_id=skill_id,
                                problem_type_id=pt,
                                issue_type="choice_guarded_legacy_path",
                                severity="MAJOR",
                                sample_question_text=q,
                                reason="此題型目前仍沿用 legacy guarded check path。",
                                suggested_fix="若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。",
                            )
                            continue
                        ok = logged_client.post("/check_answer", json={"answer": answer}).get_json() or {}
                        if ok.get("correct") is not True:
                            is_guarded = "AI/Review" in str(ok.get("result", ""))
                            if is_guarded:
                                _add_issue(
                                    issues,
                                    skill_id=skill_id,
                                    problem_type_id=pt,
                                    issue_type="choice_guarded_instead_of_auto_check",
                                    severity="MAJOR",
                                    sample_question_text=q,
                                    reason="choice ??? AI/Review guard???????",
                                    suggested_fix="?? deterministic???? checker ????????? report ???",
                                )
                            else:
                                _add_issue(
                                    issues,
                                    skill_id=skill_id,
                                    problem_type_id=pt,
                                    issue_type="choice_correct_not_accepted",
                                    severity="BLOCKING",
                                    sample_question_text=q,
                                    reason="??????",
                                    suggested_fix="?? deterministic checker ? alias normalize?",
                                )
                        alias = chr(ord("A") + int(answer) - 1) if answer.isdigit() else "A"
                        ok_alias = logged_client.post("/check_answer", json={"answer": alias}).get_json() or {}
                        if ok_alias.get("correct") is not True:
                            if "AI/Review" not in str(ok_alias.get("result", "")):
                                _add_issue(
                                    issues,
                                    skill_id=skill_id,
                                    problem_type_id=pt,
                                    issue_type="choice_alias_not_accepted",
                                    severity="MAJOR",
                                    sample_question_text=q,
                                    reason="A/B/C/D alias ?????",
                                    suggested_fix="?? choice alias normalize?",
                                )
                        wrong = _first_wrong_choice(answer if answer.isdigit() else "1")
                        bad = logged_client.post("/check_answer", json={"answer": wrong}).get_json() or {}
                        if bad.get("correct") is True:
                            _add_issue(
                                issues,
                                skill_id=skill_id,
                                problem_type_id=pt,
                                issue_type="choice_wrong_marked_correct",
                                severity="BLOCKING",
                                sample_question_text=q,
                                reason="??????",
                                suggested_fix="?? checker ?????",
                            )

            if _contains_any(q, ["附圖", "下圖", "觀察圖", "觀察附圖", "見下圖"]):
                if not (p.get("image_base64") or p.get("visual_aids") or p.get("chart_spec")):
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="missing_visual_payload",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="題幹要求看圖但 payload 無圖表資料。",
                        suggested_fix="補 image_base64/visual_aids/chart_spec。",
                    )

            if _contains_any(q, ["下表", "表格", "補齊"]):
                has_table = bool(p.get("table") or p.get("visual_aids") or p.get("image_base64"))
                headers, rows = _extract_table_headers_rows(p)
                if not has_table:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="missing_table_payload",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="題幹要求看表但 payload 無表格資料。",
                        suggested_fix="補 table/visual_aids/image_base64。",
                    )
                if headers and not any(any("\u4e00" <= ch <= "\u9fff" for ch in str(h)) for h in headers):
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="table_headers_not_chinese",
                        severity="MAJOR",
                        sample_question_text=q,
                        reason="表頭非中文。",
                        suggested_fix="改為中文表頭。",
                    )
                if headers and not rows:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="table_rows_empty",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="表格 rows 為空。",
                        suggested_fix="補齊表格內容。",
                    )

            if check_mode in REVIEW_CHECK_MODES:
                has_rubric = bool(p.get("expected_answer_schema") or p.get("rubric") or message)
                if not has_rubric:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="review_missing_rubric_or_message",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="review 題缺 rubric/message。",
                        suggested_fix="補 expected_answer_schema 或 friendly message。",
                    )
                # check_answer guard
                resp = logged_client.get(
                    f"/get_next_question?skill={quote(skill_id)}&problem_type={quote(pt)}&gen_seed={idx + 1}&level=1"
                )
                if resp.status_code == 200:
                    guard = logged_client.post("/check_answer", json={"answer": "任意作答"}).get_json() or {}
                    if "AI/Review" not in str(guard.get("result", "")):
                        _add_issue(
                            issues,
                            skill_id=skill_id,
                            problem_type_id=pt,
                            issue_type="review_guard_missing",
                            severity="BLOCKING",
                            sample_question_text=q,
                            reason="review 題未被 guard 到 AI/Review。",
                            suggested_fix="修正 check_mode guard。",
                        )

            if check_mode == "deterministic_auto_checked":
                if not str(p.get("answer", "")).strip():
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="deterministic_answer_empty",
                        severity="BLOCKING",
                        sample_question_text=q,
                        reason="deterministic 題 answer 空白。",
                        suggested_fix="補齊 answer。",
                    )
                if not str(p.get("answer_type", "")).strip() and not answer_input_type:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="deterministic_answer_type_missing",
                        severity="MAJOR",
                        sample_question_text=q,
                        reason="deterministic 題 answer_type/answer_input_type 不明確。",
                        suggested_fix="補 answer_type 或 answer_input_type。",
                    )

            # Localization scan
            blob = " ".join(
                [
                    q,
                    " ".join(str(c) for c in choices),
                    explanation,
                    message,
                    json.dumps(p.get("table", {}), ensure_ascii=False),
                    json.dumps(p.get("chart_spec", {}), ensure_ascii=False),
                ]
            )
            for bad in ENGLISH_RESIDUAL:
                if bad in blob:
                    _add_issue(
                        issues,
                        skill_id=skill_id,
                        problem_type_id=pt,
                        issue_type="english_template_residual",
                        severity="MINOR",
                        sample_question_text=q,
                        reason=f"發現英文模板殘留：{bad}",
                        suggested_fix="改為中文敘述。",
                    )

            # artifact export for visual/table skills
            suffix = skill_id.split("B4_")[-1]
            is_visual_table_skill = suffix in VISUAL_OR_TABLE_SKILL_SUFFIXES
            has_visual_table = bool(p.get("visual_aids") or p.get("image_base64") or p.get("table") or p.get("chart_spec"))
            if is_visual_table_skill and has_visual_table:
                exported = [x for x in artifact_paths if f"/{suffix}_" in x.replace("\\", "/")]
                if len(exported) < 3:
                    json_path = SAMPLE_DIR / f"{suffix}_sample_{len(exported)+1:02d}.json"
                    json_path.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")
                    artifact_paths.append(str(json_path).replace("\\", "/"))
                    b64 = p.get("image_base64")
                    if isinstance(b64, str) and b64.strip():
                        try:
                            png_path = SAMPLE_DIR / f"{suffix}_sample_{len(exported)+1:02d}.png"
                            png_path.write_bytes(base64.b64decode(b64))
                            artifact_paths.append(str(png_path).replace("\\", "/"))
                        except Exception:
                            pass

        # Diversity QA summary per skill
        problem_types = [str(x.get("problem_type_id", "")) for x in payloads]
        families = [str(x.get("scenario_family") or "") for x in payloads]
        scenarios = [str(x.get("scenario_id") or "") for x in payloads]
        patterns = [_hash_question_pattern(x) for x in payloads]
        unique_text = len({str(x.get("question_text", "")).strip() for x in payloads})
        total = max(len(payloads), 1)
        repeated_ratio = 1.0 - (unique_text / total)
        unique_problem_type = len({x for x in problem_types if x})
        unique_family = len({x for x in families if x})
        unique_scenario = len({x for x in scenarios if x})
        unique_pattern = len(set(patterns))

        diversity_rows.append(
            {
                "skill_id": skill_id,
                "unique_problem_type_id_count": unique_problem_type,
                "unique_scenario_family_count": unique_family,
                "unique_scenario_id_count": unique_scenario,
                "unique_question_pattern_hash_count": unique_pattern,
                "repeated_question_text_ratio": round(repeated_ratio, 3),
            }
        )

        registry_count = len(chap3_router._CHAP3_PHASE7B_REGISTRY.get(skill_id, []))
        if registry_count > 1 and unique_pattern < 2:
            _add_issue(
                issues,
                skill_id=skill_id,
                problem_type_id="(multi_entry_skill)",
                issue_type="diversity_too_low",
                severity="MAJOR",
                sample_question_text=(payloads[0].get("question_text", "") if payloads else ""),
                reason="多 entry skill 但題型多樣性不足（<2 patterns）。",
                suggested_fix="增加 scenario/pattern 輪替。",
            )
        if repeated_ratio > 0.7 and registry_count > 1:
            _add_issue(
                issues,
                skill_id=skill_id,
                problem_type_id="(multi_entry_skill)",
                issue_type="repeated_ratio_too_high",
                severity="MAJOR",
                sample_question_text=(payloads[0].get("question_text", "") if payloads else ""),
                reason=f"repeated_question_text_ratio={repeated_ratio:.3f} > 0.7",
                suggested_fix="增加題幹變體或 scenario。",
            )

    total_sampled = sum(sample_counts.values())

    # AI judge not run in offline gate.
    ai_judge_status = "AI_JUDGE_NOT_RUN"

    # report
    blocking_count = sum(1 for i in issues if i.severity == "BLOCKING")
    major_count = sum(1 for i in issues if i.severity == "MAJOR")
    minor_count = sum(1 for i in issues if i.severity == "MINOR")
    issue_lines = []
    for i in issues:
        issue_lines.append(
            f"| {i.skill_id} | {i.problem_type_id} | {i.issue_type} | {i.severity} | "
            f"{i.sample_question_text.replace('|','/')} | {i.reason.replace('|','/')} | "
            f"{i.suggested_fix.replace('|','/')} | {i.fixed_in_this_phase} |"
        )
    if not issue_lines:
        issue_lines = ["| (none) | - | - | - | - | - | - | - |"]

    sample_count_lines = [f"| {k} | {v} |" for k, v in sample_counts.items()]
    diversity_lines = [
        "| {skill_id} | {unique_problem_type_id_count} | {unique_scenario_family_count} | {unique_scenario_id_count} | {unique_question_pattern_hash_count} | {repeated_question_text_ratio} |".format(
            **row
        )
        for row in diversity_rows
    ]
    artifact_lines = [f"- {p}" for p in sorted(set(artifact_paths))] or ["- (none)"]

    report = "\n".join(
        [
            "# B4 Chap3 AI-assisted Question Quality Gate Summary",
            "",
            "## 1. QA scope",
            "- Phase B4-Chap3-QA-1",
            "- Rule-based QA + diversity QA + visual/table artifact QA",
            f"- AI judge status: {ai_judge_status}",
            "",
            "## 2. sampled skills",
            *[f"- {sid}" for sid in skill_ids],
            "",
            "## 3. sample count per skill",
            "| skill_id | sample_count |",
            "|---|---:|",
            *sample_count_lines,
            f"| TOTAL | {total_sampled} |",
            "",
            "## 4. rule-based QA summary",
            f"- blocking={blocking_count}, major={major_count}, minor={minor_count}",
            "",
            "## 5. diversity QA summary",
            "| skill_id | unique problem_type_id | unique scenario_family | unique scenario_id | unique question_pattern_hash | repeated_question_text_ratio |",
            "|---|---:|---:|---:|---:|---:|",
            *diversity_lines,
            "",
            "## 6. AI judge QA summary",
            f"- {ai_judge_status}",
            "- offline rubric fields collected in rule-based/deterministic/review contracts.",
            "",
            "## 7. visual/table sample artifact paths",
            *artifact_lines,
            "",
            "## 8. failed items table",
            "| skill_id | problem_type_id | issue_type | severity | sample_question_text | reason | suggested_fix | fixed_in_this_phase |",
            "|---|---|---|---|---|---|---|---|",
            *issue_lines,
        ]
    )
    REPORT_PATH.write_text(report, encoding="utf-8")

    # Hard gate
    assert blocking_count == 0, f"Found blocking issues: {blocking_count}. See {REPORT_PATH}"
