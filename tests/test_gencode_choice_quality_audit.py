from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
from scripts.gencode_choice_quality_audit import _evaluate_choice_label_distribution


def test_choice_quality_audit_for_skill() -> None:
    cmd = [
        sys.executable,
        "scripts/gencode_choice_quality_audit.py",
        "--skill-id",
        "vh_數學B1_AbsoluteValueInequality",
        "--samples",
        "100",
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=True)
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    rows = payload.get("results", [])
    target = None
    for r in rows:
        if r.get("module") == "skills.vh_數學B1_AbsoluteValueInequality":
            target = r
            break
    assert target is not None
    assert target.get("choice_question_count", 0) >= 20
    counts = target.get("choice_answer_label_counts", {})
    assert len([k for k, v in counts.items() if v > 0]) >= 2
    assert target.get("fixed_label_detected") is False


def test_fixed_label_detected_when_count_ge_20_single_label() -> None:
    out = _evaluate_choice_label_distribution(25, {"A": 25})
    assert out["fixed_detected"] is True
    assert "choice_answer_fixed_label_detected" in out["issues"]


def test_not_fixed_when_two_labels_present() -> None:
    out = _evaluate_choice_label_distribution(25, {"A": 10, "B": 15})
    assert out["fixed_detected"] is False
    assert "choice_answer_fixed_label_detected" not in out["issues"]


def test_insufficient_samples_adds_warning_only() -> None:
    out = _evaluate_choice_label_distribution(10, {"A": 10})
    assert out["fixed_detected"] is False
    assert "insufficient_choice_samples_for_label_distribution" in out["warnings"]
