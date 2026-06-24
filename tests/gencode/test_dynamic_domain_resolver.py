import pytest
from core.gencode.skill_fixed_domain_authority import (
    resolve_fixed_domain_context,
    ComponentOverrideContext,
    SkillFixedDomainError,
)
from core.gencode.v3_error_codes import (
    DOMAIN_CAPABILITY_UNRESOLVED,
    DOMAIN_OVERRIDE_NOT_FOUND,
)

def test_dynamic_resolution_no_binding():
    # A. 無 skill binding 仍可解析
    ctx = resolve_fixed_domain_context("vh_數學B4_HistogramsAndFrequencyPolygons_Dummy")
    assert ctx.fixed_domain_key == "statistics.frequency_distribution"
    assert "frequency_table_construction_review" in ctx.allowed_operations

def test_explicit_override_priority():
    # B. Explicit override 優先
    ctx = resolve_fixed_domain_context("vh_數學B1_PointSlopeForm")
    assert ctx.fixed_domain_key == "coordinate_geometry.line_equation"

    # component-level explicit override takes top precedence
    with ComponentOverrideContext({"fixed_domain_key": "coordinate_geometry.point_line_distance"}):
        ctx_override = resolve_fixed_domain_context("vh_數學B1_PointSlopeForm")
        assert ctx_override.fixed_domain_key == "coordinate_geometry.point_line_distance"

def test_similar_skills_share_domain():
    # C. 相似 skill 共用 domain
    ctx1 = resolve_fixed_domain_context("vh_數學B4_HistogramsAndFrequencyPolygons_Alpha")
    ctx2 = resolve_fixed_domain_context("vh_數學B4_HistogramsAndFrequencyPolygons_Beta")
    assert ctx1.fixed_domain_key == "statistics.frequency_distribution"
    assert ctx2.fixed_domain_key == "statistics.frequency_distribution"

def test_component_isolation():
    # D. Component 隔離
    with ComponentOverrideContext({"fixed_domain_key": "invalid_domain"}):
        with pytest.raises(SkillFixedDomainError) as exc:
            resolve_fixed_domain_context("some_skill")
        assert exc.value.code == DOMAIN_OVERRIDE_NOT_FOUND

    # Outside the context, it falls back to normal dynamic resolution
    ctx = resolve_fixed_domain_context("vh_數學B4_HistogramsAndFrequencyPolygons_Dummy")
    assert ctx.fixed_domain_key == "statistics.frequency_distribution"

def test_complete_unresolvable_raises_unresolved():
    # F. 完全無法解析
    with pytest.raises(SkillFixedDomainError) as exc:
        resolve_fixed_domain_context("completely_unresolvable_random_skill_name_xyz")
    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED
