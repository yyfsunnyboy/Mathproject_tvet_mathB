"""Textbook-order practice: the student's "next question" walks the textbook's own order, one row at a time.

For a skill that has reviewed fixed textbook rows (``configs/fixed_textbook_practice.json``), the rows of the skill are ordered by the Stage 1
reading order (``notes.question_anchor.source_order``; never by id) and every row is served the way it can be practised:

* a published generator component ``src_<id>``   -> the dynamic question of that row (generator, checker and progress rules untouched);
* else a reviewed fixed entry                      -> the original textbook question (graded or self-check);
* else                                             -> skipped: it is not offered as practice.

Dynamic and fixed rows are one pool and one sequence.  Skills without fixed rows are not affected (the existing rotation stays in charge).
Nothing here writes to the database.
"""

from __future__ import annotations

import json
from typing import Any

from core.fixed_textbook_practice import entry_for_row

_LAST = 10 ** 9


def reading_order_key(row: Any) -> tuple[int, int]:
    """(Stage 1 reading order, id): the anchor's ``source_order`` is the authority, id only breaks ties / covers rows without an anchor."""
    try:
        notes = json.loads(getattr(row, "notes", None) or "{}")
        order = int((notes.get("question_anchor") or {}).get("source_order") or _LAST)
    except (TypeError, ValueError, AttributeError):
        order = _LAST
    return order, int(getattr(row, "id", 0) or 0)


def textbook_sequence(rows: list[Any], generator_keys: set[str] | frozenset[str]) -> list[dict[str, Any]]:
    """Practisable rows in textbook order with the way each one is served."""
    items: list[dict[str, Any]] = []
    for row in sorted(rows, key=reading_order_key):
        component_id = f"src_{row.id}"
        if component_id in generator_keys:
            items.append({"row": row, "kind": "dynamic", "component_id": component_id})
        elif entry_for_row(row) is not None:
            items.append({"row": row, "kind": "fixed", "component_id": None})
    return items


def pick_next_in_textbook_order(rows: list[Any], *, last_served_id: Any, generator_keys: set[str] | frozenset[str],
                                stay_on_last: bool = False) -> dict[str, Any] | None:
    """The row after ``last_served_id`` in the textbook sequence (the first one when there is no usable position; cyclic).  ``stay_on_last`` repeats ``last_served_id`` itself (resume of an unanswered row).

    Returns None - leaving the existing selection untouched - unless the skill has at least one fixed textbook row.
    """
    if not any(entry_for_row(row) is not None for row in rows):
        return None
    items = textbook_sequence(rows, generator_keys)
    if not items:
        return None
    try:
        last = int(str(last_served_id).strip())
    except (TypeError, ValueError):
        last = None
    ids = [item["row"].id for item in items]
    position = (ids.index(last) + (0 if stay_on_last else 1)) % len(items) if last in ids else 0
    return items[position]
