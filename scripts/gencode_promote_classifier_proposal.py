from __future__ import annotations

import argparse
import json
import py_compile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
CLASSIFIER_INIT = PROJECT_ROOT / "core" / "gencode" / "classifiers" / "__init__.py"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _ensure_registered(skill_id: str, class_name: str, module_name: str) -> bool:
    text = CLASSIFIER_INIT.read_text(encoding="utf-8")
    import_line = f"from .{module_name} import {class_name}"
    route_line = f'    if sid == "{skill_id}":\n        return {class_name}()'

    changed = False
    if import_line not in text:
        text = text.replace(
            "from .vocational_math_b1_absolute_value import VocationalMathB1AbsoluteValueClassifier\n",
            "from .vocational_math_b1_absolute_value import VocationalMathB1AbsoluteValueClassifier\n" + import_line + "\n",
        )
        changed = True
    if route_line not in text:
        marker = '    if sid == "vh_數學B1_AbsoluteValue":\n        return VocationalMathB1AbsoluteValueClassifier()\n'
        if marker in text:
            text = text.replace(marker, marker + route_line + "\n")
            changed = True
    if changed:
        CLASSIFIER_INIT.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    skill_id = args.skill_id
    proposal_path = REPORT_DIR / f"{skill_id}_classifier_proposal.json"
    proposal = _load_json(proposal_path)
    if not proposal:
        raise RuntimeError(f"proposal not found or invalid: {proposal_path}")

    if str(proposal.get("proposal_status", "GENERATED")) != "GENERATED":
        raise RuntimeError("proposal_status is not GENERATED")
    if proposal.get("promote_ready", True) is False:
        raise RuntimeError("proposal is not promote_ready")

    required_keys = ["proposed_problem_types", "proposed_example_map", "proposed_answer_contracts"]
    for k in required_keys:
        if k not in proposal or not proposal.get(k):
            raise RuntimeError(f"proposal missing required key: {k}")

    if skill_id != "vh_數學B1_AbsoluteValueInequality":
        raise RuntimeError("current promote script supports only vh_數學B1_AbsoluteValueInequality")

    target = PROJECT_ROOT / "core" / "gencode" / "classifiers" / "vocational_math_b1_absolute_value_inequality.py"
    if target.exists() and not args.force:
        # Safe default: keep existing classifier, only ensure registration/compile.
        pass
    else:
        template_src = PROJECT_ROOT / "core" / "gencode" / "classifiers" / "vocational_math_b1_absolute_value_inequality.py"
        if not template_src.exists():
            raise RuntimeError("template classifier file missing")
        content = template_src.read_text(encoding="utf-8")
        target.write_text(content, encoding="utf-8")

    class_name = "VocationalMathB1AbsoluteValueInequalityClassifier"
    module_name = "vocational_math_b1_absolute_value_inequality"
    _ensure_registered(skill_id, class_name, module_name)

    py_compile.compile(str(target), doraise=True)
    py_compile.compile(str(CLASSIFIER_INIT), doraise=True)

    print(
        json.dumps(
            {
                "success": True,
                "skill_id": skill_id,
                "proposal_path": str(proposal_path),
                "classifier_path": str(target),
                "registered": True,
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
