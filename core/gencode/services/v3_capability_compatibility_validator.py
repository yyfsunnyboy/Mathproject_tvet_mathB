# -*- coding: utf-8 -*-
"""Official Gencode V3 compatibility gates for capability-fill candidates.

These checks are read-only against core/registry/taxonomy. They never promote
or write production files. Compile-only candidate trees must not await.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
from pathlib import Path
from typing import Any

from core.gencode.answer_schema_registry import (
    ANSWER_SCHEMAS,
    DOMAIN_OPERATION_ANSWER_SCHEMA,
    resolve_answer_schema_key,
)
from core.gencode.domain_matrix_adapter import MATRIX_REQUIRED_FIELDS
from core.registry.domain_operation_registry import (
    get_domain_spec,
    list_registered_domains,
    operation_is_registered,
)
from core.registry.taxonomy_registry import (
    SKILL_TO_DOMAIN,
    SkillDomainNotRegisteredError,
    resolve_domain_for_skill,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ALLOWED_OFFICIAL_TARGETS = (
    "configs/gencode_taxonomy/k12_component_taxonomy.yaml",
    "core/registry/domain_operation_registry.py",
    "core/registry/taxonomy_registry.py",
    "core/domain/",
    "core/gencode/domain_matrix_adapter.py",
    "core/gencode/answer_schema_registry.py",
    "core/gencode/answer_payload.py",
    "configs/gencode/classifiers/phase1_rule_packs.yaml",
    "tests/gencode/",
    "skills/",
)

CONTRACT_ONLY_TARGETS = frozenset(
    {
        "candidate_contract/coverage_matrix.json",
    }
)

KNOWN_CHECKER_KEYS = frozenset(
    {
        "rational_checker",
        "fraction_checker",
        "integer_checker",
        "numeric_checker",
        "decimal_tolerance_checker",
        "choice_label_checker",
        "linear_equation_equivalent_checker",
        "interval_checker",
        "coordinate_pair_checker",
    }
)

PLACEHOLDER_RE = re.compile(
    r"(?i)\b(placeholder|pending_implementation|not implemented|todo|fixme)\b"
)
VERTICAL_BOUNDARY_RE = re.compile(
    r"(?i)(vertical|undefined|does not exist|不存在|斜率不存在)"
)
FORBIDDEN_STANDALONE_RE = re.compile(
    r"(?i)(isomorphism_mapping_table|domain_registry_v1|_calculator_engine|standalone helper)"
)

BLOCK_INCOMPATIBLE = "incompatible_candidate"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/").strip().lstrip("/")


def _is_allowed_target(target: str) -> bool:
    text = _norm(target)
    if not text:
        return False
    if text in CONTRACT_ONLY_TARGETS:
        return True
    return any(text == prefix or text.startswith(prefix) for prefix in ALLOWED_OFFICIAL_TARGETS)


def _is_runtime_read_target(target: str) -> bool:
    text = _norm(target)
    if text in CONTRACT_ONLY_TARGETS or text.startswith("tests/gencode/"):
        return False
    return _is_allowed_target(text)


def official_matrix_fields() -> list[str]:
    return list(MATRIX_REQUIRED_FIELDS)


def validate_architect_spec(
    spec: dict[str, Any],
    *,
    skill_id: str,
    example_ids: list[int],
) -> list[str]:
    blockers: list[str] = []
    if not isinstance(spec, dict) or not spec:
        return ["architect_json_missing"]

    skill_key = str(skill_id or "").strip()
    spec_skill = str(spec.get("skill_id") or "").strip()
    if spec_skill != skill_key:
        blockers.append("skill_id_mismatch")

    domain_key = str(spec.get("domain_key") or spec.get("domain_key_suggestion") or "").strip()
    if not domain_key:
        blockers.append("spec_missing_domain_key")
    elif domain_key not in set(list_registered_domains()):
        blockers.append("invented_domain_forbidden")

    domain_spec = get_domain_spec(domain_key) if domain_key else None
    domain_module = str(spec.get("domain_module") or "").strip()
    entrypoint = str(spec.get("entrypoint") or "").strip()
    if domain_spec is not None:
        if domain_module and domain_module != domain_spec.domain_module:
            blockers.append("spec_domain_module_mismatch")
        if not domain_module:
            blockers.append("spec_missing_domain_module")
        if entrypoint and entrypoint != domain_spec.entrypoint:
            blockers.append("spec_entrypoint_mismatch")
        if not entrypoint:
            blockers.append("spec_missing_entrypoint")
    elif domain_key:
        if not domain_module:
            blockers.append("spec_missing_domain_module")
        if not entrypoint:
            blockers.append("spec_missing_entrypoint")

    ops = spec.get("required_operations")
    if not isinstance(ops, list) or not [str(x).strip() for x in ops if str(x).strip()]:
        blockers.append("spec_missing_required_operations")
        ops = []
    ops = [str(x).strip() for x in ops if str(x).strip()]
    proposed_ops = {
        str(x).strip()
        for x in (spec.get("registry_operation_proposals") or [])
        if str(x).strip()
    }
    allowed_files = [
        _norm(x) for x in (spec.get("allowed_official_files") or []) if _norm(x)
    ]
    if not allowed_files:
        blockers.append("spec_missing_allowed_official_files")
    illegal_files = [p for p in allowed_files if not _is_allowed_target(p)]
    if illegal_files:
        blockers.append("spec_illegal_official_file")

    for op in ops:
        if domain_key and operation_is_registered(domain_key, op):
            continue
        if op in proposed_ops and "core/registry/domain_operation_registry.py" in allowed_files:
            continue
        blockers.append(f"operation_unregistered:{op}")

    matrix_fields = spec.get("matrix_required_fields")
    expected = official_matrix_fields()
    if not isinstance(matrix_fields, list) or [str(x) for x in matrix_fields] != expected:
        blockers.append("spec_matrix_fields_mismatch")

    schemas = spec.get("answer_schema")
    if not isinstance(schemas, dict) or not schemas:
        blockers.append("spec_missing_answer_schema")
        schemas = {}
    checkers = spec.get("checker")
    if not isinstance(checkers, dict) or not checkers:
        blockers.append("spec_missing_checker")
        checkers = {}
    for op in ops:
        schema_key = str(schemas.get(op) or "").strip()
        resolved = resolve_answer_schema_key(
            answer_schema_key=schema_key or None,
            domain_operation=op,
        )
        if schema_key and schema_key not in ANSWER_SCHEMAS:
            blockers.append(f"answer_schema_unknown:{op}")
        elif not resolved and "core/gencode/answer_schema_registry.py" not in allowed_files:
            blockers.append(f"answer_schema_unresolved:{op}")
        checker_key = str(checkers.get(op) or "").strip()
        if checker_key not in KNOWN_CHECKER_KEYS:
            blockers.append(f"checker_unresolved:{op}")

    taxonomy_bound = False
    try:
        routing = resolve_domain_for_skill(skill_key)
        taxonomy_bound = True
        if domain_key and str(routing.get("fixed_domain_key") or "") != domain_key:
            blockers.append("spec_domain_key_mismatch_taxonomy")
    except SkillDomainNotRegisteredError:
        taxonomy_bound = False
    if not taxonomy_bound:
        if "configs/gencode_taxonomy/k12_component_taxonomy.yaml" not in allowed_files:
            blockers.append("spec_missing_taxonomy_binding_proposal")

    coverage = spec.get("example_coverage")
    if not isinstance(coverage, list) or not coverage:
        blockers.append("spec_missing_example_coverage")
        coverage = []
    covered_ids: set[int] = set()
    for row in coverage:
        if not isinstance(row, dict):
            blockers.append("spec_invalid_example_coverage")
            continue
        try:
            eid = int(row.get("textbook_example_id"))
        except (TypeError, ValueError):
            blockers.append("spec_invalid_example_coverage")
            continue
        covered_ids.add(eid)
        op = str(row.get("operation") or "").strip()
        contract = row.get("answer_contract") if isinstance(row.get("answer_contract"), dict) else {}
        if not op:
            blockers.append(f"example_missing_operation:{eid}")
        if not str(contract.get("checker_key") or contract.get("checker") or "").strip():
            blockers.append(f"example_missing_answer_contract:{eid}")
    expected_ids = {int(x) for x in example_ids}
    if expected_ids and covered_ids != expected_ids:
        blockers.append("example_coverage_incomplete")
    unknown = covered_ids - expected_ids
    if unknown:
        blockers.append("unknown_example_id")

    guards = spec.get("regression_guards")
    if not isinstance(guards, list) or not [str(x).strip() for x in guards if str(x).strip()]:
        blockers.append("spec_missing_regression_guards")
    else:
        known_skills = set(SKILL_TO_DOMAIN.keys())
        if not any(str(g).strip() in known_skills for g in guards):
            blockers.append("spec_regression_guards_unverified")

    return list(dict.fromkeys(blockers))


def parse_coder_contract(
    payload: dict[str, Any],
    *,
    skill_id: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    blockers: list[str] = []
    if not isinstance(payload, dict) or not payload:
        return [], ["coder_json_missing"]
    payload_skill = str(payload.get("skill_id") or "").strip()
    if payload_skill and payload_skill != str(skill_id).strip():
        blockers.append("coder_skill_id_mismatch")

    files = payload.get("files")
    if not isinstance(files, list) or not files:
        return [], ["coder_files_missing"]

    coverage = payload.get("coverage_matrix")
    cleaned: list[dict[str, Any]] = []
    if isinstance(coverage, list):
        cleaned.append(
            {
                "path": "coverage_matrix.json",
                "target": "candidate_contract/coverage_matrix.json",
                "mutation": "example_coverage",
                "content": json.dumps(coverage, ensure_ascii=False, indent=2),
            }
        )

    for item in files:
        if not isinstance(item, dict):
            continue
        rel = str(item.get("path") or "").replace("\\", "/").strip().lstrip("/")
        if not rel or rel.startswith("..") or "/../" in f"/{rel}/" or Path(rel).is_absolute():
            continue
        target = _norm(str(item.get("target") or ""))
        mutation = str(item.get("mutation") or "").strip()
        cleaned.append(
            {
                "path": rel,
                "target": target,
                "mutation": mutation,
                "content": str(item.get("content") or ""),
            }
        )

    if not cleaned:
        blockers.append("coder_files_invalid")
    return cleaned, list(dict.fromkeys(blockers))


def _read_candidate_blob(cand_root: Path) -> str:
    parts: list[str] = []
    if not cand_root.is_dir():
        return ""
    for path in cand_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return "\n".join(parts)


def _load_manifest_mutations(job_dir: Path) -> list[dict[str, Any]]:
    manifest_path = job_dir / "candidate_manifest.json"
    if not manifest_path.is_file():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows = data.get("mutations")
    return rows if isinstance(rows, list) else []


def _load_coverage_matrix(cand_root: Path, spec: dict[str, Any]) -> list[dict[str, Any]]:
    path = cand_root / "coverage_matrix.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            return []
    coverage = spec.get("example_coverage")
    return coverage if isinstance(coverage, list) else []


def _collect_example_ids(payload: Any) -> set[int]:
    found: set[int] = set()
    if isinstance(payload, dict):
        raw_ids = payload.get("textbook_example_ids")
        if isinstance(raw_ids, list):
            for raw in raw_ids:
                try:
                    found.add(int(raw))
                except (TypeError, ValueError):
                    continue
        for value in payload.values():
            found.update(_collect_example_ids(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_collect_example_ids(item))
    return found


def _entrypoint_importable(domain_module: str, entrypoint: str) -> list[str]:
    blockers: list[str] = []
    if not domain_module or not entrypoint:
        return ["entrypoint_not_official"]
    try:
        module = importlib.import_module(domain_module)
    except Exception:
        return ["entrypoint_not_importable"]
    fn = getattr(module, entrypoint, None)
    if not callable(fn):
        blockers.append("entrypoint_not_callable")
    return blockers


def _needs_slope_math_boundaries(skill_id: str, operations: list[str]) -> bool:
    blob = " ".join([skill_id, *operations]).lower()
    return any(token in blob for token in ("slope", "vertical", "two_points"))


def validate_official_compatibility(
    job_dir: Path,
    spec: dict[str, Any],
    *,
    skill_id: str,
    example_ids: list[int],
) -> dict[str, Any]:
    """Block awaiting unless the candidate is a legal official-architecture proposal."""
    blockers: list[str] = []
    skill_key = str(skill_id or "").strip()
    cand_root = job_dir / "candidate"
    files = (
        sorted(str(p.relative_to(cand_root)).replace("\\", "/") for p in cand_root.rglob("*") if p.is_file())
        if cand_root.is_dir()
        else []
    )
    if not cand_root.is_dir() or not files:
        blockers.append("missing_candidate_dir" if not cand_root.is_dir() else "no_candidate_files")

    spec_blockers = validate_architect_spec(spec, skill_id=skill_key, example_ids=example_ids)
    blockers.extend(spec_blockers)

    mutations = _load_manifest_mutations(job_dir)
    blob = _read_candidate_blob(cand_root)
    if PLACEHOLDER_RE.search(blob):
        blockers.append("placeholder_or_pending")
    if FORBIDDEN_STANDALONE_RE.search(" ".join(files) + "\n" + blob):
        blockers.append("standalone_helper_forbidden")

    runtime_mutations = 0
    focused_tests = 0
    for row in mutations:
        target = _norm(str(row.get("target") or ""))
        rel = _norm(str(row.get("path") or ""))
        if not target:
            blockers.append(f"unwired_artifact:{rel or '?'}")
            continue
        if not _is_allowed_target(target):
            blockers.append(f"illegal_mutation_target:{target}")
            continue
        if _is_runtime_read_target(target):
            runtime_mutations += 1
        if target.startswith("tests/gencode/") and rel.endswith(".py"):
            focused_tests += 1
            src = ""
            src_path = cand_root / rel
            if src_path.is_file():
                src = src_path.read_text(encoding="utf-8")
            if "def test_" not in src:
                blockers.append("focused_tests_missing_assertions")
    if runtime_mutations == 0:
        blockers.append("unwired_artifact")
    if focused_tests == 0:
        blockers.append("missing_focused_tests")

    for rel in files:
        if rel == "coverage_matrix.json":
            continue
        matched = any(_norm(str(row.get("path") or "")) == rel for row in mutations)
        if not matched:
            blockers.append(f"unwired_artifact:{rel}")

    domain_key = str(spec.get("domain_key") or spec.get("domain_key_suggestion") or "").strip()
    domain_spec = get_domain_spec(domain_key) if domain_key else None
    domain_module = str(spec.get("domain_module") or (domain_spec.domain_module if domain_spec else "")).strip()
    entrypoint = str(spec.get("entrypoint") or (domain_spec.entrypoint if domain_spec else "")).strip()
    blockers.extend(_entrypoint_importable(domain_module, entrypoint))

    ops = [str(x).strip() for x in (spec.get("required_operations") or []) if str(x).strip()]
    adapter_src = (PROJECT_ROOT / "core" / "gencode" / "domain_matrix_adapter.py").read_text(encoding="utf-8")
    adapter_mutation = any(
        _norm(str(row.get("target") or "")) == "core/gencode/domain_matrix_adapter.py" for row in mutations
    )
    schema_mutation = any(
        _norm(str(row.get("target") or "")) == "core/gencode/answer_schema_registry.py" for row in mutations
    )
    for op in ops:
        if op not in adapter_src and not adapter_mutation:
            blockers.append(f"adapter_unresolved:{op}")
        resolved = resolve_answer_schema_key(domain_operation=op)
        spec_schema = ""
        if isinstance(spec.get("answer_schema"), dict):
            spec_schema = str(spec["answer_schema"].get(op) or "").strip()
        if not resolved and spec_schema not in ANSWER_SCHEMAS and not schema_mutation:
            blockers.append(f"answer_schema_unresolved:{op}")
        if spec_schema and spec_schema not in ANSWER_SCHEMAS and spec_schema not in DOMAIN_OPERATION_ANSWER_SCHEMA.values():
            blockers.append(f"answer_schema_unknown:{op}")

    coverage = _load_coverage_matrix(cand_root, spec)
    covered_ids: set[int] = set()
    for row in coverage:
        if not isinstance(row, dict):
            continue
        try:
            eid = int(row.get("textbook_example_id"))
        except (TypeError, ValueError):
            blockers.append("unknown_example_id")
            continue
        covered_ids.add(eid)
        if not str(row.get("operation") or "").strip():
            blockers.append(f"example_missing_operation:{eid}")
        contract = row.get("answer_contract") if isinstance(row.get("answer_contract"), dict) else {}
        if not str(contract.get("checker_key") or contract.get("checker") or "").strip():
            blockers.append(f"example_missing_answer_contract:{eid}")
    expected_ids = {int(x) for x in example_ids}
    if expected_ids and covered_ids != expected_ids:
        blockers.append("example_coverage_incomplete")
    extra_ids: set[int] = _collect_example_ids(spec)
    for rel in files:
        if not rel.endswith(".json"):
            continue
        try:
            extra_ids.update(_collect_example_ids(json.loads((cand_root / rel).read_text(encoding="utf-8"))))
        except Exception:
            continue
    if expected_ids and extra_ids - expected_ids:
        blockers.append("unknown_example_id")

    if _needs_slope_math_boundaries(skill_key, ops):
        py_blob = blob
        if "Fraction" not in py_blob:
            blockers.append("math_boundary_fraction_missing")
        if not VERTICAL_BOUNDARY_RE.search(py_blob):
            blockers.append("math_boundary_vertical_undefined_missing")

    guards = [str(g).strip() for g in (spec.get("regression_guards") or []) if str(g).strip()]
    if not any(g in SKILL_TO_DOMAIN for g in guards):
        blockers.append("verified_regression_unspecified")
    else:
        other_production = [
            g for g in guards if g in SKILL_TO_DOMAIN and g != skill_key
        ]
        for row in mutations:
            target = _norm(str(row.get("target") or ""))
            for other in other_production:
                if target.startswith(f"agent_skills_v3/{other}/") or target == f"skills/{other}.py":
                    blockers.append(f"verified_skill_mutation_forbidden:{other}")

    # Syntax remains a hard gate for python mutations.
    for rel in files:
        if not rel.endswith(".py"):
            continue
        src = (cand_root / rel).read_text(encoding="utf-8")
        try:
            ast.parse(src)
        except SyntaxError as exc:
            blockers.append(f"python_syntax_error:{rel}:{exc.msg}")

    unique = list(dict.fromkeys(blockers))
    return {
        "passed": not unique,
        "blockers": unique,
        "gate": "official_compatibility",
        "file_count": len(files),
        "files": files,
        "runtime_mutation_count": runtime_mutations,
        "focused_test_count": focused_tests,
    }
