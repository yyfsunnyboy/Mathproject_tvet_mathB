# -*- coding: utf-8 -*-
"""Sync 資一乙 official roster (19 students) into production DB."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from scripts.roster_sync_lib import ensure_schema, sync_class_roster

CLASS_NAME = "資一乙"
REFERENCE_CLASS = "多三甲"
EXPECTED_COUNT = 19

OFFICIAL_ROSTER: list[tuple[int, str, str]] = [
    (1, "511031", "林千玄"),
    (2, "511032", "林庚德"),
    (3, "511033", "紀宥任"),
    (4, "511034", "陳世邦"),
    (5, "511035", "游楊浩恩"),
    (6, "511036", "黃麒澔"),
    (7, "511037", "廖品綸"),
    (8, "511038", "賴昶易"),
    (9, "511040", "温睿洋"),
    (10, "511039", "王恩敏"),
    (11, "511041", "江品萱"),
    (12, "511042", "吳岱錡"),
    (13, "511043", "呂沛潔"),
    (14, "511044", "汪佩伶"),
    (15, "511045", "張佳怡"),
    (16, "511046", "陳莃"),
    (17, "511047", "黃敏綺"),
    (18, "511048", "董鈺瑄"),
    (19, "511050", "賴家宇"),
]


def main(dry_run: bool = False) -> dict:
    app = create_app()
    ensure_schema(app)
    with app.app_context():
        return sync_class_roster(
            class_name=CLASS_NAME,
            official_roster=OFFICIAL_ROSTER,
            expected_count=EXPECTED_COUNT,
            backup_suffix="ziyiB_roster_sync",
            dry_run=dry_run,
            create_if_missing=True,
            reference_class_for_teacher=REFERENCE_CLASS,
            guard_classes={REFERENCE_CLASS: 31},
            report_label="ZI-YI-B",
        )


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    result = main(dry_run=dry)
    print("\n=== SUMMARY ===")
    for k, v in result.items():
        print(f"{k}: {v}")
