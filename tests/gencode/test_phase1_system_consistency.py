# -*- coding: utf-8 -*-
"""System consistency tests for Phase 1 classifier registry and taxonomy.

Ensures that all registered skills are fully aligned between the taxonomy,
domain operations, rule packs, and python classifiers.
"""
from __future__ import annotations

import re
import yaml
from pathlib import Path
import pytest

from core.registry.taxonomy_registry import resolve_domain_for_skill
from core.registry.domain_operation_registry import get_domain_operations
from core.gencode.pipeline_orchestrator import _skill_has_python_classifier, _load_registered_classifier_rulepack

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Active V3 skills with Phase 1 custom classifiers enabled
ACTIVE_V3_PHASE1_SKILLS = {
    "vh_數學B1_AbsoluteValue",
    "vh_數學B1_AbsoluteValueInequality",
    "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning",
}


def test_active_v3_skills_resolve_domain() -> None:
    """Every active V3 skill with Phase 1 enabled must resolve its domain successfully."""
    yaml_path = PROJECT_ROOT / "configs" / "gencode_taxonomy" / "k12_component_taxonomy.yaml"
    assert yaml_path.is_file(), f"Taxonomy file missing: {yaml_path}"
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    skills = data.get("skills", {})
    assert skills, "No skills found in k12_component_taxonomy.yaml"
    
    for skill_id in ACTIVE_V3_PHASE1_SKILLS:
        assert skill_id in skills, f"Active V3 skill {skill_id} missing from k12_component_taxonomy.yaml"
        
        # Should not raise SkillDomainNotRegisteredError
        routing = resolve_domain_for_skill(skill_id)
        assert routing, f"Skill {skill_id} failed to resolve domain routing details"
        
        # Verify allowed types exist in the registered domain operations
        allowed_types = routing.get("allowed_types") or []
        fixed_domain_key = routing.get("fixed_domain_key")
        registered_ops = get_domain_operations(fixed_domain_key)
        
        for t in allowed_types:
            assert t in registered_ops, (
                f"Skill {skill_id}: Capability '{t}' specified in taxonomy is not "
                f"registered in domain operations for domain '{fixed_domain_key}'"
            )


def test_active_v3_python_classifiers_exist_in_taxonomy() -> None:
    """Every active V3 Python classifier skill must exist in the taxonomy."""
    init_path = PROJECT_ROOT / "core" / "gencode" / "classifiers" / "__init__.py"
    assert init_path.is_file(), f"Classifiers init file missing: {init_path}"
    
    with open(init_path, "r", encoding="utf-8") as f:
        init_code = f.read()
        
    yaml_path = PROJECT_ROOT / "configs" / "gencode_taxonomy" / "k12_component_taxonomy.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        taxonomy_data = yaml.safe_load(f)
    taxonomy_skills = set(taxonomy_data.get("skills", {}).keys())
    
    # Extract registered skill IDs from get_classifier_for_skill sid checks
    registered_sids = re.findall(r'sid\s*==\s*"([^"]+)"', init_code)
    
    for s in registered_sids:
        # Only verify consistency for the active V3 Phase 1 scope
        if s in ACTIVE_V3_PHASE1_SKILLS:
            assert s in taxonomy_skills, (
                f"Active skill {s} is registered in get_classifier_for_skill but "
                f"is missing from configs/gencode_taxonomy/k12_component_taxonomy.yaml"
            )
