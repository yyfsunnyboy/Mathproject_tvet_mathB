"""Sandbox-only V3 skill wrapper compiler with thin-facade double-write."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from core.gencode.v3_component_scaffold_builder import normalize_v3_component_metadata_fields

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_SKILLS_DIR = PROJECT_ROOT / "skills"
PRODUCTION_V3_DIR = PROJECT_ROOT / "agent_skills_v3"


def assert_safe_project_root(project_root: str) -> Path:
    """Validate a production project root for promote/rollback operations."""
    if not str(project_root or "").strip():
        raise ValueError("unsafe_project_root")

    normalized = Path(os.path.abspath(os.path.normpath(project_root)))
    skills_dir = normalized / "skills"
    if not skills_dir.is_dir():
        raise ValueError("unsafe_project_root")

    v3_dir = normalized / "agent_skills_v3"
    try:
        v3_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise ValueError("unsafe_project_root") from None

    return normalized


def assert_safe_sandbox_root(sandbox_root: str) -> None:
    """Reject sandbox roots that could write into production directories."""
    if not str(sandbox_root or "").strip():
        raise ValueError("unsafe_sandbox_root: empty path")

    normalized = Path(os.path.abspath(os.path.normpath(sandbox_root)))
    project_root = Path(os.path.abspath(os.path.normpath(str(PROJECT_ROOT))))
    production_skills = Path(os.path.abspath(os.path.normpath(str(PRODUCTION_SKILLS_DIR))))
    production_v3 = Path(os.path.abspath(os.path.normpath(str(PRODUCTION_V3_DIR))))

    if normalized == project_root:
        raise ValueError(f"unsafe_sandbox_root: {sandbox_root!r}")
    if normalized == production_skills:
        raise ValueError(f"unsafe_sandbox_root: {sandbox_root!r}")
    if normalized == production_v3:
        raise ValueError(f"unsafe_sandbox_root: {sandbox_root!r}")

    for blocked_parent in (production_skills, production_v3):
        if _is_path_under(normalized, blocked_parent):
            raise ValueError(f"unsafe_sandbox_root: {sandbox_root!r}")


def _is_path_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _parse_induced_spec_payload(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    text = str(raw).strip()
    if not text:
        return {}
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError("induced_spec_payload must decode to a JSON object.")
    return loaded


def _fetch_verified_components(
    conn: sqlite3.Connection,
    skill_id: str,
) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT textbook_example_id, component_id, induced_spec_payload
        FROM gencode_component_tracker
        WHERE skill_id = ? AND gencode_status = 'verified'
        ORDER BY textbook_example_id ASC, component_id ASC
        """,
        (skill_id,),
    ).fetchall()
    components: list[dict[str, Any]] = []
    for row in rows:
        if hasattr(row, "keys"):
            textbook_example_id = int(row["textbook_example_id"])
            component_id = str(row["component_id"])
            payload_raw = row["induced_spec_payload"]
        else:
            textbook_example_id = int(row[0])
            component_id = str(row[1])
            payload_raw = row[2]
        components.append(
            {
                "textbook_example_id": textbook_example_id,
                "component_id": component_id,
                "induced_spec_payload": _parse_induced_spec_payload(payload_raw),
            }
        )
    return components


