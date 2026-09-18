from __future__ import annotations

import os

import yaml

from core.gencode import pipeline_orchestrator


def _clear_cache() -> None:
    with pipeline_orchestrator._YAML_CACHE_LOCK:
        pipeline_orchestrator._YAML_CACHE.clear()


def test_load_yaml_parses_unchanged_file_once(tmp_path, monkeypatch):
    path = tmp_path / "rules.yaml"
    path.write_text("skills:\n  - skill_id: demo\n", encoding="utf-8")
    _clear_cache()
    calls = 0
    original = yaml.safe_load

    def counted(value):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(yaml, "safe_load", counted)
    assert pipeline_orchestrator._load_yaml(path)["skills"][0]["skill_id"] == "demo"
    assert pipeline_orchestrator._load_yaml(path)["skills"][0]["skill_id"] == "demo"
    assert calls == 1


def test_load_yaml_reloads_after_stat_change(tmp_path, monkeypatch):
    path = tmp_path / "rules.yaml"
    path.write_text("value: one\n", encoding="utf-8")
    _clear_cache()
    calls = 0
    original = yaml.safe_load

    def counted(value):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(yaml, "safe_load", counted)
    assert pipeline_orchestrator._load_yaml(path) == {"value": "one"}
    path.write_text("value: two-updated\n", encoding="utf-8")
    current = path.stat()
    os.utime(path, ns=(current.st_atime_ns, current.st_mtime_ns + 1_000_000))
    assert pipeline_orchestrator._load_yaml(path) == {"value": "two-updated"}
    assert calls == 2


def test_load_yaml_does_not_cache_malformed_yaml(tmp_path, monkeypatch):
    path = tmp_path / "rules.yaml"
    path.write_text("skills: [\n", encoding="utf-8")
    _clear_cache()
    calls = 0
    original = yaml.safe_load

    def counted(value):
        nonlocal calls
        calls += 1
        return original(value)

    monkeypatch.setattr(yaml, "safe_load", counted)
    assert pipeline_orchestrator._load_yaml(path) == {}
    assert pipeline_orchestrator._load_yaml(path) == {}
    assert calls == 2
