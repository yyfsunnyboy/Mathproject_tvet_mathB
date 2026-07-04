import sys
import os
import shutil
import json
import hashlib
from pathlib import Path
import subprocess

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
WORKSPACE_DIR = PROJECT_ROOT / "reports" / "domain_operation_workspaces" / "capability_64830fcffbb56fa709b9abad" / "revision_0001"
BACKUP_DIR = PROJECT_ROOT / "backups" / "promotion_capability_64830fcffbb56fa709b9abad"

FILES_TO_PROMOTE = {
    "domain_spec": PROJECT_ROOT / "core" / "registry" / "domain_operation_registry.py",
    "domain_impl": PROJECT_ROOT / "core" / "domain" / "coordinate_geometry" / "line_equation_domain.py",
    "adapter": PROJECT_ROOT / "core" / "gencode" / "domain_matrix_adapter.py",
    "test_file": PROJECT_ROOT / "tests" / "domain" / "test_graph_intercepts_and_linear_equation.py"
}

def calculate_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def backup_files():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for name, path in FILES_TO_PROMOTE.items():
        if path.is_file():
            shutil.copy2(path, BACKUP_DIR / path.name)
            print(f"Backed up {path.name} to {BACKUP_DIR}")

def restore_files():
    print("Rollback triggered! Restoring all files from backup...")
    for name, path in FILES_TO_PROMOTE.items():
        backup_file = BACKUP_DIR / path.name
        if backup_file.is_file():
            shutil.copy2(backup_file, path)
            print(f"Restored {path.name}")
        elif path.is_file():
            path.unlink()
            print(f"Removed promoted file {path.name}")

def clean_backups():
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
        print("Cleaned up backups.")

def verify_pre_conditions():
    print("Verifying pre-conditions...")
    proposal_path = PROJECT_ROOT / "reports" / "domain_capability_proposals" / "capability_64830fcffbb56fa709b9abad.json"
    if not proposal_path.is_file():
        raise FileNotFoundError("Proposal file not found")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    if proposal.get("status") != "approved":
        raise ValueError(f"Proposal is not approved: {proposal.get('status')}")

    manifest_path = WORKSPACE_DIR / "capability_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("Workspace capability manifest not found")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("proposal_revision") != 1:
        raise ValueError(f"Invalid workspace revision: {manifest.get('proposal_revision')}")
    if manifest.get("proposal_id") != "capability_64830fcffbb56fa709b9abad":
        raise ValueError(f"Proposal ID mismatch: {manifest.get('proposal_id')}")
    if manifest.get("target_domain") != "coordinate_geometry.line_equation":
        raise ValueError(f"Target domain mismatch: {manifest.get('target_domain')}")

    val_path = WORKSPACE_DIR / "validation_result.json"
    if not val_path.is_file():
        raise FileNotFoundError("Workspace validation result not found")
    val = json.loads(val_path.read_text(encoding="utf-8"))
    if val.get("review_status") != "ready_for_human_review":
        raise ValueError(f"Review status is not ready_for_human_review: {val.get('review_status')}")

    # Check hashes of production files to avoid conflicts
    for rel_path, expected_hash in val.get("production_sha256", {}).items():
        abs_path = PROJECT_ROOT / rel_path
        if abs_path.is_file():
            current_hash = calculate_sha256(abs_path)
            if current_hash != expected_hash:
                print(f"WARNING: Hash mismatch for {rel_path}: current={current_hash}, expected={expected_hash}")
    print("Pre-conditions verified successfully.")

