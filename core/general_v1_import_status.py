# -*- coding: utf-8 -*-
"""In-memory task status for 普高 (curriculum=general) V1 imports started from /textbook_importer_v3.

The V1 worker already reports progress as queue messages; ``GeneralV1StatusQueue`` keeps
forwarding them unchanged (SSE ``importer_stream`` still works) and maps the existing log
markers onto the V3 page's processing steps. Values the importer never reports stay ``None``.
"""
from __future__ import annotations

import ast
import queue
import re
import threading
import time
from collections import OrderedDict
from typing import Any

PIPELINE = "general_v1"
STAGES = (
    "file_validation",
    "word_parse",
    "equation_convert",
    "question_parse",
    "curriculum_binding",
    "ai_alignment",
    "db_write",
    "pdf_alignment",
    "asset_linking",
)
_MAX_TASKS = 50
_ERROR_MAX_CHARS = 300

_TASKS: "OrderedDict[str, GeneralV1ImportStatus]" = OrderedDict()
_TASKS_LOCK = threading.Lock()

_RE_EXTRACT = re.compile(r"正在從 .* 提取內容")
_RE_MATHTYPE = re.compile(
    r"\[MATHTYPE CONVERT\] ole=(\d+) converted=(\d+) failed=(\d+) eq_fields=(\d+) eq_converted=(\d+)"
)
_RE_BLOCK_SCAN = re.compile(r"\[DOCX BLOCK SCAN\] question_blocks=(\d+)")
_RE_AI_START = re.compile(r"AI 內容解析")
_RE_AI_ATTEMPT = re.compile(r"attempt \d+/\d+")
_RE_HYDRATE = re.compile(r"\[DOCX HYDRATE\]")
_RE_RETURNED_TITLES = re.compile(r"\[IMPORT INVENTORY GUARD\] returned_titles_count=(\d+)")
_RE_DB_START = re.compile(r"正在將解析結果寫入資料庫")
_RE_SKILL_BIND = re.compile(r"\[PRACTICE IMPORT\] detected .*\bskill_id=(\S+)")
_RE_PDF_VISUAL = re.compile(r"\[PDF VISUAL\] ok=(\w+) statuses=(\{.*?\})")
_RE_PDF_SKIPPED = re.compile(r"\[PDF VISUAL\] skipped")
_RE_IMPORT_COMPLETE = re.compile(
    r"Import complete: skills=(\d+),.*?examples=(\d+), practices=(\d+),.*?needs_review=(\d+), skipped=(\d+)"
)
_VISUAL_REVIEW_STATUSES = ("VISUAL_UNCERTAIN", "VISUAL_REQUIRED_MISSING")


def _add(current: int | None, value: int) -> int:
    return (current or 0) + value


def safe_error_summary(message: Any) -> str:
    text = str(message or "").strip()
    if "Traceback (most recent call last)" in text:
        text = text.split("Traceback (most recent call last)", 1)[0].strip()
    first_line = text.splitlines()[0] if text else ""
    return first_line[:_ERROR_MAX_CHARS] or "匯入失敗"


