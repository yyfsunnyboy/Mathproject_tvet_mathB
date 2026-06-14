from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.pipeline_state import utc_timestamp, write_json, write_md
from core.gencode.classifier_proposal import (
    build_classifier_proposal,
    build_phase1_gate_policy,
    detect_answer_shape,
)
from core.gencode.pipeline_orchestrator import run_gencode_auto_pipeline

REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
BOOTSTRAP_MAP_PATH = PROJECT_ROOT / "configs" / "gencode" / "bootstrap_skill_map.yaml"
DEFAULT_DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"

REQUIRED_CONTRACT_FIELDS = {
    "answer_type",
    "equivalence_type",
    "checker_key",
    "order_matters",
    "accepted_format_notes",
    "canonical_answer_schema",
}

ANSWER_CONTRACT_DEFAULTS: dict[str, dict[str, dict[str, Any]]] = {
    "vh_數學B1_AbsoluteValue": {
        "absolute_value_numeric_evaluation": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": "int",
        },
        "absolute_value_distance_from_zero": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": True,
            "accepted_format_notes": ["A/a/(A)/A./1/choice text aliases accepted by label checker"],
            "canonical_answer_schema": "choice_label",
        },
        "absolute_value_distance_between_two_points": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer distance"],
            "canonical_answer_schema": "int",
        },
        "absolute_value_equation_basic": {
            "answer_type": "solution_set",
            "equivalence_type": "unordered_solution_set",
            "checker_key": "solution_set_checker",
            "order_matters": False,
            "accepted_format_notes": ["17,-17", "-17,17", "x=17 或 x=-17", "x=-17 或 x=17", "±17"],
            "canonical_answer_schema": "set[int]",
        },
    },
    "vh_數學B1_NumberLine": {
        "number_line_point_value_reading": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": False,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        },
        "number_line_distance_between_points": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": False,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        },
    },
    "vh_數學B1_AbsoluteValueInequality": {
        "absolute_value_inequality_zero_center_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_shifted_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_linear_expression_basic": {
            "answer_type": "interval_set",
            "equivalence_type": "interval_set",
            "checker_key": "interval_checker",
            "order_matters": False,
            "accepted_format_notes": ["x > a", "x < a", "x ≤ a", "x ≥ a", "interval notation"],
            "canonical_answer_schema": {"type": "interval_set"},
        },
        "absolute_value_inequality_integer_solution_count_choice": {
            "answer_type": "choice",
            "equivalence_type": "choice_label",
            "checker_key": "choice_label_checker",
            "order_matters": False,
            "accepted_format_notes": ["A/B/C/D labels"],
            "canonical_answer_schema": {"type": "choice_label"},
        },
        "absolute_value_inequality_malformed_source_review": {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
            "order_matters": False,
            "accepted_format_notes": ["requires source text correction before deterministic generation"],
            "canonical_answer_schema": {"type": "manual_review"},
        },
    },
    "vh_數學B1_LinearFunction": {
        "integer_numeric_evaluate_function_notation": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        },
    },
    "vh_數學B1_SlopeOfALine": {
        "text_short_slope_of_line_problems": {
            "answer_type": "rational",
            "equivalence_type": "rational_equivalent",
            "checker_key": "rational_checker",
            "order_matters": True,
            "accepted_format_notes": ["integer or fraction slope answer"],
            "canonical_answer_schema": {"type": "rational"},
        }
    },
    "vh_數學B1_PropertiesOfParallelLines": {
        "parallel_lines_properties": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"},
        }
    }
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    return obj if isinstance(obj, dict) else {}


def _load_bootstrap_config(skill_id: str) -> dict[str, Any]:
    data = _load_yaml(BOOTSTRAP_MAP_PATH)
    cfg = data.get(skill_id)
    return cfg if isinstance(cfg, dict) else {}


def _run_json_cmd(cmd: list[str], timeout: int = 600) -> tuple[int, dict[str, Any], str, str]:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
    parsed: dict[str, Any] = {}
    for ln in reversed([x.strip() for x in proc.stdout.splitlines() if x.strip()]):
        try:
            j = json.loads(ln)
        except Exception:
            continue
        if isinstance(j, dict):
            parsed = j
            break
    return proc.returncode, parsed, proc.stdout, proc.stderr


