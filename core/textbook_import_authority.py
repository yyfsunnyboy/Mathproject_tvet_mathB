# -*- coding: utf-8 -*-
"""
Math B V2 DOCX 匯入：統一座標與 policy 權威決策（evidence -> authority -> execution）。

Phase2 / Phase4 不得各自猜測 chapter / section / skill policy；
一律透過 ImportAuthorityResolver。
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Callable

from core.textbook_filename_parser import (
    detect_docx_source_scope_from_content,
    merge_source_scope_detection,
    parse_textbook_filename_metadata,
)
from core.textbook_processor import extract_section_code_from_title
from models import SkillCurriculum

LogFn = Callable[[str], None]

_log_fn: LogFn | None = None

SKILL_POLICIES = frozenset(
    {
        "create_or_reuse_from_docx_heading",
        "use_existing_only",
        "readonly_outline_only",
        "skip_needs_review",
    }
)

SCOPE_SECTION_TEXTBOOK = "section_textbook"
SCOPE_CHAPTER_SELF_ASSESSMENT = "chapter_self_assessment"

_FALLBACK_SKILL_ID_RE = re.compile(
    r"SelfAssessment|MixedExercise|UnknownConcept|UnknownFormalConcept|Concept_|ConceptHash|SubSection_",
    re.IGNORECASE,
)


def set_authority_log_fn(fn: LogFn | None) -> None:
    global _log_fn
    _log_fn = fn


def _log(msg: str) -> None:
    if _log_fn:
        _log_fn(msg)
        return
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            current_app.logger.info(msg)
    except Exception:
        pass


def normalize_section_code(raw: str) -> str:
    text = unicodedata.normalize("NFKC", str(raw or "").strip())
    if not text or text.endswith("-review"):
        return ""
    m = re.match(r"^(\d+-\d+)", text)
    return m.group(1) if m else ""


def section_code_from_concept_code(concept_code: str) -> str:
    cc = unicodedata.normalize("NFKC", str(concept_code or "").strip())
    m = re.match(r"^(\d+-\d+)\.\d+", cc)
    return normalize_section_code(m.group(1) if m else "")


def is_chapter_self_assessment_scope(source_scope: str) -> bool:
    return str(source_scope or "").strip() in (
        SCOPE_CHAPTER_SELF_ASSESSMENT,
        "chapter_review",
    )


def is_fallback_skill_id(skill_id: str) -> bool:
    sid = str(skill_id or "").strip()
    if not sid:
        return True
    return bool(_FALLBACK_SKILL_ID_RE.search(sid))


def section_code_boundary_matches(section_code: str, section_label: str) -> bool:
    code = unicodedata.normalize("NFKC", str(section_code or "").strip())
    label = unicodedata.normalize("NFKC", str(section_label or "").strip())
    if not code or not label.startswith(code):
        return False
    if len(label) == len(code):
        return True
    return label[len(code)] in " \t\u3000.-：:"


def extract_section_code_from_block_key(block_key: str) -> str:
    m = re.search(r"(\d+-\d+)", str(block_key or ""))
    return normalize_section_code(m.group(1) if m else "")


@dataclass
class ImportEvidence:
    """匯入決策前收集的訊號（不可直接當最終座標）。"""

    source_scope_candidates: dict[str, str] = field(default_factory=dict)
    original_filename: str = ""
    parse_filename: str = ""
    filename_meta: dict[str, Any] = field(default_factory=dict)
    content_meta: dict[str, Any] = field(default_factory=dict)
    form_curriculum_info: dict[str, Any] = field(default_factory=dict)
    docx_section_headings: list[str] = field(default_factory=list)
    docx_concept_headings: list[str] = field(default_factory=list)
    block_meta: dict[str, Any] = field(default_factory=dict)
    matched_key: str = ""
    gemini_section_title: str = ""
    gemini_section_code: str = ""
    title: str = ""


@dataclass
class ImportAuthority:
    """匯入執行層使用的權威座標與 policy。"""

    source_scope: str = SCOPE_SECTION_TEXTBOOK
    curriculum: str = "vocational"
    grade: int = 10
    volume: str = ""
    chapter_title: str = ""
    section_code: str = ""
    section_title: str = ""
    concept_code: str = ""
    concept_name: str = ""
    skill_policy: str = "skip_needs_review"
    authority_source: str = ""
    outline_skill_id: str = ""
    section_source: str = ""
    form_section_code: str = ""
    overrode_form: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_scope": self.source_scope,
            "curriculum": self.curriculum,
            "grade": self.grade,
            "volume": self.volume,
            "chapter_title": self.chapter_title,
            "section_code": self.section_code,
            "section_title": self.section_title,
            "concept_code": self.concept_code,
            "concept_name": self.concept_name,
            "skill_policy": self.skill_policy,
            "authority_source": self.authority_source,
            "outline_skill_id": self.outline_skill_id,
            "section_source": self.section_source,
            "form_section_code": self.form_section_code,
            "overrode_form": self.overrode_form,
            "warnings": list(self.warnings),
        }


class ImportAuthorityResolver:
    """集中處理 source_scope、section_code、outline 座標與 skill policy。"""

    @staticmethod
    def import_scope_coords(curriculum_info: dict | None) -> dict[str, Any]:
        info = dict(curriculum_info or {})
        return {
            "curriculum": str(info.get("curriculum") or "vocational").strip(),
            "volume": str(info.get("volume") or "").strip(),
            "grade": int(info.get("grade") or 10),
        }

    @staticmethod
    def skill_policy_for_scope(source_scope: str) -> str:
        if is_chapter_self_assessment_scope(source_scope):
            return "use_existing_only"
        return "create_or_reuse_from_docx_heading"

    @staticmethod
    def resolve_import_source_scope(
        parse_filename: str,
        lines: list[str],
        curriculum_info: dict | None,
    ) -> tuple[str, ImportEvidence, dict[str, Any]]:
        """
        單一 source_scope 決策；回傳 (final_scope, evidence, updated_curriculum_info)。
        """
        info = dict(curriculum_info or {})
        filename_meta = parse_textbook_filename_metadata(parse_filename)
        filename_meta["parse_filename"] = parse_filename
        content_meta = detect_docx_source_scope_from_content(lines, curriculum_info)
        merged = merge_source_scope_detection(filename_meta, content_meta)

        fn_scope = str(filename_meta.get("source_scope") or SCOPE_SECTION_TEXTBOOK).strip()
        ct_scope = str(content_meta.get("source_scope") or "").strip()
        form_scope = str(info.get("source_scope") or "").strip()

        final_scope = str(merged.get("source_scope") or SCOPE_SECTION_TEXTBOOK).strip()
        if is_chapter_self_assessment_scope(final_scope):
            final_scope = SCOPE_CHAPTER_SELF_ASSESSMENT

        source = "filename_meta"
        if fn_scope == SCOPE_CHAPTER_SELF_ASSESSMENT:
            source = "filename_meta"
        elif ct_scope == SCOPE_CHAPTER_SELF_ASSESSMENT and final_scope == SCOPE_CHAPTER_SELF_ASSESSMENT:
            source = "content_meta"
        elif fn_scope == SCOPE_SECTION_TEXTBOOK and filename_meta.get("section_code"):
            source = "filename_meta"
        elif ct_scope == SCOPE_SECTION_TEXTBOOK and content_meta.get("section_code"):
            source = "content_meta"
        elif form_scope in (SCOPE_CHAPTER_SELF_ASSESSMENT, SCOPE_SECTION_TEXTBOOK):
            source = "form"
            final_scope = form_scope
        else:
            source = "default"

        evidence = ImportEvidence(
            source_scope_candidates={
                "filename": fn_scope,
                "content": ct_scope,
                "form": form_scope,
            },
            original_filename=str(info.get("original_filename") or parse_filename),
            parse_filename=parse_filename,
            filename_meta=filename_meta,
            content_meta=content_meta,
            form_curriculum_info=info,
        )

        _log(
            "[SOURCE_SCOPE_AUTHORITY] "
            f"filename_scope={fn_scope!r} content_scope={ct_scope!r} "
            f"form_scope={form_scope!r} final_scope={final_scope!r} source={source!r}"
        )

        info["source_scope"] = final_scope
        info["filename_meta"] = filename_meta
        if merged.get("chapter_index") is not None:
            info["chapter_index"] = merged["chapter_index"]

        form_section_code = normalize_section_code(str(info.get("section_code") or ""))
        info["form_section_code"] = form_section_code

        file_section_code = normalize_section_code(str(filename_meta.get("section_code") or ""))
        if file_section_code:
            info["filename_section_code"] = file_section_code

        if final_scope == SCOPE_CHAPTER_SELF_ASSESSMENT:
            info["section_code"] = ""
        elif file_section_code:
            if form_section_code and form_section_code != file_section_code:
                _log(
                    "[SECTION_CODE_OVERRIDE] "
                    f"form_section_code={form_section_code!r} "
                    f"resolved_section_code={file_section_code!r} "
                    f"source=filename_meta reason=form_stale_or_conflict"
                )
            info["section_code"] = file_section_code
        elif merged.get("section_code"):
            merged_code = normalize_section_code(str(merged.get("section_code") or ""))
            if merged_code:
                info["section_code"] = merged_code
        elif form_section_code:
            info["section_code"] = form_section_code

        volume_hint = str(filename_meta.get("volume_hint") or "").strip()
        if volume_hint and not str(info.get("volume") or "").strip():
            info["volume"] = volume_hint

        return final_scope, evidence, info

    @staticmethod
    def resolve_section_authority(
        *,
        source_scope: str,
        curriculum_info: dict | None,
        filename_meta: dict | None = None,
        content_meta: dict | None = None,
        block_meta: dict | None = None,
        matched_key: str = "",
        gemini_section_code: str = "",
        gemini_section_title: str = "",
        title: str = "",
        concept_code: str = "",
        docx_section_code: str = "",
        phase4: bool = False,
    ) -> dict[str, Any]:
        """單一 section_code 權威決策。"""
        info = dict(curriculum_info or {})
        meta = dict(block_meta or {})
        fn_meta = dict(filename_meta or info.get("filename_meta") or {})
        ct_meta = dict(content_meta or info.get("content_meta") or {})
        form_code = normalize_section_code(
            str(info.get("form_section_code") or info.get("section_code") or "")
        )

        from_concept = section_code_from_concept_code(
            str(concept_code or meta.get("concept_code") or "")
        )
        from_block = normalize_section_code(str(meta.get("section_code") or ""))
        from_filename = normalize_section_code(
            str(fn_meta.get("section_code") or info.get("filename_section_code") or "")
        )
        from_content = normalize_section_code(str(ct_meta.get("section_code") or ""))
        if not from_content and ct_meta.get("section_codes"):
            codes = ct_meta.get("section_codes") or []
            if len(codes) == 1:
                from_content = normalize_section_code(str(codes[0]))
        from_docx = normalize_section_code(docx_section_code) or extract_section_code_from_title(
            str(meta.get("section_title") or "")
        )
        from_key = extract_section_code_from_block_key(matched_key)
        from_gemini = normalize_section_code(gemini_section_code) or extract_section_code_from_title(
            gemini_section_title
        )
        from_title = extract_section_code_from_title(title)
        from_title = normalize_section_code(from_title) if from_title else ""

        is_sa = is_chapter_self_assessment_scope(source_scope)

        if is_sa:
            chain: list[tuple[str, str]] = [
                (from_block, "block_meta"),
                (from_key, "matched_key"),
                (from_gemini, "gemini"),
                (from_title, "gemini"),
            ]
        elif phase4:
            chain = [
                (from_concept, "concept_heading"),
                (from_block, "block_meta"),
                (from_filename, "filename_meta"),
                (from_docx, "docx_heading"),
                (from_key, "matched_key"),
                (from_gemini, "gemini"),
                (from_title, "gemini"),
                (form_code, "form"),
            ]
        else:
            chain = [
                (from_concept, "concept_heading"),
                (from_block, "block_meta"),
                (from_filename, "filename_meta"),
                (from_content, "docx_heading"),
                (from_docx, "docx_heading"),
                (from_key, "matched_key"),
                (from_gemini, "gemini"),
                (from_title, "gemini"),
                (form_code, "form"),
            ]

        resolved = ""
        source = "none"
        for code, src in chain:
            if code:
                resolved = code
                source = src
                break

        overrode_form = bool(form_code and resolved and form_code != resolved and source != "form")
        if overrode_form:
            _log(
                "[SECTION_CODE_OVERRIDE] "
                f"form_section_code={form_code!r} resolved_section_code={resolved!r} "
                f"source={source!r} reason=higher_authority_than_form"
            )

        return {
            "section_code": resolved,
            "section_source": source,
            "form_section_code": form_code,
            "overrode_form": overrode_form,
            "source": source,
        }

    @staticmethod
    def lookup_outline_row(
        curriculum: str,
        volume: str,
        section_code: str,
    ) -> SkillCurriculum | None:
        curr = str(curriculum or "").strip()
        vol = str(volume or "").strip()
        code = normalize_section_code(section_code)
        if not curr or not vol or not code:
            return None
        prefix = f"{code} "
        candidates = (
            SkillCurriculum.query.filter(
                SkillCurriculum.curriculum == curr,
                SkillCurriculum.volume == vol,
                SkillCurriculum.section.startswith(prefix),
                SkillCurriculum.skill_id.startswith("outline_"),
            )
            .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
            .all()
        )
        bounded = [
            c
            for c in candidates
            if section_code_boundary_matches(code, str(getattr(c, "section", "") or ""))
        ]
        if not bounded:
            return None
        if len(bounded) == 1:
            return bounded[0]
        return min(
            bounded,
            key=lambda row: (
                len(str(getattr(row, "section", "") or "")),
                int(getattr(row, "display_order", 0) or 0),
                int(getattr(row, "id", 0) or 0),
            ),
        )

    @staticmethod
    def resolve_outline_authority(
        curriculum_info: dict | None,
        section_code: str,
        *,
        source_scope: str = SCOPE_SECTION_TEXTBOOK,
    ) -> ImportAuthority:
        """以 outline SkillCurriculum row 決定 chapter / section / volume。"""
        coords = ImportAuthorityResolver.import_scope_coords(curriculum_info)
        code = normalize_section_code(section_code)
        auth = ImportAuthority(
            source_scope=str(source_scope or SCOPE_SECTION_TEXTBOOK).strip(),
            curriculum=coords["curriculum"],
            grade=coords["grade"],
            volume=coords["volume"],
            section_code=code,
            skill_policy=ImportAuthorityResolver.skill_policy_for_scope(source_scope),
        )

        row = ImportAuthorityResolver.lookup_outline_row(
            auth.curriculum, auth.volume, code
        )
        if row is None:
            auth.skill_policy = "skip_needs_review"
            auth.authority_source = "missing_outline"
            auth.warnings.append("no_outline_row")
            _log(
                "[SECTION_COORD_MISSING] "
                f"section_code={code!r} curriculum={auth.curriculum!r} "
                f"volume={auth.volume!r} reason=no_outline_row"
            )
            return auth

        auth.chapter_title = str(getattr(row, "chapter", "") or "").strip()
        auth.section_title = str(getattr(row, "section", "") or "").strip()
        auth.volume = str(getattr(row, "volume", "") or auth.volume).strip()
        auth.outline_skill_id = str(getattr(row, "skill_id", "") or "").strip()
        auth.authority_source = "outline"
        auth.skill_policy = ImportAuthorityResolver.skill_policy_for_scope(source_scope)

        _log(
            "[SECTION_COORD_AUTHORITY] "
            f"section_code={code!r} chapter={auth.chapter_title!r} "
            f"section={auth.section_title!r} source=outline"
        )
        return auth

    @staticmethod
    def resolve_phase4_item_authority(
        *,
        source_scope: str,
        curriculum_info: dict | None,
        block_meta: dict | None,
        matched_key: str = "",
        gemini_section_code: str = "",
        gemini_section_title: str = "",
        title: str = "",
    ) -> ImportAuthority:
        """Phase4 單題：section_code -> outline -> policy。"""
        sec = ImportAuthorityResolver.resolve_section_authority(
            source_scope=source_scope,
            curriculum_info=curriculum_info,
            filename_meta=(curriculum_info or {}).get("filename_meta"),
            content_meta=(curriculum_info or {}).get("content_meta"),
            block_meta=block_meta,
            matched_key=matched_key,
            gemini_section_code=gemini_section_code,
            gemini_section_title=gemini_section_title,
            title=title,
            phase4=True,
        )
        auth = ImportAuthorityResolver.resolve_outline_authority(
            curriculum_info,
            sec["section_code"],
            source_scope=source_scope,
        )
        auth.section_source = sec.get("section_source") or sec.get("source") or ""
        auth.form_section_code = sec.get("form_section_code") or ""
        auth.overrode_form = bool(sec.get("overrode_form"))
        meta = dict(block_meta or {})
        auth.concept_code = str(meta.get("concept_code") or "").strip()
        auth.concept_name = str(meta.get("concept_name") or "").strip()

        _log(
            "[PHASE4_SECTION_CODE_AUTHORITY] "
            f"title={title!r} block_meta_section_code={meta.get('section_code')!r} "
            f"filename_section_code={(curriculum_info or {}).get('filename_section_code')!r} "
            f"matched_key_section_code={extract_section_code_from_block_key(matched_key)!r} "
            f"form_section_code={auth.form_section_code!r} "
            f"final_section_code={auth.section_code!r} source={auth.section_source!r}"
        )
        return auth

    @staticmethod
    def log_form_coord_override(
        curriculum_info: dict | None,
        outline_auth: ImportAuthority,
    ) -> None:
        info = dict(curriculum_info or {})
        form_chapter = str(info.get("chapter") or "").strip()
        form_section = str(info.get("section") or "").strip()
        if form_chapter and form_chapter != outline_auth.chapter_title:
            _log(
                "[CHAPTER_COORD_OVERRIDE] "
                f"form_chapter={form_chapter!r} resolved_chapter={outline_auth.chapter_title!r} "
                f"section_code={outline_auth.section_code!r} "
                f"reason=section_code_outline_authority"
            )
        if form_section and form_section != outline_auth.section_title:
            _log(
                "[CHAPTER_COORD_OVERRIDE] "
                f"form_section={form_section!r} resolved_section={outline_auth.section_title!r} "
                f"section_code={outline_auth.section_code!r} "
                f"reason=section_code_outline_authority"
            )


def resolve_section_code_with_authority(**kwargs: Any) -> dict[str, Any]:
    """向後相容 wrapper；請優先使用 ImportAuthorityResolver。"""
    mode = str(kwargs.pop("authority_mode", "import") or "import").strip()
    scope = str(kwargs.pop("source_scope", SCOPE_SECTION_TEXTBOOK) or SCOPE_SECTION_TEXTBOOK)
    result = ImportAuthorityResolver.resolve_section_authority(
        source_scope=scope,
        curriculum_info=kwargs.pop("curriculum_info", None),
        filename_meta=kwargs.pop("filename_meta", None),
        content_meta=kwargs.pop("content_meta", None),
        block_meta=kwargs.pop("block_meta", None),
        matched_key=kwargs.pop("matched_key", ""),
        gemini_section_code=kwargs.pop("gemini_section_code", ""),
        gemini_section_title=kwargs.pop("gemini_section_title", ""),
        title=kwargs.pop("title", ""),
        concept_code=kwargs.pop("concept_code", ""),
        docx_section_code=kwargs.pop("docx_section_code", ""),
        phase4=(mode == "phase4"),
    )
    result.setdefault("source", result.get("section_source", "none"))
    result.setdefault(
        "reason",
        "higher_authority_source" if result.get("overrode_form") else "",
    )
    return result
