"""Generic table-fill question contract normalization for practice UI."""

from __future__ import annotations

import re
from typing import Any

_ENGINEERING_KEY_RE = re.compile(r"^(lt|gt|part|field)_\d+$", re.IGNORECASE)
_BLANK_LABEL_MODES_SHOW = frozenset({"named_blanks", "reference_by_label"})
_BLANK_LABEL_MODES_HIDE = frozenset({"complete_table", "inline_input"})


def _stem_references_named_blanks(question_text: str, labels: list[str]) -> bool:
    """True when the stem explicitly asks for letter-labeled blanks (e.g. 試求 a, b, c, d)."""
    stem = str(question_text or "").strip()
    if not stem:
        return False
    alpha_labels = [lbl for lbl in labels if _is_student_facing_label(lbl)]
    if not alpha_labels:
        return False
    stem_lower = stem.lower()
    mentioned = sum(
        1
        for lbl in alpha_labels
        if re.search(rf"(?:^|[^a-z]){re.escape(lbl.lower())}(?:[^a-z]|$)", stem_lower)
    )
    if mentioned >= 2:
        return True
    if re.search(r"試求\s*[a-z]", stem, re.IGNORECASE):
        return True
    if re.search(r"求\s*[a-z]\s*[,、]", stem, re.IGNORECASE):
        return True
    return False


def _resolve_blank_label_display(
    table_data: dict[str, Any],
    *,
    question_text: str,
    enriched_blanks: list[dict[str, Any]],
) -> tuple[bool, str]:
    """Return (show_blank_labels, blank_label_mode) for table_fill UI."""
    mode_raw = str(table_data.get("blank_label_mode") or "").strip().lower()
    if table_data.get("show_blank_labels") is not None:
        show = bool(table_data.get("show_blank_labels"))
        mode = mode_raw or ("named_blanks" if show else "complete_table")
        return show, mode
    if mode_raw in _BLANK_LABEL_MODES_SHOW:
        return True, mode_raw
    if mode_raw in _BLANK_LABEL_MODES_HIDE:
        return False, mode_raw
    labels = [str(cell.get("label") or "") for cell in enriched_blanks]
    if _stem_references_named_blanks(question_text, labels):
        return True, "named_blanks"
    return False, "complete_table"


def _student_label_sequence(count: int) -> list[str]:
    labels: list[str] = []
    for index in range(count):
        if index < 26:
            labels.append(chr(ord("a") + index))
        else:
            labels.append(f"a{index - 25}")
    return labels


def _is_student_facing_label(text: str) -> bool:
    token = str(text or "").strip()
    if not token:
        return False
    if _ENGINEERING_KEY_RE.match(token):
        return False
    if len(token) <= 2 and token.isalpha():
        return True
    return False


def _sorted_blank_cells(cells: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in cells or []:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "row": int(item.get("row", 0)),
                "col": int(item.get("col", 0)),
                "label": str(item.get("label") or "").strip(),
                "field_key": str(item.get("field_key") or "").strip(),
                "expected_answer": item.get("expected_answer"),
                "input_type": str(item.get("input_type") or "number").strip() or "number",
            }
        )
    return sorted(normalized, key=lambda cell: (cell["row"], cell["col"]))


def _part_specs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
    if parts:
        return [dict(part) for part in parts if isinstance(part, dict)]
    subquestions = payload.get("subquestions") if isinstance(payload.get("subquestions"), list) else []
    return [
        {
            "key": str(sq.get("part") or f"part_{idx + 1}"),
            "label": str(sq.get("part") or f"part_{idx + 1}"),
            "expected_answer": sq.get("expected_answer"),
        }
        for idx, sq in enumerate(subquestions)
        if isinstance(sq, dict)
    ]


def _display_matrix(table_data: dict[str, Any]) -> list[list[Any]]:
    rows = table_data.get("display_rows") or table_data.get("rows") or table_data.get("visible_table") or []
    return [list(row) for row in rows if isinstance(row, (list, tuple))]


def is_fillable_table_payload(payload: dict[str, Any]) -> bool:
    table_data = payload.get("table_data")
    if not isinstance(table_data, dict):
        return False
    if table_data.get("legacy_readonly") or table_data.get("interaction_mode") == "readonly":
        return False
    blank_cells = table_data.get("blank_cells")
    return isinstance(blank_cells, list) and len(blank_cells) > 0


def is_readonly_table_payload(payload: dict[str, Any]) -> bool:
    table_data = payload.get("table_data")
    if not isinstance(table_data, dict):
        return False
    if table_data.get("legacy_readonly") or table_data.get("interaction_mode") == "readonly":
        return True
    blank_cells = table_data.get("blank_cells")
    has_blanks = isinstance(blank_cells, list) and len(blank_cells) > 0
    return bool(table_data.get("html")) and not has_blanks


