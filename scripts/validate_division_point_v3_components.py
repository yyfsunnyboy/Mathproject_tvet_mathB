from __future__ import annotations

import importlib.util
import json
import math
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.coordinate_pair_checker import (
    check_coordinate_pair_answer,
    parse_coordinate_pair_answer,
)
from core.gencode.services.v3_question_integrity_validator import validate_component_payload

SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
SOURCE_IDS = (4420, 4421, 4423, 4427, 4438, 4512, 4513)
COMPONENT_ROOT = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID / "components"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module_load_failed:{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_math(payload: dict) -> None:
    operation = payload["operation"]
    coords = payload["metadata"]["generation_coords"]
    if operation == "compute_section_point_distance_from_origin":
        px, py = coords["P"]
        expected = math.isqrt(int(px * px + py * py))
        assert expected > 0 and str(expected) == payload["correct_value"]
        return
    semantic_answer = payload["metadata"].get("semantic_answer") or payload["correct_answer"]
    parsed = parse_coordinate_pair_answer(semantic_answer)
    assert parsed is not None
    if operation == "compute_centroid_coordinates":
        expected = (
            sum(coords[key][0] for key in ("A", "B", "C")) / 3,
            sum(coords[key][1] for key in ("A", "B", "C")) / 3,
        )
    else:
        m, n = [int(value) for value in payload["metadata"]["ratio_values"].split(":")]
        expected = (
            (n * coords["A"][0] + m * coords["B"][0]) / (m + n),
            (n * coords["A"][1] + m * coords["B"][1]) / (m + n),
        )
    assert math.isclose(float(parsed[0]), expected[0], abs_tol=1e-9)
    assert math.isclose(float(parsed[1]), expected[1], abs_tol=1e-9)


def _validate_checker(payload: dict) -> None:
    if payload["presentation_mode"] == "single_choice":
        choices = [choice["label"] for choice in payload["choices"]]
        correct = payload["correct_answer"]
        wrong = next(label for label in choices if label != correct)
        assert check_choice_label(correct, correct, choices)
        assert not check_choice_label(wrong, correct, choices)
        assert len(payload["choices"]) == 4
        assert len({choice["text"] for choice in payload["choices"]}) == 4
        assert choices.count(correct) == 1
    else:
        correct = payload["correct_answer"]
        parsed = parse_coordinate_pair_answer(correct)
        assert parsed is not None
        wrong = f"({parsed[0] + 1},{parsed[1]})"
        assert check_coordinate_pair_answer(correct, correct)
        assert not check_coordinate_pair_answer(wrong, correct)


def main() -> int:
    results = []
    for source_id in SOURCE_IDS:
        component_id = f"src_{source_id}"
        component_dir = COMPONENT_ROOT / component_id
        files = [component_dir / name for name in ("metadata.py", "generate.py", "get_hint.py")]
        assert all(path.is_file() for path in files)
        for path in files:
            py_compile.compile(str(path), doraise=True)
        generate_module = _load(component_dir / "generate.py", f"generate_{source_id}")
        hint_module = _load(component_dir / "get_hint.py", f"hint_{source_id}")
        for seed in range(10):
            payload = generate_module.generate(seed=seed, component_id=component_id)
            assert payload["component_id"] == component_id
            assert payload["source_id"] == source_id
            assert payload["metadata"]["source_trace"]["source_id"] == source_id
            assert payload["question_text"].strip()
            assert "placeholder" not in payload["question_text"].lower()
            assert hint_module.get_hint(1, payload).strip()
            assert hint_module.get_hint(2, payload).strip()
            assert hint_module.get_hint(3, payload).strip()
            integrity = validate_component_payload(payload, component_id=component_id)
            assert integrity["passed"], integrity["blockers"]
            _validate_math(payload)
            _validate_checker(payload)
        results.append({"component_id": component_id, "seeds": 10, "passed": 10})
    print(json.dumps({"skill_id": SKILL_ID, "validator": "PASS", "components": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
