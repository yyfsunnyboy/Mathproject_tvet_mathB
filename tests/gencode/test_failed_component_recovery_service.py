# -*- coding: utf-8 -*-
"""Tests for Failed Component Recovery Orchestrator service with Exact Operation Readiness Gate."""

from __future__ import annotations

import json
import sqlite3
import importlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.services.failed_component_recovery_service import recover_failed_components

@pytest.fixture
def mem_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    
    conn.executemany(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        [
            (4401, "vh_數學B1_LinearFunction"),
            (4402, "vh_數學B1_LinearFunction")
        ]
    )
    
    save_tracker_record(
        conn,
        textbook_example_id=4401,
        skill_id="vh_數學B1_LinearFunction",
        gencode_status="failed",
        induced_spec_payload={"required_capabilities": ["some_cap"], "problem_type_id": "some_cap"},
        gencode_error_log="Old error"
    )
    save_tracker_record(
        conn,
        textbook_example_id=4402,
        skill_id="vh_數學B1_LinearFunction",
        gencode_status="failed",
        induced_spec_payload={"required_capabilities": ["some_cap"], "problem_type_id": "some_cap"},
        gencode_error_log="Old error"
    )
    
    conn.commit()
    return conn

def test_readiness_gates(mem_conn: sqlite3.Connection):
    """Test all partial_capability scenarios and a successful ready_to_rebuild scenario."""
    
    # Selective importlib mock helper to avoid interfering with mock.patch's own imports
    orig_import = importlib.import_module
    mock_mod = MagicMock()
    def selective_import(name, *args, **kwargs):
        if "coordinate_geometry" in name or name == "mock_domain":
            return mock_mod
        return orig_import(name, *args, **kwargs)

    # 1. Test: Domain exists but operation does not exist in registry -> partial_capability
    with patch("core.gencode.services.failed_component_recovery_service.resolve_domain_authority") as mock_resolve, \
         patch("core.registry.domain_operation_registry.get_domain_spec") as mock_dom_spec, \
         patch("core.registry.domain_operation_registry.get_operation_spec") as mock_op_spec:
         
        res = MagicMock()
        res.fixed_domain_key = "coordinate_geometry.line_equation"
        res.selected_operation = "some_cap"
        mock_resolve.return_value = res
        
        dom_spec = MagicMock()
        dom_spec.capabilities = {"some_cap"}
        dom_spec.domain_module = "core.domain.coordinate_geometry.line_equation_domain"
        mock_dom_spec.return_value = dom_spec
        
        mock_op_spec.return_value = None  # Registry missing operation spec
        
        report = recover_failed_components(
            skill_id="vh_數學B1_LinearFunction",
            dry_run=True,
            db_conn=mem_conn
        )
        
        assert report["per_component_generator_plan"]["src_4401"]["final_readiness"] == "partial_capability"
        assert "registry_operation_spec" in report["per_component_generator_plan"]["src_4401"]["missing_nodes"]

    # 2. Test: Operation spec exists but implementation function is missing in domain -> partial_capability
    with patch("core.gencode.services.failed_component_recovery_service.resolve_domain_authority") as mock_resolve, \
         patch("core.registry.domain_operation_registry.get_domain_spec") as mock_dom_spec, \
         patch("core.registry.domain_operation_registry.get_operation_spec") as mock_op_spec, \
         patch("importlib.import_module", side_effect=selective_import):
         
        res = MagicMock()
        res.fixed_domain_key = "coordinate_geometry.line_equation"
        res.selected_operation = "some_cap"
        mock_resolve.return_value = res
        
        dom_spec = MagicMock()
        dom_spec.capabilities = {"some_cap"}
        dom_spec.domain_module = "core.domain.coordinate_geometry.line_equation_domain"
        mock_dom_spec.return_value = dom_spec
        
        op_spec = MagicMock()
        op_spec.handler = "non_existent_function"
        op_spec.supported_presentation_modes = ("short_answer",)
        op_spec.supported_answer_types = ("multi_part",)
        mock_op_spec.return_value = op_spec
        
        # Module has no non_existent_function
        delattr(mock_mod, "non_existent_function")
        
        report = recover_failed_components(
            skill_id="vh_數學B1_LinearFunction",
            dry_run=True,
            db_conn=mem_conn
        )
        
        assert report["per_component_generator_plan"]["src_4401"]["final_readiness"] == "partial_capability"
        assert "implementation_function" in report["per_component_generator_plan"]["src_4401"]["missing_nodes"]

    # 3. Test: Full chain complete -> ready_to_rebuild
    with patch("core.gencode.services.failed_component_recovery_service.resolve_domain_authority") as mock_resolve, \
         patch("core.registry.domain_operation_registry.get_domain_spec") as mock_dom_spec, \
         patch("core.registry.domain_operation_registry.get_operation_spec") as mock_op_spec, \
         patch("importlib.import_module", side_effect=selective_import), \
         patch("inspect.getsource") as mock_source:
         
        res = MagicMock()
        res.fixed_domain_key = "coordinate_geometry.line_equation"
        res.selected_operation = "some_cap"
        mock_resolve.return_value = res
        
        dom_spec = MagicMock()
        dom_spec.capabilities = {"some_cap"}
        dom_spec.domain_module = "core.domain.coordinate_geometry.line_equation_domain"
        mock_dom_spec.return_value = dom_spec
        
        op_spec = MagicMock()
        op_spec.handler = "build_some_cap_matrix"
        op_spec.supported_presentation_modes = ("short_answer",)
        op_spec.supported_answer_types = ("multi_part",)
        mock_op_spec.return_value = op_spec
        
        # Module has the handler function
        mock_mod.build_some_cap_matrix = MagicMock()
        
        # Adapter has the route
        mock_source.return_value = 'if op == "some_cap":'
        
        report = recover_failed_components(
            skill_id="vh_數學B1_LinearFunction",
            dry_run=True,
            db_conn=mem_conn
        )
        
        assert report["per_component_generator_plan"]["src_4401"]["final_readiness"] == "ready_to_rebuild"
        assert len(report["per_component_generator_plan"]["src_4401"]["missing_nodes"]) == 0