def normalize_table_question_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy table_data + subquestions into unified table_fill contract."""
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    table_data = out.get("table_data")
    if not isinstance(table_data, dict):
        return out

    blank_cells = table_data.get("blank_cells")
    if not isinstance(blank_cells, list) or not blank_cells:
        if table_data.get("html") and not table_data.get("rows"):
            table_data = dict(table_data)
            table_data["legacy_readonly"] = True
            table_data["interaction_mode"] = "readonly"
            out["table_data"] = table_data
        return out

    table_data = dict(table_data)
    parts = _part_specs(out)
    sorted_blanks = _sorted_blank_cells(blank_cells)
    auto_labels = _student_label_sequence(len(sorted_blanks))
    enriched_blanks: list[dict[str, Any]] = []
    answer_order: list[str] = []

    for index, blank in enumerate(sorted_blanks):
        part = parts[index] if index < len(parts) else {}
        field_key = str(blank.get("field_key") or part.get("key") or f"field_{index + 1}").strip()
        existing_label = str(blank.get("label") or "").strip()
        part_label = str(part.get("label") or part.get("key") or "").strip()
        if _is_student_facing_label(existing_label):
            student_label = existing_label
        elif _is_student_facing_label(part_label):
            student_label = part_label
        else:
            student_label = auto_labels[index]
        expected = blank.get("expected_answer")
        if expected is None:
            expected = part.get("expected_answer")
        enriched = {
            "row": blank["row"],
            "col": blank["col"],
            "field_key": field_key,
            "label": student_label,
            "expected_answer": expected,
            "input_type": blank.get("input_type") or "number",
        }
        enriched_blanks.append(enriched)
        answer_order.append(field_key)

    display_rows = _display_matrix(table_data)
    if not display_rows:
        source_rows = table_data.get("rows") or []
        display_rows = [list(row) for row in source_rows if isinstance(row, (list, tuple))]
    blank_lookup = {(cell["row"], cell["col"]): cell for cell in enriched_blanks}
    show_blank_labels, blank_label_mode = _resolve_blank_label_display(
        table_data,
        question_text=str(out.get("question_text") or ""),
        enriched_blanks=enriched_blanks,
    )
    visible_rows: list[list[Any]] = []
    for row_idx, row in enumerate(display_rows):
        visible_row: list[Any] = []
        for col_idx, cell in enumerate(row):
            spec = blank_lookup.get((row_idx, col_idx))
            if spec:
                visible_row.append(spec["label"] if show_blank_labels else "")
            else:
                visible_row.append(cell)
        visible_rows.append(visible_row)

    table_data.update(
        {
            "type": "table_fill",
            "interaction_mode": "inline_input",
            "blank_label_mode": blank_label_mode,
            "show_blank_labels": show_blank_labels,
            "legacy_readonly": False,
            "blank_cells": enriched_blanks,
            "answer_order": answer_order,
            "display_rows": visible_rows,
            "visible_table": visible_rows,
            "show_caption": False,
        }
    )
    out["table_data"] = table_data
    out["table_question"] = {
        "type": "table_fill",
        "headers": list(table_data.get("headers") or []),
        "rows": visible_rows,
        "blank_cells": enriched_blanks,
        "answer_order": answer_order,
        "interaction_mode": "inline_input",
        "blank_label_mode": blank_label_mode,
        "show_blank_labels": show_blank_labels,
        "show_caption": table_data.get("show_caption", False),
        "title": str(table_data.get("title") or "").strip(),
    }

    ac = dict(out.get("answer_contract") or {})
    updated_parts: list[dict[str, Any]] = []
    for index, blank in enumerate(enriched_blanks):
        base = dict(parts[index]) if index < len(parts) else {}
        updated_parts.append(
            {
                **base,
                "key": blank["field_key"],
                "label": blank["label"],
                "field_key": blank["field_key"],
                "expected_answer": base.get("expected_answer", blank.get("expected_answer")),
                "checker": str(base.get("checker") or base.get("checker_key") or "integer_checker"),
                "equivalence_type": str(base.get("equivalence_type") or "numeric_exact"),
            }
        )
    if updated_parts:
        ac["parts"] = updated_parts
        ac.setdefault("answer_type", "multi_part")
        ac.setdefault("checker", "multi_part_answer_checker")
        ac.setdefault("checker_key", "multi_part_answer_checker")
        ui = dict(ac.get("ui_contract") or out.get("ui_contract") or {})
        ui.update({
            "response_mode": "table_fill",
            "text_input_enabled": True,
            "inline_table_inputs": True,
            "show_blank_labels": show_blank_labels,
            "blank_label_mode": blank_label_mode,
        })
        ac["ui_contract"] = ui
        out["answer_contract"] = ac
        out["ui_contract"] = ui
        out.setdefault("answer_type", "multi_part")

    student_subquestions = [
        {
            "part": blank["label"],
            "field_key": blank["field_key"],
            "prompt": "：____",
            "expected_answer": blank.get("expected_answer"),
        }
        for blank in enriched_blanks
    ]
    out["subquestions"] = student_subquestions
    return out


def normalize_table_student_answer(
    user_answer: Any,
    payload: dict[str, Any],
) -> Any:
    """Convert table-fill dict answers into ordered list for multi_part checker."""
    table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
    answer_order = table_data.get("answer_order") if isinstance(table_data.get("answer_order"), list) else []
    if not answer_order:
        return user_answer
    if isinstance(user_answer, dict):
        return [str(user_answer.get(key, "")).strip() for key in answer_order]
    if isinstance(user_answer, list):
        return user_answer
    return user_answer
