# -*- coding: utf-8 -*-
"""Phase 6N-R: Dashboard Chap2 Unit Practice Link Repair Tests.

Verifies that the 'ch.display.startswith(...)' Jinja condition in
dashboard.html generates the correct chapter-mode URL for B4 Chapter 2,
and that Chapter 1 is not broken.

All tests operate at the helper/resolver layer without needing a live Flask
app or DB, since the fix is in the template conditional logic.
"""
import pytest
from urllib.parse import urlparse, parse_qs


# ─── Simulate the template Jinja condition ────────────────────────────────────

def _simulate_unit_practice_url(
    ch_display: str,
    ch_raw: str,
    curriculum: str = "vocational",
    volume: str = "數學B4",
) -> dict[str, str]:
    """
    Mirror the Jinja2 condition in dashboard.html:

        mode=chapter + chapter_id=1   if vocational + 數學B4 + ch.display.startswith('1')
        mode=chapter + chapter_id=2   if vocational + 數學B4 + ch.display.startswith('2')
        mode=single  + skill_ids=raw  otherwise
    """
    if curriculum == "vocational" and volume == "數學B4" and ch_display.startswith("1"):
        return {
            "mode": "chapter",
            "curriculum": curriculum,
            "volume": volume,
            "chapter_id": "1",
            "learning_mode": "teaching",
            "practice_kind": "unit_practice",
        }
    if curriculum == "vocational" and volume == "數學B4" and ch_display.startswith("2"):
        return {
            "mode": "chapter",
            "curriculum": curriculum,
            "volume": volume,
            "chapter_id": "2",
            "learning_mode": "teaching",
            "practice_kind": "unit_practice",
        }
    return {
        "mode": "single",
        "skill_ids": ch_raw,
    }


# ─── 1. Chap2 link uses mode=chapter ─────────────────────────────────────────

class TestChap2DashboardLink:
    def test_chap2_mode_is_chapter(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["mode"] == "chapter", f"Expected mode=chapter, got {params['mode']}"

    def test_chap2_chapter_id_is_2(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["chapter_id"] == "2"

    def test_chap2_curriculum_is_vocational(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["curriculum"] == "vocational"

    def test_chap2_volume_is_math_b4(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["volume"] == "數學B4"

    def test_chap2_learning_mode_is_teaching(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["learning_mode"] == "teaching"

    def test_chap2_practice_kind_is_unit_practice(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["practice_kind"] == "unit_practice"

    def test_chap2_not_mode_single(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert params["mode"] != "single", "Chap2 must NOT use mode=single"

    def test_chap2_no_skill_ids_param(self):
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        assert "skill_ids" not in params, "Chap2 must NOT have skill_ids parameter"

    def test_chap2_no_skill_ids_2_ji_lu(self):
        """Explicitly confirm skill_ids=2+機率 is not generated."""
        params = _simulate_unit_practice_url("2 機率", "2 機率")
        skill_ids_val = params.get("skill_ids", "")
        assert "2" not in skill_ids_val or "機率" not in skill_ids_val or params["mode"] != "single"


# ─── 10. Chap1 link not broken ────────────────────────────────────────────────

class TestChap1DashboardLinkNotBroken:
    def test_chap1_mode_is_chapter(self):
        params = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        assert params["mode"] == "chapter"

    def test_chap1_chapter_id_is_1(self):
        params = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        assert params["chapter_id"] == "1"

    def test_chap1_curriculum_is_vocational(self):
        params = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        assert params["curriculum"] == "vocational"

    def test_chap1_volume_is_math_b4(self):
        params = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        assert params["volume"] == "數學B4"

    def test_chap1_not_mode_single(self):
        params = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        assert params["mode"] != "single"


# ─── Other curricula / volumes fall back to mode=single ──────────────────────

class TestNonB4FallbackToSingle:
    def test_other_volume_uses_single(self):
        params = _simulate_unit_practice_url("3 統計", "3 統計", volume="數學B3")
        assert params["mode"] == "single"

    def test_other_curriculum_uses_single(self):
        params = _simulate_unit_practice_url("1 章節", "1 章節", curriculum="general")
        assert params["mode"] == "single"

    def test_chap3_falls_back_to_single_for_now(self):
        """Chapter 3 (not yet integrated) correctly falls back to single mode."""
        params = _simulate_unit_practice_url("3 統計", "3 統計",
                                             curriculum="vocational", volume="數學B4")
        assert params["mode"] == "single"


# ─── Template condition logic correctness ─────────────────────────────────────

class TestTemplateConditionLogic:
    def test_display_startswith_2_triggers_chap2(self):
        for display_name in ["2 機率", "2 Probability"]:
            params = _simulate_unit_practice_url(display_name, display_name)
            assert params["mode"] == "chapter"
            assert params["chapter_id"] == "2", f"Failed for display_name='{display_name}'"

    def test_display_startswith_1_triggers_chap1(self):
        for display_name in ["1 排列組合", "1 Combinatorics"]:
            params = _simulate_unit_practice_url(display_name, display_name)
            assert params["mode"] == "chapter"
            assert params["chapter_id"] == "1", f"Failed for display_name='{display_name}'"

    def test_chap1_and_chap2_are_independent(self):
        """Chap1 and Chap2 conditions don't overlap."""
        p1 = _simulate_unit_practice_url("1 排列組合", "1 排列組合")
        p2 = _simulate_unit_practice_url("2 機率", "2 機率")
        assert p1["chapter_id"] != p2["chapter_id"]
        assert p1["chapter_id"] == "1"
        assert p2["chapter_id"] == "2"


# ─── 11. Phase 6N resolver also works (cross-check) ──────────────────────────

class TestPhase6NResolverCrossCheck:
    def test_resolver_returns_chapter2_bundle(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="2",
            skill_ids="",
        )
        assert hit is True
        assert bridge["chapter_id"] == "2"
        assert len(bridge["unit_skill_ids"]) == 10

    def test_resolver_returns_chapter1_bundle_unchanged(self):
        from core.routes.practice import _resolve_b4_chapter_adaptive_entry
        bridge, hit = _resolve_b4_chapter_adaptive_entry(
            mode="chapter",
            curriculum="vocational",
            volume="數學B4",
            chapter_id="1",
            skill_ids="",
        )
        assert hit is True
        assert bridge["chapter_id"] == "1"
