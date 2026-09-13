from __future__ import annotations

import json
import os
from pathlib import Path


def test_catalog_cache_is_copy_safe_and_invalidates(tmp_path):
    from core.adaptive.catalog_loader import load_catalog

    path = tmp_path / "catalog.csv"
    header = "skill_id,skill_name,family_id,family_name,theme,subskill_nodes,notes\n"
    path.write_text(header + "s1,S1,f1,F1,T,a;b,n1\n", encoding="utf-8")
    first = load_catalog(path)
    first[0].subskill_nodes.append("mutated")
    assert load_catalog(path)[0].subskill_nodes == ["a", "b"]

    path.write_text(header + "s1,S1,f1,F1,T,a;b;c,n2\n", encoding="utf-8")
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
    assert load_catalog(path)[0].subskill_nodes == ["a", "b", "c"]


def test_manifest_cache_is_copy_safe_and_writer_invalidates(tmp_path):
    from core.adaptive.manifest_registry import load_manifest, save_manifest
    from core.adaptive.schema import ManifestEntry

    path = tmp_path / "manifest.json"
    payload = {
        "skill_id": "s1",
        "family_id": "f1",
        "script_path": "one.py",
        "version": 1,
        "subskill_nodes": ["a"],
        "generated_at": "2026-09-13T00:00:00",
        "model_name": "test",
        "healer_applied": False,
    }
    path.write_text(json.dumps([payload]), encoding="utf-8")
    first = load_manifest(path)
    first[0].subskill_nodes.append("mutated")
    assert load_manifest(path)[0].subskill_nodes == ["a"]

    updated = ManifestEntry.from_dict({**payload, "script_path": "two.py"})
    save_manifest([updated], path)
    assert load_manifest(path)[0].script_path == "two.py"


def test_load_scenario_declares_exactly_23_published_b1_skills():
    root = Path(__file__).resolve().parents[1]
    manifests = list((root / "agent_skills_v3").glob("vh_數學B1_*/component_manifest.json"))
    published = [
        path for path in manifests
        if json.loads(path.read_text(encoding="utf-8-sig")).get("publish_status")
        == "production_manifest_compiled"
    ]
    assert len(published) == 23
