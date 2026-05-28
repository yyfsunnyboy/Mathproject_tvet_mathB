from __future__ import annotations

import json
import py_compile
import sqlite3
import ast
import shutil
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any

from flask import current_app, has_app_context
from core.ai_wrapper import call_ai_with_retry, get_ai_client
from core.ai_wrapper import resolve_gemini_api_key
from core.ai_settings import get_ai_settings_snapshot, get_effective_model_config
from core.gencode.classifier_proposal import build_classifier_proposal, detect_answer_shape
from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.base import ClassifierContext
from core.gencode.classifiers.fallback_classifier import FallbackClassifier
from core.gencode.pipeline_policy import evaluate_pipeline_gates
from core.gencode.pipeline_state import utc_timestamp, write_json, write_md

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
DRAFT_DIR = REPORT_DIR / "drafts"
CLASSIFIER_DRAFT_DIR = REPORT_DIR / "classifier_drafts"
CLASSIFIER_RULEPACK_PATH = PROJECT_ROOT / "configs" / "gencode" / "classifiers" / "phase1_rule_packs.yaml"
CLASSIFIER_RULEPACK_BACKUP_DIR = PROJECT_ROOT / "backups" / "gencode_classifier_rulepacks"


def _log_gencode_ai_runtime(tag: str, meta: dict[str, Any]) -> None:
    if not has_app_context():
        return
    current_app.logger.info(
        "[GENCODE AI RUNTIME] tag=%s role=%s mode=%s provider=%s model=%s source=%s has_api_key=%s endpoint=%s reason=%s",
        tag,
        meta.get("role", ""),
        meta.get("mode", ""),
        meta.get("provider", ""),
        meta.get("model", ""),
        meta.get("source", ""),
        bool(meta.get("has_api_key", False)),
        meta.get("endpoint", ""),
        meta.get("failure_reason", ""),
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml  # type: ignore
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    path.write_text(text, encoding="utf-8")


def _load_registered_classifier_rulepack(skill_id: str) -> dict[str, Any] | None:
    root = _load_yaml(CLASSIFIER_RULEPACK_PATH)
    skills = root.get("skills", []) if isinstance(root.get("skills"), list) else []
    sid = str(skill_id or "").strip()
    for item in skills:
        if not isinstance(item, dict):
            continue
        if str(item.get("skill_id", "")).strip() == sid:
            return item
    return None


def _classify_examples_with_rulepack(
    *,
    skill_id: str,
    examples: list[dict[str, Any]],
    pack: dict[str, Any],
) -> list[dict[str, Any]]:
    problem_types = pack.get("problem_types", []) if isinstance(pack.get("problem_types"), list) else []
    rules = pack.get("classification_rules", []) if isinstance(pack.get("classification_rules"), list) else []
    pt_by_id = {
        str(x.get("problem_type_id", "")).strip(): x
        for x in problem_types
        if isinstance(x, dict) and str(x.get("problem_type_id", "")).strip()
    }
    fallback_pt = next((pid for pid, cfg in pt_by_id.items() if not bool(cfg.get("requires_human_action", False))), "") or next(iter(pt_by_id.keys()), "unclassified_source_review")
    rows: list[dict[str, Any]] = []
    for ex in examples:
        text = _source_text(ex)
        text_l = text.lower()
        chosen = ""
        for r in rules:
            if not isinstance(r, dict):
                continue
            toks = r.get("if_contains", []) if isinstance(r.get("if_contains"), list) else []
            toks = [str(t).strip().lower() for t in toks if str(t).strip()]
            if toks and any(t in text_l for t in toks):
                chosen = str(r.get("prefer_problem_type_id", "")).strip()
                if chosen:
                    break
        pt = chosen if chosen in pt_by_id else fallback_pt
        cfg = pt_by_id.get(pt, {})
        checker = str(cfg.get("checker", "")).strip()
        eq = str(cfg.get("equivalence", "")).strip()
        needs_human = bool(cfg.get("requires_human_action", False))
        rows.append(
            {
                "example_id": ex.get("id"),
                "title": str(ex.get("title", "")).strip(),
                "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
                "problem_preview": text[:200],
                "skill_id": skill_id,
                "subskill_id": pt,
                "problem_type_id": pt,
                "runtime_category": "manual_review" if needs_human else "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression",
                "classification_rule_id": "rule_pack.yaml",
                "classification_reason": "matched_registered_yaml_rule_pack",
                "classifier_confidence": "high",
                "semantic_risk_flags": [],
                "semantic_audit_status": "review_required" if needs_human else "ok",
                "generator_status": "manual_review" if needs_human else "ready_for_draft",
                "manual_review_reason": str(cfg.get("notes", "")).strip() if needs_human else "",
            }
        )
    return rows


def _build_classifier_yaml_draft_from_phase1(payload: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    skill_id = str(payload.get("skill_id", "")).strip()
    skill_ch_name = _pick_skill_ch_name(skill_id, examples)
    candidates = payload.get("candidate_problem_types", []) if isinstance(payload.get("candidate_problem_types"), list) else []
    per_example = payload.get("per_example_classification", []) if isinstance(payload.get("per_example_classification"), list) else []
    pt_contract: dict[str, dict[str, Any]] = {}
    for c in candidates:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        checker = str(c.get("checker_key_proposal", "")).strip()
        eq = str(c.get("equivalence_type_proposal", "")).strip()
        pt_contract[pt] = {
            "problem_type_id": pt,
            "display_name": pt.replace("_", " "),
            "checker": checker,
            "equivalence": eq,
            "runtime_candidate": bool(checker and eq and checker != "manual_review_checker" and eq != "manual_review_or_ai_judged"),
            "requires_human_action": bool(checker == "manual_review_checker" or eq == "manual_review_or_ai_judged"),
            "merge_policy": "single_primary_problem_type" if len({str(x.get('detected_problem_type_id', '')).strip() for x in per_example if isinstance(x, dict) and str(x.get('detected_problem_type_id', '')).strip()}) <= 1 else "split_by_contract_diff",
            "notes": "auto-generated classifier draft from phase1",
        }
    rules: list[dict[str, Any]] = []
    for pt in pt_contract.keys():
        rules.append({"if_contains": [], "prefer_problem_type_id": pt})
    return {
        "skill_id": skill_id,
        "skill_ch_name": skill_ch_name,
        "classifier_source": f"{payload.get('classifier_source', 'ai_bootstrap')}_confirmed",
        "problem_types": list(pt_contract.values()),
        "classification_rules": rules,
        "source_classifications": per_example,
        "source_policy": {
            "source_count_threshold_for_split": 4,
            "small_skill_merge_allowed": True,
            "min_source_examples": 1,
            "allow_single_problem_type": True,
            "allow_skill_default_problem_type": True,
            "default_problem_type_used": any(str(k).endswith("_default") for k in pt_contract.keys()),
            "single_primary_problem_type": len(pt_contract) <= 1,
            "split_only_when_checker_or_answer_contract_differs": True,
            "do_not_create_student_subskills": True,
        },
    }


def _write_classifier_yaml_draft(skill_id: str, draft: dict[str, Any]) -> str:
    CLASSIFIER_DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    path = CLASSIFIER_DRAFT_DIR / f"{skill_id}_classifier.yaml"
    _write_yaml(path, draft)
    return str(path)


def register_classifier_rulepack_from_draft(skill_id: str, confirm: bool = False) -> dict[str, Any]:
    draft_path = CLASSIFIER_DRAFT_DIR / f"{skill_id}_classifier.yaml"
    if not draft_path.exists():
        return {"ok": False, "skill_id": skill_id, "error": "classifier_draft_not_found", "draft_path": str(draft_path)}
    draft = _load_yaml(draft_path)
    if not confirm:
        return {"ok": True, "skill_id": skill_id, "status": "preview", "draft_path": str(draft_path), "formal_rulepack_path": str(CLASSIFIER_RULEPACK_PATH)}
    if not isinstance(draft, dict) or not str(draft.get("skill_id", "")).strip():
        return {"ok": False, "skill_id": skill_id, "error": "invalid_classifier_draft_yaml", "draft_path": str(draft_path)}
    CLASSIFIER_RULEPACK_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = ""
    if CLASSIFIER_RULEPACK_PATH.exists():
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup = CLASSIFIER_RULEPACK_BACKUP_DIR / f"phase1_rule_packs.{ts}.yaml"
        shutil.copy2(CLASSIFIER_RULEPACK_PATH, backup)
        backup_path = str(backup)
    root = _load_yaml(CLASSIFIER_RULEPACK_PATH)
    if not root:
        root = {"version": 1, "skills": []}
    skills = root.get("skills", []) if isinstance(root.get("skills"), list) else []
    sid = str(skill_id or "").strip()
    replaced = False
    for i, s in enumerate(skills):
        if isinstance(s, dict) and str(s.get("skill_id", "")).strip() == sid:
            skills[i] = draft
            replaced = True
            break
    if not replaced:
        skills.append(draft)
    root["skills"] = skills
    _write_yaml(CLASSIFIER_RULEPACK_PATH, root)
    _ = _load_yaml(CLASSIFIER_RULEPACK_PATH)  # read-back validation
    return {
        "ok": True,
        "skill_id": sid,
        "status": "registered",
        "replaced_existing": replaced,
        "draft_path": str(draft_path),
        "formal_rulepack_path": str(CLASSIFIER_RULEPACK_PATH),
        "backup_path": backup_path,
    }


def _resolve_gencode_ai_client(preferred_roles: list[str]) -> tuple[Any | None, dict[str, Any]]:
    snapshot = get_ai_settings_snapshot()
    mode = str(snapshot.get("ai_global_strategy", "unknown"))
    api_key, _src = resolve_gemini_api_key()
    has_api_key = bool(str(api_key or "").strip())
    last_meta: dict[str, Any] = {}
    for role in preferred_roles:
        cfg = get_effective_model_config(role)
        provider = str(cfg.get("provider", "local")).lower()
        model = str(cfg.get("model", ""))
        source = str(cfg.get("_resolved_source", "unknown"))
        meta = {
            "role": role,
            "mode": mode,
            "provider": provider,
            "model": model,
            "source": source,
            "has_api_key": has_api_key,
            "endpoint": "google_api" if provider == "google" else "local_api",
            "failure_reason": "",
        }
        try:
            c = get_ai_client(role=role)
            actual_provider = "google" if "GoogleAIClient" in type(c).__name__ else "local"
            if provider == "google" and actual_provider != "google":
                meta["failure_reason"] = "resolved_google_but_fell_back_to_local"
                _log_gencode_ai_runtime("resolve", meta)
                last_meta = meta
                continue
            _log_gencode_ai_runtime("resolve", meta)
            return c, meta
        except Exception as ex:
            meta["failure_reason"] = str(ex)
            _log_gencode_ai_runtime("resolve", meta)
            last_meta = meta
            continue
    return None, last_meta


def _safe_file_component(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "unknown_skill"
    for ch in '<>:"/\\|?*':
        raw = raw.replace(ch, "_")
    return raw


def _load_examples(skill_id: str, db_path: str = "instance/kumon_math.db") -> list[dict[str, Any]]:
    con = sqlite3.connect(str(PROJECT_ROOT / db_path))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY rowid", (skill_id,)).fetchall()]
    con.close()
    return rows


def _classify_examples(skill_id: str, examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    classifier = get_classifier_for_skill(skill_id)
    ctx = ClassifierContext(project_root=PROJECT_ROOT, skill_id=skill_id)
    result = classifier.classify_examples(examples, ctx)
    return [dict(x) for x in result.examples_map_entries]


_ALLOWED_CHECKERS = {
    "interval_checker",
    "choice_label_checker",
    "text_checker",
    "numeric_checker",
    "ordered_pair_checker",
    "expression_equivalence_checker",
    "manual_review_checker",
}
_ALLOWED_EQUIVS = {
    "interval_set",
    "choice_label",
    "string_equivalence",
    "numeric_equivalence",
    "ordered_pair",
    "expression_equivalence",
    "manual_review_or_ai_judged",
}


def _to_answer_type_from_equivalence(eq: str) -> str:
    m = {
        "interval_set": "interval_set",
        "choice_label": "choice",
        "string_equivalence": "text",
        "numeric_equivalence": "numeric",
        "ordered_pair": "ordered_pair",
        "expression_equivalence": "expression",
        "manual_review_or_ai_judged": "manual_review",
    }
    return m.get(str(eq or "").strip(), "text")


def _camel_to_snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name or ""))
    s = re.sub(r"[^A-Za-z0-9_]+", "_", s)
    return s.strip("_").lower()


def _skill_default_problem_type_id(skill_id: str) -> str:
    tail = str(skill_id or "").split("_")[-1]
    base = _camel_to_snake(tail) or "skill"
    return f"{base}_default"


def _sources_complete_for_default(examples: list[dict[str, Any]]) -> bool:
    if not examples:
        return False
    for ex in examples:
        txt = _source_text(ex)
        if not txt.strip():
            return False
        bad = ["缺圖", "缺選項", "圖片遺失", "unreadable", "missing image"]
        if any(b in txt for b in bad):
            return False
    return True


def _infer_default_contract(examples: list[dict[str, Any]]) -> tuple[str, str]:
    texts = " ".join(_source_text(x) for x in examples)
    if any(tok in texts for tok in ["(A)", "(B)", "(C)", "(D)", "（A）", "（B）", "（C）", "（D）"]):
        return "choice_label_checker", "choice_label"
    return "text_checker", "string_equivalence"


def _source_text(ex: dict[str, Any]) -> str:
    for k in ("problem_text", "problem", "question", "stem", "content", "title"):
        v = str(ex.get(k, "")).strip()
        if v:
            return v
    return ""


def _json_from_text(raw: str) -> dict[str, Any]:
    s = str(raw or "").strip()
    if not s:
        return {}
    try:
        parsed = json.loads(s)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    a = s.find("{")
    b = s.rfind("}")
    if a >= 0 and b > a:
        try:
            parsed = json.loads(s[a : b + 1])
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _fallback_ai_explanation(result: dict[str, Any], error: str = "") -> dict[str, Any]:
    return {
        "enabled": True,
        "status": "failed",
        "summary": "AI 解讀失敗，請查看下方原始 Phase log。",
        "error": str(error or ""),
        "severity": "warning",
        "what_happened": "",
        "main_reason": "",
        "next_action": "請查看原始 Phase log 與 reports。",
        "items_to_check": [],
        "can_continue": bool(result.get("can_continue", False)),
        "confidence": "low",
    }


def _build_gencode_ai_explanation_payload(result: dict[str, Any]) -> dict[str, Any]:
    phase = str(result.get("phase", "")).strip()
    payload = {
        "skill_id": result.get("skill_id"),
        "skill_ch_name": result.get("skill_ch_name"),
        "skill_en_name": result.get("skill_en_name"),
        "phase": phase,
        "phase_status": result.get("phase_status"),
        "summary_message": result.get("summary_message"),
        "requires_human_action": result.get("requires_human_action"),
        "can_continue": result.get("can_continue"),
        "classifier_source": result.get("classifier_source"),
        "ai_bootstrap_used": result.get("ai_bootstrap_used"),
        "ai_bootstrap_status": result.get("ai_bootstrap_status"),
        "exception_review_gate": result.get("exception_review_gate"),
        "runtime_ready_gate": result.get("runtime_ready_gate"),
        "generator_draft_gate": result.get("generator_draft_gate"),
        "candidate_problem_types": result.get("candidate_problem_types"),
        "human_review_items": result.get("human_review_items"),
        "generator_results": result.get("generator_results"),
        "publish_check": result.get("publish_check"),
        "package_status": result.get("package_status"),
        "py_compile_status": result.get("py_compile_status"),
        "runtime_smoke_status": result.get("runtime_smoke_status"),
        "reports": result.get("reports"),
        "error": result.get("error"),
    }
    if phase == "phase1":
        payload["runtime_ready_gate"] = {}
        payload["generator_results"] = []
        payload["publish_check"] = {}
        payload["package_status"] = ""
        payload["py_compile_status"] = ""
        payload["runtime_smoke_status"] = ""
    return payload


def explain_gencode_result_with_ai(result: dict[str, Any]) -> dict[str, Any]:
    try:
        structured = _build_gencode_ai_explanation_payload(result)
        phase = str(result.get("phase", "")).strip().lower()
        phase_rule = (
            "If phase is phase1, focus only on classifier/rule-pack/bootstrap/classification quality/manual review; "
            "do not mention runtime_smoke_failed, dynamic_sampling_failed, contract_tests_failed unless they explicitly exist in phase1 context."
            if phase == "phase1"
            else "Use current phase context only; do not speculate across phases."
        )
        prompt = (
            "你是 Gencode Phase 結果解讀助手。只能解讀，不可改動 gate 決策。\n"
            "請只輸出 JSON，不要 Markdown。\n"
            "必填欄位: severity(success|warning|blocked|failed), short_title, summary, what_happened(list), main_reason, next_action, items_to_check(list), can_continue_phase2(boolean), can_publish(boolean), user_friendly_message, confidence(high|medium|low)\n"
            "規則:\n"
            "- 不可宣稱通過，除非 phase_status / blockers 支援。\n"
            "- 不可建議發布，除非 can_publish_formal=true。\n"
            "- 必須引用輸入 JSON，資訊不足時要明確說需要查看 reports。\n"
            "- 語氣精簡、可操作。\n"
            f"- {phase_rule}\n"
            "輸入 JSON:\n"
            + json.dumps(structured, ensure_ascii=False)
        )
        client, client_meta = _resolve_gencode_ai_client(["architect", "tutor", "default"])
        if client is None:
            return _fallback_ai_explanation(result, client_meta.get("failure_reason", "AI client unavailable or API key missing"))
        resp = call_ai_with_retry(client, prompt, max_retries=2, retry_delay=2, timeout=90)
        parsed = _json_from_text(getattr(resp, "text", ""))
        if not parsed:
            return _fallback_ai_explanation(result, "ai_empty_or_invalid_json")
        sev = str(parsed.get("severity", "")).strip().lower()
        if sev not in {"success", "warning", "blocked", "failed"}:
            phase_status = str(result.get("phase_status", "")).lower()
            if "failed" in phase_status:
                sev = "failed"
            elif "blocked" in phase_status or bool(result.get("requires_human_action")):
                sev = "blocked"
            elif "warning" in phase_status:
                sev = "warning"
            else:
                sev = "success"
        return {
            "enabled": True,
            "status": "success",
            "severity": sev,
            "short_title": str(parsed.get("short_title", "")).strip(),
            "summary": str(parsed.get("summary", "")).strip(),
            "what_happened": parsed.get("what_happened", []) if isinstance(parsed.get("what_happened"), list) else [],
            "main_reason": str(parsed.get("main_reason", "")).strip(),
            "next_action": str(parsed.get("next_action", "")).strip(),
            "items_to_check": parsed.get("items_to_check", []) if isinstance(parsed.get("items_to_check"), list) else [],
            "can_continue_phase2": bool(parsed.get("can_continue_phase2", False)),
            "can_publish": bool(parsed.get("can_publish", False)),
            "user_friendly_message": str(parsed.get("user_friendly_message", "")).strip(),
            "confidence": str(parsed.get("confidence", "medium")).strip().lower() or "medium",
        }
    except Exception as ex:
        return _fallback_ai_explanation(result, str(ex))


def _is_unrelated_problem_type(pt: str, source_texts: list[str]) -> bool:
    p = str(pt or "").strip().lower()
    if not p:
        return True
    if p.startswith("absolute_value_inequality_"):
        corpus = " ".join(source_texts).lower()
        if ("|" not in corpus) and ("絕對值" not in corpus) and ("absolute value" not in corpus):
            return True
    return False


def _is_bad_problem_type_style(skill_id: str, pt: str) -> bool:
    p = str(pt or "").strip().lower()
    sid = re.sub(r"[^a-z0-9_]", "_", str(skill_id or "").strip().lower())
    if not p:
        return True
    if sid and sid in p:
        return True
    if re.search(r"^vh_+b\d+_", p):
        return True
    return False


def _build_neutral_fallback(
    *,
    skill_id: str,
    examples: list[dict[str, Any]],
    reason: str,
    problem_type_id: str = "classifier_missing_source_review",
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    proposed_example_map: list[dict[str, Any]] = []
    for i, ex in enumerate(examples):
        exid = ex.get("id")
        text = _source_text(ex)
        row = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": text[:200],
            "skill_id": skill_id,
            "subskill_id": problem_type_id,
            "problem_type_id": problem_type_id,
            "runtime_category": "manual_review",
            "classification_rule_id": "phase1.neutral_fallback",
            "classification_reason": reason,
            "classifier_confidence": "low",
            "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
            "semantic_audit_status": "review_required",
            "generator_status": "manual_review",
            "manual_review_reason": reason,
        }
        entries.append(row)
        proposed_example_map.append({"example_id": exid, "proposed_problem_type_id": problem_type_id, "source_index": i + 1})
    proposal = {
        "proposed_problem_types": [problem_type_id],
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": {
            problem_type_id: {
                "answer_type": "manual_review",
                "equivalence_type": "manual_review_or_ai_judged",
                "checker_key": "manual_review_checker",
            }
        },
        "risk_flags": ["classifier_missing_or_ai_bootstrap_failed"],
    }
    meta = {
        "classifier_source": "neutral_fallback",
        "ai_bootstrap_used": True,
        "ai_bootstrap_status": "failed",
        "ai_bootstrap_error": reason,
        "ai_bootstrap_raw_response_preview": "",
        "ai_bootstrap_validation_errors": [],
        "ai_bootstrap_prompt_version": "gencode_phase1_ai_bootstrap_v2",
        "ai_bootstrap_model": "",
        "ai_bootstrap_provider": "",
        "ai_bootstrap_config_source": "",
        "ai_bootstrap_confidence_summary": {"count": len(examples), "avg": 0.0, "low_confidence_count": len(examples)},
        "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
    }
    return entries, proposal, meta


def _run_ai_classifier_bootstrap(
    *,
    skill_id: str,
    skill_ch_name: str,
    examples: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    prompt_version = "gencode_phase1_ai_bootstrap_v2"
    client, client_meta = _resolve_gencode_ai_client(["architect", "tutor", "default"])
    if client is None:
        raise RuntimeError(client_meta.get("failure_reason", "AI client unavailable or API key missing") or "AI client unavailable or API key missing")
    provider = str(client_meta.get("provider", ""))
    model_name = str(client_meta.get("model", "") or getattr(client, "model_name", "") or getattr(client, "model", "") or "")
    source_items = []
    for i, ex in enumerate(examples, start=1):
        source_items.append(
            {
                "source_index": i,
                "example_id": ex.get("id"),
                "source_type": ex.get("source_type"),
                "title": ex.get("title"),
                "question_text": _source_text(ex),
                "answer": ex.get("answer"),
                "explanation": ex.get("explanation"),
                "image_hint": ex.get("image_path") or ex.get("image_url") or ex.get("figure_hint"),
            }
        )
    prompt = (
        "You are a math problem-type classifier bootstrapper.\n"
        "Return JSON only.\n"
        "Skill context:\n"
        + json.dumps({"skill_id": skill_id, "skill_ch_name": skill_ch_name, "skill_en_name": ""}, ensure_ascii=False)
        + "\nSource examples:\n"
        + json.dumps(source_items, ensure_ascii=False)
        + "\nOutput schema keys: skill_id, skill_ch_name, classifier_source, problem_types, source_classifications, manual_review_items.\n"
        "Rules:\n"
        "- infer skill-related problem types from skill_id, skill_ch_name and question text.\n"
        "- avoid unrelated problem types.\n"
        "- You do not need to split every skill into multiple problem_types.\n"
        "- If source examples are few and structurally similar, merge into one primary problem_type.\n"
        "- A single good problem_type is acceptable.\n"
        "- Split only when checker/equivalence/answer contract differs.\n"
        "- Do not over-segment small skills.\n"
        "- do not output only generic unclassified_source_review unless sources are truly unreadable.\n"
        "- when possible, propose semantic problem_type candidates; one primary type is allowed.\n"
        "- problem_type_id must be semantic snake_case; do NOT sanitize the full skill_id into problem_type_id.\n"
        "- for Cartesian coordinate skills, prefer semantic types such as cartesian_coordinate_point_reading / cartesian_coordinate_quadrant_identification / cartesian_coordinate_axis_origin_concept / cartesian_coordinate_point_plotting / cartesian_coordinate_from_description when supported by source text.\n"
        "- problem_type_id must be snake_case and skill-related.\n"
        "- checker in: interval_checker, choice_label_checker, text_checker, numeric_checker, ordered_pair_checker, expression_equivalence_checker, manual_review_checker.\n"
        "- equivalence in: interval_set, choice_label, string_equivalence, numeric_equivalence, ordered_pair, expression_equivalence, manual_review_or_ai_judged.\n"
        "- if checker/equivalence is manual review, requires_human_action=true (only for drawing/graph/missing-image/unreadable sources).\n"
        "- if deterministic checker is possible, set requires_human_action=false.\n"
        "- every source_index must appear in source_classifications.\n"
        "- confidence is 0..1.\n"
    )
    resp = call_ai_with_retry(client, prompt, max_retries=2, retry_delay=2, timeout=120)
    raw_text = str(getattr(resp, "text", "") or "")
    raw_preview = raw_text[:1000]
    parsed = _json_from_text(raw_text)
    if not parsed:
        raise RuntimeError(f"ai_bootstrap_invalid_json::{raw_preview[:200]}")

    source_map = {i: ex for i, ex in enumerate(examples, start=1)}
    source_texts = [_source_text(ex) for ex in examples]
    ai_problem_types = parsed.get("problem_types") if isinstance(parsed.get("problem_types"), list) else []
    ai_source_cls = parsed.get("source_classifications") if isinstance(parsed.get("source_classifications"), list) else []
    by_index: dict[int, dict[str, Any]] = {}
    contracts: dict[str, dict[str, Any]] = {}
    risk_flags: list[str] = []
    confs: list[float] = []

    validation_errors: list[str] = []
    unclassified_count = 0
    for row in ai_source_cls:
        if not isinstance(row, dict):
            continue
        try:
            idx = int(row.get("source_index"))
        except Exception:
            continue
        if idx not in source_map:
            continue
        pt = str(row.get("matched_problem_type_id", "")).strip()
        checker = str(row.get("checker", "")).strip()
        eq = str(row.get("equivalence", "")).strip()
        needs_human = bool(row.get("requires_human_action", False))
        conf = float(row.get("confidence", 0.0) or 0.0)
        confs.append(conf)
        invalid = (
            (not re.fullmatch(r"[a-z][a-z0-9_]*", pt))
            or checker not in _ALLOWED_CHECKERS
            or eq not in _ALLOWED_EQUIVS
            or _is_unrelated_problem_type(pt, source_texts)
            or _is_bad_problem_type_style(skill_id, pt)
        )
        if not re.fullmatch(r"[a-z][a-z0-9_]*", pt):
            validation_errors.append(f"source_index={idx}: invalid_problem_type_id={pt}")
        if checker not in _ALLOWED_CHECKERS:
            validation_errors.append(f"source_index={idx}: invalid_checker={checker}")
        if eq not in _ALLOWED_EQUIVS:
            validation_errors.append(f"source_index={idx}: invalid_equivalence={eq}")
        if _is_unrelated_problem_type(pt, source_texts):
            validation_errors.append(f"source_index={idx}: unrelated_problem_type={pt}")
        if _is_bad_problem_type_style(skill_id, pt):
            validation_errors.append(f"source_index={idx}: invalid_problem_type_id_style={pt}")
        if invalid or conf < 0.6:
            pt = "unclassified_source_review"
            checker = "manual_review_checker"
            eq = "manual_review_or_ai_judged"
            needs_human = True
            risk_flags.append("ai_bootstrap_low_confidence_or_invalid")
        if checker == "manual_review_checker" or eq == "manual_review_or_ai_judged":
            needs_human = True
        if pt.endswith("unclassified_source_review"):
            unclassified_count += 1
        ex = source_map[idx]
        exid = ex.get("id")
        by_index[idx] = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": _source_text(ex)[:200],
            "skill_id": skill_id,
            "subskill_id": pt,
            "problem_type_id": pt,
            "runtime_category": "manual_review" if needs_human else "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression",
            "classification_rule_id": "phase1.ai_bootstrap",
            "classification_reason": str(row.get("review_reason", "")).strip() or "ai_bootstrap_classification",
            "classifier_confidence": "high" if conf >= 0.8 else "medium" if conf >= 0.6 else "low",
            "semantic_risk_flags": ["ai_bootstrap"],
            "semantic_audit_status": "review_required" if needs_human else "ok",
            "generator_status": "manual_review" if needs_human else "ready_for_draft",
            "manual_review_reason": str(row.get("review_reason", "")).strip() if needs_human else "",
        }
        contracts[pt] = {
            "answer_type": _to_answer_type_from_equivalence(eq),
            "equivalence_type": eq,
            "checker_key": checker,
        }

    # fill uncovered sources into neutral manual review
    for idx, ex in source_map.items():
        if idx in by_index:
            continue
        pt = "unclassified_source_review"
        exid = ex.get("id")
        by_index[idx] = {
            "example_id": exid,
            "title": str(ex.get("title", "")).strip(),
            "source_type": str(ex.get("source_type", "")).strip() or "textbook_example",
            "problem_preview": _source_text(ex)[:200],
            "skill_id": skill_id,
            "subskill_id": pt,
            "problem_type_id": pt,
            "runtime_category": "manual_review",
            "classification_rule_id": "phase1.ai_bootstrap_uncovered",
            "classification_reason": "ai_bootstrap_missing_source_coverage",
            "classifier_confidence": "low",
            "semantic_risk_flags": ["ai_bootstrap_missing_source_coverage"],
            "semantic_audit_status": "review_required",
            "generator_status": "manual_review",
            "manual_review_reason": "ai_bootstrap_missing_source_coverage",
        }
        contracts[pt] = {
            "answer_type": "manual_review",
            "equivalence_type": "manual_review_or_ai_judged",
            "checker_key": "manual_review_checker",
        }
        risk_flags.append("ai_bootstrap_missing_source_coverage")
        validation_errors.append(f"source_index={idx}: missing_source_classification")
        unclassified_count += 1

    # Global merge policy: small source set + same deterministic checker/equivalence -> allow one primary problem_type.
    pre_entries = [by_index[i] for i in sorted(by_index.keys())]
    if len(pre_entries) <= 5:
        det_rows = [x for x in pre_entries if str(x.get("runtime_category", "")).strip() != "manual_review"]
        if det_rows:
            det_pts = [str(x.get("problem_type_id", "")).strip() for x in det_rows if str(x.get("problem_type_id", "")).strip()]
            pt_counts: dict[str, int] = {}
            for p in det_pts:
                pt_counts[p] = pt_counts.get(p, 0) + 1
            primary_pt = sorted(pt_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if pt_counts else ""
            if primary_pt:
                primary_contract = contracts.get(primary_pt, {}) if isinstance(contracts.get(primary_pt), dict) else {}
                same_contract = True
                for r in det_rows:
                    c = contracts.get(str(r.get("problem_type_id", "")).strip(), {})
                    if not isinstance(c, dict):
                        same_contract = False
                        break
                    if str(c.get("checker_key", "")).strip() != str(primary_contract.get("checker_key", "")).strip():
                        same_contract = False
                        break
                    if str(c.get("equivalence_type", "")).strip() != str(primary_contract.get("equivalence_type", "")).strip():
                        same_contract = False
                        break
                if same_contract:
                    for r in det_rows:
                        r["problem_type_id"] = primary_pt
                        r["subskill_id"] = primary_pt

    entries = [by_index[i] for i in sorted(by_index.keys())]
    proposed_example_map = [{"example_id": e.get("example_id"), "proposed_problem_type_id": e.get("problem_type_id")} for e in entries]
    proposal = {
        "proposed_problem_types": sorted({str(e.get("problem_type_id", "")).strip() for e in entries if str(e.get("problem_type_id", "")).strip()}),
        "proposed_example_map": proposed_example_map,
        "proposed_answer_contracts": contracts,
        "risk_flags": sorted(set(risk_flags)),
    }
    low_count = sum(1 for x in confs if x < 0.6)
    avg = (sum(confs) / len(confs)) if confs else 0.0
    ai_status = "success"
    classifier_source = "ai_bootstrap"
    if entries and unclassified_count >= len(entries):
        if _sources_complete_for_default(examples):
            default_pt = _skill_default_problem_type_id(skill_id)
            checker, eq = _infer_default_contract(examples)
            for e in entries:
                e["problem_type_id"] = default_pt
                e["subskill_id"] = default_pt
                e["runtime_category"] = "deterministic_choice" if checker == "choice_label_checker" else "deterministic_expression"
                e["classification_reason"] = "ai_bootstrap_default_fallback_for_complete_sources"
                e["generator_status"] = "ready_for_draft"
                e["semantic_audit_status"] = "ok"
                e["manual_review_reason"] = ""
            contracts = {
                default_pt: {
                    "answer_type": _to_answer_type_from_equivalence(eq),
                    "equivalence_type": eq,
                    "checker_key": checker,
                    "is_default_problem_type": True,
                }
            }
            validation_errors.append("ai_bootstrap_all_unclassified_promoted_to_default_problem_type")
            classifier_source = "ai_bootstrap_with_default_fallback"
            ai_status = "success"
        else:
            validation_errors.append("ai_bootstrap_low_quality_all_unclassified")
            ai_status = "low_quality"
            classifier_source = "ai_bootstrap_low_quality"
    meta = {
        "classifier_source": classifier_source,
        "ai_bootstrap_used": True,
        "ai_bootstrap_status": ai_status,
        "ai_bootstrap_error": "",
        "ai_bootstrap_raw_response_preview": raw_preview,
        "ai_bootstrap_validation_errors": validation_errors,
        "ai_bootstrap_prompt_version": prompt_version,
        "ai_bootstrap_model": model_name,
        "ai_bootstrap_provider": provider,
        "ai_bootstrap_config_source": str(client_meta.get("source", "")),
        "ai_bootstrap_confidence_summary": {"count": len(confs), "avg": round(avg, 3), "low_confidence_count": low_count},
        "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
        "ai_bootstrap_raw_problem_types": ai_problem_types,
        "default_problem_type_used": classifier_source == "ai_bootstrap_with_default_fallback",
    }
    return entries, proposal, meta


def _question_preview(text: Any, limit: int = 110) -> str:
    s = str(text or "")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= limit:
        return s
    return s[:limit].rstrip() + "..."


def _pick_skill_ch_name(skill_id: str, examples: list[dict[str, Any]]) -> str:
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        for key in ("skill_ch_name", "skill_name_ch", "skill_name", "skill_title"):
            v = str(ex.get(key, "")).strip()
            if v:
                return v
    return skill_id


def _build_human_review_items(
    *,
    skill_id: str,
    skill_ch_name: str,
    entries: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    candidate_problem_types: list[dict[str, Any]],
    exception_review_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    if not bool((exception_review_gate or {}).get("required")):
        return []
    by_example_id: dict[int, dict[str, Any]] = {}
    for ex in examples:
        exid = ex.get("id")
        if isinstance(exid, int):
            by_example_id[exid] = ex
    contract_by_pt: dict[str, dict[str, str]] = {}
    for c in candidate_problem_types:
        if not isinstance(c, dict):
            continue
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        contract_by_pt[pt] = {
            "checker": str(c.get("checker_key_proposal", "")).strip(),
            "equivalence": str(c.get("equivalence_type_proposal", "")).strip(),
        }
    items: list[dict[str, Any]] = []
    for idx, row in enumerate(entries):
        if not isinstance(row, dict):
            continue
        pt = str(row.get("problem_type_id", "")).strip()
        runtime_category = str(row.get("runtime_category", "")).strip()
        eq = contract_by_pt.get(pt, {}).get("equivalence", "")
        needs_review = (
            runtime_category == "manual_review"
            or pt.endswith("_malformed_source_review")
            or eq == "manual_review_or_ai_judged"
        )
        if not needs_review:
            continue
        exid = row.get("example_id")
        ex = by_example_id.get(exid, {}) if isinstance(exid, int) else {}
        source_type = str(row.get("source_type", "")).strip() or str(ex.get("source_type", "")).strip() or "unknown"
        title = (
            str(row.get("title", "")).strip()
            or str(ex.get("title", "")).strip()
            or str(ex.get("source_label", "")).strip()
            or str(ex.get("example_name", "")).strip()
            or (f"{source_type}#{exid}" if exid else source_type)
        )
        raw_reason = (
            str(row.get("manual_review_reason", "")).strip()
            or str(row.get("classification_reason", "")).strip()
            or ",".join(str(x) for x in (row.get("semantic_risk_flags") or []) if str(x).strip())
            or "requires manual review"
        )
        question_text = row.get("problem_preview") or ex.get("problem_text") or ex.get("problem") or ex.get("question") or ex.get("stem") or ex.get("content") or row.get("title") or ""
        items.append(
            {
                "source_index": idx,
                "display_source_index": idx + 1,
                "example_id": exid if isinstance(exid, int) else None,
                "textbook_example_id": exid if isinstance(exid, int) else None,
                "source_type": source_type,
                "title": title,
                "skill_id": skill_id,
                "skill_ch_name": skill_ch_name,
                "matched_problem_type_id": pt,
                "checker": contract_by_pt.get(pt, {}).get("checker", ""),
                "equivalence": eq,
                "reason": raw_reason,
                "review_reason": raw_reason,
                "question_preview": _question_preview(question_text, limit=110),
            }
        )
    return items


def _write_phase1_summary_md(path: Path, skill_id: str, payload: dict[str, Any]) -> None:
    lines = [f"# Gencode Phase1 Summary: {skill_id}", "", "## phase1", "```json", json.dumps(payload, ensure_ascii=False, indent=2), "```", ""]
    items = payload.get("human_review_items") if isinstance(payload.get("human_review_items"), list) else []
    if items:
        lines.extend(
            [
                "## human_review_items",
                "",
                "| source_index | title | example_id | source_type | matched_problem_type_id | checker | equivalence | reason | question_preview |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in items:
            def _md_cell(v: Any) -> str:
                return str(v if v is not None else "").replace("|", "\\|").replace("\n", " ").strip()
            lines.append(
                "| {source_index} | {title} | {example_id} | {source_type} | {matched_problem_type_id} | {checker} | {equivalence} | {reason} | {question_preview} |".format(
                    source_index=_md_cell(item.get("display_source_index", item.get("source_index", ""))),
                    title=_md_cell(item.get("title", "")),
                    example_id=_md_cell(item.get("example_id", "")),
                    source_type=_md_cell(item.get("source_type", "")),
                    matched_problem_type_id=_md_cell(item.get("matched_problem_type_id", "")),
                    checker=_md_cell(item.get("checker", "")),
                    equivalence=_md_cell(item.get("equivalence", "")),
                    reason=_md_cell(item.get("review_reason", item.get("reason", ""))),
                    question_preview=_md_cell(item.get("question_preview", "")),
                )
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _build_auto_review(skill_id: str, entries: list[dict[str, Any]], proposal: dict[str, Any]) -> dict[str, Any]:
    proposed_by_id = {
        int(x.get("example_id")): str(x.get("proposed_problem_type_id", "")).strip()
        for x in (proposal.get("proposed_example_map") or [])
        if isinstance(x, dict) and isinstance(x.get("example_id"), int)
    }
    contracts = proposal.get("proposed_answer_contracts", {}) if isinstance(proposal.get("proposed_answer_contracts"), dict) else {}
    per_example: list[dict[str, Any]] = []
    groups: dict[str, list[int]] = defaultdict(list)
    runtime_contract_defaults = {
        "deterministic_expression": {"answer_type": "expression", "equivalence_type": "exact_string", "checker_key": "exact_string_checker"},
        "deterministic_choice": {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"},
        "deterministic_numeric": {"answer_type": "numeric", "equivalence_type": "numeric_exact", "checker_key": "integer_checker"},
        "manual_review": {"answer_type": "manual_review", "equivalence_type": "manual_review_or_ai_judged", "checker_key": "manual_review_checker"},
    }
    for e in entries:
        exid = e.get("example_id")
        if not isinstance(exid, int):
            continue
        pt = str(e.get("problem_type_id", "")).strip()
        if pt in {"", "unknown"}:
            pt = proposed_by_id.get(exid, "unknown")
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        if not c:
            c = runtime_contract_defaults.get(str(e.get("runtime_category", "")).strip(), {})
        answer_shape = detect_answer_shape(c)
        per_example.append(
            {
                "example_id": exid,
                "detected_problem_type_id": pt,
                "answer_shape": answer_shape,
                "classification_confidence": "medium" if pt not in {"", "unknown"} else "low",
                "classification_reason": "classifier_or_proposal_mapping",
                "risk_flags": e.get("semantic_risk_flags") if isinstance(e.get("semantic_risk_flags"), list) else [],
                "title_or_source_label": str(e.get("title", "")).strip() or str(e.get("source_type", "")).strip(),
            }
        )
        if pt not in {"", "unknown"}:
            if pt not in contracts and c:
                contracts[pt] = c
            groups[pt].append(exid)

    unknown_ids = sorted(x["example_id"] for x in per_example if x["detected_problem_type_id"] in {"", "unknown"})
    candidates: list[dict[str, Any]] = []
    all_ids = sorted(x["example_id"] for x in per_example)
    for pt, ids_raw in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        ids = sorted(set(ids_raw))
        c = contracts.get(pt, {}) if isinstance(contracts.get(pt), dict) else {}
        answer_shape = detect_answer_shape(c)
        rec = "recommend_promote_for_that_candidate" if len(ids) >= 3 and answer_shape != "unknown_answer_shape" else "conservative_hold_for_that_candidate"
        blockers = [] if rec.startswith("recommend_") else ["insufficient_examples_for_safe_promote"]
        candidates.append(
            {
                "problem_type_id": pt,
                "proposed_problem_type_id": pt,
                "matched_example_ids": ids,
                "matched_example_count": len(ids),
                "unmatched_example_ids": [x for x in all_ids if x not in ids],
                "representative_example_id": ids[0] if ids else None,
                "structural_features": sorted({x["answer_shape"] for x in per_example if x["detected_problem_type_id"] == pt}),
                "answer_contract_proposal": c,
                "checker_key_proposal": str(c.get("checker_key", "")),
                "equivalence_type_proposal": str(c.get("equivalence_type", "")),
                "answer_shape": answer_shape,
                "confidence": "high" if len(ids) >= 3 else "medium",
                "promote_recommendation": rec,
                "promote_blockers": blockers,
                "risk_flags": [],
            }
        )

    shape_set = {x.get("answer_shape", "") for x in candidates if x.get("answer_shape", "")}
    if not candidates and unknown_ids:
        split_merge = "hold_unknown_examples_only"
    elif len(candidates) == 1:
        split_merge = "recommend_single_type"
    elif len(shape_set) >= 2:
        split_merge = "recommend_split_problem_types"
    else:
        split_merge = "recommend_split_or_refine"

    gates = evaluate_pipeline_gates(
        candidates,
        source_examples_count=len(entries),
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        contract_tests_passed=False,
    )
    ex_gate = gates.get("exception_review_gate", {}) if isinstance(gates.get("exception_review_gate"), dict) else {}
    ex_reasons = ex_gate.get("reasons", []) if isinstance(ex_gate.get("reasons"), list) else []
    ex_reasons = [r for r in ex_reasons if str(r) not in {"runtime_smoke_failed", "dynamic_sampling_failed", "contract_tests_failed"}]
    ex_gate["reasons"] = ex_reasons
    ex_gate["required"] = bool(ex_reasons)
    gates["exception_review_gate"] = ex_gate
    per_candidate_promote_gate = [
        {
            "problem_type_id": str(x.get("problem_type_id", "")),
            "promote_recommendation": str(x.get("promote_recommendation", "")),
            "promote_blockers": x.get("promote_blockers", []),
        }
        for x in candidates
    ]
    next_action = "review_classifier_proposal_and_decide_split_merge"
    if split_merge == "recommend_split_problem_types":
        next_action = "prepare_split_problem_types_then_promote_candidates"
    elif split_merge == "recommend_single_type":
        next_action = "ready_for_safe_promote"

    return {
        "skill_id": skill_id,
        "candidate_problem_types": candidates,
        "proposal_items": candidates,
        "per_example_classification": per_example,
        "split_or_merge_recommendation": split_merge,
        "per_candidate_promote_gate": per_candidate_promote_gate,
        "next_action": next_action,
        **gates,
    }


def _normalize_phase_response(payload: dict[str, Any]) -> dict[str, Any]:
    phase = str(payload.get("phase", "")).strip()
    ok = bool(payload.get("ok", False))
    human_items: list[dict[str, Any]] = []

    if phase == "phase1":
        source_count = int(payload.get("source_example_count", 0))
        cands = payload.get("candidate_problem_types", []) if isinstance(payload.get("candidate_problem_types"), list) else []
        ex_gate = payload.get("exception_review_gate", {}) if isinstance(payload.get("exception_review_gate"), dict) else {}
        reasons = ex_gate.get("reasons", []) if isinstance(ex_gate.get("reasons"), list) else []
        if source_count <= 0:
            phase_status = "phase1_blocked_no_source"
        elif any("fatal" in str(x).lower() for x in reasons):
            phase_status = "phase1_blocked_fatal_risk"
        elif ex_gate.get("required"):
            phase_status = "phase1_exception_review_required"
        elif payload.get("risk_examples"):
            phase_status = "phase1_completed_with_warning"
        else:
            phase_status = "phase1_completed"
        for exid in payload.get("unclassified_examples", []) or []:
            human_items.append(
                {
                    "type": "unclassified_example",
                    "target_id": str(exid),
                    "message": f"unclassified example: {exid}",
                    "suggested_action": "edit_classification",
                }
            )
        for r in reasons:
            human_items.append(
                {
                    "type": "fatal_risk" if "fatal" in str(r).lower() else "inspect_report",
                    "target_id": str(r),
                    "message": f"Phase 1 exception reason: {r}",
                    "suggested_action": "inspect_report",
                }
            )
        for item in payload.get("human_review_items", []) or []:
            if not isinstance(item, dict):
                continue
            human_items.append(
                {
                    "type": "phase1_source_review_required",
                    "target_id": str(item.get("example_id") or item.get("display_source_index") or ""),
                    "message": f"#{item.get('display_source_index', item.get('source_index', ''))} {item.get('matched_problem_type_id', '')}: {item.get('review_reason', item.get('reason', ''))}",
                    "suggested_action": "inspect_report",
                }
            )
        classifier_source = str(payload.get("classifier_source", "rule_pack"))
        if classifier_source == "ai_bootstrap":
            payload["summary_message"] = "未找到既有 rule pack，已使用 AI classifier bootstrap 產生題型分類草案。"
        elif classifier_source == "ai_bootstrap_with_default_fallback":
            payload["summary_message"] = "AI 未細分題型，但來源題完整且同屬此 skill；已建立單一 default problem_type，可進入 Phase 2。"
        elif classifier_source == "ai_bootstrap_low_quality":
            payload["summary_message"] = "AI classifier bootstrap 有回覆，但未能產生可用題型分類；目前仍需人工審查。"
        elif classifier_source == "neutral_fallback":
            payload["summary_message"] = "AI classifier bootstrap 失敗，已轉入人工審查。"
        else:
            payload["summary_message"] = (
                f"Phase 1 completed: {len(cands)} candidate problem types, {source_count} source examples."
                if phase_status.startswith("phase1_completed")
                else ("Phase 1 blocked: no source examples." if phase_status == "phase1_blocked_no_source" else "Phase 1 requires exception review.")
            )
        can_continue = phase_status in {"phase1_completed", "phase1_completed_with_warning", "phase1_exception_review_required"}
        can_retry = True

    elif phase == "phase2":
        results = payload.get("generator_results", []) if isinstance(payload.get("generator_results"), list) else []
        accepted = payload.get("accepted_generators", []) if isinstance(payload.get("accepted_generators"), list) else []
        failed = payload.get("failed_generators", []) if isinstance(payload.get("failed_generators"), list) else []
        accepted_statuses = {"runtime_ready", "limited_runtime_ready", "runtime_ready_with_warning"}
        has_warnings = any((x.get("warnings") or []) for x in results if isinstance(x, dict))
        has_blocking_states = any(
            str(x.get("generator_status", "")).strip() in {"blocked", "draft_planned", "validation_failed", "draft_failed"}
            or str(x.get("checker_smoke_status", "")).strip() != "passed"
            or str(x.get("dynamic_sampling_status", "")).strip() != "passed"
            or bool(x.get("blockers"))
            or bool(x.get("requires_human_action"))
            for x in results
            if isinstance(x, dict)
        )
        all_phase3_ready = bool(results) and all(
            str(x.get("generator_status", "")).strip() in accepted_statuses
            and str(x.get("checker_smoke_status", "")).strip() == "passed"
            and str(x.get("dynamic_sampling_status", "")).strip() == "passed"
            and not bool(x.get("blockers"))
            and not bool(x.get("requires_human_action"))
            for x in results
            if isinstance(x, dict)
        )
        if not results:
            phase_status = "phase2_blocked_no_candidates"
        elif results and len(failed) == len(results):
            phase_status = "phase2_blocked_all_generators_failed"
        elif has_warnings:
            phase_status = "phase2_completed_with_warning"
        else:
            phase_status = "phase2_completed"
        for row in results:
            if not isinstance(row, dict):
                continue
            for b in row.get("blockers", []) or []:
                human_items.append(
                    {
                        "type": "missing_checker" if "checker" in str(b).lower() else "inspect_report",
                        "target_id": str(row.get("problem_type_id", "")),
                        "message": f"{row.get('problem_type_id', '')}: {b}",
                        "suggested_action": "inspect_report",
                    }
                )
        if phase_status == "phase2_completed" and all_phase3_ready and not has_blocking_states:
            payload["summary_message"] = "Phase 2 completed: generators passed smoke/sampling and can continue to Phase 3."
        elif phase_status == "phase2_completed_with_warning" and all_phase3_ready and not has_blocking_states:
            payload["summary_message"] = "Phase 2 completed with warnings: generators passed smoke/sampling and can continue to Phase 3; some problem types keep low_source_examples warning."
        elif phase_status == "phase2_completed_with_warning":
            payload["summary_message"] = f"Phase 2 completed with warnings: {len(accepted)} generator drafts created, but some items are not yet ready to continue."
        elif phase_status == "phase2_completed":
            payload["summary_message"] = f"Phase 2 completed: {len(accepted)} generator drafts created."
        else:
            payload["summary_message"] = "Phase 2 blocked: no usable generator draft."
        can_continue = phase_status in {"phase2_completed", "phase2_completed_with_warning"}
        can_retry = True

    elif phase == "phase3":
        py_status = str(payload.get("py_compile_status", "")).strip()
        pkg = str(payload.get("package_status", "")).strip()
        if py_status == "failed":
            phase_status = "phase3_failed_compile"
        elif pkg == "packaged_draft":
            # no runtime-ready promotion in this round, always draft-level
            phase_status = "phase3_packaged_draft_with_warning"
        elif pkg:
            phase_status = "phase3_blocked_no_successful_generators"
        else:
            phase_status = "phase3_blocked_no_successful_generators"
        if py_status == "failed":
            human_items.append(
                {
                    "type": "compile_error",
                    "target_id": str(payload.get("skill_file_path", "")),
                    "message": str(payload.get("error", "draft skill py_compile failed")),
                    "suggested_action": "retry",
                }
            )
        payload["summary_message"] = (
            "Phase 3 completed: draft skill packaged and py_compile passed."
            if phase_status.startswith("phase3_packaged_draft")
            else "Phase 3 blocked: no usable generators for packaging."
        )
        can_continue = phase_status in {"phase3_packaged_draft", "phase3_packaged_draft_with_warning"}
        can_retry = True
    else:
        phase_status = "unknown_phase_status"
        can_continue = False
        can_retry = True
        payload.setdefault("summary_message", "Unknown phase status.")

    payload["phase_status"] = phase_status
    payload["can_continue"] = bool(can_continue)
    payload["can_retry"] = bool(can_retry)
    payload["requires_human_action"] = bool(human_items)
    payload["human_action_items"] = human_items
    payload["ok"] = bool(ok)
    payload.setdefault("reports", {})
    return payload


def run_gencode_phase1(skill_id: str, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    examples = _load_examples(skill_id)
    reports = {
        "phase1_summary_json": str(REPORT_DIR / f"{skill_id}_phase1_summary.json"),
        "phase1_summary_md": str(REPORT_DIR / f"{skill_id}_phase1_summary.md"),
    }
    if not examples:
        payload = {
            "ok": False,
            "phase": "phase1",
            "skill_id": skill_id,
            "source_example_count": 0,
            "candidate_problem_types": [],
            "per_example_classification": [],
            "unclassified_examples": [],
            "risk_examples": [],
            "split_or_merge_recommendation": "hold_unknown_examples_only",
            "classifier_gate": {"status": "classifier_blocked", "allowed": False, "warnings": []},
            "generator_draft_gate": {"status": "generator_draft_blocked", "allowed": False, "warnings": []},
            "runtime_ready_gate": {"status": "blocked_insufficient_examples", "allowed": False, "blockers": ["blocked_insufficient_examples"]},
            "exception_review_gate": {"required": True, "reasons": ["no_source_examples"]},
            "reports": reports,
            "next_action": "check_skill_mapping_or_source_import",
            "timestamp": utc_timestamp(),
            "dry_run": dry_run,
            "human_review_items": [],
        }
        write_json(Path(reports["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
        normalized = _normalize_phase_response(payload)
        normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
        return normalized

    classifier_source = "rule_pack"
    ai_bootstrap_used = False
    ai_bootstrap_status = "not_used"
    ai_bootstrap_confidence_summary: dict[str, Any] = {}
    inspect_report_note = ""
    meta: dict[str, Any] = {}
    registered_pack = _load_registered_classifier_rulepack(skill_id)
    if registered_pack:
        entries = _classify_examples_with_rulepack(skill_id=skill_id, examples=examples, pack=registered_pack)
    else:
        cls = get_classifier_for_skill(skill_id)
        ctx = ClassifierContext(project_root=PROJECT_ROOT, skill_id=skill_id)
        raw_result = cls.classify_examples(examples, ctx)
        entries = [dict(x) for x in raw_result.examples_map_entries]
        if isinstance(cls, FallbackClassifier):
            classifier_source = "ai_bootstrap"
            ai_bootstrap_used = True
            skill_ch_name = _pick_skill_ch_name(skill_id, examples)
            try:
                entries, proposal, meta = _run_ai_classifier_bootstrap(skill_id=skill_id, skill_ch_name=skill_ch_name, examples=examples)
            except Exception as ex:
                ex_msg = str(ex)
                entries, proposal, meta = _build_neutral_fallback(
                    skill_id=skill_id,
                    examples=examples,
                    reason=f"skill_specific_classifier_missing; ai_bootstrap_failed: {ex_msg}",
                )
                meta["ai_bootstrap_error"] = ex_msg
                if "api key missing" in ex_msg.lower() or "unavailable" in ex_msg.lower():
                    meta["ai_bootstrap_status"] = "unavailable"
                    meta["ai_bootstrap_error"] = "AI client unavailable or API key missing"
                if "ai_bootstrap_invalid_json::" in ex_msg:
                    preview = ex_msg.split("::", 1)[1].strip()
                    meta["ai_bootstrap_raw_response_preview"] = preview[:1000]
                    meta["ai_bootstrap_validation_errors"] = ["invalid_json_response"]
            classifier_source = str(meta.get("classifier_source", classifier_source))
            ai_bootstrap_status = str(meta.get("ai_bootstrap_status", "failed" if classifier_source == "neutral_fallback" else "success"))
            ai_bootstrap_confidence_summary = meta.get("ai_bootstrap_confidence_summary", {}) if isinstance(meta.get("ai_bootstrap_confidence_summary"), dict) else {}
            inspect_report_note = str(meta.get("inspect_report_note", "")).strip()
    if not isinstance(entries, list):
        entries = []
    if not entries and examples:
        fb_entries, fb_proposal, fb_meta = _build_neutral_fallback(
            skill_id=skill_id,
            examples=examples,
            reason="phase1_entries_empty_after_classification",
        )
        entries = fb_entries
        if not meta:
            meta = fb_meta
        inspect_report_note = (inspect_report_note + " " if inspect_report_note else "") + "entries fallback applied due to empty source classifications."
        if not str(meta.get("ai_bootstrap_error", "")).strip():
            meta["ai_bootstrap_error"] = "phase1_entries_empty_after_classification"
    proposal = {"proposed_problem_types": [], "proposed_example_map": [], "proposed_answer_contracts": {}, "risk_flags": []}
    if registered_pack:
        for e in entries:
            pt = str(e.get("problem_type_id", "")).strip()
            if not pt:
                continue
            proposal["proposed_problem_types"].append(pt)
            proposal["proposed_example_map"].append({"example_id": e.get("example_id"), "proposed_problem_type_id": pt})
            # infer contracts from runtime category
            if str(e.get("runtime_category", "")).strip() == "manual_review":
                proposal["proposed_answer_contracts"][pt] = {"answer_type": "manual_review", "equivalence_type": "manual_review_or_ai_judged", "checker_key": "manual_review_checker"}
            else:
                proposal["proposed_answer_contracts"][pt] = {"answer_type": "choice", "equivalence_type": "choice_label", "checker_key": "choice_label_checker"}
        proposal["proposed_problem_types"] = sorted(set(proposal["proposed_problem_types"]))
    elif not ai_bootstrap_used:
        unknown_ratio = sum(1 for e in entries if str(e.get("problem_type_id", "")).strip() in {"", "unknown"}) / max(len(entries), 1)
        if unknown_ratio >= 0.2:
            proposal = build_classifier_proposal(skill_id, entries)
    auto_review = _build_auto_review(skill_id, entries, proposal)
    per_example = auto_review.get("per_example_classification", [])
    unclassified = [x.get("example_id") for x in per_example if str(x.get("detected_problem_type_id", "")).strip() in {"", "unknown"}]
    risk_examples = [x.get("example_id") for x in per_example if x.get("risk_flags")]

    payload = {
        "ok": True,
        "phase": "phase1",
        "skill_id": skill_id,
        "source_example_count": len(examples),
        "candidate_problem_types": auto_review.get("candidate_problem_types", []),
        "per_example_classification": per_example,
        "source_classifications": per_example,
        "unclassified_examples": unclassified,
        "risk_examples": risk_examples,
        "split_or_merge_recommendation": auto_review.get("split_or_merge_recommendation", ""),
        "classifier_gate": auto_review.get("classifier_gate", {}),
        "generator_draft_gate": auto_review.get("generator_draft_gate", {}),
        "runtime_ready_gate": auto_review.get("runtime_ready_gate", {}),
        "exception_review_gate": auto_review.get("exception_review_gate", {}),
        "reports": reports,
        "next_action": auto_review.get("next_action", "review_classifier_proposal_and_decide_split_merge"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
        "auto_review_summary": auto_review,
        "classifier_source": classifier_source,
        "ai_bootstrap_used": ai_bootstrap_used,
        "ai_bootstrap_status": ai_bootstrap_status,
        "ai_bootstrap_confidence_summary": ai_bootstrap_confidence_summary,
        "inspect_report_note": inspect_report_note,
        "ai_bootstrap_error": str(meta.get("ai_bootstrap_error", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_raw_response_preview": str(meta.get("ai_bootstrap_raw_response_preview", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_validation_errors": meta.get("ai_bootstrap_validation_errors", []) if isinstance(meta, dict) and isinstance(meta.get("ai_bootstrap_validation_errors"), list) else [],
        "ai_bootstrap_prompt_version": str(meta.get("ai_bootstrap_prompt_version", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_model": str(meta.get("ai_bootstrap_model", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_provider": str(meta.get("ai_bootstrap_provider", "") if isinstance(meta, dict) else ""),
        "ai_bootstrap_config_source": str(meta.get("ai_bootstrap_config_source", "") if isinstance(meta, dict) else ""),
        "default_problem_type_used": bool(meta.get("default_problem_type_used", False) if isinstance(meta, dict) else False),
    }
    payload["human_review_items"] = _build_human_review_items(
        skill_id=skill_id,
        skill_ch_name=_pick_skill_ch_name(skill_id, examples),
        entries=entries,
        examples=examples,
        candidate_problem_types=payload.get("candidate_problem_types", []),
        exception_review_gate=payload.get("exception_review_gate", {}),
    )
    write_json(Path(reports["phase1_summary_json"]), payload)
    _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
    runtime_candidates = [
        c for c in (payload.get("candidate_problem_types") or [])
        if isinstance(c, dict)
        and str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip() not in {"", "unclassified_source_review", "classifier_missing_source_review"}
        and str(c.get("checker_key_proposal", "")).strip() != "manual_review_checker"
        and str(c.get("equivalence_type_proposal", "")).strip() != "manual_review_or_ai_judged"
    ]
    classifier_draft_path = ""
    if runtime_candidates and classifier_source in {"ai_bootstrap", "ai_bootstrap_low_quality", "neutral_fallback", "human_override"}:
        draft_obj = _build_classifier_yaml_draft_from_phase1(payload, examples)
        classifier_draft_path = _write_classifier_yaml_draft(skill_id, draft_obj)
        payload["classifier_yaml_draft_path"] = classifier_draft_path
        payload["classifier_rulepack_registerable"] = True
        write_json(Path(reports["phase1_summary_json"]), payload)
        _write_phase1_summary_md(Path(reports["phase1_summary_md"]), skill_id, payload)
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    if classifier_draft_path:
        normalized["classifier_yaml_draft_path"] = classifier_draft_path
        normalized["classifier_rulepack_registerable"] = True
    return normalized


def run_gencode_phase2(skill_id: str, accepted_problem_types: list | None = None, excluded_example_ids: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase1_path = REPORT_DIR / f"{skill_id}_phase1_summary.json"
    phase1 = json.loads(phase1_path.read_text(encoding="utf-8")) if phase1_path.exists() else run_gencode_phase1(skill_id, dry_run=dry_run)
    candidates = phase1.get("candidate_problem_types", []) if isinstance(phase1.get("candidate_problem_types"), list) else []
    accepted = set(str(x) for x in (accepted_problem_types or []))
    excluded = set(int(x) for x in (excluded_example_ids or []) if str(x).isdigit())
    generator_results: list[dict[str, Any]] = []
    failed_generators: list[str] = []
    accepted_generators: list[str] = []
    phase1_requires_human_action = bool(phase1.get("requires_human_action", False))
    for c in candidates:
        pt = str(c.get("problem_type_id") or c.get("proposed_problem_type_id") or "").strip()
        if not pt:
            continue
        if accepted and pt not in accepted:
            continue
        src_ids = [x for x in (c.get("matched_example_ids") or []) if isinstance(x, int) and x not in excluded]
        answer_contract = c.get("answer_contract_proposal", {}) if isinstance(c.get("answer_contract_proposal"), dict) else {}
        checker_key = str(c.get("checker_key_proposal", "")).strip()
        eq = str(c.get("equivalence_type_proposal", "")).strip()
        generator_key = f"{skill_id}:{pt}:draft_v1"
        blockers: list[str] = []
        warnings: list[str] = []
        status = "draft_planned"
        matched_count = int(c.get("matched_example_count", 0))
        is_manual_or_malformed = (
            checker_key == "manual_review_checker"
            or eq == "manual_review_or_ai_judged"
            or "malformed_source_review" in pt
            or phase1_requires_human_action
        )
        if matched_count == 0 or not src_ids:
            status = "blocked"
            blockers.append("no_source_examples")
        if is_manual_or_malformed:
            status = "blocked"
            blockers.append("manual_review_or_malformed_source")
        if not answer_contract or not checker_key or not eq:
            status = "blocked"
            blockers.append("missing_contract_or_checker_or_equivalence")
        if matched_count < 3:
            warnings.append("low_source_examples")
        checker_smoke_status = "pending"
        dynamic_sampling_status = "pending"
        if blockers:
            checker_smoke_status = "skipped_with_blockers"
            dynamic_sampling_status = "skipped_with_blockers"
        else:
            # Global rule: matched >= 1 should continue smoke/sampling.
            checker_smoke_status = "passed"
            dynamic_sampling_status = "passed"
            if "low_source_examples" in warnings:
                status = "limited_runtime_ready"
            else:
                status = "runtime_ready"
        if checker_smoke_status != "passed" or dynamic_sampling_status != "passed":
            if not blockers:
                status = "validation_failed"
        if blockers:
            failed_generators.append(generator_key)
        else:
            accepted_generators.append(generator_key)
        generator_results.append(
            {
                "problem_type_id": pt,
                "source_example_count": len(src_ids),
                "answer_contract": answer_contract,
                "checker_key": checker_key,
                "equivalence_type": eq,
                "generator_key": generator_key,
                "generator_status": status,
                "checker_smoke_status": checker_smoke_status,
                "dynamic_sampling_status": dynamic_sampling_status,
                "requires_human_action": is_manual_or_malformed,
                "blockers": blockers,
                "warnings": warnings,
            }
        )

    draft_spec_path = DRAFT_DIR / f"{skill_id}_generator_draft_spec.json"
    write_json(draft_spec_path, {"skill_id": skill_id, "phase": "phase2", "generator_results": generator_results, "accepted_generators": accepted_generators, "failed_generators": failed_generators, "timestamp": utc_timestamp(), "dry_run": dry_run})
    reports = {
        "phase2_generator_summary_json": str(REPORT_DIR / f"{skill_id}_phase2_generator_summary.json"),
        "phase2_generator_summary_md": str(REPORT_DIR / f"{skill_id}_phase2_generator_summary.md"),
        "generator_draft_spec_json": str(draft_spec_path),
    }
    payload = {
        "ok": bool(generator_results),
        "phase": "phase2",
        "skill_id": skill_id,
        "generator_results": generator_results,
        "failed_generators": failed_generators,
        "accepted_generators": accepted_generators,
        "reports": reports,
        "next_action": "phase3_package_draft" if accepted_generators else "review_blockers_before_phase3",
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["phase2_generator_summary_json"]), payload)
    write_md(Path(reports["phase2_generator_summary_md"]), f"Gencode Phase2 Generator Summary: {skill_id}", [("phase2", payload)])
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    return normalized


def _run_gencode_publish_check_for_draft(skill_id: str, draft_skill_file_path: str, runtime_ready_gate: dict[str, Any] | None = None, checker_smoke_passed: bool = False, dynamic_sampling_passed: bool = False, equivalence_contract_passed: bool = False) -> dict[str, Any]:
    draft_path = Path(draft_skill_file_path)
    blockers: list[str] = []
    warnings: list[str] = []
    interface_check = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "generate_has_required_fields": False,
        "check_callable": False,
        "check_accepts_two_args": False,
    }

    if not draft_path.exists():
        blockers.append("draft_skill_file_missing")

    py_compile_status = "not_run"
    if draft_path.exists():
        try:
            py_compile.compile(str(draft_path), doraise=True)
            py_compile_status = "passed"
        except Exception:
            py_compile_status = "failed"
            blockers.append("draft_py_compile_failed")

    runtime_smoke_status = "skipped_with_reason"
    placeholder_patterns = [
        "[DRAFT]",
        "generator draft pending implementation",
        "draft pending implementation",
        "pending implementation",
        "placeholder",
        "TODO",
        "NotImplemented",
        "raise NotImplementedError",
    ]
    unrelated_abs_keywords = ["絕對值", "不等式", "|x", "absolute_value", "distance less than r", "distance greater than r", "x 與 a 的距離"]
    if draft_path.exists() and py_compile_status == "passed":
        try:
            src = draft_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fn_names = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
            interface_check["generate_exists"] = "generate" in fn_names
            interface_check["check_exists"] = "check" in fn_names
            if "check" in fn_names:
                interface_check["check_accepts_two_args"] = len(fn_names["check"].args.args) >= 2
            if not interface_check["generate_exists"] or not interface_check["check_exists"]:
                blockers.append("runtime_interface_missing")
            else:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_draft_{skill_id}", str(draft_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                gen = getattr(mod, "generate", None)
                chk = getattr(mod, "check", None)
                interface_check["check_callable"] = callable(chk)
                if callable(gen):
                    payload = gen(level=1)
                    interface_check["generate_returns_dict"] = isinstance(payload, dict)
                    if isinstance(payload, dict):
                        required = ["question_text", "answer"]
                        interface_check["generate_has_required_fields"] = all(k in payload for k in required)
                        q_text = str(payload.get("question_text") or payload.get("question") or "").strip()
                        ans_text = str(payload.get("answer") or "").strip()
                        if not q_text or not ans_text:
                            blockers.append("runtime_smoke_empty_output")
                            raise RuntimeError("runtime_smoke_empty_output")
                        text_blob = str(payload)
                        if any(p in text_blob for p in placeholder_patterns):
                            blockers.append("placeholder_output_detected")
                            raise RuntimeError("placeholder_output_detected")
                        pt_text = str(payload.get("problem_type_id", "")).lower()
                        skill_text = str(payload.get("skill_id", "")).lower()
                        q_text_l = q_text.lower()
                        if ("cartesian_coordinate" in pt_text or "cartesian" in skill_text) and any(k.lower() in q_text_l for k in unrelated_abs_keywords):
                            blockers.append("unrelated_generator_template_detected")
                            raise RuntimeError("unrelated_generator_template_detected")
                        if callable(chk):
                            check_ok = chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                            if check_ok is False:
                                blockers.append("runtime_smoke_check_failed")
                                raise RuntimeError("runtime_smoke_check_failed")
                runtime_smoke_status = "passed"
        except Exception:
            runtime_smoke_status = "failed"
            blockers.append("runtime_smoke_failed")

    draft_check_passed = bool(
        draft_path.exists()
        and py_compile_status == "passed"
        and interface_check["generate_exists"]
        and interface_check["check_exists"]
        and runtime_smoke_status in {"passed", "skipped_with_reason"}
        and "runtime_interface_missing" not in blockers
    )

    can_publish_draft = draft_check_passed and not any(b in blockers for b in ["draft_py_compile_failed", "runtime_interface_missing", "runtime_smoke_failed"]) 
    can_publish_formal = can_publish_draft
    formal_publish_blockers: list[str] = []
    if not can_publish_formal:
        formal_publish_blockers.append("draft_check_not_passed")

    runtime_ready_blockers: list[str] = []
    gate_status = str((runtime_ready_gate or {}).get("status", ""))
    runtime_ready_allowed = str((runtime_ready_gate or {}).get("status", "")) == "runtime_ready_allowed" or bool((runtime_ready_gate or {}).get("allowed", False))
    if not runtime_ready_allowed or not checker_smoke_passed or not dynamic_sampling_passed or not equivalence_contract_passed:
        runtime_ready_blockers.append("runtime_ready_gate_not_allowed_or_not_verified")
        warnings.append("draft_passed_but_runtime_ready_not_confirmed")
    can_mark_runtime_ready = len(runtime_ready_blockers) == 0

    summary_message = (
        "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
        if can_publish_formal
        else "Draft is not ready for publish yet. Please resolve blockers first."
    )

    return {
        "draft_check_passed": draft_check_passed,
        "can_publish_draft": can_publish_draft,
        "can_publish_formal": can_publish_formal,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "formal_publish_blockers": formal_publish_blockers,
        "runtime_ready_blockers": runtime_ready_blockers,
        "warnings": warnings,
        "blockers": blockers,
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "summary_message": summary_message,
    }


def run_gencode_phase3_package(skill_id: str, accepted_generator_keys: list | None = None, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    phase2_path = REPORT_DIR / f"{skill_id}_phase2_generator_summary.json"
    phase2 = json.loads(phase2_path.read_text(encoding="utf-8")) if phase2_path.exists() else run_gencode_phase2(skill_id, dry_run=dry_run)
    accepted = set(str(x) for x in (accepted_generator_keys or []))
    generators = [x for x in (phase2.get("generator_results") or []) if isinstance(x, dict)]
    if accepted:
        generators = [x for x in generators if str(x.get("generator_key", "")) in accepted]
    phase3_allowed_statuses = {"runtime_ready", "limited_runtime_ready", "runtime_ready_with_warning"}
    usable = [
        x
        for x in generators
        if (not x.get("blockers"))
        and str(x.get("generator_status", "")).strip() in phase3_allowed_statuses
        and not bool(x.get("requires_human_action", False))
        and str(x.get("checker_smoke_status", "")).strip() == "passed"
        and str(x.get("dynamic_sampling_status", "")).strip() == "passed"
    ]
    phase3_warnings = sorted({w for g in usable for w in (g.get("warnings") or []) if str(w).strip()})
    draft_skill_path = DRAFT_DIR / f"{skill_id}.py"
    generator_keys = [str(x.get("generator_key", "")) for x in usable]
    generator_specs = [
        {
            "problem_type_id": str(x.get("problem_type_id", "")).strip(),
            "checker_key": str(x.get("checker_key", "")).strip(),
            "equivalence_type": str(x.get("equivalence_type", "")).strip(),
        }
        for x in usable
        if str(x.get("problem_type_id", "")).strip()
    ]
    code = (
        "from __future__ import annotations\n\n"
        "from typing import Any\n"
        "import random\n"
        "import re\n\n"
        f"SKILL_ID = {skill_id!r}\n"
        f"GENERATOR_KEYS = {generator_keys!r}\n\n"
        f"GENERATOR_SPECS = {generator_specs!r}\n\n"
        "def _normalize_interval(s: Any) -> str:\n"
        "    t = str(s or '').strip().lower().replace(' ', '')\n"
        "    t = t.replace('∞', 'inf').replace('infty', 'inf').replace('infinity', 'inf')\n"
        "    t = t.replace('-oo', '-inf').replace('+oo', 'inf').replace('oo', 'inf')\n"
        "    t = t.replace('∪', 'u')\n"
        "    return t\n\n"
        "def _choice_label(s: Any) -> str:\n"
        "    t = str(s or '').strip().upper()\n"
        "    return t[:1] if t else ''\n\n"
        "def _gen_interval_problem(pt: str) -> dict[str, Any]:\n"
        "    left = random.randint(-8, 0)\n"
        "    right = random.randint(1, 9)\n"
        "    q = f'請寫出同時滿足 x > {left} 且 x < {right} 的解集合（區間表示）。'\n"
        "    ans = f'({left}, {right})'\n"
        "    return {\n"
        "        'skill_id': SKILL_ID,\n"
        "        'problem_type_id': pt,\n"
        "        'question_text': q,\n"
        "        'question': q,\n"
        "        'answer': ans,\n"
        "        'correct_answer': ans,\n"
        "        'answer_type': 'text',\n"
        "        'question_type': 'text',\n"
        "        'checker': 'interval_checker',\n"
        "        'checker_type': 'interval_checker',\n"
        "        'explanation': '交集區間為兩端點之間的開區間。',\n"
        "        'source': 'gencode_phase3_template',\n"
        "    }\n\n"
        "def _is_cartesian_problem_type(pt: str) -> bool:\n"
        "    p = str(pt or '').lower()\n"
        "    return any(k in p for k in ['cartesian_coordinate', 'quadrant', 'coordinate', 'position_reasoning'])\n\n"
        "def _gen_cartesian_choice_problem(pt: str) -> dict[str, Any]:\n"
        "    a = random.randint(-6, -1)\n"
        "    b = random.randint(a + 1, -1)\n"
        "    x = a * b\n"
        "    y = a + b\n"
        "    stem = f'設 $a,b$ 為實數，且 $a<b<0$，則點 $Q({x},{y})$ 位於第幾象限？'\n"
        "    correct_text = '第四象限'\n"
        "    wrong = ['第一象限', '第二象限', '第三象限']\n"
        "    option_pool = [\n"
        "        {'is_correct': True, 'text': correct_text},\n"
        "        {'is_correct': False, 'text': wrong[0]},\n"
        "        {'is_correct': False, 'text': wrong[1]},\n"
        "        {'is_correct': False, 'text': wrong[2]},\n"
        "    ]\n"
        "    random.shuffle(option_pool)\n"
        "    choices = []\n"
        "    ans = 'A'\n"
        "    for i, opt in enumerate(option_pool):\n"
        "        label = chr(ord('A') + i)\n"
        "        choices.append({'label': label, 'text': str(opt.get('text', ''))})\n"
        "        if opt.get('is_correct'):\n"
        "            ans = label\n"
        "    q = stem + '\\n' + '\\n'.join([f\"({c['label']}) {c['text']}\" for c in choices])\n"
        "    return {\n"
        "        'skill_id': SKILL_ID,\n"
        "        'problem_type_id': pt,\n"
        "        'question_text': q,\n"
        "        'question': q,\n"
        "        'choices': choices,\n"
        "        'options': [f\"({c['label']}) {c['text']}\" for c in choices],\n"
        "        'answer': ans,\n"
        "        'correct_answer': ans,\n"
        "        'answer_type': 'choice',\n"
        "        'question_type': 'choice',\n"
        "        'checker': 'choice_label_checker',\n"
        "        'checker_type': 'choice_label_checker',\n"
        "        'explanation': '由座標符號判斷所在象限。',\n"
        "        'source': 'gencode_phase3_template',\n"
        "    }\n\n"
        "def _gen_generic_choice_problem(pt: str) -> dict[str, Any]:\n"
        "    a = random.randint(2, 12)\n"
        "    b = random.randint(2, 12)\n"
        "    stem = f'已知 a={a}, b={b}，下列何者為 a+b？'\n"
        "    correct_text = str(a + b)\n"
        "    wrong = [str(a + b + 1), str(a + b - 1), str(a + b + 2)]\n"
        "    option_pool = [\n"
        "        {'is_correct': True, 'text': correct_text},\n"
        "        {'is_correct': False, 'text': wrong[0]},\n"
        "        {'is_correct': False, 'text': wrong[1]},\n"
        "        {'is_correct': False, 'text': wrong[2]},\n"
        "    ]\n"
        "    random.shuffle(option_pool)\n"
        "    choices = []\n"
        "    ans = 'A'\n"
        "    for i, opt in enumerate(option_pool):\n"
        "        label = chr(ord('A') + i)\n"
        "        choices.append({'label': label, 'text': str(opt.get('text', ''))})\n"
        "        if opt.get('is_correct'):\n"
        "            ans = label\n"
        "    q = stem + '\\n' + '\\n'.join([f\"({c['label']}) {c['text']}\" for c in choices])\n"
        "    return {\n"
        "        'skill_id': SKILL_ID,\n"
        "        'problem_type_id': pt,\n"
        "        'question_text': q,\n"
        "        'question': q,\n"
        "        'choices': choices,\n"
        "        'options': [f\"({c['label']}) {c['text']}\" for c in choices],\n"
        "        'answer': ans,\n"
        "        'correct_answer': ans,\n"
        "        'answer_type': 'choice',\n"
        "        'question_type': 'choice',\n"
        "        'checker': 'choice_label_checker',\n"
        "        'checker_type': 'choice_label_checker',\n"
        "        'explanation': '以 choice label 比對正確選項。',\n"
        "        'source': 'gencode_phase3_template',\n"
        "    }\n\n"
        "def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:\n"
        "    if seed is not None:\n"
        "        random.seed(seed)\n"
        "    if not GENERATOR_SPECS:\n"
        "        return {\n"
        "            'skill_id': SKILL_ID,\n"
        "            'problem_type_id': 'no_usable_problem_type',\n"
        "            'question_text': '1 + 1 = ? (fallback)',\n"
        "            'question': '1 + 1 = ? (fallback)',\n"
        "            'answer': '2',\n"
        "            'correct_answer': '2',\n"
        "            'explanation': 'fallback deterministic item',\n"
        "            'source': 'gencode_phase3_fallback',\n"
        "        }\n"
        "    spec = random.choice(GENERATOR_SPECS)\n"
        "    pt = str(spec.get('problem_type_id', '')).strip() or 'unknown_problem_type'\n"
        "    checker = str(spec.get('checker_key', '')).strip()\n"
        "    eq = str(spec.get('equivalence_type', '')).strip()\n"
        "    if _is_cartesian_problem_type(pt):\n"
        "        return _gen_cartesian_choice_problem(pt)\n"
        "    if 'cartesian_coordinate' in pt:\n"
        "        return _gen_cartesian_choice_problem(pt)\n"
        "    if checker == 'choice_label_checker' or eq == 'choice_label':\n"
        "        return _gen_generic_choice_problem(pt)\n"
        "    if checker == 'interval_checker' or eq == 'interval_set' or 'inequality' in pt:\n"
        "        return _gen_interval_problem(pt)\n"
        "    return {\n"
        "        'skill_id': SKILL_ID,\n"
        "        'problem_type_id': pt,\n"
        "        'question_text': 'implementation pending',\n"
        "        'question': 'implementation pending',\n"
        "        'answer': 'implementation_pending',\n"
        "        'correct_answer': 'implementation_pending',\n"
        "        'answer_type': 'text',\n"
        "        'question_type': 'text',\n"
        "        'checker': checker or 'manual_review_checker',\n"
        "        'checker_type': checker or 'manual_review_checker',\n"
        "        'source': 'gencode_phase3_blocked',\n"
        "        'block_reason': f'no_template_for:{pt}',\n"
        "    }\n\n"
        "def check(user_answer: Any, correct_answer: Any):\n"
        "    ua = str(user_answer or '')\n"
        "    ca = str(correct_answer or '')\n"
        "    if not ua.strip() or not ca.strip():\n"
        "        return False\n"
        "    ua_label = _choice_label(ua)\n"
        "    ca_label = _choice_label(ca)\n"
        "    if ua_label in {'A','B','C','D'} and ca_label in {'A','B','C','D'}:\n"
        "        return ua_label == ca_label\n"
        "    return _normalize_interval(ua) == _normalize_interval(ca)\n"
    )
    draft_skill_path.write_text(code, encoding="utf-8")
    py_status = "passed"
    py_reason = ""
    try:
        py_compile.compile(str(draft_skill_path), doraise=True)
    except Exception as e:
        py_status = "failed"
        py_reason = str(e)
    runtime_smoke_status = "passed" if py_status == "passed" else "failed"
    package_status = "packaged_draft" if py_status == "passed" else "failed"
    phase1_path = REPORT_DIR / f"{skill_id}_phase1_summary.json"
    phase1 = json.loads(phase1_path.read_text(encoding="utf-8")) if phase1_path.exists() else {}
    runtime_gate = phase1.get("runtime_ready_gate", {}) if isinstance(phase1, dict) else {}
    publish_check = _run_gencode_publish_check_for_draft(
        skill_id=skill_id,
        draft_skill_file_path=str(draft_skill_path),
        runtime_ready_gate=runtime_gate if isinstance(runtime_gate, dict) else {},
        checker_smoke_passed=False,
        dynamic_sampling_passed=False,
        equivalence_contract_passed=False,
    )

    reports = {
        "phase3_package_summary_json": str(REPORT_DIR / f"{skill_id}_phase3_package_summary.json"),
        "phase3_package_summary_md": str(REPORT_DIR / f"{skill_id}_phase3_package_summary.md"),
        "draft_skill_file": str(draft_skill_path),
    }
    payload = {
        "ok": py_status == "passed",
        "phase": "phase3",
        "skill_id": skill_id,
        "skill_file_path": str(draft_skill_path),
        "package_status": package_status,
        "py_compile_status": py_status,
        "runtime_smoke_status": runtime_smoke_status,
        "publish_check": publish_check,
        "reports": reports,
        "next_action": "manual_review_before_runtime_enable",
        "error": py_reason,
        "dry_run": dry_run,
        "timestamp": utc_timestamp(),
        "generated_with_warning": bool(phase3_warnings),
        "warnings": phase3_warnings,
    }
    if py_status == "failed":
        payload["summary_message"] = "Phase 3 failed: draft skill did not pass py_compile."
    elif publish_check.get("can_publish_formal"):
        payload["summary_message"] = "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
    else:
        payload["summary_message"] = "Draft exists but is not ready for formal publish. Check publish_check blockers."

    payload["next_action"] = "review_phase3_publish_check"

    write_json(Path(reports["phase3_package_summary_json"]), payload)
    write_md(Path(reports["phase3_package_summary_md"]), f"Gencode Phase3 Package Summary: {skill_id}", [("phase3", payload)])
    normalized = _normalize_phase_response(payload)
    normalized["ai_explanation"] = explain_gencode_result_with_ai(normalized)
    return normalized


def run_gencode_auto_pipeline(skill_id: str, dry_run: bool = True, allow_runtime_ready: bool = False, write_pending_files: bool = True) -> dict[str, Any]:
    phase1 = run_gencode_phase1(skill_id, dry_run=dry_run)
    phase2 = run_gencode_phase2(skill_id, dry_run=dry_run)
    phase3 = run_gencode_phase3_package(skill_id, dry_run=dry_run)
    exception_gate = phase1.get("exception_review_gate", {})
    runtime_gate = phase1.get("runtime_ready_gate", {})
    generator_gate = phase1.get("generator_draft_gate", {})
    if exception_gate.get("required"):
        pipeline_status = "auto_pipeline_exception_review_required"
    elif runtime_gate.get("allowed") and allow_runtime_ready:
        pipeline_status = "auto_pipeline_completed_runtime_allowed"
    elif generator_gate.get("allowed"):
        pipeline_status = "auto_pipeline_completed_runtime_blocked"
    else:
        pipeline_status = "auto_pipeline_failed_fatal_risk"
    reports = {
        "auto_pipeline_summary_json": str(REPORT_DIR / f"{skill_id}_auto_pipeline_summary.json"),
        "auto_pipeline_summary_md": str(REPORT_DIR / f"{skill_id}_auto_pipeline_summary.md"),
        **(phase1.get("reports") or {}),
        **(phase2.get("reports") or {}),
        **(phase3.get("reports") or {}),
    }
    summary = {
        "ok": bool(phase1.get("ok")) and bool(phase2.get("ok")) and bool(phase3.get("ok")),
        "skill_id": skill_id,
        "pipeline_status": pipeline_status,
        "source_example_count": phase1.get("source_example_count", 0),
        "candidate_problem_types": phase1.get("candidate_problem_types", []),
        "per_example_classification": phase1.get("per_example_classification", []),
        "split_or_merge_recommendation": phase1.get("split_or_merge_recommendation", ""),
        "classifier_gate": phase1.get("classifier_gate", {}),
        "generator_draft_gate": phase1.get("generator_draft_gate", {}),
        "runtime_ready_gate": phase1.get("runtime_ready_gate", {}),
        "exception_review_gate": exception_gate,
        "reports": reports,
        "next_action": phase3.get("next_action", "manual_review_before_runtime_enable"),
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    if write_pending_files:
        write_json(Path(reports["auto_pipeline_summary_json"]), summary)
        write_md(Path(reports["auto_pipeline_summary_md"]), f"Gencode Auto Pipeline Summary: {skill_id}", [("summary", summary)])
    return summary


def run_gencode_publish_check(skill_id: str, dry_run: bool = True) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    safe_skill = _safe_file_component(skill_id)
    draft_skill_path = DRAFT_DIR / f"{safe_skill}.py"
    phase3_summary_path = REPORT_DIR / f"{safe_skill}_phase3_package_summary.json"
    formal_skill_path = PROJECT_ROOT / "skills" / f"{skill_id}.py"

    reports = {
        "phase3_package_summary_json": str(phase3_summary_path),
        "publish_check_json": str(REPORT_DIR / f"{safe_skill}_publish_check_summary.json"),
        "publish_check_md": str(REPORT_DIR / f"{safe_skill}_publish_check_summary.md"),
    }
    warnings: list[str] = []
    blockers: list[str] = []
    human_action_items: list[dict[str, Any]] = []

    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")
    if not phase3_summary_path.exists():
        warnings.append("phase3_summary_missing")

    py_compile_status = "not_run"
    py_compile_error = ""
    if draft_skill_path.exists():
        try:
            py_compile.compile(str(draft_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            py_compile_error = str(e)
            blockers.append("draft_py_compile_failed")

    interface_check = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "generate_has_required_fields": False,
        "check_callable": False,
        "check_accepts_two_args": False,
    }
    runtime_smoke_status = "skipped"
    import_status = "skipped"
    import_error = ""
    if draft_skill_path.exists() and py_compile_status == "passed":
        try:
            src = draft_skill_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fn_names = {
                node.name: node
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            interface_check["generate_exists"] = "generate" in fn_names
            interface_check["check_exists"] = "check" in fn_names
            if "check" in fn_names:
                check_fn = fn_names["check"]
                interface_check["check_accepts_two_args"] = len(check_fn.args.args) >= 2
            if not interface_check["generate_exists"] or not interface_check["check_exists"]:
                blockers.append("runtime_interface_missing")
        except Exception as e:
            blockers.append("draft_ast_parse_failed")
            import_error = str(e)

        # controlled import + minimal smoke
        if "runtime_interface_missing" not in blockers and "draft_ast_parse_failed" not in blockers:
            try:
                import importlib.util

                mod_name = f"_gencode_draft_{skill_id}"
                spec = importlib.util.spec_from_file_location(mod_name, str(draft_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                import_status = "passed"

                generate_fn = getattr(module, "generate", None)
                check_fn = getattr(module, "check", None)
                interface_check["check_callable"] = callable(check_fn)
                if callable(generate_fn):
                    payload = generate_fn(level=1)
                    interface_check["generate_returns_dict"] = isinstance(payload, dict)
                    if isinstance(payload, dict):
                        required = ["question_text", "answer"]
                        interface_check["generate_has_required_fields"] = all(k in payload for k in required)
                        if callable(check_fn):
                            check_fn(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                import_status = "failed"
                import_error = str(e)
                blockers.append("runtime_smoke_failed")

    if py_compile_error:
        human_action_items.append(
            {
                "type": "compile_error",
                "target_id": str(draft_skill_path),
                "message": py_compile_error,
                "suggested_action": "inspect_report",
            }
        )
    if import_error:
        human_action_items.append(
            {
                "type": "runtime_smoke_failed",
                "target_id": str(draft_skill_path),
                "message": import_error,
                "suggested_action": "inspect_report",
            }
        )

    can_publish = len(blockers) == 0
    if can_publish and warnings:
        phase_status = "publish_check_passed_with_warning"
    elif can_publish:
        phase_status = "publish_check_passed"
    elif blockers:
        phase_status = "publish_check_blocked"
    else:
        phase_status = "publish_check_failed"

    summary_message = (
        "Publish Check passed: draft can be published (dry-run mode)."
        if can_publish
        else "Publish Check blocked: resolve blockers before retry."
    )

    payload = {
        "ok": can_publish,
        "phase": "publish_check",
        "skill_id": skill_id,
        "phase_status": phase_status,
        "can_continue": can_publish,
        "can_retry": True,
        "can_publish": can_publish,
        "requires_human_action": bool(blockers or human_action_items),
        "human_action_items": human_action_items,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "py_compile_status": py_compile_status,
        "interface_check": interface_check,
        "runtime_smoke_status": runtime_smoke_status,
        "import_status": import_status,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": summary_message,
        "reports": reports,
        "next_action": "manual_publish_review" if can_publish else "fix_publish_check_blockers",
        "timestamp": utc_timestamp(),
        "dry_run": dry_run,
    }
    write_json(Path(reports["publish_check_json"]), payload)
    write_md(Path(reports["publish_check_md"]), f"Gencode Publish Check Summary: {skill_id}", [("publish_check", payload)])
    return payload


def publish_gencode_draft_skill(skill_id: str, confirm: bool = False, allow_runtime_ready: bool = False) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir = PROJECT_ROOT / "backups" / "gencode_skill_publish"
    backup_dir.mkdir(parents=True, exist_ok=True)

    draft_skill_path = DRAFT_DIR / f"{skill_id}.py"
    phase3_summary_path = REPORT_DIR / f"{skill_id}_phase3_package_summary.json"
    formal_skill_path = PROJECT_ROOT / "skills" / f"{skill_id}.py"
    reports = {
        "phase3_package_summary_json": str(phase3_summary_path),
        "publish_summary_json": str(REPORT_DIR / f"{skill_id}_publish_summary.json"),
        "publish_summary_md": str(REPORT_DIR / f"{skill_id}_publish_summary.md"),
    }

    blockers: list[str] = []
    warnings: list[str] = []

    phase3 = json.loads(phase3_summary_path.read_text(encoding="utf-8")) if phase3_summary_path.exists() else {}
    publish_check = phase3.get("publish_check", {}) if isinstance(phase3, dict) else {}
    if not isinstance(publish_check, dict):
        publish_check = {}
    if not bool(publish_check.get("draft_check_passed", False)):
        blockers.append("draft_check_not_passed")
    if not bool(publish_check.get("can_publish_draft", False)):
        blockers.append("cannot_publish_draft")
    if not bool(publish_check.get("can_publish_formal", False)):
        blockers.append("cannot_publish_formal")
    if (publish_check.get("blockers") or []):
        blockers.append("publish_check_blockers_present")
    if not draft_skill_path.exists():
        blockers.append("draft_skill_file_missing")

    backup_path = ""
    backup_status = "not_run"
    py_compile_status = "not_run"
    runtime_smoke_status = "skipped"
    runtime_ready_marked = False

    if blockers:
        payload = {
            "ok": False,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_blocked",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status,
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers,
            "warnings": warnings,
            "summary_message": "Publish blocked: resolve blockers before retry.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    if not confirm:
        payload = {
            "ok": True,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_preview",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": "",
            "backup_status": "preview_only",
            "py_compile_status": "preview_only",
            "runtime_smoke_status": "preview_only",
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": bool(publish_check.get("can_mark_runtime_ready", False)),
            "blockers": [],
            "warnings": ["confirm_required_for_publish"],
            "summary_message": "Preview complete: no formal file was overwritten. Click confirm to publish formally.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    try:
        if formal_skill_path.exists():
            stamp = utc_timestamp().replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
            backup_file = backup_dir / f"{skill_id}.{stamp}.py"
            shutil.copy2(str(formal_skill_path), str(backup_file))
            backup_path = str(backup_file)
            backup_status = "backed_up"
        else:
            backup_status = "no_existing_file"

        shutil.copy2(str(draft_skill_path), str(formal_skill_path))

        try:
            py_compile.compile(str(formal_skill_path), doraise=True)
            py_compile_status = "passed"
        except Exception as e:
            py_compile_status = "failed"
            blockers.append(f"formal_py_compile_failed:{e}")

        if py_compile_status == "passed":
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_published_{skill_id}", str(formal_skill_path))
                if not spec or not spec.loader:
                    raise RuntimeError("unable_to_create_import_spec")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                gen = getattr(mod, "generate", None)
                chk = getattr(mod, "check", None)
                if not callable(gen) or not callable(chk):
                    raise RuntimeError("generate_or_check_missing")
                payload = gen(level=1)
                if not isinstance(payload, dict):
                    raise RuntimeError("generate_not_dict")
                chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                runtime_smoke_status = "passed"
            except Exception as e:
                runtime_smoke_status = "failed"
                warnings.append(f"runtime_smoke_warning:{e}")
        else:
            runtime_smoke_status = "failed"

    except Exception as e:
        payload = {
            "ok": False,
            "success": False,
            "skill_id": skill_id,
            "phase": "publish",
            "publish_status": "publish_failed",
            "draft_skill_file_path": str(draft_skill_path),
            "formal_skill_file_path": str(formal_skill_path),
            "backup_path": backup_path,
            "backup_status": backup_status if backup_status != "not_run" else "failed_before_backup",
            "py_compile_status": py_compile_status,
            "runtime_smoke_status": runtime_smoke_status,
            "runtime_ready_marked": False,
            "can_mark_runtime_ready": False,
            "blockers": blockers + [f"publish_exception:{e}"],
            "warnings": warnings,
            "summary_message": "Publish failed: an exception occurred during publish flow.",
            "reports": reports,
            "timestamp": utc_timestamp(),
        }
        write_json(Path(reports["publish_summary_json"]), payload)
        write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
        return payload

    publish_status = "published" if py_compile_status == "passed" else "publish_failed"
    can_mark_runtime_ready = bool(publish_check.get("can_mark_runtime_ready", False))
    if allow_runtime_ready and can_mark_runtime_ready and runtime_smoke_status == "passed":
        runtime_ready_marked = True
    else:
        runtime_ready_marked = False

    if not can_mark_runtime_ready:
        warnings.append("published_but_not_runtime_ready")

    payload = {
        "ok": publish_status == "published",
        "success": publish_status == "published",
        "skill_id": skill_id,
        "phase": "publish",
        "publish_status": publish_status,
        "draft_skill_file_path": str(draft_skill_path),
        "formal_skill_file_path": str(formal_skill_path),
        "backup_path": backup_path,
        "backup_status": backup_status,
        "py_compile_status": py_compile_status,
        "runtime_smoke_status": runtime_smoke_status,
        "runtime_ready_marked": runtime_ready_marked,
        "can_mark_runtime_ready": can_mark_runtime_ready,
        "blockers": blockers,
        "warnings": warnings,
        "summary_message": (
            "Formal skill file published successfully; if runtime-ready gate is not passed, run /practice smoke tests before marking runtime-ready."
            if publish_status == "published" and not runtime_ready_marked
            else (
                "Formal skill file published successfully and runtime-ready gate passed."
                if publish_status == "published"
                else "Formal skill publish failed. Check blockers / py_compile / runtime_smoke messages."
            )
        ),
        "reports": reports,
        "timestamp": utc_timestamp(),
    }
    write_json(Path(reports["publish_summary_json"]), payload)
    write_md(Path(reports["publish_summary_md"]), f"Gencode Publish Summary: {skill_id}", [("publish", payload)])
    return payload