def _resolve_table_name(con: sqlite3.Connection, candidates: list[str]) -> str:
    names = {
        str(r[0])
        for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    for c in candidates:
        if c in names:
            return c
    for n in names:
        ln = n.lower()
        for c in candidates:
            if c.lower() in ln:
                return n
    return ""


def _table_columns(con: sqlite3.Connection, table: str) -> list[str]:
    if not table:
        return []
    try:
        return [str(r[1]) for r in con.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _safe_like_patterns(skill_id: str) -> list[str]:
    raw = str(skill_id or "").strip()
    parts = [x for x in re.split(r"[_\\-\\s]+", raw) if x and len(x) >= 3]
    pats = [raw] + parts
    out: list[str] = []
    for p in pats:
        if p not in out:
            out.append(p)
    return out[:8]


def _inventory_failure_diagnostics(skill_id: str, db_path: Path) -> dict[str, Any]:
    diag: dict[str, Any] = {
        "inventory_failed_reason": "inventory_query_failed",
        "skill_exists": False,
        "skill_profile": {},
        "exact_example_count": 0,
        "nearby_skill_candidates": [],
        "nearby_example_candidates": [],
        "outline_example_candidates": [],
        "recommended_action": "檢查 skill_id 與教材來源映射設定。",
    }
    if not db_path.exists():
        diag["inventory_failed_reason"] = f"db_not_found:{db_path}"
        diag["recommended_action"] = "找不到 DB，請先確認 instance/kumon_math.db。"
        return diag

    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    skill_table = _resolve_table_name(con, ["skill_info", "skills_info"])
    ex_table = _resolve_table_name(con, ["textbook_examples"])
    skill_cols = _table_columns(con, skill_table)
    ex_cols = _table_columns(con, ex_table)

    skill_row: dict[str, Any] = {}
    if skill_table and "skill_id" in skill_cols:
        row = con.execute(f"SELECT * FROM {skill_table} WHERE skill_id=? LIMIT 1", (skill_id,)).fetchone()
        if row:
            skill_row = dict(row)
            diag["skill_exists"] = True
            diag["skill_profile"] = {
                "skill_id": skill_row.get("skill_id", ""),
                "skill_ch_name": skill_row.get("skill_ch_name", ""),
                "unit_name": skill_row.get("unit_name", ""),
                "chapter": skill_row.get("chapter", ""),
                "section_code": skill_row.get("section_code", ""),
                "volume": skill_row.get("volume", ""),
                "curriculum": skill_row.get("curriculum", ""),
            }

    if ex_table and "skill_id" in ex_cols:
        diag["exact_example_count"] = int(
            con.execute(f"SELECT COUNT(*) FROM {ex_table} WHERE skill_id=?", (skill_id,)).fetchone()[0]
        )
        patterns = _safe_like_patterns(skill_id)
        by_skill: dict[str, int] = {}
        for p in patterns:
            rows = con.execute(
                f"SELECT skill_id, COUNT(*) AS c FROM {ex_table} WHERE skill_id LIKE ? GROUP BY skill_id ORDER BY c DESC LIMIT 30",
                (f"%{p}%",),
            ).fetchall()
            for r in rows:
                sid = str(r["skill_id"])
                by_skill[sid] = max(by_skill.get(sid, 0), int(r["c"]))
        diag["nearby_skill_candidates"] = [
            {"skill_id": sid, "example_count": by_skill[sid]}
            for sid in sorted(by_skill, key=lambda x: (-by_skill[x], x))
            if sid != skill_id
        ][:30]

        section_vals: list[tuple[str, Any]] = []
        for k in ["volume", "chapter", "section_code", "unit_name", "curriculum"]:
            if k in ex_cols and skill_row.get(k) not in ("", None):
                section_vals.append((k, skill_row.get(k)))
        if section_vals:
            where = " OR ".join([f"{k}=?" for k, _ in section_vals])
            vals = tuple(v for _, v in section_vals)
            rows = con.execute(
                f"SELECT skill_id, COUNT(*) AS c FROM {ex_table} WHERE {where} GROUP BY skill_id ORDER BY c DESC LIMIT 50",
                vals,
            ).fetchall()
            diag["nearby_example_candidates"] = [
                {"skill_id": str(r["skill_id"]), "example_count": int(r["c"]), "match_scope": "same_section_or_unit"}
                for r in rows
            ]
            diag["outline_example_candidates"] = [
                r for r in diag["nearby_example_candidates"] if str(r.get("skill_id", "")).startswith("outline_")
            ]

    con.close()

    if not diag["skill_exists"]:
        diag["recommended_action"] = "skill_id 不存在：請先修正 skill_id 或技能建立流程。"
    elif diag["exact_example_count"] == 0 and diag["outline_example_candidates"]:
        diag["recommended_action"] = "例題掛在 outline skill：建議建立 source mapping 或人工遷移。"
    elif diag["exact_example_count"] == 0 and diag["nearby_skill_candidates"]:
        diag["recommended_action"] = "例題掛在相近 skill：建議人工確認 alias/合併/拆分策略。"
    elif diag["exact_example_count"] == 0 and diag["nearby_example_candidates"]:
        diag["recommended_action"] = "同章節有例題但未掛在此 skill：建議先做 source alignment/classification。"
    elif diag["exact_example_count"] == 0:
        diag["recommended_action"] = "skill 存在但無例題：建議檢查匯入對應或人工建立 source mapping。"
    else:
        diag["recommended_action"] = "已有例題，建議重新執行 Phase 1 audit。"
    return diag


def _short(s: object, limit: int = 100) -> str:
    t = str(s or "").replace("\n", " ").strip()
    return t if len(t) <= limit else t[: limit - 3] + "..."


def _format_list(xs: list[Any]) -> str:
    return "無" if not xs else ", ".join(str(x) for x in xs)


def _build_problem_type_rows(examples: list[dict[str, Any]], contracts: dict[str, Any]) -> list[dict[str, Any]]:
    by_pt: dict[str, dict[str, Any]] = {}
    for e in examples:
        pt = str(e.get("problem_type_id", "")).strip()
        if not pt or pt == "unknown":
            continue
        by_pt.setdefault(pt, {"example_ids": [], "runtime_category": str(e.get("runtime_category", "")).strip()})
        if isinstance(e.get("example_id"), int):
            by_pt[pt]["example_ids"].append(int(e["example_id"]))
    rows: list[dict[str, Any]] = []
    for pt in sorted(by_pt.keys()):
        c = contracts.get(pt) if isinstance(contracts.get(pt), dict) else {}
        rows.append(
            {
                "problem_type_id": pt,
                "runtime_category": by_pt[pt]["runtime_category"],
                "example_ids": sorted(set(by_pt[pt]["example_ids"])),
                "answer_type": c.get("answer_type", ""),
                "equivalence_type": c.get("equivalence_type", ""),
                "checker_key": c.get("checker_key", ""),
            }
        )
    return rows


def _problem_type_name_zh(problem_type_id: str) -> str:
    names = {
        "absolute_value_inequality_geometric_meaning": "絕對值不等式幾何意義判讀",
        "absolute_value_inequality_interval_interpretation": "絕對值不等式區間詮釋",
        "absolute_value_inequality_distance_form": "絕對值距離型不等式",
        "absolute_value_inequality_linear_expression_basic": "一次式絕對值不等式",
        "absolute_value_inequality_shifted_basic": "平移型絕對值不等式",
        "absolute_value_inequality_zero_center_basic": "中心在 0 的絕對值不等式",
        "absolute_value_inequality_integer_solution_count_choice": "整數解個數選擇題",
    }
    return names.get(problem_type_id, "")


def _propose_for_unknown_examples(skill_id: str, examples: list[dict[str, Any]], proposal: dict[str, Any]) -> dict[str, Any]:
    proposed_map = proposal.get("proposed_example_map", [])
    manual_candidates = set(proposal.get("manual_review_candidates", []) or [])
    proposal_by_id = {
        int(x.get("example_id")): str(x.get("proposed_problem_type_id", "")).strip()
        for x in proposed_map
        if isinstance(x, dict) and isinstance(x.get("example_id"), int)
    }
    contracts = proposal.get("proposed_answer_contracts", {}) if isinstance(proposal.get("proposed_answer_contracts"), dict) else {}
    buckets: dict[str, dict[str, Any]] = {}
    per_example_details: list[dict[str, Any]] = []
    unknown_example_ids: list[int] = []
    for e in examples:
        exid = e.get("example_id")
        if not isinstance(exid, int):
            continue
        if str(e.get("problem_type_id", "")).strip() not in {"", "unknown"}:
            continue
        unknown_example_ids.append(exid)
        text = str(e.get("problem_preview") or e.get("problem_text") or e.get("question_text") or "")
        pt = proposal_by_id.get(exid, "")
        if exid in manual_candidates and "象限" in text and "(A)" in text:
            pt = "absolute_value_inequality_geometric_meaning"
            contracts.setdefault(
                pt,
                {
                    "answer_type": "choice",
                    "equivalence_type": "choice_label",
                    "checker_key": "choice_label_checker",
                    "order_matters": True,
                    "accepted_format_notes": ["A/B/C/D labels"],
                    "canonical_answer_schema": {"type": "choice_label"},
                },
            )
        if not pt or pt == "unknown":
            pt = "absolute_value_inequality_interval_interpretation"
            contracts.setdefault(
                pt,
                {
                    "answer_type": "interval_set",
                    "equivalence_type": "interval_set",
                    "checker_key": "interval_checker",
                    "order_matters": False,
                    "accepted_format_notes": ["interval notation or equivalent inequality form"],
                    "canonical_answer_schema": {"type": "interval_set"},
                },
            )
        feats: list[str] = []
        if "象限" in text:
            feats.append("quadrant_choice")
        if "左" in text or "右" in text or "距離" in text:
            feats.append("geometric_distance_phrase")
        if "(1)" in text and "(2)" in text:
            feats.append("multi_part")
        if "| " in text or "|x" in text or "\\left|" in text:
            feats.append("absolute_value_inequality_form")
        b = buckets.setdefault(pt, {"example_ids": [], "features": set(), "risk_flags": set()})
        b["example_ids"].append(exid)
        b["features"].update(feats)
        if exid in manual_candidates:
            b["risk_flags"].add("manual_review_candidate_in_proposal")
        per_example_details.append(
            {
                "example_id": exid,
                "title_or_source_label": str(e.get("title", "")).strip() or str(e.get("source_type", "")).strip(),
                "detected_problem_type_id": pt,
                "answer_shape": detect_answer_shape(contracts.get(pt, {})),
                "classification_confidence": "medium",
                "classification_reason": "heuristic_pattern_match",
                "risk_flags": sorted(set((e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else []) + (["manual_review_candidate_in_proposal"] if exid in manual_candidates else []))),
            }
        )

    total_unknown = sum(len(v["example_ids"]) for v in buckets.values())
    proposals: list[dict[str, Any]] = []
    for pt, v in sorted(buckets.items(), key=lambda kv: (-len(kv[1]["example_ids"]), kv[0])):
        ids = sorted(set(v["example_ids"]))
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        answer_type = str(c.get("answer_type", "")).strip()
        eq = str(c.get("equivalence_type", "")).strip()
        checker = str(c.get("checker_key", "")).strip()
        features = sorted(v["features"])
        risk_flags = sorted(v["risk_flags"])
        if len(ids) < 3:
            rec = "conservative_hold"
            blockers = ["insufficient_examples_for_safe_promote"]
            conf = "medium"
        elif len(buckets) > 1:
            rec = "split_required"
            blockers = ["mixed_structures_detected"]
            conf = "medium"
        elif not (answer_type and eq and checker):
            rec = "reject"
            blockers = ["missing_answer_contract_components"]
            conf = "low"
        elif "manual_review_candidate_in_proposal" in risk_flags:
            rec = "recommend_with_warning"
            blockers = []
            conf = "medium"
        else:
            rec = "recommend"
            blockers = []
            conf = "high"
        proposals.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "proposed_problem_type_name_zh": _problem_type_name_zh(pt),
                "matched_example_ids": ids,
                "matched_example_count": len(ids),
                "unmatched_example_ids": sorted(set(unknown_example_ids) - set(ids)),
                "representative_example_id": ids[0] if ids else None,
                "confidence": conf,
                "classification_confidence": conf,
                "structural_features": features,
                "answer_contract_proposal": c,
                "checker_key_proposal": checker,
                "equivalence_type_proposal": eq,
                "answer_shape": detect_answer_shape(c),
                "risk_flags": risk_flags,
                "promote_recommendation": rec,
                "promote_blockers": blockers,
            }
        )

    answer_shapes = {
        str(x.get("answer_contract_proposal", {}).get("answer_type", "")).strip()
        for x in proposals
        if isinstance(x.get("answer_contract_proposal"), dict)
    }
    multi_shapes = len({x for x in answer_shapes if x}) >= 2
    single_structure = len(proposals) == 1
    has_singleton = any(int(x.get("matched_example_count", 0)) == 1 for x in proposals)
    has_fatal = any("fatal" in str(x).lower() for x in proposal.get("risk_flags", []))
    if has_fatal:
        split_merge = "hold_fatal_inconsistency"
    elif not proposals and total_unknown > 0:
        split_merge = "hold_unknown_examples_only"
    elif single_structure:
        split_merge = "recommend_single_type"
    elif multi_shapes:
        split_merge = "recommend_split_problem_types"
    elif len(proposals) > 1:
        split_merge = "recommend_split_or_refine"
    else:
        split_merge = "block_promote_until_split"
    if has_singleton and split_merge == "recommend_split_problem_types":
        split_merge = "recommend_split_problem_types"

    precheck = {
        "proposed_problem_type_id_not_unknown": all(x.get("proposed_problem_type_id") not in {"", "unknown"} for x in proposals),
        "matched_example_ids_not_empty": all(bool(x.get("matched_example_ids")) for x in proposals),
        "answer_contract_not_empty": all(isinstance(x.get("answer_contract_proposal"), dict) and bool(x.get("answer_contract_proposal")) for x in proposals),
        "checker_key_not_empty": all(bool(x.get("checker_key_proposal")) for x in proposals),
        "equivalence_type_not_empty": all(bool(x.get("equivalence_type_proposal")) for x in proposals),
        "recommendation_not_reject": all(x.get("promote_recommendation") != "reject" for x in proposals),
        "no_fatal_risk_flags": not has_fatal,
    }
    gate_policy = build_phase1_gate_policy(
        proposals,
        source_examples_count=total_unknown,
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        min_examples_runtime_ready=3,
    )
    recommendation_gate = all(
        str(x.get("promote_recommendation", "")) in {"recommend", "recommend_with_warning"}
        for x in proposals
    )
    auto_approve_safe = bool(proposals) and all(precheck.values()) and recommendation_gate
    next_action = "review_classifier_proposal_and_decide_split_merge"
    if split_merge == "recommend_split_problem_types":
        next_action = "prepare_split_problem_types_then_promote_candidates"
    elif split_merge == "recommend_single_type" and auto_approve_safe:
        next_action = "ready_for_safe_promote"
    next_cmds = {
        "audit": f"python scripts\\gencode_pipeline_phase1_audit.py --skill-id {skill_id}",
        "review": f"python scripts\\gencode_pipeline_phase1_audit.py --skill-id {skill_id} --json",
        "promote": f"python scripts\\gencode_promote_classifier_proposal.py --skill-id {skill_id}",
        "auto_approve_safe": f"python scripts\\gencode_promote_classifier_proposal.py --skill-id {skill_id} --auto-approve-safe",
    }
    return {
        "skill_id": skill_id,
        "unknown_examples_total": total_unknown,
        "proposal_count": len(proposals),
        "candidate_problem_types": proposals,
        "proposal_items": proposals,
        "per_example_classification": per_example_details,
        "example_classification_details": per_example_details,
        "split_or_merge_recommendation": split_merge,
        **gate_policy,
        "per_candidate_promote_gate": [
            {
                "problem_type_id": str(x.get("problem_type_id", "")),
                "promote_recommendation": str(x.get("promote_recommendation", "")),
                "promote_blockers": x.get("promote_blockers", []),
            }
            for x in proposals
        ],
        "next_action": next_action,
        "promote_precheck": precheck,
        "auto_approve_safe_eligible": auto_approve_safe,
        "workflow_commands": next_cmds,
        "next_command_suggestions": next_cmds,
    }


