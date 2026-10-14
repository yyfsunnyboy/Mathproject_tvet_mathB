"""Promote a human-reviewed capability workspace into production, atomically.

A reviewed workspace revision contains ``promotion_bundle.json`` plus a
self-contained production package.  Promotion copies that package (byte-for-byte
as reviewed) into the promoted package root, records the domain, operations,
adapters, validators and skill bindings in the promoted capability store, and
applies them to the live registries.  Any failure restores package files, the
store and in-memory registry state to their exact pre-promotion values.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from core.registry import promoted_capability_store as store_mod

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE_ROOT = PROJECT_ROOT / "core" / "domain" / "promoted"
DEFAULT_PACKAGE_IMPORT_PREFIX = "core.domain.promoted"
BUNDLE_FILENAME = "promotion_bundle.json"
BUNDLE_SCHEMA = "reviewed_capability_bundle.v1"

_DOMAIN_KEY = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PACKAGE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")


class CapabilityPromotionError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _package_files(directory: Path) -> dict[str, Path]:
    return {
        path.relative_to(directory).as_posix(): path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def _package_matches(directory: Path, expected: dict[str, str]) -> bool:
    if not directory.is_dir():
        return False
    files = _package_files(directory)
    return set(files) == set(expected) and all(_sha256(files[name]) == digest for name, digest in expected.items())


def _import_blockers(name: str, source: str, local_modules: set[str]) -> list[str]:
    try:
        tree = ast.parse(source, filename=name)
    except SyntaxError as exc:
        return [f"package_syntax_error:{name}:{exc.lineno}"]
    blockers: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in local_modules:
                    blockers.append(f"workspace_local_import:{name}:{alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module.split(".")[0] in local_modules:
                blockers.append(f"workspace_local_import:{name}:{node.module}")
        elif (
            isinstance(node, ast.Attribute)
            and node.attr == "path"
            and isinstance(node.value, ast.Name)
            and node.value.id == "sys"
        ):
            blockers.append(f"sys_path_access:{name}")
    return blockers


def _checker_registered(checker_key: str) -> bool:
    from core.gencode.checker_registry import CHECKER_CAPABILITIES

    row = CHECKER_CAPABILITIES.get(checker_key)
    return isinstance(row, dict) and bool(row.get("runtime_available"))


def load_reviewed_bundle(workspace_dir: str | Path) -> dict[str, Any]:
    path = Path(workspace_dir) / BUNDLE_FILENAME
    if not path.is_file():
        raise CapabilityPromotionError("bundle_missing", f"{BUNDLE_FILENAME} not found in {workspace_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_sha256(bundle: dict[str, Any]) -> str:
    encoded = json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _bundle_blockers(workspace: Path, bundle: dict[str, Any], store: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if bundle.get("schema") != BUNDLE_SCHEMA:
        return ["bundle_schema_invalid"]

    review = bundle.get("review") if isinstance(bundle.get("review"), dict) else {}
    if review.get("status") != "human_approved" or not str(review.get("approved_by") or "").strip():
        blockers.append("human_review_not_approved")
    if review.get("approved_revision") != bundle.get("proposal_revision"):
        blockers.append("approved_revision_mismatch")

    domain_key = str(bundle.get("domain_key") or "")
    package_name = str(bundle.get("package_name") or "")
    if not _DOMAIN_KEY.match(domain_key):
        blockers.append("domain_key_invalid")
    if not _PACKAGE_NAME.match(package_name):
        blockers.append("package_name_invalid")

    package_dir = workspace / str(bundle.get("package_dir") or "")
    files = bundle.get("files") if isinstance(bundle.get("files"), dict) else {}
    if not package_dir.is_dir() or package_dir.resolve() == workspace.resolve():
        blockers.append("package_dir_missing")
        return blockers
    if "__init__.py" not in files:
        blockers.append("package_init_missing")
    actual = _package_files(package_dir)
    for name in sorted(set(actual) - set(files)):
        blockers.append(f"package_unreviewed_file:{name}")
    for name, digest in sorted(files.items()):
        if name not in actual:
            blockers.append(f"package_file_missing:{name}")
        elif _sha256(actual[name]) != digest:
            blockers.append(f"package_file_hash_mismatch:{name}")

    local_modules = {p.stem for p in workspace.glob("*.py")} | {
        Path(name).stem for name in files if name.endswith(".py") and name != "__init__.py"
    }
    for name, path in actual.items():
        if name.endswith(".py"):
            blockers.extend(_import_blockers(name, path.read_text(encoding="utf-8"), local_modules))

    domain_module = str(bundle.get("domain_module") or "")
    entrypoint = str(bundle.get("entrypoint") or "")
    if f"{domain_module}.py" not in files:
        blockers.append("domain_module_not_in_package")
    if not _IDENTIFIER.match(entrypoint):
        blockers.append("entrypoint_invalid")
    if not [c for c in bundle.get("capabilities") or [] if isinstance(c, str) and c.strip()]:
        blockers.append("capabilities_missing")

    operations = bundle.get("operations") if isinstance(bundle.get("operations"), dict) else {}
    if not operations:
        blockers.append("operations_missing")
    smoke_cases = bundle.get("smoke_cases") if isinstance(bundle.get("smoke_cases"), dict) else {}
    for op_key, op in operations.items():
        if not _IDENTIFIER.match(str(op_key)) or not isinstance(op, dict):
            blockers.append(f"operation_invalid:{op_key}")
            continue
        for field in ("handler", "validator"):
            if op.get(field) and not _IDENTIFIER.match(str(op[field])):
                blockers.append(f"operation_{field}_invalid:{op_key}")
        adapter_module, _, adapter_fn = str(op.get("payload_adapter") or "").rpartition(".")
        if f"{adapter_module}.py" not in files or not _IDENTIFIER.match(adapter_fn):
            blockers.append(f"operation_payload_adapter_invalid:{op_key}")
        for checker_key in op.get("checker_keys") or []:
            if not _checker_registered(str(checker_key)):
                blockers.append(f"checker_not_registered:{op_key}:{checker_key}")
        cases = smoke_cases.get(op_key)
        if not isinstance(cases, list) or not cases or not all(
            isinstance(case, dict) and isinstance(case.get("seed"), int) for case in cases
        ):
            blockers.append(f"smoke_cases_missing:{op_key}")

    bindings = bundle.get("skill_bindings") if isinstance(bundle.get("skill_bindings"), dict) else {}
    if not bindings:
        blockers.append("skill_bindings_missing")
    promoted_domains = store.get("domains") or {}
    for skill_id, binding in bindings.items():
        if not isinstance(binding, dict) or not str(binding.get("default_curriculum_profile") or "").strip():
            blockers.append(f"skill_binding_invalid:{skill_id}")
            continue
        extra_ops = set(binding.get("allowed_operations") or []) - set(operations)
        if extra_ops:
            blockers.append(f"skill_binding_operation_unknown:{skill_id}:{','.join(sorted(extra_ops))}")
        if store_mod.is_static_skill_binding(str(skill_id)):
            blockers.append(f"skill_binding_conflict_static:{skill_id}")
        for other_key, other in promoted_domains.items():
            if other_key != domain_key and skill_id in (other.get("skill_bindings") or {}):
                blockers.append(f"skill_binding_conflict_promoted:{skill_id}:{other_key}")

    from core.registry.domain_operation_registry import get_domain_spec

    if domain_key and get_domain_spec(domain_key) is not None and domain_key not in promoted_domains:
        blockers.append("domain_conflict_static")
    previous = promoted_domains.get(domain_key)
    if previous and previous.get("package_name") != package_name:
        blockers.append("package_name_changed")
    for other_key, other in promoted_domains.items():
        if other_key != domain_key and other.get("package_name") == package_name:
            blockers.append(f"package_name_conflict:{other_key}")
    return blockers


def preflight_reviewed_bundle(workspace_dir: str | Path, *, store_path: str | Path | None = None) -> dict[str, Any]:
    """Validate a reviewed workspace without writing anything."""
    workspace = Path(workspace_dir)
    bundle = load_reviewed_bundle(workspace)
    blockers = _bundle_blockers(workspace, bundle, store_mod.load_store(store_path))
    return {
        "passed": not blockers,
        "blockers": blockers,
        "bundle": bundle,
        "bundle_sha256": bundle_sha256(bundle),
    }


def _build_store_entry(bundle: dict[str, Any], digest: str, package_import: str) -> dict[str, Any]:
    entrypoint = str(bundle["entrypoint"])
    operations = {}
    for op_key, op in bundle["operations"].items():
        operations[op_key] = {
            "handler": str(op.get("handler") or entrypoint),
            "validator": str(op.get("validator") or "") or None,
            "payload_adapter": f"{package_import}.{op['payload_adapter']}",
            "checker_keys": list(op.get("checker_keys") or []),
            "supported_answer_types": list(op.get("supported_answer_types") or []),
            "supported_presentation_modes": list(op.get("supported_presentation_modes") or ["short_answer"]),
            "runtime_contract": op.get("runtime_contract") or None,
            "provided_capabilities": list(op.get("provided_capabilities") or [op_key]),
        }
    return {
        "proposal_id": str(bundle.get("proposal_id") or ""),
        "proposal_revision": bundle.get("proposal_revision"),
        "approved_by": str(bundle["review"]["approved_by"]),
        "bundle_sha256": digest,
        "registry_revision": f"promoted-{digest[:12]}",
        "package_name": str(bundle["package_name"]),
        "package_import": package_import,
        "package_files": dict(bundle["files"]),
        "domain_module": f"{package_import}.{bundle['domain_module']}",
        "entrypoint": entrypoint,
        "capabilities": sorted({str(c) for c in bundle["capabilities"]}),
        "operations": operations,
        "skill_bindings": {
            str(skill_id): {
                "default_curriculum_profile": str(binding["default_curriculum_profile"]),
                "allowed_operations": list(binding.get("allowed_operations") or bundle["operations"].keys()),
            }
            for skill_id, binding in bundle["skill_bindings"].items()
        },
    }


def _payload_checker(payload: dict[str, Any]) -> str:
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    return str(
        contract.get("checker_key") or payload.get("checker_key") or contract.get("checker") or payload.get("checker") or ""
    ).strip()


def _verify_promoted_capability(domain_key: str, entry: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
    from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
    from core.registry.taxonomy_registry import get_allowed_operations, get_confirmed_skill_binding

    blockers = [
        f"registry_inconsistent:{issue.get('missing_layers')}"
        for issue in check_registry_consistency()
        if issue.get("domain_key") == domain_key
    ]
    spec = get_domain_spec(domain_key)
    expected_ops = set(entry["operations"])
    if spec is None or set(spec.allowed_operations) != expected_ops:
        blockers.append("registry_operations_incomplete")

    executed: dict[str, int] = {}
    for op_key, op in entry["operations"].items():
        for case in bundle["smoke_cases"][op_key]:
            try:
                kwargs = {"seed": case["seed"], "constraints": case.get("constraints") or {}}
                _, payload = dispatch_registered_operation(domain_key, op_key, **kwargs)
                _, repeat = dispatch_registered_operation(domain_key, op_key, **kwargs)
            except Exception as exc:
                blockers.append(f"operation_dispatch_failed:{op_key}:{type(exc).__name__}:{exc}")
                continue
            if json.dumps(payload, sort_keys=True, default=str) != json.dumps(repeat, sort_keys=True, default=str):
                blockers.append(f"operation_not_deterministic:{op_key}")
            checker = _payload_checker(payload)
            if op["checker_keys"] and checker not in op["checker_keys"]:
                blockers.append(f"payload_checker_not_declared:{op_key}:{checker}")
            if checker and not _checker_registered(checker):
                blockers.append(f"payload_checker_not_registered:{op_key}:{checker}")
            executed[op_key] = executed.get(op_key, 0) + 1

    bindings: dict[str, Any] = {}
    for skill_id, binding in entry["skill_bindings"].items():
        confirmed = get_confirmed_skill_binding(skill_id) or {}
        allowed = get_allowed_operations(domain_key, skill_id=skill_id)
        if confirmed.get("fixed_domain_key") != domain_key:
            blockers.append(f"skill_binding_unresolved:{skill_id}")
        if set(allowed) != set(binding["allowed_operations"]):
            blockers.append(f"skill_allowed_operations_mismatch:{skill_id}")
        for op_key in binding["allowed_operations"]:
            resolved = resolve_domain_authority(skill_id, selected_operation=op_key)
            if resolved.fixed_domain_key != domain_key or resolved.selected_operation != op_key:
                blockers.append(f"skill_operation_unroutable:{skill_id}:{op_key}")
        bindings[skill_id] = {"fixed_domain_key": confirmed.get("fixed_domain_key"), "allowed_operations": sorted(allowed)}

    if blockers:
        raise CapabilityPromotionError(
            "post_promotion_verification_failed", "; ".join(blockers), details={"blockers": blockers}
        )
    return {"operations_executed": executed, "skill_bindings": bindings}


def promote_reviewed_workspace(
    workspace_dir: str | Path,
    *,
    teacher_approved: bool,
    store_path: str | Path | None = None,
    package_root: str | Path | None = None,
    package_import_prefix: str | None = None,
) -> dict[str, Any]:
    if not teacher_approved:
        raise CapabilityPromotionError("teacher_not_approved", "teacher approval required")
    workspace = Path(workspace_dir)
    preflight = preflight_reviewed_bundle(workspace, store_path=store_path)
    if not preflight["passed"]:
        raise CapabilityPromotionError(
            "preflight_failed", "reviewed bundle preflight failed", details={"blockers": preflight["blockers"]}
        )

    bundle = preflight["bundle"]
    domain_key = str(bundle["domain_key"])
    package_name = str(bundle["package_name"])
    root = Path(package_root or DEFAULT_PACKAGE_ROOT)
    package_import = f"{package_import_prefix or DEFAULT_PACKAGE_IMPORT_PREFIX}.{package_name}"
    entry = _build_store_entry(bundle, preflight["bundle_sha256"], package_import)

    store_file = store_mod.store_path(store_path)
    store_before = store_file.read_bytes() if store_file.is_file() else None
    store_payload = store_mod.load_store(store_path)
    previous_entry = store_payload["domains"].get(domain_key)
    target_dir = root / package_name
    skill_ids = set(entry["skill_bindings"]) | set((previous_entry or {}).get("skill_bindings") or {})
    snapshot = store_mod.snapshot_runtime_state(domain_key, skill_ids, package_import)

    if previous_entry == entry and _package_matches(target_dir, bundle["files"]):
        try:
            store_mod.apply_promoted_entry(domain_key, entry)
            verification = _verify_promoted_capability(domain_key, entry, bundle)
        except Exception:
            store_mod.restore_runtime_state(snapshot)
            raise
        return _result(domain_key, entry, verification, target_dir, unchanged=True)

    staging = root / f".{package_name}.staging"
    backup = root / f".{package_name}.rollback"
    root_existed = root.exists()
    target_existed = target_dir.exists()
    backup_ready = False
    committed = False
    rolled_back = False
    try:
        root.mkdir(parents=True, exist_ok=True)
        for leftover in (staging, backup):
            if leftover.exists():
                shutil.rmtree(leftover)
        shutil.copytree(workspace / str(bundle["package_dir"]), staging, ignore=shutil.ignore_patterns("__pycache__"))
        if not _package_matches(staging, bundle["files"]):
            raise CapabilityPromotionError("package_copy_mismatch", "staged package differs from reviewed files")
        if target_existed:
            target_dir.replace(backup)
            backup_ready = True
        staging.replace(target_dir)

        store_payload["domains"][domain_key] = entry
        store_mod.write_store_atomic(store_path, store_payload)

        store_mod.remove_promoted_entry(domain_key, previous_entry)
        store_mod.purge_package_modules(package_import)
        importlib.invalidate_caches()
        store_mod.apply_promoted_entry(domain_key, entry)
        verification = _verify_promoted_capability(domain_key, entry, bundle)
        committed = True
    except Exception as exc:
        def _restore_package() -> None:
            if target_dir.exists() and (backup_ready or not target_existed):
                shutil.rmtree(target_dir)
            if backup_ready:
                backup.replace(target_dir)
            if staging.exists():
                shutil.rmtree(staging)
            if not root_existed and root.exists() and not any(root.iterdir()):
                root.rmdir()

        def _restore_store() -> None:
            if store_before is not None:
                store_file.write_bytes(store_before)
            elif store_file.exists():
                store_file.unlink()

        def _restore_runtime() -> None:
            store_mod.restore_runtime_state(snapshot)
            importlib.invalidate_caches()

        rollback_errors: list[str] = []
        for label, step in (("package", _restore_package), ("store", _restore_store), ("runtime", _restore_runtime)):
            try:
                step()
            except Exception as rollback_exc:
                rollback_errors.append(f"{label}:{type(rollback_exc).__name__}:{rollback_exc}")
        if rollback_errors:
            raise CapabilityPromotionError(
                "rollback_incomplete",
                f"promotion failed ({exc}) and rollback was incomplete",
                details={"rollback_errors": rollback_errors, "backup_path": str(backup)},
            ) from exc
        rolled_back = True
        code = exc.code if isinstance(exc, CapabilityPromotionError) else "promotion_failed"
        details = dict(getattr(exc, "details", {}) or {})
        details["rolled_back"] = True
        raise CapabilityPromotionError(code, str(exc), details=details) from exc
    finally:
        # A failed rollback keeps the backup: it is the only copy of the previous package.
        if committed or rolled_back:
            shutil.rmtree(backup, ignore_errors=True)
            shutil.rmtree(staging, ignore_errors=True)

    return _result(domain_key, entry, verification, target_dir, unchanged=False)


def _result(
    domain_key: str, entry: dict[str, Any], verification: dict[str, Any], target_dir: Path, *, unchanged: bool
) -> dict[str, Any]:
    return {
        "promoted": True,
        "unchanged": unchanged,
        "domain_key": domain_key,
        "registry_revision": entry["registry_revision"],
        "bundle_sha256": entry["bundle_sha256"],
        "allowed_operations": sorted(entry["operations"]),
        "skill_bindings": verification["skill_bindings"],
        "operations_executed": verification["operations_executed"],
        "package_path": str(target_dir),
    }
