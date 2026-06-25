"""Verify 3884-3886 generators and isomorphism."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from core.gencode.services.v3_source_topology_service import (
    build_source_topology_from_textbook_row,
    enrich_induced_spec_with_source_topology,
)
from core.gencode.validators.source_isomorphism_validator import validate_source_isomorphism

ROWS = {
    3884: {
        "id": 3884,
        "problem_text": "某班英文段考成績的以上累積次數分配折線圖如右，試問：以60分為準，不及格者有多少人？(A) 32 (B) 30 (C) 18 (D) 20。",
        "correct_answer": "",
        "detailed_solution": "需觀察圖中60分對應的以上累積次數，總人數減去及格人數即為不及格人數。",
    },
    3885: {
        "id": 3885,
        "problem_text": "接續上題，成績在70～80分有多少人？ (A) 20 (B) 13 (C) 7 (D) 6。",
        "correct_answer": "",
        "detailed_solution": "需觀察圖中70分與80分對應的累積次數差值。",
    },
    3886: {
        "id": 3886,
        "problem_text": "依某公司40名員工的年齡繪製以下累積次數分配折線圖如右所示，請問年齡在30～40歲有多少人？ (A) 9 (B) 10 (C) 27 (D) 32。",
        "correct_answer": "",
        "detailed_solution": "需觀察圖中40歲以下累積次數減去30歲以下累積次數。",
    },
}

root = Path("agent_skills_v3/vh_數學B4_StatisticalChartReading/components")
for eid, row in ROWS.items():
    comp = f"src_{eid}"
    spec = importlib.util.spec_from_file_location("g", root / comp / "generate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    topo = build_source_topology_from_textbook_row(row)
    induced = enrich_induced_spec_with_source_topology(
        {"textbook_example_id": eid, "domain_operation": topo["exact_task_operation"]},
        textbook_row=row,
    )
    print(f"\n===== {comp} =====")
    print("topology op:", topo.get("exact_task_operation"))
    for seed in [1, 2, 3]:
        p = mod.generate(seed=seed)
        iso = validate_source_isomorphism(p, induced_spec=induced)
        cum = (p.get("visual_spec") or {}).get("cumulative_values")
        neg = any(v < 0 for v in (cum or []))
        print(
            f"seed={seed} op={p.get('domain_operation')} answer={p.get('answer')} "
            f"semantic={p.get('semantic_answer')} iso={iso['passed']} neg_cum={neg}"
        )
        print("  stem:", p.get("question_text"))
        print("  has_image:", bool(p.get("image_base64")))
        if iso.get("blockers"):
            print("  blockers:", iso["blockers"])
