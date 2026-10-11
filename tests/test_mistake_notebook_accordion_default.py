"""Mistake notebook accordion: default open depth and preserved manual state (shared, not per skill)."""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "templates" / "mistake_notebook.html").read_text(encoding="utf-8")


def test_curriculum_volume_chapter_open_by_default_and_sections_closed():
    assert "DEFAULT_OPEN_LEVELS=3" in SOURCE
    assert "details.open=openState.has(key)?openState.get(key):level<DEFAULT_OPEN_LEVELS" in SOURCE


def test_manual_toggle_state_survives_rerender():
    assert "details.addEventListener('toggle',()=>openState.set(key,details.open))" in SOURCE
    assert "tree.replaceChildren(" in SOURCE
    assert "mistake-notebook:refresh" in SOURCE


def test_opening_a_section_reveals_cards_once_without_overriding_manual_state():
    assert "if(childName==='skills')details.addEventListener('toggle'" in SOURCE
    assert "if(!openState.has(skill.dataset.nodeKey))skill.open=true" in SOURCE
    assert "if(details.open&&loadEntries)loadEntries()" in SOURCE


def test_only_nodes_with_mistakes_are_rendered_and_nothing_is_hardcoded():
    assert ".filter(hasMistakes)" in SOURCE
    for hardcoded in ("B1", "數學B", "vh_", "jh_", "第1章"):
        assert hardcoded not in SOURCE