class GeneralV1ImportStatus:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self._lock = threading.Lock()
        self.state = "queued"
        self.message = "已排入匯入佇列"
        self.stages = {stage: "pending" for stage in STAGES}
        self.stages["file_validation"] = "done"
        self.current_pair = None
        self.pair_index = 0
        self.pair_total = 0
        self.pairs: list[dict[str, Any]] = []
        self._pair_open = False
        self.error: dict[str, str] | None = None
        self.skill_ids: set[str] = set()
        self.counts: dict[str, Any] = {
            "source_pairs": None,
            "successful_pairs": 0,
            "failed_pairs": 0,
            "docx_files": None,
            "pdf_files": None,
            "parsed_questions": None,
            "imported_questions": None,
            "existing_reused_questions": None,
            "formal_skills_created": None,
            "question_needs_review": None,
            "gemini_requests": None,
            "mathtype_found": None,
            "mathtype_converted": None,
            "eq_fields": None,
            "formula_failures": None,
            "question_blocks": None,
            "visual_attached": None,
            "visual_needs_review": None,
            "pdf_visual_status_counts": None,
        }
        self.updated_at = time.time()

    # ---- worker lifecycle -------------------------------------------------
    def start(self, grouped_files: list[tuple[str, str | None]]) -> None:
        with self._lock:
            docx = [d for d, _pdf in grouped_files if str(d).lower().endswith((".docx", ".doc"))]
            self.state = "running"
            self.message = "教材解析中"
            self.pair_total = len(docx)
            self.counts["source_pairs"] = len(docx)
            self.counts["docx_files"] = len(docx)
            self.counts["pdf_files"] = sum(1 for d, pdf in grouped_files if pdf and d in docx)
            self._touch()

    def begin_pair(self, name: str, index: int) -> None:
        with self._lock:
            self.current_pair = name
            self.pair_index = index
            self._pair_open = True
            if self.stages["word_parse"] == "pending":
                self.stages["word_parse"] = "running"
            self._touch()

    def finish_pair(self, name: str, process_result: Any = None, exc: BaseException | None = None) -> None:
        with self._lock:
            if not self._pair_open:
                return
            self._pair_open = False
            status = str((process_result or {}).get("status") or "") if isinstance(process_result, dict) else ""
            if exc is None and status == "success":
                self.counts["successful_pairs"] += 1
                for stage, value in self.stages.items():
                    if value == "running":
                        self.stages[stage] = "done"
                self.pairs.append({"base_name": name, "status": "success", "message": ""})
            else:
                raw = exc if exc is not None else (process_result or {}).get("message") if isinstance(process_result, dict) else ""
                summary = safe_error_summary(raw)
                failed_stage = self.current_stage() or "word_parse"
                self.stages[failed_stage] = "failed"
                self.counts["failed_pairs"] += 1
                self.error = {"stage": failed_stage, "message": summary}
                self.pairs.append({"base_name": name, "status": "failed", "message": summary})
            self._touch()

    def finish(self) -> None:
        with self._lock:
            if self.counts["successful_pairs"] == 0:
                self.state = "failed"
                if self.error is None:
                    self.error = {"stage": "file_validation", "message": "沒有可匯入的 DOCX 教材"}
                self.message = "教材匯入失敗"
            else:
                self.state = "completed"
                self.message = "教材匯入完成"
            self._touch()

    def fail(self, exc: BaseException | str) -> None:
        with self._lock:
            failed_stage = self.current_stage() or "file_validation"
            self.stages[failed_stage] = "failed"
            self.error = {"stage": failed_stage, "message": safe_error_summary(exc)}
            self.state = "failed"
            self.message = "教材匯入失敗"
            self._touch()

    # ---- queue message observation ---------------------------------------
    def observe(self, message: Any) -> None:
        text = str(message or "")
        with self._lock:
            self._observe_locked(text)
            self._touch()

    def _set(self, stage: str, value: str) -> None:
        if self.stages.get(stage) != "failed":
            self.stages[stage] = value

    def _observe_locked(self, text: str) -> None:
        c = self.counts
        if _RE_EXTRACT.search(text):
            self._set("word_parse", "running")
            return
        m = _RE_MATHTYPE.search(text)
        if m:
            ole, converted, failed, eq_fields, eq_converted = (int(x) for x in m.groups())
            c["mathtype_found"] = _add(c["mathtype_found"], ole)
            c["mathtype_converted"] = _add(c["mathtype_converted"], converted)
            c["eq_fields"] = _add(c["eq_fields"], eq_fields)
            c["formula_failures"] = _add(c["formula_failures"], failed + max(0, eq_fields - eq_converted))
            self._set("word_parse", "done")
            self._set("equation_convert", "done")
            return
        m = _RE_BLOCK_SCAN.search(text)
        if m:
            c["question_blocks"] = _add(c["question_blocks"], int(m.group(1)))
            self._set("word_parse", "done")
            if self.stages["equation_convert"] == "pending":
                self._set("equation_convert", "skipped")
            self._set("question_parse", "running")
            return
        if _RE_AI_START.search(text):
            self._set("ai_alignment", "running")
            return
        if _RE_AI_ATTEMPT.search(text):
            c["gemini_requests"] = _add(c["gemini_requests"], 1)
            return
        if _RE_HYDRATE.search(text):
            self._set("ai_alignment", "done")
            return
        m = _RE_RETURNED_TITLES.search(text)
        if m:
            c["parsed_questions"] = _add(c["parsed_questions"], int(m.group(1)))
            self._set("question_parse", "done")
            return
        if _RE_DB_START.search(text):
            self._set("curriculum_binding", "running")
            self._set("db_write", "running")
            return
        m = _RE_SKILL_BIND.search(text)
        if m:
            self.skill_ids.add(m.group(1))
            return
        m = _RE_PDF_VISUAL.search(text)
        if m:
            self._set("curriculum_binding", "done")
            self._set("db_write", "done")
            try:
                statuses = ast.literal_eval(m.group(2))
            except (ValueError, SyntaxError):
                statuses = {}
            statuses = {str(k): int(v) for k, v in (statuses or {}).items()}
            merged = dict(c["pdf_visual_status_counts"] or {})
            for key, value in statuses.items():
                merged[key] = merged.get(key, 0) + value
            c["pdf_visual_status_counts"] = merged
            c["visual_attached"] = _add(c["visual_attached"], statuses.get("VISUAL_ATTACHED", 0))
            c["visual_needs_review"] = _add(
                c["visual_needs_review"], sum(statuses.get(k, 0) for k in _VISUAL_REVIEW_STATUSES)
            )
            ok = m.group(1) == "True"
            self._set("pdf_alignment", "done" if ok else "failed")
            self._set("asset_linking", "done" if ok else "failed")
            return
        if _RE_PDF_SKIPPED.search(text):
            self._set("pdf_alignment", "skipped")
            self._set("asset_linking", "skipped")
            return
        m = _RE_IMPORT_COMPLETE.search(text)
        if m:
            created, examples, practices, needs_review, skipped = (int(x) for x in m.groups())
            c["formal_skills_created"] = _add(c["formal_skills_created"], created)
            c["imported_questions"] = _add(c["imported_questions"], examples + practices)
            c["question_needs_review"] = _add(c["question_needs_review"], needs_review)
            c["existing_reused_questions"] = _add(c["existing_reused_questions"], skipped)
            self._set("curriculum_binding", "done")
            self._set("db_write", "done")

    # ---- read side ---------------------------------------------------------
    def current_stage(self) -> str | None:
        for stage in STAGES:
            if self.stages[stage] == "running":
                return stage
        return None

    def _touch(self) -> None:
        self.updated_at = time.time()

    def _result(self) -> dict[str, Any]:
        c = dict(self.counts)
        created = c["formal_skills_created"]
        reused = None
        if self.skill_ids:
            reused = max(0, len(self.skill_ids) - (created or 0))
        needs_review = None
        if c["question_needs_review"] is not None or c["visual_needs_review"] is not None:
            needs_review = (c["question_needs_review"] or 0) + (c["visual_needs_review"] or 0)
        c.update(
            {
                "formal_skills_reused": reused,
                "bound_skill_ids": sorted(self.skill_ids),
                "needs_review": needs_review,
                "pairs": list(self.pairs),
            }
        )
        return c

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "ok": True,
                "task_id": self.task_id,
                "pipeline": PIPELINE,
                "state": self.state,
                "current_stage": self.current_stage(),
                "completed_stages": [s for s in STAGES if self.stages[s] == "done"],
                "stages": dict(self.stages),
                "message": self.message,
                "current_pair": self.current_pair,
                "pair_index": self.pair_index,
                "pair_total": self.pair_total,
                "result": self._result(),
                "error": dict(self.error) if self.error else None,
            }


class GeneralV1StatusQueue(queue.Queue):
    """V1 task queue that also feeds the general task status."""

    def __init__(self, status: GeneralV1ImportStatus):
        super().__init__()
        self.general_status = status

    def put(self, item, block=True, timeout=None):
        try:
            self.general_status.observe(item)
        finally:
            super().put(item, block, timeout)


def register_general_v1_task(task_id: str) -> GeneralV1StatusQueue:
    status = GeneralV1ImportStatus(task_id)
    with _TASKS_LOCK:
        _TASKS[task_id] = status
        while len(_TASKS) > _MAX_TASKS:
            _TASKS.popitem(last=False)
    return GeneralV1StatusQueue(status)


def get_general_v1_task_snapshot(task_id: str) -> dict[str, Any] | None:
    with _TASKS_LOCK:
        status = _TASKS.get(task_id)
    return status.snapshot() if status else None