def _build_stdout_summary(report: dict[str, Any]) -> str:
    lines: list[str] = []
    skill_id = report.get("skill_id", "")
    lines += [
        "============================================================",
        "Gencode 第一階段盤點摘要",
        "============================================================",
        f"skill_id: {skill_id}",
        f"階段狀態: {report.get('final_status', '')}",
        f"建議下一步: {report.get('recommended_next_phase', '')}",
        "",
        "題庫覆蓋狀態:",
        f"- 題庫例題總數: {report.get('examples_total', 0)}",
        f"- 已分類例題數: {report.get('examples_covered', 0)}",
        f"- 來源覆蓋判定: {report.get('source_coverage_status', '')}",
        f"- 是否可能完整覆蓋: {str(report.get('source_coverage_status', '') == 'FULL_OBSERVED_COVERAGE_CANDIDATE').lower()}",
        "",
        "題型分類結果:",
    ]
    rows = _build_problem_type_rows(report.get("examples_map", []), report.get("answer_contract_summary", {}))
    if not rows:
        lines.append("- none")
    else:
        for idx, r in enumerate(rows, start=1):
            lines += [
                f"{idx}. {r['problem_type_id']}",
                f"   - 對應例題: {_format_list(r['example_ids'])}",
                f"   - 執行類型: {r['runtime_category']}",
                f"   - 答案判分規格: {r['equivalence_type']} / {r['checker_key']}",
            ]
    lines += [
        "",
        "答案規格檢查:",
        f"- 缺少 answer_contract 的題型: {_format_list(report.get('missing_answer_contract_problem_types', []))}",
        f"- 缺少 checker_key 的題型: {_format_list(report.get('missing_checker_key_problem_types', []))}",
        f"- 需要等價答案測試的題型: {_format_list(report.get('equivalence_test_required_problem_types', []))}",
        "",
        "需人工審查:",
    ]
    manual_pts = report.get("manual_review_problem_types", [])
    if manual_pts:
        ex_map = report.get("examples_map", [])
        for pt in manual_pts:
            ids = [str(e.get("example_id")) for e in ex_map if str(e.get("problem_type_id", "")).strip() == pt and e.get("example_id") is not None]
            lines.append(f"- {pt}: 例題 {', '.join(ids) if ids else '無'}")
    else:
        lines.append("- 無")
    lines += [
        "",
        f"阻塞原因:\n- {_format_list(report.get('blocking_reasons', []))}",
        "",
        "警告:",
        "",
        "報告檔案:",
        f"- JSON: reports/gencode_closed_loop/{skill_id}_phase1_audit.json",
        f"- Markdown: reports/gencode_closed_loop/{skill_id}_phase1_audit.md",
        "",
    ]
    ars = report.get("auto_review_summary", {}) if isinstance(report.get("auto_review_summary"), dict) else {}
    auto_items = ars.get("proposal_items", []) if isinstance(ars.get("proposal_items"), list) else []
    if auto_items:
        lines.append("Auto Review Summary:")
        for idx, item in enumerate(auto_items, start=1):
            lines += [
                f"{idx}. proposed_problem_type_id: {item.get('proposed_problem_type_id', '')}" ,
                f"   - proposed_problem_type_name_zh: {item.get('proposed_problem_type_name_zh', '')}" ,
                f"   - matched_example_ids: {_format_list(item.get('matched_example_ids', []))}" ,
                f"   - matched_example_count: {item.get('matched_example_count', 0)}" ,
                f"   - unmatched_example_ids: {_format_list(item.get('unmatched_example_ids', []))}" ,
                f"   - representative_example_id: {item.get('representative_example_id', '')}" ,
                f"   - classification_confidence: {item.get('classification_confidence', '')}" ,
                f"   - answer_contract_proposal: {json.dumps(item.get('answer_contract_proposal', {}), ensure_ascii=True)}" ,
                f"   - checker_key_proposal: {item.get('checker_key_proposal', '')}" ,
                f"   - equivalence_type_proposal: {item.get('equivalence_type_proposal', '')}" ,
                f"   - promote_recommendation: {item.get('promote_recommendation', '')}" ,
                f"   - promote_blockers: {_format_list(item.get('promote_blockers', []))}" ,
            ]
        lines += [
            f"- auto_approve_safe_eligible: {str(bool(ars.get('auto_approve_safe_eligible', False))).lower()}" ,
            f"- split_or_merge_recommendation: {ars.get('split_or_merge_recommendation', '')}",
            f"- classifier_gate: {json.dumps(ars.get('classifier_gate', {}), ensure_ascii=True)}",
            f"- generator_draft_gate: {json.dumps(ars.get('generator_draft_gate', {}), ensure_ascii=True)}",
            f"- runtime_ready_gate: {json.dumps(ars.get('runtime_ready_gate', {}), ensure_ascii=True)}",
            f"- per_candidate_promote_gate: {json.dumps(ars.get('per_candidate_promote_gate', []), ensure_ascii=True)}",
            f"- next_action: {ars.get('next_action', '')}",
            "",
        ]
    ex_details = ars.get("example_classification_details", []) if isinstance(ars.get("example_classification_details"), list) else []
    if ex_details:
        lines.append("Example Classification Details:")
        for d in ex_details:
            lines.append(
                f"- example_id={d.get('example_id', '')}, detected_problem_type_id={d.get('detected_problem_type_id', '')}, answer_shape={d.get('answer_shape', '')}, classification_reason={d.get('classification_reason', '')}, risk_flags={_format_list(d.get('risk_flags', []))}"
            )
    if report.get("final_status") == "AUDIT_FAIL" and "inventory_failed" in (report.get("blocking_reasons") or []):
        lines += [
            "Inventory 診斷:",
            f"- inventory_failed_reason: {report.get('inventory_failed_reason', '')}",
            f"- skill_exists: {str(bool(report.get('skill_exists', False))).lower()}",
            f"- exact_example_count: {report.get('exact_example_count', 0)}",
            f"- nearby_skill_candidates: {_format_list([x.get('skill_id') for x in (report.get('nearby_skill_candidates') or [])])}",
            f"- nearby_example_candidates: {_format_list([x.get('skill_id') for x in (report.get('nearby_example_candidates') or [])])}",
            f"- outline_example_candidates: {_format_list([x.get('skill_id') for x in (report.get('outline_example_candidates') or [])])}",
            f"- recommended_action: {report.get('recommended_action', '')}",
            "",
        ]
    warn_map = {
        "manual_review_problem_types_present": "有題型需要人工審查",
        "risk_flags_present": "有來源或分類風險標記",
        "skill_specific_classifier_missing": "缺少 skill-specific classifier",
        "classifier_proposal_generated": "已產生 classifier proposal，待人工審核",
    }
    ws = report.get("warnings", [])
    if ws:
        for w in ws:
            lines.append(f"- {w}：{warn_map.get(str(w), '請檢查此警告')}")
    else:
        lines.append("- 無")
    lines.append("")
    if report.get("final_status") == "AUDIT_PARTIAL" and report.get("recommended_next_phase") == "phase2_build":
        lines += [
            "判讀說明:",
            "Phase 1 分類結果可使用。",
            "目前是 AUDIT_PARTIAL，原因是存在 manual_review 或 risk warning，不是 classifier 失敗。",
            "",
        ]
    lines += [
        "下一步建議:",
    ]
    if report.get("recommended_next_phase") == "phase2_build":
        lines.append(f"執行：\npython scripts\\gencode_pipeline_phase2_build.py --skill-id {skill_id}")
    elif report.get("recommended_next_phase") == "review_classifier_proposal":
        lines.append("請先審核 classifier proposal，再執行 promote。")
    else:
        lines.append(f"- {report.get('recommended_next_phase', '')}")
    lines.append("============================================================")
    return "\n".join(lines)


