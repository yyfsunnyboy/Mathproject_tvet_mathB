#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only storage usage audit for question_assets."""

from __future__ import annotations

import argparse
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"


def audit_storage(base_dir: Path) -> dict:
    if not base_dir.exists():
        return {"exists": False, "total_files": 0, "total_bytes": 0, "by_ext": {}}
    total_files = 0
    total_bytes = 0
    by_ext: dict[str, dict[str, int]] = {}
    for p in base_dir.rglob("*"):
        if not p.is_file():
            continue
        total_files += 1
        size = p.stat().st_size
        total_bytes += size
        ext = p.suffix.lower().lstrip(".") or "no_ext"
        if ext not in by_ext:
            by_ext[ext] = {"files": 0, "bytes": 0}
        by_ext[ext]["files"] += 1
        by_ext[ext]["bytes"] += size
    return {
        "exists": True,
        "total_files": total_files,
        "total_bytes": total_bytes,
        "by_ext": dict(sorted(by_ext.items(), key=lambda kv: kv[1]["bytes"], reverse=True)),
    }


def render_markdown(result: dict, target: Path) -> str:
    lines = [
        "# Question Assets Storage Audit",
        "",
        f"- target_dir: `{target.as_posix()}`",
        f"- exists: `{result.get('exists')}`",
        f"- total_files: {result.get('total_files', 0)}",
        f"- total_bytes: {result.get('total_bytes', 0)}",
        f"- total_size_human: {_human_size(int(result.get('total_bytes', 0)))}",
        "",
        "## By Extension",
    ]
    by_ext = result.get("by_ext", {})
    if not by_ext:
        lines.append("- no files")
        return "\n".join(lines) + "\n"
    for ext, stats in by_ext.items():
        lines.append(
            f"- .{ext}: files={stats.get('files', 0)} bytes={stats.get('bytes', 0)} size={_human_size(int(stats.get('bytes', 0)))}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only audit for question_assets storage usage.")
    parser.add_argument("--target-dir", default="uploads/question_assets")
    parser.add_argument("--report", default="reports/b1_import_debug/question_assets_storage_audit_report.md")
    args = parser.parse_args()

    target = Path(args.target_dir)
    if not target.is_absolute():
        target = project_root() / target
    result = audit_storage(target)
    report = Path(args.report)
    if not report.is_absolute():
        report = project_root() / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_markdown(result, target), encoding="utf-8")
    print(render_markdown(result, target))
    print(f"Report written: {report.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