def _build_generator_specs(components: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    generator_keys: list[str] = []
    generator_specs: list[dict[str, Any]] = []
    for index, row in enumerate(components):
        component_id = str(row["component_id"])
        payload = row["induced_spec_payload"]
        textbook_example_id = int(row["textbook_example_id"])
        normalized = normalize_v3_component_metadata_fields(payload)
        generator_keys.append(component_id)
        generator_specs.append(
            {
                "textbook_example_id": textbook_example_id,
                "component_id": component_id,
                "generator_key": component_id,
                "presentation_mode": normalized["presentation_mode"],
                "response_mode": normalized["response_mode"],
                "interaction_type": normalized["interaction_type"],
                "source_kind": payload.get("source_kind"),
                "line_type": payload.get("line_type"),
                "answer_type": payload.get("answer_type"),
                "answer_value_type": normalized["answer_value_type"],
                "problem_type_id": payload.get("problem_type_id"),
                "display_order": int(payload.get("display_order", textbook_example_id)),
                "source_order": int(payload.get("source_order", textbook_example_id)),
                "sampling_weight": float(payload.get("sampling_weight", 1) or 1),
            }
        )
    generator_specs.sort(
        key=lambda spec: (
            int(spec.get("display_order", 0)),
            int(spec.get("textbook_example_id", 0)),
            str(spec.get("component_id", "")),
        )
    )
    generator_keys = [str(spec["component_id"]) for spec in generator_specs]
    return generator_keys, generator_specs


def _render_new_house_init_py(
    *,
    skill_id: str,
    generator_keys: list[str],
    generator_specs: list[dict[str, Any]],
) -> str:
    component_dispatch = {
        component_id: f"components/{component_id}/generate.py"
        for component_id in generator_keys
    }
    return f'''from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = {skill_id!r}
GENERATOR_KEYS = {generator_keys!r}
GENERATOR_SPECS = {generator_specs!r}
_COMPONENT_DISPATCH = {component_dispatch!r}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _component_sampling_weight(component_id: str) -> float:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return float(row.get("sampling_weight", 1) or 1)
    return 1.0


def _ordered_generator_keys() -> list[str]:
    specs_by_id = {{
        str(row.get("component_id") or ""): row
        for row in GENERATOR_SPECS
        if isinstance(row, dict) and str(row.get("component_id") or "")
    }}
    return sorted(
        GENERATOR_KEYS,
        key=lambda key: (
            int((specs_by_id.get(key) or {{}}).get("display_order", 0)),
            int((specs_by_id.get(key) or {{}}).get("textbook_example_id", 0)),
            key,
        ),
    )


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    module_name = f"v3_{{SKILL_ID}}_{{component_id}}_{{module_filename.replace('.py', '')}}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{{component_id}}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pick_component_id(
    seed: int | None = None,
    component_id: str | None = None,
) -> str:
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    ordered_keys = _ordered_generator_keys()
    if not ordered_keys:
        raise RuntimeError("generator_keys_empty")
    
    import math
    from functools import reduce
    
    raw_weights = []
    for key in ordered_keys:
        w = int(_component_sampling_weight(key) or 1)
        raw_weights.append(max(1, w))
        
    g = reduce(math.gcd, raw_weights) if raw_weights else 1
    normalized_weights = [w // g for w in raw_weights]
    
    cycle = []
    for key, w in zip(ordered_keys, normalized_weights):
        cycle.extend([key] * w)

    if seed is None:
        global _RR_CURSOR, _SHUFFLED_CYCLE
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            import random
            _SHUFFLED_CYCLE = list(cycle)
            random.shuffle(_SHUFFLED_CYCLE)
            _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]
        _RR_CURSOR += 1
        return picked
    else:
        import random
        cycle_len = len(cycle)
        cycle_seed = int(seed) // cycle_len
        shuffled = list(cycle)
        random.Random(cycle_seed).shuffle(shuffled)
        return shuffled[int(seed) % cycle_len]



def _spec_for_component(component_id: str) -> dict[str, Any]:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return dict(row)
    return {{}}


def _minimal_answer_contract(payload: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    embedded = payload.get("answer_contract")
    if isinstance(embedded, dict) and embedded.get("answer_type"):
        return dict(embedded)
    presentation_mode = str(
        payload.get("presentation_mode")
        or spec.get("presentation_mode")
        or (payload.get("metadata") or {{}}).get("presentation_mode")
        or "short_answer"
    ).strip()
    answer_type = str(
        payload.get("answer_type")
        or spec.get("answer_type")
        or (payload.get("metadata") or {{}}).get("answer_type")
        or ("single_choice" if presentation_mode == "single_choice" else "expression")
    ).strip()
    semantic_answer = str(
        payload.get("semantic_answer")
        or (payload.get("metadata") or {{}}).get("semantic_answer")
        or payload.get("display_answer")
        or payload.get("correct_answer")
        or ""
    ).strip()
    if presentation_mode == "single_choice":
        return {{
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }}
    return {{
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }}


def _merge_generator_spec(payload: dict[str, Any], component_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    spec = _spec_for_component(component_id)
    out = dict(payload)
    merge_keys = (
        "textbook_example_id",
        "component_id",
        "generator_key",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "source_kind",
        "line_type",
        "display_order",
        "source_order",
        "sampling_weight",
    )
    for key in merge_keys:
        if spec.get(key) is not None:
            out[key] = spec[key]
    out.setdefault("component_id", component_id)
    out.setdefault("generator_key", component_id)
    meta = dict(out.get("metadata") or {{}}) if isinstance(out.get("metadata"), dict) else {{}}
    for key in (
        "textbook_example_id",
        "component_id",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "source_kind",
        "line_type",
        "semantic_answer",
    ):
        if out.get(key) is not None:
            meta.setdefault(key, out.get(key))
        elif spec.get(key) is not None:
            meta.setdefault(key, spec.get(key))
    if out.get("semantic_answer") is not None:
        meta.setdefault("semantic_answer", out.get("semantic_answer"))
    out["metadata"] = meta
    if not isinstance(out.get("answer_contract"), dict) or not out.get("answer_contract"):
        out["answer_contract"] = _minimal_answer_contract(out, spec)
    if out["answer_contract"].get("checker"):
        out["checker"] = out["answer_contract"].get("checker")
        out.setdefault("checker_type", out["answer_contract"].get("checker"))
    if out["answer_contract"].get("answer_equivalence"):
        out["equivalence"] = out["answer_contract"].get("answer_equivalence")
    return out


def generate(
    level: int = 1,
    seed: int | None = None,
    component_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    picked = _pick_component_id(seed=seed, component_id=component_id)
    module = _load_component_module(picked, "generate.py")
    generate_fn = getattr(module, "generate", None)
    if not callable(generate_fn):
        raise RuntimeError(f"component_generate_missing:{{picked}}")
    payload = generate_fn(level=level, seed=seed, component_id=picked, **kwargs)
    if isinstance(payload, dict):
        if not payload.get("component_id"):
            payload["component_id"] = picked
        return _merge_generator_spec(payload, picked)
    return payload


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    payload = dict(question_payload or {{}})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "generate.py")
        check_fn = getattr(module, "check", None)
        if callable(check_fn):
            return check_fn(user_answer, correct_answer, payload)
    from core.gencode.runtime_skill_wrapper import check_answer

    return check_answer(user_answer, correct_answer, payload=payload)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = dict(question_payload or {{}})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "get_hint.py")
        hint_fn = getattr(module, "get_hint", None)
        if callable(hint_fn):
            return str(hint_fn(step, payload) or "")
    return ""
'''


def resolve_v3_package_root_from_facade(facade_path: str | Path) -> Path:
    """Resolve agent_skills_v3 root relative to a thin facade at <root>/skills/<skill_id>.py."""
    facade = Path(facade_path).resolve()
    return (facade.parent.parent / "agent_skills_v3").resolve()


def _render_thin_facade_py(
    *,
    skill_id: str,
    generator_keys: list[str],
    generator_specs: list[dict[str, Any]],
) -> str:
    return f'''from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = {skill_id!r}
GENERATOR_KEYS = {generator_keys!r}
GENERATOR_SPECS = {generator_specs!r}


def _resolve_v3_package_root() -> str:
    """Resolve V3 house root from this facade location: skills/ -> <root>/agent_skills_v3."""
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID,
        GENERATOR_KEYS,
        GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level,
        seed=seed,
        difficulty=difficulty,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return dispatch_check(
        user_answer,
        correct_answer,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )
'''


def compile_and_double_write_skill(
    conn: sqlite3.Connection,
    skill_id: str,
    sandbox_root: str,
) -> dict[str, object]:
    """Compile verified tracker rows into sandbox new-house router and thin facade."""
    assert_safe_sandbox_root(sandbox_root)

    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("skill_id must be provided.")

    components = _fetch_verified_components(conn, skill_key)
    if not components:
        raise ValueError(f"no_verified_components: {skill_key}")

    generator_keys, generator_specs = _build_generator_specs(components)

    sandbox_path = Path(os.path.abspath(os.path.normpath(sandbox_root)))
    v3_package_root = sandbox_path / "agent_skills_v3"
    new_house_path = v3_package_root / skill_key / "__init__.py"
    thin_facade_path = sandbox_path / "skills" / f"{skill_key}.py"

    new_house_path.parent.mkdir(parents=True, exist_ok=True)
    thin_facade_path.parent.mkdir(parents=True, exist_ok=True)

    new_house_source = _render_new_house_init_py(
        skill_id=skill_key,
        generator_keys=generator_keys,
        generator_specs=generator_specs,
    )
    thin_facade_source = _render_thin_facade_py(
        skill_id=skill_key,
        generator_keys=generator_keys,
        generator_specs=generator_specs,
    )

    new_house_path.write_text(new_house_source, encoding="utf-8")

    backup_path = thin_facade_path.with_suffix(f"{thin_facade_path.suffix}.bak")
    if thin_facade_path.exists() and not backup_path.exists():
        backup_path.write_text(thin_facade_path.read_text(encoding="utf-8"), encoding="utf-8")
    thin_facade_path.write_text(thin_facade_source, encoding="utf-8")

    return {
        "status": "compiled",
        "skill_id": skill_key,
        "component_count": len(generator_keys),
        "generator_keys": generator_keys,
        "generator_specs": generator_specs,
        "new_house_path": str(new_house_path.resolve()),
        "thin_facade_path": str(thin_facade_path.resolve()),
    }


def rollback_v3_to_v2_facade(
    skill_id: str,
    sandbox_root: str,
    *,
    trusted_project_root: bool = False,
) -> dict[str, object]:
    """Rollback sandbox thin facade and remove sandbox V3 route for one skill."""
    if trusted_project_root:
        assert_safe_project_root(sandbox_root)
    else:
        assert_safe_sandbox_root(sandbox_root)

    skill_key = str(skill_id or "").strip()
    if not skill_key:
        raise ValueError("skill_id must be provided.")

    sandbox_path = Path(os.path.abspath(os.path.normpath(sandbox_root)))
    facade_path = sandbox_path / "skills" / f"{skill_key}.py"
    backup_path = facade_path.with_suffix(f"{facade_path.suffix}.bak")
    v3_skill_dir = sandbox_path / "agent_skills_v3" / skill_key

    facade_restored = False
    backup_removed = False
    v3_skill_dir_removed = False
    status = "rolled_back"

    if backup_path.exists():
        facade_path.parent.mkdir(parents=True, exist_ok=True)
        facade_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        facade_restored = True
        backup_path.unlink()
        backup_removed = True
    elif facade_path.exists():
        facade_text = facade_path.read_text(encoding="utf-8")
        looks_like_v3_facade = "runtime_skill_wrapper" in facade_text or "dispatch_generate" in facade_text
        if looks_like_v3_facade:
            facade_path.unlink()
        else:
            status = "skipped_no_backup_non_v3_file"

    if v3_skill_dir.exists():
        for child in sorted(v3_skill_dir.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                child.rmdir()
        if v3_skill_dir.exists():
            v3_skill_dir.rmdir()
        v3_skill_dir_removed = True

    return {
        "status": status,
        "skill_id": skill_key,
        "facade_restored": facade_restored,
        "backup_removed": backup_removed,
        "v3_skill_dir_removed": v3_skill_dir_removed,
        "facade_path": str(facade_path.resolve()),
        "backup_path": str(backup_path.resolve()),
        "v3_skill_dir": str(v3_skill_dir.resolve()),
    }
