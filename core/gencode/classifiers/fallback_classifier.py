from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .base import ClassificationResult, ClassifierContext


class FallbackClassifier:
    def classify_examples(self, examples: list[dict[str, Any]], context: ClassifierContext) -> ClassificationResult:
        package_dir = context.project_root / "agent_skills_v2" / "_generated" / context.skill_id
        try:
            from core.gencode.pipeline_orchestrator import _load_registered_classifier_rulepack, _classify_examples_with_rulepack
            pack = _load_registered_classifier_rulepack(context.skill_id)
            if pack:
                rows = _classify_examples_with_rulepack(skill_id=context.skill_id, examples=examples, pack=pack)
                return ClassificationResult(package_dir=package_dir, examples_map_entries=rows)
        except Exception:
            pass

        rows: list[dict[str, Any]] = []
        
        try:
            from core.registry.taxonomy_registry import resolve_domain_for_skill
            from core.gencode.services.v3_example_semantic_classifier import TextbookExampleSource, classify_textbook_example, calculate_source_hash
            
            routing = resolve_domain_for_skill(context.skill_id)
            if routing:
                taxonomy_entry = {
                    "fixed_domain_key": routing.get("fixed_domain_key"),
                    "allowed_operations": routing.get("allowed_operations") or routing.get("allowed_types") or [],
                    "allowed_types": routing.get("allowed_types") or routing.get("allowed_operations") or [],
                }
                for ex in examples:
                    q_txt = ex.get("problem_text") or ex.get("question") or ex.get("stem") or ex.get("problem_preview") or ""
                    ans_txt = ex.get("correct_answer") or ex.get("answer") or ""
                    exp_txt = ex.get("explanation") or ex.get("detailed_solution") or ""
                    choices = ex.get("choices") or []
                    source = TextbookExampleSource(
                        skill_id=context.skill_id,
                        textbook_example_id=ex.get("id"),
                        question_text=q_txt,
                        answer=ans_txt,
                        choices=choices,
                        explanation=exp_txt,
                        source_label="",
                        source_type="",
                        presentation_mode="single_choice" if choices else "short_answer",
                        question_type="",
                        source_hash=calculate_source_hash(q_txt, ans_txt, exp_txt),
                    )
                    classification = classify_textbook_example(source, taxonomy_entry)
                    if classification:
                        pt = classification["problem_type_id"]
                        rt = classification.get("runtime_category", "rule_only")
                        rows.append({
                            "example_id": ex.get("id"),
                            "title": str(ex.get("title", "") or ""),
                            "source_type": "textbook_example",
                            "source_chapter": "unknown",
                            "source_section": "unknown",
                            "problem_preview": q_txt[:200],
                            "problem_text_hash": source.source_hash,
                            "skill_id": context.skill_id,
                            "subskill_id": pt,
                            "problem_type_id": pt,
                            "target_task": pt,
                            "task_family": pt,
                            "answer_type": classification.get("answer_type", ""),
                            "answer_shape": classification.get("answer_shape", ""),
                            "math_objects": [],
                            "runtime_category": rt,
                            "classification_rule_id": "fallback.domain_analyzer",
                            "classification_reason": "Domain analyzer classified the example based on taxonomy.",
                            "classifier_confidence": "high",
                            "semantic_risk_flags": [],
                            "semantic_audit_status": "pass",
                            "generator_status": "candidate",
                            "manual_review_reason": "",
                        })
                    else:
                        rows.append({
                            "example_id": ex.get("id"),
                            "title": str(ex.get("title", "") or ""),
                            "source_type": "textbook_example",
                            "source_chapter": "unknown",
                            "source_section": "unknown",
                            "problem_preview": q_txt[:200],
                            "problem_text_hash": source.source_hash,
                            "skill_id": context.skill_id,
                            "subskill_id": "unknown",
                            "problem_type_id": "unknown",
                            "runtime_category": "manual_review",
                            "classification_rule_id": "fallback.domain_analyzer_failed",
                            "classification_reason": "Domain analyzer failed to classify the example.",
                            "classifier_confidence": "low",
                            "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
                            "semantic_audit_status": "review_required",
                            "generator_status": "manual_review",
                            "manual_review_reason": "Domain analyzer did not match any allowed operations.",
                        })
                return ClassificationResult(package_dir=package_dir, examples_map_entries=rows)
        except Exception:
            pass

        for ex in examples:
            text = _example_text(ex)
            rule_feature: dict[str, Any] = {}
            target_task = ""
            task_in_scope = False
            try:
                from core.gencode.example_feature_extractor import extract_example_feature_rule_only
                from core.gencode.main_skill_anchor import build_main_skill_anchor
                from core.gencode.task_families import task_family_for_task

                rule_feature = extract_example_feature_rule_only(ex)
                target_task = str(rule_feature.get("target_task", "")).strip()
                anchor = build_main_skill_anchor(context.skill_id)
                expected_tasks = {
                    str(t).strip()
                    for t in (anchor.get("expected_subskill_candidates", []) if isinstance(anchor, dict) else [])
                    if str(t).strip()
                }
                expected_families = {
                    str(f).strip()
                    for f in (anchor.get("expected_task_families", []) if isinstance(anchor, dict) else [])
                    if str(f).strip()
                }
                task_in_scope = bool(
                    target_task
                    and target_task not in {"unknown", "needs_review", "compute_numeric"}
                    and (
                        target_task in expected_tasks
                        or task_family_for_task(target_task) in expected_families
                    )
                )
            except Exception:
                rule_feature = {}
                target_task = ""
                task_in_scope = False

            if task_in_scope:
                rows.append(
                    {
                        "example_id": ex.get("id"),
                        "title": str(ex.get("title", "") or ""),
                        "source_type": "textbook_example",
                        "source_chapter": "unknown",
                        "source_section": "unknown",
                        "problem_preview": text[:200],
                        "problem_text_hash": hashlib.sha1(text.encode("utf-8")).hexdigest() if text else "",
                        "skill_id": context.skill_id,
                        "subskill_id": target_task,
                        "problem_type_id": target_task,
                        "target_task": target_task,
                        "task_family": str(rule_feature.get("task_family", "")),
                        "answer_type": str(rule_feature.get("answer_type", "")),
                        "answer_shape": str(rule_feature.get("answer_shape", "")),
                        "math_objects": list(rule_feature.get("math_objects") or []),
                        "runtime_category": "rule_only",
                        "classification_rule_id": "fallback.rule_only_feature_extractor",
                        "classification_reason": "Rule-only feature extractor matched an in-scope skill candidate.",
                        "classifier_confidence": "medium",
                        "semantic_risk_flags": [],
                        "semantic_audit_status": "pass",
                        "generator_status": "candidate",
                        "manual_review_reason": "",
                    }
                )
                continue
            rows.append(
                {
                    "example_id": ex.get("id"),
                    "title": str(ex.get("title", "") or ""),
                    "source_type": "textbook_example",
                    "source_chapter": "unknown",
                    "source_section": "unknown",
                    "problem_preview": text[:200],
                    "problem_text_hash": hashlib.sha1(text.encode("utf-8")).hexdigest() if text else "",
                    "skill_id": context.skill_id,
                    "subskill_id": "unknown",
                    "problem_type_id": "unknown",
                    "runtime_category": "manual_review",
                    "classification_rule_id": "fallback.unknown",
                    "classification_reason": "No skill-specific classifier found; fallback classifier routes to manual review.",
                    "classifier_confidence": "low",
                    "semantic_risk_flags": ["possible_missing_problem_type", "weak_classifier_match"],
                    "semantic_audit_status": "review_required",
                    "generator_status": "manual_review",
                    "manual_review_reason": "Skill-specific classifier/rule pack is missing.",
                }
            )
        return ClassificationResult(package_dir=package_dir, examples_map_entries=rows)


def _example_text(ex: dict[str, Any]) -> str:
    parts = []
    for k in ("problem_text", "problem", "question", "stem", "content", "title"):
        val = ex.get(k)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    return " ".join(parts)

