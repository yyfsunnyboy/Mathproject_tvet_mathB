"""The V3 entry is available for leaf skills before capability is ready."""

from pathlib import Path
import re

from flask import render_template
import pytest

from app import app


def test_v2_management_entry_points_are_removed():
    template = (Path(__file__).resolve().parents[2] / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    admin_routes = (Path(__file__).resolve().parents[2] / "core" / "routes" / "admin.py").read_text(encoding="utf-8")
    assert "regenerateSkillCode" not in template
    assert "admin_regenerate_skill_code" not in template
    assert "V2 舊版重建" not in template
    assert not any(rule.endpoint == "core.admin_regenerate_skill_code" for rule in app.url_map.iter_rules())
    assert not any(rule.rule == "/skills/<skill_id>/regenerate" for rule in app.url_map.iter_rules())
    assert "auto_generate_skill_code" not in admin_routes
    assert any(rule.endpoint == "core.admin_run_skill_v3_build" for rule in app.url_map.iter_rules())


@pytest.mark.parametrize(
    ("skill_id", "v3_ui", "allow_rebuild", "publish_ready", "expected"),
    [
        ("vh_數學B2_SubSection_2_1_1", "建立 V3", False, False, "建立 V3"),
        ("vh_數學B2_SubSection_2_1_2", "READY", True, True, "REBUILD"),
        ("vh_test_leaf", "NEEDS_CAPABILITY", False, False, "NEEDS_CAPABILITY"),
        ("outline_test_section", "建立 V3", False, False, None),
    ],
)
def test_v3_entry_visibility(skill_id, v3_ui, allow_rebuild, publish_ready, expected):
    skill = {
        "skill_id": skill_id,
        "skill_ch_name": "Test Skill",
        "is_active": True,
        "curriculum": "vocational",
        "grade": 10,
        "volume": "數學B2",
        "chapter": "2",
        "section": "2-1",
    }
    gencode = {
        "capability_status": (
            "ready"
            if v3_ui == "READY"
            else ("needs_capability" if v3_ui == "NEEDS_CAPABILITY" else "missing")
        ),
        "allow_v3_rebuild": allow_rebuild,
        "v3_ui_status": v3_ui,
        "publish_ready": publish_ready,
        "production_wrapper_exists": False,
        "v3_package_exists": False,
    }
    with app.test_request_context():
        html = render_template(
            "admin_skills.html",
            skills=[skill],
            v3_gencode_status_map={skill_id: gencode},
            gencode_status_map={},
            filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
            selected_filters={"f_curriculum": "all", "f_grade": "all", "f_volume": "all", "f_chapter": "all", "f_section": "all"},
            grade_map={},
            curriculum_map={},
            username="admin",
        )
    row = html.split('<td class="v3-cell">', 1)[1].split("</tr>", 1)[0]
    actions = row.split('class="v3-actions"', 1)[-1] if 'class="v3-actions"' in row else row
    compact_row = re.sub(r"\s+", " ", actions)
    if expected is None:
        assert "建立 V3" not in actions
        assert "REBUILD" not in compact_row
        assert "NEEDS_CAPABILITY" not in actions
    else:
        assert expected in actions
    assert "V2 舊版重建" not in row