def promote():
    print("Applying changes to line_equation_domain.py...")
    # 1. Append implementation to line_equation_domain.py
    domain_impl_file = FILES_TO_PROMOTE["domain_impl"]
    operation_code = (WORKSPACE_DIR / "operation.py").read_text(encoding="utf-8")
    
    # Extract code starting after import statements, keeping helper functions and build matrix
    lines = operation_code.splitlines()
    clean_lines = []
    for line in lines:
        if line.startswith("from ") or line.startswith("import ") or line.startswith('"""'):
            continue
        clean_lines.append(line)
    operation_impl = "\n".join(clean_lines)

    # Append custom checkers from adapter.py
    adapter_code = (WORKSPACE_DIR / "adapter.py").read_text(encoding="utf-8")
    adapter_lines = adapter_code.splitlines()
    checker_lines = []
    for line in adapter_lines:
        if line.startswith("from ") or line.startswith("import ") or line.startswith('"""') or "adapt_matrix_to_component_payload" in line:
            # stop copy when reaching adapt_matrix_to_component_payload
            if "adapt_matrix_to_component_payload" in line:
                break
            continue
        checker_lines.append(line)
    checker_impl = "\n".join(checker_lines)

    domain_impl_orig = domain_impl_file.read_text(encoding="utf-8")
    
    # Add to _SUPPORTED_LINE_TYPES
    orig_caps = '"compare_point_to_line_distances",\n    }'
    new_caps = '"compare_point_to_line_distances", "graph_intercepts_and_linear_equation",\n    }'
    if orig_caps not in domain_impl_orig:
        raise ValueError("Could not find _SUPPORTED_LINE_TYPES in line_equation_domain.py")
    domain_impl_orig = domain_impl_orig.replace(orig_caps, new_caps)
    
    # Add to build_line_equation_matrix routing
    orig_route = 'normalized_type = str(line_type or "").strip()\n    if normalized_type not in _SUPPORTED_LINE_TYPES:'
    new_route = (
        'normalized_type = str(line_type or "").strip()\n'
        '    if normalized_type == "graph_intercepts_and_linear_equation":\n'
        '        return build_graph_intercepts_and_linear_equation_matrix(\n'
        '            seed=seed,\n'
        '            constraints=constraints,\n'
        '        )\n'
        '    if normalized_type not in _SUPPORTED_LINE_TYPES:'
    )
    if orig_route not in domain_impl_orig:
        raise ValueError("Could not find routing entry in build_line_equation_matrix")
    domain_impl_orig = domain_impl_orig.replace(orig_route, new_route)

    new_domain_impl = domain_impl_orig + "\n\n" + operation_impl + "\n\n" + checker_impl
    domain_impl_file.write_text(new_domain_impl, encoding="utf-8")
    print("Applied implementation to line_equation_domain.py")

    # 2. Add specification to domain_operation_registry.py
    print("Applying changes to domain_operation_registry.py...")
    registry_file = FILES_TO_PROMOTE["domain_spec"]
    registry_code = registry_file.read_text(encoding="utf-8")
    
    # Find capabilities set of coordinate_geometry.line_equation and add capability
    caps_pattern = '"coordinate_geometry_word_problem",\n    }),'
    if caps_pattern not in registry_code:
        raise ValueError("Could not find capabilities block in domain_operation_registry.py")
    
    registry_code = registry_code.replace(
        caps_pattern,
        '"coordinate_geometry_word_problem", "graph_intercepts_and_linear_equation",\n    }),'
    )

    # Find operations block of coordinate_geometry.line_equation and add operation spec
    op_pattern = '"coordinate_geometry_word_problem":             _op("coordinate_geometry_word_problem",             "build_line_equation_matrix", supported_answer_types=("expression",)),'
    if op_pattern not in registry_code:
        raise ValueError("Could not find operations block in domain_operation_registry.py")

    new_op_spec = (
        '"coordinate_geometry_word_problem":             _op("coordinate_geometry_word_problem",             "build_line_equation_matrix", supported_answer_types=("expression",)),\n'
        '        "graph_intercepts_and_linear_equation":         _op("graph_intercepts_and_linear_equation",         "build_graph_intercepts_and_linear_equation_matrix", supported_answer_types=("multi_part",), provided_capabilities=("graph_intercepts_and_linear_equation",)),'
    )
    registry_code = registry_code.replace(op_pattern, new_op_spec)
    registry_file.write_text(registry_code, encoding="utf-8")
    print("Applied specification to domain_operation_registry.py")

    # 3. Add adapter to domain_matrix_adapter.py
    print("Applying changes to domain_matrix_adapter.py...")
    adapter_file = FILES_TO_PROMOTE["adapter"]
    adapter_code = adapter_file.read_text(encoding="utf-8")

    # Route in convert_domain_matrix_to_question_payload
    route_pattern = 'op = str(domain_operation or kwargs.get("domain_operation") or "").strip()\n    if op in _DESCRIPTIVE_STATS_OPS:'
    if route_pattern not in adapter_code:
        raise ValueError("Could not find routing entry in domain_matrix_adapter.py")
    
    new_route = (
        'op = str(domain_operation or kwargs.get("domain_operation") or "").strip()\n'
        '    if op == "graph_intercepts_and_linear_equation":\n'
        '        return _finalize_question_payload(\n'
        '            _convert_graph_intercepts_and_linear_equation_payload(\n'
        '                matrix,\n'
        '                component_id=component_id,\n'
        '                textbook_example_id=textbook_example_id,\n'
        '                **kwargs\n'
        '            )\n'
        '        )\n'
        '    if op in _DESCRIPTIVE_STATS_OPS:'
    )
    adapter_code = adapter_code.replace(route_pattern, new_route)

    # Append custom payload converter function at the end
    converter_function = """

def _convert_graph_intercepts_and_linear_equation_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    canonical = dict(matrix["semantic_answer"])
    parts = [
        {
            "key": key,
            "label": label,
            "checker": checker,
            "expected_answer": canonical.get(key),
        }
        for key, label, checker in (
            ("x_intercept", "x 截距", "rational_checker"),
            ("y_intercept", "y 截距", "rational_checker"),
            ("function_equation", "f(x)", "linear_equation_equivalent_checker"),
        )
    ]
    return {
        "question_text": matrix["question"],
        "answer": canonical,
        "correct_answer": canonical,
        "display_answer": canonical,
        "semantic_answer": canonical,
        "semantic_answer_type": "multi_part",
        "answer_type": "multi_part",
        "presentation_mode": "graph_multi_part",
        "interaction_type": "multi_part",
        "problem_type_id": "graph_intercepts_and_linear_equation",
        "domain_operation": "graph_intercepts_and_linear_equation",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "topology_tags": list(matrix["topology_tags"]),
        "visual_spec": dict(matrix["visual_spec"]),
        "answer_contract": {
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": canonical,
            "parts": parts,
            "ui_contract": {
                "response_mode": "multi_part",
                "text_input_enabled": True,
            },
        },
        "metadata": {
            "givens": dict(matrix["givens"]),
            "semantic_answer": canonical,
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "source_example_id": textbook_example_id or 0,
        },
        "math_core": {
            "givens": dict(matrix["givens"]),
            "target": canonical,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": dict(matrix["validation_facts"]),
        },
        "choices": [],
        "options": [],
        "auto_checkable": True,
        "grading_mode": "auto",
    }
"""
    adapter_code += converter_function
    adapter_file.write_text(adapter_code, encoding="utf-8")
    print("Applied custom converter to domain_matrix_adapter.py")

    # 4. Write promoted test file
    print("Writing promoted test file...")
    cand_test_code = (WORKSPACE_DIR / "test_src_4424_candidate.py").read_text(encoding="utf-8")
    
    # Adjust imports and adapter calling
    new_test_code = cand_test_code.replace(
        "from adapter import adapt_matrix_to_component_payload, check_multi_part_answer",
        "from core.domain.coordinate_geometry.line_equation_domain import (\n"
        "    build_graph_intercepts_and_linear_equation_matrix,\n"
        "    check_multi_part_answer,\n"
        ")\n"
        "from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload"
    )
    new_test_code = new_test_code.replace(
        "from operation import build_graph_intercepts_and_linear_equation_matrix",
        ""
    )
    new_test_code = new_test_code.replace(
        "PROJECT_ROOT = Path(__file__).resolve().parents[4]",
        "PROJECT_ROOT = Path(__file__).resolve().parents[2]"
    )
    
    adapt_pattern = """        payload = adapt_matrix_to_component_payload(
            matrix,
            component_ref=source["source_ref"],
            source_example_ref=source["source_example_id"],
        )"""
    new_adapt = """        payload = convert_domain_matrix_to_question_payload(
            matrix,
            presentation_mode="graph_multi_part",
            answer_type="multi_part",
            problem_type_id="graph_intercepts_and_linear_equation",
            component_id=source["source_ref"],
            textbook_example_id=source["source_example_id"],
            domain_operation="graph_intercepts_and_linear_equation"
        )"""
    new_test_code = new_test_code.replace(adapt_pattern, new_adapt)
    
    FILES_TO_PROMOTE["test_file"].write_text(new_test_code, encoding="utf-8")
    print("Promoted test file written.")

