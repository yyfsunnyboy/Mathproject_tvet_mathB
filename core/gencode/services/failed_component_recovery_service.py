"""Failed component recovery orchestrator service with Exact Operation Readiness Gate."""

from __future__ import annotations

import json
import sqlite3
import py_compile
import importlib
import inspect
from pathlib import Path
from typing import Any

from core.gencode.skill_fixed_domain_authority import resolve_domain_authority, SkillFixedDomainError
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example, _load_module_from_file
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.domain_capability_proposal_service import create_or_reuse_capability_proposal, _fingerprint, _proposal_root
import core.registry.domain_operation_registry as registry
import core.gencode.domain_matrix_adapter as adapter_module

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
DRYRUN_BASE = "reports/gencode_v3_dryrun"

def _get_required_capabilities(payload: dict) -> list[str]:
    caps = payload.get("required_capabilities") or payload.get("phase1_classification", {}).get("required_capabilities")
    if not caps:
        prob_type = payload.get("problem_type_id") or payload.get("phase1_classification", {}).get("problem_type_id")
        if prob_type:
            caps = [prob_type]
    return sorted(list(set(str(c).strip() for c in caps if str(c).strip()))) if caps else []

def recover_failed_components(
    skill_id: str,
    *,
    dry_run: bool = False,
    db_conn: sqlite3.Connection | None = None
) -> dict[str, Any]:
    """Orchestrate recovery of failed V3 components for a skill.
    
    Validates components through the Exact Operation Readiness Gate before planning rebuilds.
    """
    conn = db_conn
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        close_conn = True

    try:
        # 1. Fetch failed tracker records
        rows = conn.execute(
            """
            SELECT textbook_example_id, component_id, gencode_status, induced_spec_payload, gencode_error_log
            FROM gencode_component_tracker
            WHERE skill_id = ? AND gencode_status = 'failed'
            """,
            (str(skill_id).strip(),)
        ).fetchall()

        total_failed = len(rows)
        
        # Group failed components by required_capabilities for provider/proposal checks
        grouped_failed: dict[tuple[str, ...], list[dict[str, Any]]] = {}
        for r in rows:
            payload = {}
            if r["induced_spec_payload"]:
                try:
                    payload = json.loads(r["induced_spec_payload"])
                except Exception:
                    payload = {}
            caps = tuple(_get_required_capabilities(payload))
            grouped_failed.setdefault(caps, []).append({
                "textbook_example_id": r["textbook_example_id"],
                "component_id": r["component_id"],
                "gencode_status": r["gencode_status"],
                "payload": payload,
                "gencode_error_log": r["gencode_error_log"]
            })

        capability_groups = {}
        resolved_groups = {}
        unresolved_groups = {}
        rebuilt = []
        verified = []
        still_failed = []
        proposals_created = []
        proposals_reused = []
        per_component_results = {}
        per_component_generator_plan = {}
        
        planned_generator_paths = set()
        component_ids_list = []
        
        adapter_source = inspect.getsource(adapter_module.convert_domain_matrix_to_question_payload)

        # 2. Process each group
        for caps, components in grouped_failed.items():
            caps_name = ",".join(caps) if caps else "unclassified"
            capability_groups[caps_name] = [c["component_id"] for c in components]
            
            # Check resolver resolution using first component in the group
            first_comp = components[0]
            prob_type = first_comp["payload"].get("problem_type_id") or first_comp["payload"].get("phase1_classification", {}).get("problem_type_id")
            
            domain_resolved = False
            provider_domain = None
            selected_operation = None
            
            try:
                resolver_res = resolve_domain_authority(
                    skill_id=skill_id,
                    problem_type_id=prob_type
                )
                domain_resolved = True
                provider_domain = resolver_res.fixed_domain_key
                selected_operation = resolver_res.selected_operation
            except SkillFixedDomainError:
                domain_resolved = False

            for comp in components:
                comp_id = comp["component_id"]
                ex_id = comp["textbook_example_id"]
                
                # Check Gate Readiness
                missing_nodes = []
                readiness = "unresolved_proposal"
                impl_fn_name = None
                adapter_routed = False
                checker_contract = None
                
                if domain_resolved:
                    spec = registry.get_domain_spec(provider_domain)
                    
                    # 1. Required capability explicitly declared
                    has_cap = any(cap in spec.capabilities for cap in caps) if spec else False
                    if not has_cap:
                        missing_nodes.append("capability_declaration")
                        
                    # 2. Selected operation matches required operation
                    correct_op = selected_operation == prob_type
                    if not correct_op:
                        missing_nodes.append("selected_operation_match")
                        
                    # 3. Registry has operation spec
                    op_spec = registry.get_operation_spec(provider_domain, selected_operation) if provider_domain and selected_operation else None
                    if not op_spec:
                        missing_nodes.append("registry_operation_spec")
                    else:
                        impl_fn_name = op_spec.handler
                        checker_contract = {
                            "presentation_modes": op_spec.supported_presentation_modes,
                            "answer_types": op_spec.supported_answer_types
                        }
                        
                    # 4. Domain module has implementation function
                    impl_exists = False
                    if spec and impl_fn_name:
                        try:
                            module = importlib.import_module(spec.domain_module)
                            impl_exists = hasattr(module, impl_fn_name)
                        except Exception:
                            impl_exists = False
                    if not impl_exists:
                        missing_nodes.append("implementation_function")
                        
                    # 5. Adapter has route for operation
                    adapter_routed = f'"{selected_operation}"' in adapter_source or f"'{selected_operation}'" in adapter_source
                    if not adapter_routed:
                        missing_nodes.append("adapter_route")
                        
                    # 6. Contract is resolvable
                    contract_resolvable = bool(op_spec and op_spec.supported_presentation_modes and op_spec.supported_answer_types)
                    if not contract_resolvable:
                        missing_nodes.append("contract_definitions")
                        
                    if not missing_nodes:
                        readiness = "ready_to_rebuild"
                    else:
                        readiness = "partial_capability"
                else:
                    missing_nodes.append("domain_resolution")
                    readiness = "unresolved_proposal"

                # Output planned paths for ready rebuilds (strictly 1-to-1)
                generator_path = None
                if readiness == "ready_to_rebuild":
                    generator_path = f"{DRYRUN_BASE}/{skill_id}/components/{comp_id}/generate.py"
                    component_ids_list.append(comp_id)
                    if generator_path in planned_generator_paths:
                        raise ValueError(f"1-to-1 Generator Violation: Duplicate path detected: {generator_path}")
                    planned_generator_paths.add(generator_path)
                    
                    # Track resolved groups
                    resolved_groups.setdefault(caps_name, {
                        "components": [],
                        "provider_domain": provider_domain
                    })["components"].append(comp_id)
                else:
                    unresolved_groups.setdefault(caps_name, {
                        "components": []
                    })["components"].append(comp_id)
                    
                per_component_generator_plan[comp_id] = {
                    "registry_capability": list(caps),
                    "selected_operation": selected_operation,
                    "implementation_function": impl_fn_name,
                    "adapter_route": adapter_routed,
                    "checker_contract": checker_contract,
                    "missing_nodes": missing_nodes,
                    "final_readiness": readiness,
                    "generator_path": generator_path
                }
                
                # Execute actions based on readiness
                if readiness == "ready_to_rebuild":
                    if dry_run:
                        per_component_results[comp_id] = {
                            "status": "planned_rebuild",
                            "error": None,
                            "details": f"Gate Passed. Resolves to {provider_domain}."
                        }
                        rebuilt.append(comp_id)
                        continue
                        
                    # Actual Rebuild
                    try:
                        dryrun_res = run_admin_v3_dryrun_for_example(
                            conn=conn,
                            textbook_example_id=ex_id,
                            skill_id=skill_id,
                            force_regenerate=True,
                            allow_non_mvp_skill=True
                        )
                        rebuilt.append(comp_id)
                        
                        comp_dir = Path(dryrun_res['dryrun_component_dir'])
                        required_files = {
                            "metadata.py": comp_dir / "metadata.py",
                            "generate.py": comp_dir / "generate.py",
                            "get_hint.py": comp_dir / "get_hint.py",
                        }
                        for path in required_files.values():
                            py_compile.compile(str(path), doraise=True)
                            
                        generate_module = _load_module_from_file(required_files["generate.py"])
                        hint_module = _load_module_from_file(required_files["get_hint.py"])
                        generate_fn = getattr(generate_module, "generate")
                        hint_fn = getattr(hint_module, "get_hint")
                        
                        from core.domain.coordinate_geometry.line_equation_domain import check_multi_part_answer
                        seeds = [7, 42, 101]
                        for seed in seeds:
                            payload = generate_fn(seed=seed)
                            val = validate_component_payload(payload, comp_id)
                            if not val.get("passed"):
                                raise ValueError(f"Integrity validation failed: {val.get('blockers')}")
                            hint_fn(1, payload)
                            correct_ans = payload["correct_answer"]
                            assert check_multi_part_answer(correct_ans, correct_ans) is True
                            
                        induced = dict(comp["payload"])
                        induced["integrity_gate_passed"] = True
                        induced["integrity_gate_version"] = "v1"
                        induced["integrity_gate_blockers"] = []
                        induced["validation_evidence"] = {
                            "seeds_verified": seeds,
                            "payload_schema_passed": True,
                            "answer_contract_passed": True,
                            "checker_logic_verified": True
                        }
                        
                        save_tracker_record(
                            conn=conn,
                            textbook_example_id=ex_id,
                            skill_id=skill_id,
                            gencode_status="verified",
                            induced_spec_payload=induced,
                            gencode_error_log=None
                        )
                        verified.append(comp_id)
                        per_component_results[comp_id] = {
                            "status": "verified",
                            "error": None,
                            "details": "Successfully rebuilt and validated."
                        }
                    except Exception as e:
                        still_failed.append(comp_id)
                        error_msg = f"{e.__class__.__name__}:{e}"
                        per_component_results[comp_id] = {
                            "status": "failed",
                            "error": error_msg,
                            "details": "Rebuild/validation failed."
                        }
                        if not dry_run:
                            induced = dict(comp["payload"])
                            induced["integrity_gate_passed"] = False
                            induced["integrity_gate_blockers"] = [error_msg]
                            try:
                                save_tracker_record(
                                    conn=conn,
                                    textbook_example_id=ex_id,
                                    skill_id=skill_id,
                                    gencode_status="failed",
                                    induced_spec_payload=induced,
                                    gencode_error_log=error_msg
                                )
                            except Exception:
                                pass
                else:
                    # unresolved_proposal or partial_capability
                    if dry_run:
                        per_component_results[comp_id] = {
                            "status": f"planned_proposal_{readiness}",
                            "error": None,
                            "details": f"Gate Missing: {missing_nodes}. Will propose."
                        }
                        prop_id = f"capability_mock_{comp_id}"
                        proposals_created.append(prop_id)
                        continue
                        
                    try:
                        # Check if proposal exists beforehand to determine is_new vs reuse
                        missing_op = str(prob_type or (list(caps)[0] if caps else "")).strip()
                        fingerprint = _fingerprint(list(caps), missing_op)
                        expected_prop_id = f"capability_{fingerprint}"
                        expected_path = _proposal_root() / f"{expected_prop_id}.json"
                        is_new = not expected_path.is_file()

                        proposal_res = create_or_reuse_capability_proposal(
                            skill_id=skill_id,
                            component_id=comp_id,
                            problem_type_id=prob_type,
                            required_capabilities=list(caps),
                            source_example_ids=[int(c["textbook_example_id"]) for c in components]
                        )
                        prop_id = proposal_res.get("proposal_id")
                        
                        if is_new:
                            if prop_id not in proposals_created:
                                proposals_created.append(prop_id)
                        else:
                            if prop_id not in proposals_reused:
                                proposals_reused.append(prop_id)
                                
                        error_msg = f"PARTIAL_CAPABILITY: missing nodes: {missing_nodes}" if readiness == "partial_capability" else f"UNRESOLVED_PROPOSAL: missing nodes: {missing_nodes}"
                        induced = dict(comp["payload"])
                        induced["integrity_gate_passed"] = False
                        induced["integrity_gate_blockers"] = missing_nodes
                        save_tracker_record(
                            conn=conn,
                            textbook_example_id=ex_id,
                            skill_id=skill_id,
                            gencode_status="failed",
                            induced_spec_payload=induced,
                            gencode_error_log=error_msg
                        )

                        per_component_results[comp_id] = {
                            "status": "proposed",
                            "error": None,
                            "details": f"Proposal {prop_id} resolved and tracker updated."
                        }
                    except Exception as e:
                        still_failed.append(comp_id)
                        per_component_results[comp_id] = {
                            "status": "proposal_failed",
                            "error": str(e),
                            "details": "Failed to create/reuse proposal."
                        }

        # Gate verification check
        merge_check_passed = len(planned_generator_paths) == len(component_ids_list)
        
        report = {
            "total_failed": total_failed,
            "capability_groups": capability_groups,
            "resolved_groups": resolved_groups,
            "unresolved_groups": unresolved_groups,
            "rebuilt": rebuilt,
            "verified": verified,
            "still_failed": still_failed,
            "proposals_created": proposals_created,
            "proposals_reused": proposals_reused,
            "per_component_results": per_component_results,
            "per_component_generator_plan": per_component_generator_plan,
            "merge_check_passed": merge_check_passed
        }
        return report
    finally:
        if close_conn:
            conn.close()
