# -*- coding: utf-8 -*-
"""V3 Phase1–3 dry-run for B2 1-1 (no Phase4 DB commit)."""

from __future__ import annotations

import json
import queue
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.textbook_importer_v3_orchestrate import (
    find_b2_11_source_pair,
    resolve_latex_docx_path,
)
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx
from core.textbook_processor import get_question_title
from core.textbook_question_anchor import (
    build_anchors_from_block_meta,
    detect_anchor_id_collisions,
    normalize_fingerprint_text,
    summarize_anchor_collection,
)

DRYRUN_DIR = Path("textbook_import") / "debug"
DEFAULT_DRYRUN_NAME = "B2_1-1_phase3_dryrun.json"


def ensure_b2_11_latex_docx(project_root: Path | str) -> dict[str, Any]:
    """Ensure *_Latex.docx exists via in-repo MTEF converter (no Word COM)."""
    root = Path(project_root)
    pair = find_b2_11_source_pair(root)
    source_dir = pair.source_dir
    original = pair.original_docx
    if original is None:
        # Fall back to any non-latex 1-1 課本 docx
        candidates = sorted(
            p
            for p in source_dir.glob("*1-1*課本*.docx")
            if p.is_file() and "latex" not in p.stem.lower() and "自我評量" not in p.name
        )
        original = candidates[0] if candidates else None
    if original is None:
        return {
            "status": "missing_original_docx",
            "source_dir": str(source_dir),
            "latex_docx": None,
        }

    resolved = resolve_latex_docx_path(source_dir, original.name)
    if resolved.status == "ok" and resolved.path and resolved.path.is_file():
        return {
            "status": "ok",
            "source_dir": str(source_dir),
            "original_docx": str(original),
            "latex_docx": str(resolved.path),
            "converted_now": False,
        }

    report = convert_docx_mathtype_to_latex_docx(original)
    out = Path(report.get("output") or "")
    return {
        "status": "ok" if out.is_file() else "convert_failed",
        "source_dir": str(source_dir),
        "original_docx": str(original),
        "latex_docx": str(out) if out else None,
        "converted_now": True,
        "converter_report": {
            "mathtype_ole": report.get("mathtype_ole"),
            "converted_ok": report.get("converted_ok"),
            "converted_failed": report.get("converted_failed"),
            "eq_fields": report.get("eq_fields"),
            "eq_converted_ok": report.get("eq_converted_ok"),
        },
    }


def build_b2_11_curriculum_info(latex_docx_path: Path | str, original_docx_name: str = "") -> dict[str, Any]:
    latex_name = Path(latex_docx_path).name
    parse_name = original_docx_name or latex_name
    meta = parse_textbook_filename_metadata(parse_name)
    return {
        "curriculum": "vocational",
        "publisher": "longteng",
        "grade": 10,
        "volume": "數學B2",
        "section_code": str(meta.get("section_code") or "1-1"),
        "chapter_index": meta.get("chapter_index") or 1,
        "source_scope": str(meta.get("source_scope") or "section_textbook"),
        "import_mode": "docx_problems",
        "original_filename": parse_name,
        "saved_filename": latex_name,
        "parse_filename": parse_name,
        "section": "1-1 角度的基本性質",
        "chapter": "1 三角函數",
    }


