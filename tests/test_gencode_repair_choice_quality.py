from __future__ import annotations

from pathlib import Path

from core.domain.choices_unique_validator import build_shuffled_choice_payload, repair_choice_payload
from scripts.gencode_repair_choice_quality import _repair_source_file


def test_build_shuffled_choice_payload_not_fixed_a() -> None:
    labels = set()
    for seed in range(20):
        payload = build_shuffled_choice_payload("10", ["7", "8", "9"], seed=seed)
        labels.add(payload["answer"])
        assert len({c["text"] for c in payload["choices"]}) == 4
        correct_label = payload["answer"]
        mapped = {item["label"]: item["text"] for item in payload["choices"]}
        assert mapped[correct_label] == payload["correct_text"]
    assert len(labels) >= 2


def test_repair_choice_payload_normalizes_label_and_uniqueness() -> None:
    payload = {
        "choices": ["10", "10", "9", "8", "7"],
        "answer": "10",
        "correct_answer": "10",
        "answer_type": "choice_label",
    }
    out = repair_choice_payload(payload, seed=3)
    assert out["answer"] in {"A", "B", "C", "D"}
    assert out["correct_answer"] in {"A", "B", "C", "D"}
    assert len(out["choices"]) == 4
    assert len(set(out["choices"])) == 4
    assert out["correct_text"] in out["choices"]


def test_repair_source_file_requires_manual_when_pattern_unknown(tmp_path: Path) -> None:
    f = tmp_path / "demo.py"
    f.write_text("def generate(level=1):\n    return {'ok': True}\n", encoding="utf-8")
    modified, reasons = _repair_source_file(f)
    assert modified is False
    assert any("requires_manual_repair" in x for x in reasons)