def _write_phase1_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = _build_problem_type_rows(report.get("examples_map", []), report.get("answer_contract_summary", {}))
    lines: list[str] = [
        "# Gencode 第一階段盤點報告",
        "",
        "## 1. 摘要",
        f"- skill_id: {report.get('skill_id', '')}",
        f"- 階段狀態: {report.get('final_status', '')}",
        f"- 建議下一步: {report.get('recommended_next_phase', '')}",
        f"- 題庫例題總數: {report.get('examples_total', 0)}",
        f"- 已分類例題數: {report.get('examples_covered', 0)}",
        f"- 來源覆蓋判定: {report.get('source_coverage_status', '')}",
        "",
        "## 2. 題型覆蓋表",
        "",
        "| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        status = "manual_review" if r["runtime_category"] == "manual_review" else "classified"
        lines.append(
            f"| {r['problem_type_id']} | {r['runtime_category']} | {', '.join(str(x) for x in r['example_ids'])} | {r['answer_type']} | {r['equivalence_type']} | {r['checker_key']} | {status} |"
        )
    lines += [
        "",
        "## 3. 例題分類表",
        "",
        "| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for e in report.get("examples_map", []):
        lines.append(
            "| {id} | {pt} | {rt} | {cf} | {rf} | {pv} |".format(
                id=e.get("example_id", ""),
                pt=str(e.get("problem_type_id", "")).strip(),
                rt=str(e.get("runtime_category", "")).strip(),
                cf=str(e.get("classifier_confidence", "")).strip(),
                rf=_short(",".join(e.get("semantic_risk_flags", []) if isinstance(e.get("semantic_risk_flags"), list) else []), 60),
                pv=_short(e.get("problem_preview", ""), 110).replace("|", "\\|"),
            )
        )
    lines += [
        "",
        "## 4. 答案規格檢查",
        f"- 缺少 answer_contract 的題型: {_format_list(report.get('missing_answer_contract_problem_types', []))}",
        f"- 缺少 checker_key 的題型: {_format_list(report.get('missing_checker_key_problem_types', []))}",
        f"- 需要等價答案測試的題型: {_format_list(report.get('equivalence_test_required_problem_types', []))}",
        "",
        "## 5. 人工審查與風險標記",
        f"- manual_review_problem_types: {_format_list(report.get('manual_review_problem_types', []))}",
        f"- risk_flags: {_format_list(report.get('risk_flags', []))}",
    ]
    for e in report.get("examples_map", []):
        if str(e.get("runtime_category", "")).strip() == "manual_review":
            lines.append(
                f"- example {e.get('example_id')}: {_short(e.get('manual_review_reason', ''), 120)}"
            )
    cp = report.get("classifier_proposal", {}) if isinstance(report.get("classifier_proposal"), dict) else {}
    lines += [
        "",
        "## 6. Classifier Proposal 狀態",
        f"- classifier_proposal.enabled: {cp.get('enabled', False)}",
        f"- proposal_status: {cp.get('proposal_status', 'SKIPPED')}",
        f"- reason: {cp.get('reason', '')}",
        f"- proposal_path: {cp.get('proposal_path', '')}",
        f"- promote_ready: {cp.get('promote_ready', False)}",
        f"- promote_command_suggestion: {cp.get('promote_command_suggestion', '')}",
        "",
        "## 7. Auto Review Summary",
    ]
    ars = report.get("auto_review_summary", {}) if isinstance(report.get("auto_review_summary"), dict) else {}
    auto_items = ars.get("proposal_items", []) if isinstance(ars.get("proposal_items"), list) else []
    lines += [
        f"- proposal_count: {ars.get('proposal_count', 0)}",
        f"- unknown_examples_total: {ars.get('unknown_examples_total', 0)}",
        f"- auto_approve_safe_eligible: {ars.get('auto_approve_safe_eligible', False)}",
        f"- split_or_merge_recommendation: {ars.get('split_or_merge_recommendation', '')}",
        f"- classifier_gate: {ars.get('classifier_gate', {})}",
        f"- generator_draft_gate: {ars.get('generator_draft_gate', {})}",
        f"- runtime_ready_gate: {ars.get('runtime_ready_gate', {})}",
        f"- per_candidate_promote_gate: {ars.get('per_candidate_promote_gate', [])}",
        f"- next_action: {ars.get('next_action', '')}",
    ]
    if auto_items:
        lines += [
            "",
            "| problem_type_id | name_zh | matched_example_ids | matched_count | unmatched_example_ids | representative_example_id | confidence | checker_key | equivalence_type | recommendation | blockers |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in auto_items:
            lines.append(
                "| {pt} | {zh} | {ids} | {cnt} | {uids} | {rep} | {cf} | {ck} | {eq} | {rec} | {blk} |".format(
                    pt=item.get("proposed_problem_type_id", ""),
                    zh=item.get("proposed_problem_type_name_zh", ""),
                    ids=", ".join(str(x) for x in (item.get("matched_example_ids") or [])),
                    cnt=item.get("matched_example_count", 0),
                    uids=", ".join(str(x) for x in (item.get("unmatched_example_ids") or [])),
                    rep=item.get("representative_example_id", ""),
                    cf=item.get("classification_confidence", ""),
                    ck=item.get("checker_key_proposal", ""),
                    eq=item.get("equivalence_type_proposal", ""),
                    rec=item.get("promote_recommendation", ""),
                    blk=", ".join(str(x) for x in (item.get("promote_blockers") or [])),
                )
            )
    ex_details = ars.get("example_classification_details", []) if isinstance(ars.get("example_classification_details"), list) else []
    if ex_details:
        lines += [
            "",
            "### Candidate-to-Example Mapping",
            "",
            "| example_id | title/source | detected_problem_type_id | answer_shape | classification_reason | risk_flags |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for d in ex_details:
            lines.append(
                "| {eid} | {title} | {pt} | {shape} | {reason} | {risk} |".format(
                    eid=d.get("example_id", ""),
                    title=str(d.get("title_or_source_label", "")).replace("|", "\\|"),
                    pt=d.get("detected_problem_type_id", ""),
                    shape=d.get("answer_shape", ""),
                    reason=d.get("classification_reason", ""),
                    risk=", ".join(str(x) for x in (d.get("risk_flags") or [])),
                )
            )
    precheck = ars.get("promote_precheck", {}) if isinstance(ars.get("promote_precheck"), dict) else {}
    if precheck:
        lines.append(f"- promote_precheck: {precheck}")
    cmds = ars.get("workflow_commands", {}) if isinstance(ars.get("workflow_commands"), dict) else {}
    if cmds:
        lines.append(f"- workflow_commands: {cmds}")
    next_cmds = ars.get("next_command_suggestions", {}) if isinstance(ars.get("next_command_suggestions"), dict) else {}
    if next_cmds:
        lines.append(f"- next_command_suggestions: {next_cmds}")
    lines += [
        "",
        "## 8. 下一步建議",
    ]
    if report.get("recommended_next_phase") == "phase2_build":
        lines.append(f"python scripts\\gencode_pipeline_phase2_build.py --skill-id {report.get('skill_id', '')}")
    elif report.get("recommended_next_phase") == "review_classifier_proposal":
        lines.append("請先審核 classifier proposal，再執行 promote。")
    else:
        lines.append(str(report.get("recommended_next_phase", "")))
    if report.get("missing_checker_key_problem_types"):
        lines.append("請先實作或註冊 checker。")
    ars = report.get("auto_review_summary", {}) if isinstance(report.get("auto_review_summary"), dict) else {}
    auto_items = ars.get("proposal_items", []) if isinstance(ars.get("proposal_items"), list) else []
    if auto_items:
        lines.append("Auto Review Summary:")
        for idx, item in enumerate(auto_items, start=1):
            lines += [
                f"{idx}. proposed_problem_type_id: {item.get('proposed_problem_type_id', '')}" ,
                f"   - proposed_problem_type_name_zh: {item.get('proposed_problem_type_name_zh', '')}" ,
                f"   - matched_example_ids: {_format_list(item.get('matched_example_ids', []))}" ,
                f"   - classification_confidence: {item.get('classification_confidence', '')}" ,
                f"   - answer_contract_proposal: {json.dumps(item.get('answer_contract_proposal', {}), ensure_ascii=True)}" ,
                f"   - checker_key_proposal: {item.get('checker_key_proposal', '')}" ,
                f"   - equivalence_type_proposal: {item.get('equivalence_type_proposal', '')}" ,
                f"   - promote_recommendation: {item.get('promote_recommendation', '')}" ,
                f"   - promote_blockers: {_format_list(item.get('promote_blockers', []))}" ,
            ]
        lines += [
            f"- auto_approve_safe_eligible: {str(bool(ars.get('auto_approve_safe_eligible', False))).lower()}" ,
            "",
        ]
    if report.get("final_status") == "AUDIT_FAIL" and "inventory_failed" in (report.get("blocking_reasons") or []):
        lines += [
            "",
            "## Inventory 診斷",
            f"- inventory_failed_reason: {report.get('inventory_failed_reason', '')}",
            f"- skill_exists: {report.get('skill_exists', False)}",
            f"- skill_profile: {report.get('skill_profile', {})}",
            f"- exact_example_count: {report.get('exact_example_count', 0)}",
            f"- nearby_skill_candidates: {report.get('nearby_skill_candidates', [])}",
            f"- nearby_example_candidates: {report.get('nearby_example_candidates', [])}",
            f"- outline_example_candidates: {report.get('outline_example_candidates', [])}",
            f"- recommended_action: {report.get('recommended_action', '')}",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    skill_id = args.skill_id
    out_md = REPORT_DIR / f"{skill_id}_phase1_audit.md"
    proposal_json = REPORT_DIR / f"{skill_id}_classifier_proposal.json"
    proposal_md = REPORT_DIR / f"{skill_id}_classifier_proposal.md"

    # Debug CLI delegates to shared orchestrator service.
    orchestrated = run_gencode_auto_pipeline(
        skill_id=skill_id,
        dry_run=True,
        allow_runtime_ready=False,
        write_pending_files=True,
    )
    phase1_path = Path(str(orchestrated.get("reports", {}).get("phase1_json", "")))
    report: dict[str, Any] = {}
    if phase1_path.exists():
        try:
            report = json.loads(phase1_path.read_text(encoding="utf-8"))
        except Exception:
            report = {}
    if not report:
        report = {
            "skill_id": skill_id,
            "phase": "phase1_audit",
            "final_status": "AUDIT_FAIL",
            "blocking_reasons": ["orchestrator_phase1_report_missing"],
            "warnings": [],
            "artifact_paths": orchestrated.get("reports", {}),
            "timestamp": utc_timestamp(),
        }
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print(_build_stdout_summary(report))
    # return

    out_json = REPORT_DIR / f"{skill_id}_phase1_audit.json"

    inv_cmd = [sys.executable, "scripts/gencode_skill_inventory.py", "--skill-id", skill_id]
    code, inv, stdout, stderr = _run_json_cmd(inv_cmd, timeout=900)

    if code != 0 or not inv.get("success"):
        diag = _inventory_failure_diagnostics(skill_id, DEFAULT_DB_PATH)
        inv_failed_reason = ""
        if stderr.strip():
            inv_failed_reason = stderr.strip().splitlines()[-1].strip()
        elif stdout.strip():
            inv_failed_reason = stdout.strip().splitlines()[-1].strip()
        else:
            inv_failed_reason = "inventory_command_failed"
        report = {
            "skill_id": skill_id,
            "phase": "phase1_audit",
            "final_status": "AUDIT_FAIL",
            "blocking_reasons": ["inventory_failed"],
            "inventory_failed_reason": inv_failed_reason,
            "skill_exists": bool(diag.get("skill_exists", False)),
            "skill_profile": diag.get("skill_profile", {}),
            "exact_example_count": int(diag.get("exact_example_count", 0)),
            "nearby_skill_candidates": diag.get("nearby_skill_candidates", []),
            "nearby_example_candidates": diag.get("nearby_example_candidates", []),
            "outline_example_candidates": diag.get("outline_example_candidates", []),
            "recommended_action": str(diag.get("recommended_action", "")),
            "warnings": [],
            "artifact_paths": {"phase1_json": str(out_json), "phase1_md": str(out_md)},
            "timestamp": utc_timestamp(),
            "raw_inventory_stdout": stdout,
            "raw_inventory_stderr": stderr,
        }
        write_json(out_json, report)
        _write_phase1_markdown(out_md, report)
        if args.json:
            print(json.dumps(report, ensure_ascii=True))
        else:
            print(_build_stdout_summary(report))
        return

    package_dir = Path(str(inv.get("package_dir", "")))
    examples_map_path = next(iter(package_dir.glob("examples_map_*.yaml")), None)
    problem_types_path = next(iter(package_dir.glob("problem_types_*.yaml")), None)
    examples = _load_yaml(examples_map_path).get("examples", []) if examples_map_path else []
    items = _load_yaml(problem_types_path).get("items", []) if problem_types_path else []
    if not isinstance(examples, list):
        examples = []
    if not isinstance(items, list):
        items = []

    examples = [e for e in examples if isinstance(e, dict)]
    items = [i for i in items if isinstance(i, dict)]

    observed_problem_types = sorted(
        {
            str(e.get("problem_type_id", "")).strip()
            for e in examples
            if str(e.get("problem_type_id", "")).strip() and str(e.get("problem_type_id", "")).strip() != "unknown"
        }
    )

    pt_map = {str(i.get("problem_type_id", "")).strip(): i for i in items if str(i.get("problem_type_id", "")).strip()}
    defaults = ANSWER_CONTRACT_DEFAULTS.get(skill_id, {})
    observed_contracts: dict[str, Any] = {}
    missing_answer_contract_problem_types: list[str] = []
    missing_checker_key_problem_types: list[str] = []
    equivalence_test_required_problem_types: list[str] = []
    for pt in observed_problem_types:
        row = pt_map.get(pt, {})
        contract = row.get("answer_contract") if isinstance(row, dict) else None
        if not isinstance(contract, dict):
            contract = defaults.get(pt)
        if not isinstance(contract, dict):
            missing_answer_contract_problem_types.append(pt)
            observed_contracts[pt] = None
            continue
        observed_contracts[pt] = contract
        if not str(contract.get("checker_key", "")).strip():
            missing_checker_key_problem_types.append(pt)
        eq = str(contract.get("equivalence_type", "")).strip()
        if eq not in {"exact_string", "numeric_exact"}:
            equivalence_test_required_problem_types.append(pt)
        missing_fields = sorted(REQUIRED_CONTRACT_FIELDS.difference(set(contract.keys())))
        if missing_fields:
            missing_answer_contract_problem_types.append(pt)

    risk_flags = sorted({flag for e in examples for flag in (e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else [])})
    manual_review_problem_types = sorted(
        {
            str(e.get("problem_type_id", "")).strip()
            for e in examples
            if str(e.get("semantic_audit_status", "")).strip() == "review_required" and str(e.get("problem_type_id", "")).strip()
        }
    )
    future_ai_judged_problem_types: list[str] = []

    examples_total = int(inv.get("examples_count", 0))
    examples_covered = len(examples)

    unknown_count = sum(
        1
        for e in examples
        if str(e.get("problem_type_id", "")).strip() in {"", "unknown"}
        or str(e.get("classification_rule_id", "")).strip() == "fallback.unknown"
    )
    unknown_ratio = (unknown_count / max(len(examples), 1)) if examples else 0.0
    classifier_proposal_enabled = (
        examples_total >= 3
        and examples_covered > 0
        and unknown_ratio >= 0.6
    )
    classifier_proposal = {
        "enabled": classifier_proposal_enabled,
        "reason": "",
        "proposal_status": "SKIPPED",
        "proposed_problem_types": [],
        "proposed_example_map": [],
        "proposed_answer_contracts": {},
        "manual_review_candidates": [],
        "risk_flags": [],
        "proposal_path": str(proposal_json),
        "promote_ready": False,
        "promote_command_suggestion": f"python scripts\\gencode_promote_classifier_proposal.py --skill-id {skill_id}",
    }
    if classifier_proposal_enabled:
        try:
            proposal = build_classifier_proposal(skill_id, examples)
            classifier_proposal.update(
                {
                    "reason": "fallback_unknown_majority",
                    "proposal_status": "GENERATED",
                    "proposed_problem_types": proposal.get("proposed_problem_types", []),
                    "proposed_example_map": proposal.get("proposed_example_map", []),
                    "proposed_answer_contracts": proposal.get("proposed_answer_contracts", {}),
                    "manual_review_candidates": proposal.get("manual_review_candidates", []),
                    "risk_flags": proposal.get("risk_flags", []),
                    "promote_ready": True,
                }
            )
            write_json(proposal_json, proposal)
            write_md(proposal_md, f"Classifier Proposal: {skill_id}", [("proposal", proposal)])
        except Exception as e:
            classifier_proposal.update(
                {
                    "proposal_status": "FAILED",
                    "reason": f"proposal_generation_failed: {e}",
                    "promote_ready": False,
                }
            )
    auto_review_summary: dict[str, Any] = {}
    if classifier_proposal.get("proposal_status") == "GENERATED":
        auto_review_summary = _propose_for_unknown_examples(skill_id, examples, classifier_proposal)
        recommendations = [str(x.get("promote_recommendation", "")) for x in auto_review_summary.get("proposal_items", []) if isinstance(x, dict)]
        if recommendations and all(x in {"recommend", "recommend_with_warning"} for x in recommendations):
            classifier_proposal["promote_ready"] = True
        elif recommendations:
            classifier_proposal["promote_ready"] = False

    bootstrap_cfg = _load_bootstrap_config(skill_id)
    bootstrap_summary = {
        "bootstrap_mode": bool(bootstrap_cfg.get("bootstrap_mode", False)),
        "bootstrap_source_skill_id": str(bootstrap_cfg.get("bootstrap_source_skill_id", "")),
        "source_coverage_status": str(bootstrap_cfg.get("source_coverage_status", "")),
        "allowed_problem_types": bootstrap_cfg.get("allowed_problem_types", []),
    }

    if bootstrap_summary["bootstrap_mode"]:
        source_coverage_status = bootstrap_summary["source_coverage_status"] or "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
    elif examples_total >= 4 and not manual_review_problem_types:
        source_coverage_status = "FULL_OBSERVED_COVERAGE_CANDIDATE"
    elif examples_total <= 1:
        source_coverage_status = "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
    else:
        source_coverage_status = "INSUFFICIENT_SOURCE_EXAMPLES"

    blocking_reasons: list[str] = []
    warnings: list[str] = []
    if missing_answer_contract_problem_types:
        blocking_reasons.append("missing_answer_contract_problem_types")
    if missing_checker_key_problem_types:
        blocking_reasons.append("missing_checker_key_problem_types")
    if manual_review_problem_types:
        warnings.append("manual_review_problem_types_present")
    if risk_flags:
        warnings.append("risk_flags_present")

    if classifier_proposal.get("proposal_status") == "GENERATED":
        blocking_reasons.append("classifier_proposal_requires_review")
        warnings.extend(["skill_specific_classifier_missing", "classifier_proposal_generated"])

    hard_blocking_reasons = [x for x in blocking_reasons if x != "classifier_proposal_requires_review"]
    if hard_blocking_reasons:
        final_status = "AUDIT_FAIL"
    elif warnings or source_coverage_status != "FULL_OBSERVED_COVERAGE_CANDIDATE":
        final_status = "AUDIT_PARTIAL"
    else:
        final_status = "AUDIT_PASS"

    next_phase = "phase2_build"
    if classifier_proposal.get("proposal_status") == "GENERATED":
        next_phase = "review_classifier_proposal"

    report = {
        "skill_id": skill_id,
        "phase": "phase1_audit",
        "final_status": final_status,
        "examples_total": examples_total,
        "examples_covered": examples_covered,
        "examples_map": examples,
        "observed_problem_types": observed_problem_types,
        "source_coverage_status": source_coverage_status,
        "bootstrap_summary": bootstrap_summary,
        "answer_contract_summary": observed_contracts,
        "missing_answer_contract_problem_types": sorted(set(missing_answer_contract_problem_types)),
        "missing_checker_key_problem_types": sorted(set(missing_checker_key_problem_types)),
        "equivalence_test_required_problem_types": sorted(set(equivalence_test_required_problem_types)),
        "manual_review_problem_types": manual_review_problem_types,
        "future_ai_judged_problem_types": future_ai_judged_problem_types,
        "classifier_proposal": classifier_proposal,
        "auto_review_summary": auto_review_summary,
        "risk_flags": risk_flags,
        "recommended_next_phase": next_phase,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "artifact_paths": {
            "phase1_json": str(out_json),
            "phase1_md": str(out_md),
            "inventory_report": str(inv.get("report", "")),
            "classifier_proposal_json": str(proposal_json) if classifier_proposal.get("proposal_status") == "GENERATED" else "",
            "classifier_proposal_md": str(proposal_md) if classifier_proposal.get("proposal_status") == "GENERATED" else "",
        },
        "timestamp": utc_timestamp(),
    }
    write_json(out_json, report)
    _write_phase1_markdown(out_md, report)
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print(_build_stdout_summary(report))


if __name__ == "__main__":
    main()