def run_tests_and_verify():
    print("Running verification checks...")
    
    # 1. Compile checks
    for name, path in FILES_TO_PROMOTE.items():
        subprocess.run([sys.executable, "-m", "py_compile", str(path)], check=True)
        print(f"Compilation check passed for {path.name}")
        
    # 2. Pytest execution
    print("Running pytest on promoted tests...")
    res = subprocess.run([sys.executable, "-m", "pytest", str(FILES_TO_PROMOTE["test_file"])], capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError(f"Pytest failed with exit code {res.returncode}")
    print("Pytest verification checks passed.")

    # 3. Resolver verification
    print("Verifying resolver can resolve the new operation...")
    sys.path.insert(0, str(PROJECT_ROOT))
    
    # Clear cached modules to ensure they reload properly
    for mod in ["core.registry.domain_operation_registry", "core.domain.coordinate_geometry.line_equation_domain", "core.gencode.domain_matrix_adapter", "core.gencode.skill_fixed_domain_authority"]:
        if mod in sys.modules:
            del sys.modules[mod]
            
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
    res = resolve_domain_authority(
        skill_id="vh_數學B1_LinearFunction",
        problem_type_id="graph_intercepts_and_linear_equation"
    )
    if res.selected_operation != "graph_intercepts_and_linear_equation":
        raise ValueError(f"Resolver chose wrong operation: {res.selected_operation}")
    if res.fixed_domain_key != "coordinate_geometry.line_equation":
        raise ValueError(f"Resolver chose wrong domain key: {res.fixed_domain_key}")
    print("Resolver verification passed.")

    # 4. Registry consistency checks
    print("Verifying registry consistency...")
    from core.registry.domain_operation_registry import check_registry_consistency
    issues = check_registry_consistency()
    if issues:
        raise ValueError(f"Registry consistency check failed: {issues}")
    print("Registry consistency check passed.")

    # 5. Component validator verification
    print("Verifying component validator for src_4424...")
    from core.domain.coordinate_geometry.line_equation_domain import build_graph_intercepts_and_linear_equation_matrix
    from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
    from core.gencode.services.v3_question_integrity_validator import validate_component_payload

    source_spec_path = PROJECT_ROOT / "configs" / "gencode" / "source_graph_specs" / "src_4424.json"
    source = json.loads(source_spec_path.read_text(encoding="utf-8"))
    
    matrix = build_graph_intercepts_and_linear_equation_matrix(seed=4424, constraints={"line_kind": "oblique"})
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="graph_multi_part",
        answer_type="multi_part",
        problem_type_id="graph_intercepts_and_linear_equation",
        component_id=source["source_ref"],
        textbook_example_id=source["source_example_id"],
        domain_operation="graph_intercepts_and_linear_equation"
    )
    integrity = validate_component_payload(payload, component_id=source["source_ref"])
    if not integrity.get("passed", False):
        raise ValueError(f"Component validator failed: {integrity.get('blockers')}")
    print("Component validator verification passed.")

def create_promotion_manifest():
    manifest_path = WORKSPACE_DIR / "promotion_manifest.json"
    manifest = {
        "proposal_id": "capability_64830fcffbb56fa709b9abad",
        "target_domain": "coordinate_geometry.line_equation",
        "promoted_files": {rel: str(path.relative_to(PROJECT_ROOT)) for rel, path in FILES_TO_PROMOTE.items()},
        "promoted_operation": "graph_intercepts_and_linear_equation",
        "resolver_verified": True,
        "consistency_checked": True,
        "component_validator_verified": True
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created promotion manifest: {manifest_path}")

def main():
    try:
        verify_pre_conditions()
        backup_files()
        promote()
        run_tests_and_verify()
        create_promotion_manifest()
        clean_backups()
        print("PROMOTION COMPLETED SUCCESSFULLY!")
    except Exception as e:
        print(f"Promotion failed with error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        try:
            restore_files()
        except Exception as re:
            print(f"Failed to restore files: {re}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
