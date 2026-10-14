"""Safe display normalization for known-corrupted mistake notebook notes."""

from __future__ import annotations


LEGACY_UNRECOVERABLE_NOTE = "\u875f\u990c\u7d5e\u877a\u6e21?\u61bf????"
UNRECOVERABLE_NOTE_MESSAGE = "舊資料內容因編碼異常無法還原。"


def normalize_mistake_notebook_note(note: object) -> object:
    """Replace only the audited legacy value whose original bytes are lost."""
    if note == LEGACY_UNRECOVERABLE_NOTE:
        return UNRECOVERABLE_NOTE_MESSAGE
    return note