class GeminiUsageTracker:
    """Wrap model.generate_content to record request counts and usage metadata."""

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self._wrapped_models: list[tuple[Any, Any]] = []

    def wrap_model(self, model: Any) -> Any:
        if model is None or not hasattr(model, "generate_content"):
            return model
        original = model.generate_content
        tracker = self

        def wrapped(prompt, *args, **kwargs):
            prompt_text = prompt if isinstance(prompt, str) else str(prompt)
            input_chars = len(prompt_text)
            response = original(prompt, *args, **kwargs)
            usage = getattr(response, "usage_metadata", None)
            record: dict[str, Any] = {
                "request_index": len(tracker.requests) + 1,
                "input_character_count": input_chars,
                "output_character_count": len(str(getattr(response, "text", "") or "")),
                "prompt_token_count": None,
                "candidates_token_count": None,
                "total_token_count": None,
                "usage_metadata_available": usage is not None,
                "prompt_has_坐標系與函數圖形": "坐標系與函數圖形" in prompt_text,
                "prompt_has_數列與級數": "數列與級數" in prompt_text,
            }
            if usage is not None:
                for src, dst in (
                    ("prompt_token_count", "prompt_token_count"),
                    ("candidates_token_count", "candidates_token_count"),
                    ("total_token_count", "total_token_count"),
                ):
                    val = getattr(usage, src, None)
                    if val is None and isinstance(usage, dict):
                        val = usage.get(src)
                    if val is not None:
                        try:
                            record[dst] = int(val)
                        except (TypeError, ValueError):
                            record[dst] = val
            tracker.requests.append(record)
            return response

        model.generate_content = wrapped  # type: ignore[method-assign]
        self._wrapped_models.append((model, original))
        return model

    def restore(self) -> None:
        for model, original in self._wrapped_models:
            try:
                model.generate_content = original  # type: ignore[method-assign]
            except Exception:
                pass
        self._wrapped_models.clear()

    def summary(self) -> dict[str, Any]:
        prompt_tokens = [r["prompt_token_count"] for r in self.requests if r["prompt_token_count"] is not None]
        output_tokens = [
            r["candidates_token_count"] for r in self.requests if r["candidates_token_count"] is not None
        ]
        total_tokens = [r["total_token_count"] for r in self.requests if r["total_token_count"] is not None]
        return {
            "request_count": len(self.requests),
            "requests": self.requests,
            "input_character_count_total": sum(r["input_character_count"] for r in self.requests),
            "output_character_count_total": sum(r["output_character_count"] for r in self.requests),
            "prompt_token_count_total": sum(prompt_tokens) if prompt_tokens else None,
            "candidates_token_count_total": sum(output_tokens) if output_tokens else None,
            "total_token_count_total": sum(total_tokens) if total_tokens else None,
            "usage_metadata_available": any(r["usage_metadata_available"] for r in self.requests),
        }


