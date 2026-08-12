# -*- coding: utf-8 -*-
"""B1 section 1-2: sync dryrun←production where needed, then validation-only reconcile."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.v3_artifact_reconciliation_service import (  # noqa: E402
    reconcile_existing_artifacts,
)

DRY = ROOT / "reports" / "gencode_v3_dryrun"
PROD = ROOT / "agent_skills_v3"
REPORT_DIR = ROOT / "reports" / "gencode_closed_loop"

# Prefer production as canonical for mismatch / prod-only cases in 1-2.
SYNC_FROM_PROD: dict[str, tuple[int, ...]] = {
    "vh_數學B1_CartesianCoordinateSystemEstablishment": (4417, 4435, 4509, 4510),
    "vh_數學B1_DivisionPointCoordinates": (4420, 4421, 4423, 4427, 4438, 4512, 4513),
    "vh_數學B1_MidpointCoordinates": (4418, 4422, 4428, 4429, 4439, 4440, 4443, 4447, 4511, 4514),
    "vh_數學B1_LinearFunction": (4500,),  # rule pack = choice; prod matches
}

# Already hash-aligned; only need tracker reconcile (incl. drawing after harness fix).
RECONCILE_ONLY: dict[str, tuple[int, ...]] = {
    "vh_數學B1_DistanceBetweenTwoPointsInPlane": (4419, 4432, 4436, 4437),  # already online; no-op safe
    "vh_數學B1_LinearFunction": (
        4424, 4425, 4426, 4433, 4434, 4441, 4442, 4444, 4445, 4446, 4448, 4449, 4515, 4516, 4500
    ),
}


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sync_component(skill_id: str, example_id: int) -> dict:
    cid = f"src_{example_id}"
    src = PROD / skill_id / "components" / cid
    dst = DRY / skill_id / "components" / cid
    before_dry = _sha(dst / "generate.py") if dst.exists() else None
    before_prod = _sha(src / "generate.py")
    if not src.is_dir() or before_prod is None:
        return {
            "textbook_example_id": example_id,
            "skill_id": skill_id,
            "synced": False,
            "reason": "missing_production",
        }
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    # Also copy skill-level runtime helpers if referenced by generate.py
    for helper in ("component_runtime.py", "component_hint.py", "component_manifest.json", "__init__.py"):
        src_h = PROD / skill_id / helper
        dst_h = DRY / skill_id / helper
        if src_h.is_file():
            dst_h.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_h, dst_h)
    after_dry = _sha(dst / "generate.py")
    return {
        "textbook_example_id": example_id,
        "skill_id": skill_id,
        "synced": True,
        "dry_before": before_dry,
        "prod": before_prod,
        "dry_after": after_dry,
        "hash_aligned": after_dry == before_prod,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--skip-sync", action="store_true")
    args = parser.parse_args()

    sync_log = []
    if not args.skip_sync:
        for skill_id, ids in SYNC_FROM_PROD.items():
            for eid in ids:
                sync_log.append(_sync_component(skill_id, eid))

    targets: dict[str, tuple[int, ...]] = {}
    for skill_id, ids in SYNC_FROM_PROD.items():
        targets[skill_id] = tuple(sorted(set(ids) | set(targets.get(skill_id, ()))))
    for skill_id, ids in RECONCILE_ONLY.items():
        targets[skill_id] = tuple(sorted(set(ids) | set(targets.get(skill_id, ()))))

    # Drop Distance from reconcile batch (already verified) to avoid noise? Keep — should still pass.
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    result = reconcile_existing_artifacts(
        conn=conn,
        targets=targets,
        project_root=ROOT,
        commit=bool(args.commit),
    )
    try:
        conn.commit()
    except Exception:
        pass
    conn.close()

    report = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "commit": bool(args.commit),
        "sync_log": sync_log,
        "reconcile": {
            "total": result.get("total"),
            "passed_count": result.get("passed_count"),
            "failed_count": result.get("failed_count"),
            "synced_count": result.get("synced_count"),
            "all_hashes_unchanged": result.get("all_hashes_unchanged"),
            "failed_ids": [
                c.get("textbook_example_id")
                for c in (result.get("components") or [])
                if not c.get("passed")
            ],
            "blockers": {
                str(c.get("textbook_example_id")): c.get("blockers")
                for c in (result.get("components") or [])
                if not c.get("passed")
            },
            "components": result.get("components"),
        },
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / (
        "b1_12_sync_reconcile_commit.json" if args.commit else "b1_12_sync_reconcile_dryrun.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "commit": args.commit,
        "synced_components": sum(1 for x in sync_log if x.get("synced")),
        "passed_count": report["reconcile"]["passed_count"],
        "failed_count": report["reconcile"]["failed_count"],
        "failed_ids": report["reconcile"]["failed_ids"],
        "report": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not report["reconcile"]["failed_ids"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
