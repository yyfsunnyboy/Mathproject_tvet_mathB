from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

from core.gencode.skill_wrapper_compiler import _build_generator_specs


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "vh_數學B4_FrequencyDistributionTableConstruction"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _question_text(payload: dict) -> str:
    return str(payload.get("question_text") or payload.get("question") or "")


def _signature(text: str) -> str:
    text = re.sub(r"\d+", "#NUM", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def test_frequency_distribution_manifest_and_specs_keep_four_component_ids() -> None:
    package_root = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID
    manifest = json.loads((package_root / "component_manifest.json").read_text(encoding="utf-8"))
    router = _load_module(package_root / "__init__.py", "freq_runtime_router_manifest_test")

    assert [row["component_id"] for row in manifest["components"]] == [
        "src_3822",
        "src_3823",
        "src_3824",
        "src_3825",
    ]
    assert manifest["component_count"] == 4
    assert router.GENERATOR_KEYS == ["src_3822", "src_3823", "src_3824", "src_3825"]
    assert [row["component_id"] for row in router.GENERATOR_SPECS] == router.GENERATOR_KEYS
    assert len(router.GENERATOR_SPECS) == 4
    assert len(set(row["problem_type_id"] for row in router.GENERATOR_SPECS)) == 1


def test_build_generator_specs_does_not_deduplicate_same_problem_type_id() -> None:
    components = [
        {
            "textbook_example_id": 3822 + index,
            "component_id": f"src_{3822 + index}",
            "induced_spec_payload": {
                "source_kind": "example",
                "presentation_mode": "short_answer",
                "answer_type": "expression",
                "answer_value_type": "expression",
                "problem_type_id": "frequency_table_construction_review",
                "line_type": "frequency_table_construction_review",
                "display_order": 3822 + index,
                "source_order": 3822 + index,
                "sampling_weight": 1,
            },
        }
        for index in range(4)
    ]

    keys, specs = _build_generator_specs(components)

    assert keys == ["src_3822", "src_3823", "src_3824", "src_3825"]
    assert [row["component_id"] for row in specs] == keys
    assert len(specs) == 4


def test_frequency_distribution_runtime_dispatch_hits_all_components_without_fallback() -> None:
    facade = _load_module(
        PROJECT_ROOT / "skills" / f"{SKILL_ID}.py",
        "freq_runtime_facade_sampling_test",
    )

    counts: Counter[str] = Counter()
    signatures: dict[str, set[str]] = {}
    fallback_count = 0
    for seed in range(40):
        payload = facade.generate(seed=seed)
        component_id = str(payload.get("component_id") or "")
        counts[component_id] += 1
        signatures.setdefault(component_id, set()).add(_signature(_question_text(payload)))
        fallback_count += int(bool(payload.get("fallback_used", False)))
        assert component_id in {"src_3822", "src_3823", "src_3824", "src_3825"}

    assert counts == {
        "src_3822": 10,
        "src_3823": 10,
        "src_3824": 10,
        "src_3825": 10,
    }
    assert fallback_count == 0
    assert all(signatures[cid] for cid in counts)
    assert len({next(iter(value)) for value in signatures.values()}) == 4


def test_frequency_distribution_fixed_seed_reproducible_and_different_seeds_vary_component() -> None:
    facade = _load_module(
        PROJECT_ROOT / "skills" / f"{SKILL_ID}.py",
        "freq_runtime_facade_seed_test",
    )

    first = facade.generate(seed=7)
    second = facade.generate(seed=7)
    assert first["component_id"] == second["component_id"]
    assert _question_text(first) == _question_text(second)

    selected = {facade.generate(seed=seed)["component_id"] for seed in range(8)}
    assert len(selected) > 1