def _index_phase3_items(parsed: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    from core.textbook_processor_v2 import _compact_title_key

    indexed: dict[str, list[dict[str, Any]]] = {}
    for chapter in parsed.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections") or []:
            if not isinstance(section, dict):
                continue
            for concept in section.get("concepts") or []:
                if not isinstance(concept, dict):
                    continue
                for bucket in ("examples", "practice_questions"):
                    for item in concept.get(bucket) or []:
                        if not isinstance(item, dict):
                            continue
                        title = get_question_title(item)
                        if not title:
                            continue
                        enriched = dict(item)
                        enriched["_gemini_bucket"] = bucket
                        enriched["_gemini_chapter_title"] = chapter.get("chapter_title")
                        enriched["_gemini_section_title"] = section.get("section_title")
                        enriched["_gemini_section_code"] = section.get("section_code")
                        enriched["_gemini_concept_name"] = concept.get("concept_name")
                        enriched["_gemini_concept_en_id"] = concept.get("concept_en_id")
                        for key in (title, _compact_title_key(title)):
                            if key:
                                indexed.setdefault(key, []).append(enriched)
    return indexed


def _collect_phase3_titles(parsed: dict[str, Any]) -> list[str]:
    titles: list[str] = []
    for chapter in parsed.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections") or []:
            if not isinstance(section, dict):
                continue
            for concept in section.get("concepts") or []:
                if not isinstance(concept, dict):
                    continue
                for bucket in ("examples", "practice_questions"):
                    for item in concept.get(bucket) or []:
                        if isinstance(item, dict):
                            title = get_question_title(item)
                            if title:
                                titles.append(title)
    return titles


def _match_phase3_item(
    phase2_key: str,
    indexed: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    from core.textbook_processor_v2 import _compact_title_key

    for key in (phase2_key, _compact_title_key(phase2_key)):
        items = indexed.get(key) or []
        if items:
            return items[0]
    return None


def build_dryrun_questions(
    block_meta: dict[str, dict[str, Any]],
    phase3_parsed: dict[str, Any],
    curriculum_info: dict[str, Any],
) -> dict[str, Any]:
    """Join Phase2 authoritative blocks with Phase3 Gemini metadata + stable anchors."""
    anchors = build_anchors_from_block_meta(block_meta, curriculum_info)
    indexed = _index_phase3_items(phase3_parsed)
    phase3_titles = _collect_phase3_titles(phase3_parsed)
    used_phase3: set[int] = set()

    questions: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []

    for anchor, (phase2_key, meta) in zip(anchors, block_meta.items()):
        block = meta if isinstance(meta, dict) else {}
        gemini_item = _match_phase3_item(phase2_key, indexed)
        if gemini_item is not None:
            used_phase3.add(id(gemini_item))
        gemini_answer = str((gemini_item or {}).get("correct_answer") or "").strip()
        gemini_solution = str((gemini_item or {}).get("detailed_solution") or "").strip()
        phase2_solution = str(block.get("detailed_solution") or "").strip()
        solution = phase2_solution or gemini_solution
        gemini_title = get_question_title(gemini_item) if gemini_item else ""
        source_type = str(block.get("source_type") or "")
        is_section_exercise = source_type in ("textbook_exercise", "advanced_exercise")
        # Prefer Phase2 identity; section exercises keep unknown rather than Gemini guess.
        concept_name = str(block.get("concept_name") or "").strip()
        concept_en_id = str(block.get("concept_en_id") or "").strip()
        concept_code = str(block.get("concept_code") or "").strip()
        if not is_section_exercise:
            if not concept_name:
                concept_name = str((gemini_item or {}).get("_gemini_concept_name") or "").strip()
            if not concept_en_id:
                concept_en_id = str((gemini_item or {}).get("_gemini_concept_en_id") or "").strip()
        if gemini_item is None:
            anomalies.append(
                {
                    "kind": "phase3_missing_title",
                    "phase2_key": phase2_key,
                    "detail": "Phase2 block has no matching Phase3 title",
                }
            )
        elif gemini_title and gemini_title != phase2_key:
            anomalies.append(
                {
                    "kind": "phase3_title_renamed",
                    "phase2_key": phase2_key,
                    "phase3_title": gemini_title,
                }
            )

        questions.append(
            {
                "anchor_id": anchor["anchor_id"],
                "text_fingerprint": anchor["text_fingerprint"],
                "source_order": anchor["source_order"],
                "anchor": phase2_key,
                "question_label": anchor["question_label"],
                "source_type": source_type or str(anchor.get("source_type") or ""),
                "question_type": anchor["question_type"],
                "question_number": anchor["question_number"],
                "problem_text": str(block.get("problem_text") or ""),
                "correct_answer": gemini_answer,
                "detailed_solution": solution,
                "concept_code": concept_code or None,
                "concept_name": concept_name or None,
                "concept_en_id": concept_en_id or None,
                "formal_skill_id": str(block.get("formal_skill_id") or "") or None,
                "chapter_title": str(
                    (gemini_item or {}).get("_gemini_chapter_title")
                    or curriculum_info.get("chapter")
                    or ""
                ),
                "section": str(
                    (gemini_item or {}).get("_gemini_section_code")
                    or block.get("section_code")
                    or curriculum_info.get("section_code")
                    or ""
                ),
                "section_code": str(block.get("section_code") or curriculum_info.get("section_code") or ""),
                "section_title": str(
                    (gemini_item or {}).get("_gemini_section_title")
                    or block.get("section_title")
                    or ""
                ),
                "phase3_matched": gemini_item is not None,
                "phase3_title": gemini_title or None,
                "notes_preview": {
                    "question_anchor": {
                        "anchor_id": anchor["anchor_id"],
                        "text_fingerprint": anchor["text_fingerprint"],
                        "source_order": anchor["source_order"],
                    }
                },
            }
        )

    # Phase3 extras not matched to Phase2
    for title in phase3_titles:
        items = indexed.get(title) or []
        for item in items:
            if id(item) not in used_phase3:
                anomalies.append(
                    {
                        "kind": "phase3_extra_title",
                        "phase3_title": title,
                        "detail": "Phase3 title has no Phase2 block",
                    }
                )
                used_phase3.add(id(item))

    expected_section = str(curriculum_info.get("section_code") or "").strip()
    for chapter in phase3_parsed.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        ch_title = str(chapter.get("chapter_title") or "")
        for section in chapter.get("sections") or []:
            if not isinstance(section, dict):
                continue
            sec_title = str(section.get("section_title") or "")
            sec_code = str(section.get("section_code") or "")
            if expected_section and sec_code and sec_code != expected_section:
                if expected_section not in sec_title:
                    anomalies.append(
                        {
                            "kind": "phase3_section_mismatch",
                            "expected_section_code": expected_section,
                            "phase3_chapter_title": ch_title,
                            "phase3_section_title": sec_title,
                            "phase3_section_code": sec_code,
                        }
                    )
            # B2 1-1 content should not be labeled as unrelated B1 chapters.
            suspicious = ("數列", "坐標系與函數圖形", "直角坐標")
            if any(token in ch_title for token in suspicious) or any(
                token in sec_title for token in suspicious
            ):
                anomalies.append(
                    {
                        "kind": "phase3_suspicious_chapter_label",
                        "phase3_chapter_title": ch_title,
                        "phase3_section_title": sec_title,
                        "detail": "Gemini metadata chapter/section looks unrelated to B2 1-1 角度",
                    }
                )

    # Duplicate Phase3 titles
    title_counts = Counter(phase3_titles)
    for title, count in title_counts.items():
        if count > 1:
            anomalies.append(
                {
                    "kind": "phase3_duplicate_title",
                    "phase3_title": title,
                    "count": count,
                }
            )

    type_counts = Counter(q["source_type"] for q in questions)
    return {
        "questions": questions,
        "anchors": anchors,
        "anchor_summary": summarize_anchor_collection(anchors),
        "anomalies": anomalies,
        "stats": {
            "phase2_blocks": len(block_meta),
            "phase3_titles": len(phase3_titles),
            "phase3_unique_titles": len(set(phase3_titles)),
            "dryrun_questions": len(questions),
            "source_type_counts": dict(type_counts),
            "no_answer": sum(1 for q in questions if not q["correct_answer"]),
            "no_solution": sum(1 for q in questions if not q["detailed_solution"]),
            "no_skill": sum(1 for q in questions if not q["formal_skill_id"]),
            "phase3_unmatched_phase2": sum(1 for q in questions if not q["phase3_matched"]),
            "anchor_collisions": len(detect_anchor_id_collisions(anchors)),
        },
    }


def format_human_summary(payload: dict[str, Any], *, preview: int = 15) -> str:
    stats = payload.get("stats") or {}
    gemini = payload.get("gemini") or {}
    lines = [
        "B2 1-1 Phase3 Dry-run Summary",
        "-----------------------------",
        f"Latex: {payload.get('latex_docx_path')}",
        f"Phase1 lines: {payload.get('phase1_line_count')}",
        f"Phase2 blocks: {stats.get('phase2_blocks')}",
        f"Phase3 titles: {stats.get('phase3_titles')} (unique={stats.get('phase3_unique_titles')})",
        f"Dry-run questions: {stats.get('dryrun_questions')}",
        f"Gemini model: {gemini.get('model')}",
        f"Gemini requests: {gemini.get('request_count')}",
        f"Gemini input chars: {gemini.get('input_character_count_total')}",
        f"Gemini tokens total: {gemini.get('total_token_count_total')}",
        f"source_type counts: {stats.get('source_type_counts')}",
        f"no_answer={stats.get('no_answer')} no_solution={stats.get('no_solution')} no_skill={stats.get('no_skill')}",
        f"anchor_collisions={stats.get('anchor_collisions')}",
        f"anomalies={len(payload.get('anomalies') or [])}",
        "",
        f"First {preview} questions:",
    ]
    for q in (payload.get("questions") or [])[:preview]:
        text = normalize_fingerprint_text(q.get("problem_text") or "")[:80]
        lines.append(
            f"- [{q.get('source_order')}] {q.get('anchor')!r} type={q.get('source_type')} "
            f"skill={q.get('formal_skill_id')!r} concept={q.get('concept_name')!r} "
            f"anchor_id={q.get('anchor_id')} "
            f"answer={'Y' if q.get('correct_answer') else 'N'} "
            f"solution={'Y' if q.get('detailed_solution') else 'N'} "
            f"text={text!r}"
        )
    if payload.get("anomalies"):
        lines.append("")
        lines.append("Anomalies (first 20):")
        for item in (payload.get("anomalies") or [])[:20]:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def run_b2_11_phase3_dryrun(
    project_root: Path | str,
    *,
    app: Any = None,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    """
    Phase1 → Phase2 → Phase3 dry-run with stable anchors.
    Never calls Phase4. Rolls back incidental DB writes from Phase2 skill persistence.
    """
    from core.ai_analyzer import get_model, gemini_model_name
    from core.ai_wrapper import resolve_gemini_api_key
    import core.textbook_processor_v2 as tpv2
    from models import db

    root = Path(project_root)
    ensure = ensure_b2_11_latex_docx(root)
    if ensure.get("status") != "ok" or not ensure.get("latex_docx"):
        return {"status": ensure.get("status") or "missing_latex_docx", "ensure": ensure}

    latex_path = Path(ensure["latex_docx"])
    original_name = Path(ensure.get("original_docx") or latex_path).name
    curriculum_info = build_b2_11_curriculum_info(latex_path, original_name)

    api_key, key_source = resolve_gemini_api_key()
    if not api_key:
        return {
            "status": "missing_gemini_api_key",
            "message": "Set GEMINI_API_KEY or GOOGLE_API_KEY in environment / .env",
            "required_env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "ensure": ensure,
        }

    tracker = GeminiUsageTracker()
    logs: list[str] = []
    task_q: queue.Queue = queue.Queue()
    ctx = app.app_context() if app is not None else None
    entered = False
    model_name = None

    try:
        if ctx is not None:
            ctx.__enter__()
            entered = True

        # Warm model and wrap generate_content for usage tracking.
        model = get_model("architect")
        model_name = gemini_model_name or getattr(model, "model_name", None)
        tracker.wrap_model(model)

        lines = tpv2.phase1_extract_docx_lines(str(latex_path))
        blocks = tpv2.phase2_deterministic_block_slice(
            lines,
            source_scope=str(curriculum_info.get("source_scope") or "section_textbook"),
            curriculum_info=curriculum_info,
        )
        # Must read module attribute after Phase2 rebinds the global.
        block_meta = dict(tpv2._DOCX_BLOCK_META or {})
        if not block_meta:
            block_meta = {
                k: {
                    "anchor": k,
                    "source_type": "",
                    "problem_text": v,
                    "section_code": curriculum_info.get("section_code"),
                }
                for k, v in (blocks or {}).items()
            }

        # Exact V2 phase3 invocation uses sorted(question_blocks.keys())
        phase3_keys = sorted(blocks.keys()) if blocks else sorted(block_meta.keys())
        phase3_parsed = tpv2.phase3_ai_metadata_alignment(phase3_keys, curriculum_info, task_q)

        while not task_q.empty():
            logs.append(str(task_q.get_nowait()))

        joined = build_dryrun_questions(block_meta, phase3_parsed, curriculum_info)
        gemini_summary = tracker.summary()
        gemini_summary["model"] = model_name
        gemini_summary["api_key_source"] = key_source

        out_path = Path(output_path) if output_path else (root / DRYRUN_DIR / DEFAULT_DRYRUN_NAME)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "status": "ok",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "curriculum": curriculum_info.get("curriculum"),
            "publisher": curriculum_info.get("publisher"),
            "volume": curriculum_info.get("volume"),
            "chapter": curriculum_info.get("chapter"),
            "section": curriculum_info.get("section"),
            "section_code": curriculum_info.get("section_code"),
            "chapter_index": curriculum_info.get("chapter_index"),
            "latex_docx_path": str(latex_path),
            "original_docx_path": ensure.get("original_docx"),
            "converted_now": ensure.get("converted_now"),
            "phase1_line_count": len(lines),
            "phase2_block_keys": list(block_meta.keys()),
            "phase2_block_meta_fields": sorted(
                {field for meta in block_meta.values() for field in meta.keys()}
            ),
            "phase3_raw": phase3_parsed,
            "questions": joined["questions"],
            "stats": joined["stats"],
            "anomalies": joined["anomalies"],
            "anchor_summary": joined["anchor_summary"],
            "gemini": gemini_summary,
            "logs": logs,
            "phase4_executed": False,
            "db_committed": False,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["dryrun_json_path"] = str(out_path)
        payload["human_summary"] = format_human_summary(payload)
        summary_path = out_path.with_suffix(".summary.txt")
        summary_path.write_text(payload["human_summary"], encoding="utf-8")
        payload["summary_path"] = str(summary_path)
        return payload
    except Exception as exc:
        return {
            "status": "dryrun_failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "latex_docx_path": str(latex_path),
            "gemini": tracker.summary(),
            "logs": logs,
            "ensure": ensure,
        }
    finally:
        tracker.restore()
        if entered:
            try:
                db.session.rollback()
            except Exception:
                pass
            ctx.__exit__(None, None, None)
