# -*- coding: utf-8 -*-
"""Static B1–B4 Skill / Generator problem-type inventory (read-only).

Does NOT treat static PASS as dynamic generation or math correctness.
Outputs JSON + Markdown under reports/gencode_closed_loop/.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.services.generator_problem_type_inventory import (
    inventory_skill_generator_problem_types,
)
from core.gencode.services.gencode_status_query_service import (
    build_admin_skills_gencode_status_map,
)

VOLUMES = ("數學B1", "數學B2", "數學B3", "數學B4")
VOLUME_CODE = {
    "數學B1": "B1",
    "數學B2": "B2",
    "數學B3": "B3",
    "數學B4": "B4",
}


def _volume_from_skill(skill_id: str, volume: str | None) -> str:
    if volume in VOLUME_CODE:
        return VOLUME_CODE[volume]
    for code, label in (("B1", "數學B1"), ("B2", "數學B2"), ("B3", "數學B3"), ("B4", "數學B4")):
        if f"vh_{label}_" in skill_id or skill_id.startswith(f"outline_vocational_{label}"):
            return code
    return "?"


def main() -> int:
    db_path = ROOT / "instance" / "kumon_math.db"
    if not db_path.is_file():
        print(f"DB not found: {db_path}")
        return 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # All registered vocational B1–B4 skills (curriculum + outline in skills_info).
    rows = conn.execute(
        """
        SELECT
            si.skill_id,
            si.skill_ch_name,
            si.skill_en_name,
            si.category,
            si.is_active,
            sc.curriculum,
            sc.volume,
            sc.chapter,
            sc.section,
            sc.display_order
        FROM skills_info si
        LEFT JOIN skill_curriculum sc ON sc.skill_id = si.skill_id
        WHERE
            si.skill_id LIKE 'vh_數學B1_%'
            OR si.skill_id LIKE 'vh_數學B2_%'
            OR si.skill_id LIKE 'vh_數學B3_%'
            OR si.skill_id LIKE 'vh_數學B4_%'
            OR si.skill_id LIKE 'outline_vocational_數學B1%'
            OR si.skill_id LIKE 'outline_vocational_數學B2%'
            OR si.skill_id LIKE 'outline_vocational_數學B3%'
            OR si.skill_id LIKE 'outline_vocational_數學B4%'
            OR sc.volume IN ('數學B1', '數學B2', '數學B3', '數學B4')
        ORDER BY sc.volume, sc.display_order, si.skill_id
        """
    ).fetchall()

    # Deduplicate by skill_id (curriculum join may multiply).
    by_skill: dict[str, dict] = {}
    for r in rows:
        sid = str(r["skill_id"])
        if sid in by_skill:
            continue
        by_skill[sid] = {
            "skill_id": sid,
            "skill_ch_name": str(r["skill_ch_name"] or ""),
            "skill_en_name": str(r["skill_en_name"] or ""),
            "category": str(r["category"] or ""),
            "is_active": bool(r["is_active"]),
            "curriculum": str(r["curriculum"] or ""),
            "volume": str(r["volume"] or ""),
            "chapter": str(r["chapter"] or ""),
            "section": str(r["section"] or ""),
            "display_order": r["display_order"],
        }

    # Textbook / eligible counts (separate from problem-type counts).
    textbook_counts: dict[str, int] = {}
    for sid in by_skill:
        textbook_counts[sid] = int(
            conn.execute(
                "SELECT COUNT(*) c FROM textbook_examples WHERE skill_id = ?",
                (sid,),
            ).fetchone()["c"]
        )

    skill_ids = list(by_skill.keys())
    v3_map = build_admin_skills_gencode_status_map(conn, skill_ids, project_root=ROOT)

    details: list[dict] = []
    for sid, meta in by_skill.items():
        inv = inventory_skill_generator_problem_types(
            sid,
            project_root=ROOT,
            category=meta["category"],
        )
        v3 = v3_map.get(sid) or {}
        volume_code = _volume_from_skill(sid, meta["volume"] or None)
        eligible = v3.get("eligible_count")
        verified = v3.get("available_count", v3.get("verified_count"))
        teacher = (v3.get("teacher_status") or {}) if isinstance(v3.get("teacher_status"), dict) else {}
        details.append(
            {
                "volume": volume_code,
                "volume_label": meta["volume"],
                "skill_id": sid,
                "skill_ch_name": meta["skill_ch_name"],
                "category": meta["category"],
                "chapter": meta["chapter"],
                "section": meta["section"],
                "is_outline": inv["is_outline"],
                "is_active": meta["is_active"],
                "generator_impl_count": inv["generator_impl_count"],
                "usable_problem_type_count": inv["usable_problem_type_count"],
                "defined_problem_type_count": inv["defined_problem_type_count"],
                "not_runtime_problem_type_count": inv["not_runtime_problem_type_count"],
                "family_count": inv["family_count"],
                "usable_problem_type_ids": inv["usable_problem_type_ids"],
                "defined_problem_type_ids": inv["defined_problem_type_ids"],
                "not_runtime_problem_type_ids": inv["not_runtime_problem_type_ids"],
                "family_ids": inv["family_ids"],
                "display_label": inv["display_label"],
                "count_confidence": inv["count_confidence"],
                "health": inv["health"],
                "anomalies": inv["anomalies"],
                "facade_exists": inv["facade_exists"],
                "package_exists": inv["package_exists"],
                "textbook_example_count": textbook_counts.get(sid, 0),
                "eligible_example_count": eligible,
                "verified_example_count": verified,
                "v3_status_label": teacher.get("label") or v3.get("status_label") or "",
                "v3_capability_status": (v3.get("capability") or {}).get("capability_status")
                if isinstance(v3.get("capability"), dict)
                else v3.get("capability_status"),
                "runtime_published_count": v3.get("published_count"),
                "evidence": inv["evidence"],
            }
        )

    # Summaries: per-skill sums (NOT cross-skill dedupe of problem_type_id).
    by_vol: dict[str, list[dict]] = defaultdict(list)
    for row in details:
        by_vol[row["volume"]].append(row)

    def _sum_known(rows: list[dict], key: str) -> int:
        total = 0
        for r in rows:
            val = r.get(key)
            if isinstance(val, int):
                total += val
        return total

    volume_summary = {}
    for code in ("B1", "B2", "B3", "B4", "?"):
        rows_v = by_vol.get(code, [])
        if not rows_v and code == "?":
            continue
        executable = [r for r in rows_v if not r["is_outline"]]
        outlines = [r for r in rows_v if r["is_outline"]]
        volume_summary[code] = {
            "skill_total": len(rows_v),
            "executable_skill_total": len(executable),
            "outline_skill_total": len(outlines),
            "generator_impl_sum": _sum_known(executable, "generator_impl_count"),
            "usable_problem_type_sum_per_skill": _sum_known(executable, "usable_problem_type_count"),
            "note": "usable_problem_type_sum_per_skill = sum of per-skill usable counts (NOT cross-skill dedupe)",
        }

    no_generator = [
        r["skill_id"]
        for r in details
        if not r["is_outline"]
        and int(r.get("generator_impl_count") or 0) == 0
        and int(r.get("usable_problem_type_count") or 0) == 0
    ]
    type_anomalies = [
        {"skill_id": r["skill_id"], "health": r["health"], "anomalies": r["anomalies"]}
        for r in details
        if r["health"] in {"WARN", "FAIL", "UNKNOWN"} and not r["is_outline"]
    ]
    generators_not_runtime = [
        {
            "skill_id": r["skill_id"],
            "generator_impl_count": r["generator_impl_count"],
            "usable_problem_type_count": r["usable_problem_type_count"],
            "not_runtime_problem_type_ids": r["not_runtime_problem_type_ids"],
            "anomalies": r["anomalies"],
        }
        for r in details
        if not r["is_outline"]
        and int(r.get("generator_impl_count") or 0) > 0
        and (
            r.get("usable_problem_type_count") == 0
            or int(r.get("not_runtime_problem_type_count") or 0) > 0
        )
    ]

    # Cross-skill unique problem_type_id (informational only).
    cross_unique: set[str] = set()
    for r in details:
        if r["is_outline"]:
            continue
        ids = r.get("usable_problem_type_ids") or []
        if isinstance(ids, list):
            cross_unique.update(str(x) for x in ids)

    health_counts = Counter(r["health"] for r in details if not r["is_outline"])

    # Targeted static regressions mentioned by the user.
    regressions = {}
    for sid in (
        "vh_數學B1_DistanceBetweenPointAndLine",
        "vh_數學B1_DistanceBetweenTwoParallelLines",
        "vh_數學B1_SlopeOfALine",
        "vh_數學B1_PropertiesOfParallelLines",
    ):
        row = next((d for d in details if d["skill_id"] == sid), None)
        regressions[sid] = row

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "counting_rules": {
            "type_identity": "problem_type_id (normalized: strip trailing _digits only)",
            "usable_means": (
                "component in facade GENERATOR_KEYS ∩ package GENERATOR_KEYS, "
                "listed in both GENERATOR_SPECS, generate.py exists, readiness not blocked"
            ),
            "generator_impl_count": "distinct agent_skills_v3/<skill>/components/*/generate.py",
            "not_confused_with": [
                "consecutive_correct_required (晉級門檻)",
                "eligible_example_count",
                "textbook_example_count",
            ],
            "volume_usable_sum": "sum of per-skill usable counts (NOT cross-skill dedupe)",
            "cross_skill_unique_usable_types": len(cross_unique),
            "static_only": True,
        },
        "volume_summary": volume_summary,
        "system_totals": {
            "skill_total": len(details),
            "executable_skill_total": sum(1 for r in details if not r["is_outline"]),
            "outline_skill_total": sum(1 for r in details if r["is_outline"]),
            "generator_impl_sum": _sum_known(
                [r for r in details if not r["is_outline"]], "generator_impl_count"
            ),
            "usable_problem_type_sum_per_skill": _sum_known(
                [r for r in details if not r["is_outline"]], "usable_problem_type_count"
            ),
            "cross_skill_unique_usable_problem_types": len(cross_unique),
            "health_counts": dict(health_counts),
        },
        "no_generator_skills": no_generator,
        "type_anomaly_skills": type_anomalies,
        "generators_not_fully_runtime": generators_not_runtime,
        "common_defect_modules": [
            {
                "module": "core/gencode/runtime_skill_wrapper.py",
                "role": "Runtime dispatch / collect_available_runtime_problem_types",
            },
            {
                "module": "core/gencode/services/generator_problem_type_inventory.py",
                "role": "Shared static usable problem-type counting for admin + audit",
            },
            {
                "module": "core/gencode/services/gencode_status_query_service.py",
                "role": "V3 READY / published / eligible status (separate from type counts)",
            },
        ],
        "static_regressions": {
            "src_4584_point_line_not_parallel": {
                "point_line_skill": "vh_數學B1_DistanceBetweenPointAndLine",
                "parallel_skill": "vh_數學B1_DistanceBetweenTwoParallelLines",
                "point_has_src_4584": "src_4584"
                in str(
                    (regressions.get("vh_數學B1_DistanceBetweenPointAndLine") or {}).get(
                        "usable_problem_type_ids"
                    )
                )
                or True,  # binding checked via component registry in unit tests
            },
            "slope_of_a_line": regressions.get("vh_數學B1_SlopeOfALine"),
            "properties_of_parallel_lines": regressions.get(
                "vh_數學B1_PropertiesOfParallelLines"
            ),
        },
        "skills": details,
    }

    # Fix regression evidence properly with component ids from inventory evidence paths.
    from core.gencode.services.gencode_status_query_service import load_v3_skill_generator_specs

    point_specs = load_v3_skill_generator_specs(skill_id="vh_數學B1_DistanceBetweenPointAndLine")
    parallel_specs = load_v3_skill_generator_specs(
        skill_id="vh_數學B1_DistanceBetweenTwoParallelLines"
    )
    payload["static_regressions"]["src_4584_point_line_not_parallel"] = {
        "point_components": sorted(
            {str(r.get("component_id")) for r in point_specs if r.get("component_id")}
        ),
        "parallel_components": sorted(
            {str(r.get("component_id")) for r in parallel_specs if r.get("component_id")}
        ),
        "src_4584_in_point": any(str(r.get("component_id")) == "src_4584" for r in point_specs),
        "src_4584_in_parallel": any(
            str(r.get("component_id")) == "src_4584" for r in parallel_specs
        ),
    }

    out_dir = ROOT / "reports" / "gencode_closed_loop"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "b1_b4_generator_problem_type_inventory.json"
    md_path = out_dir / "b1_b4_generator_problem_type_inventory.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# 技高數學 B1～B4 Generator 題型靜態盤點")
    lines.append("")
    lines.append(f"- 產生時間：`{payload['generated_at']}`")
    lines.append("- 性質：**靜態分析**（不可視為動態出題或數學正確性已通過）")
    lines.append(
        "- 題型身分：`problem_type_id`（僅去除尾隨 `_數字` 變體；跨教材來源／隨機 seed 不去重膨脹）"
    )
    lines.append(
        "- 可用題型：facade∩package `GENERATOR_KEYS` + 雙邊 `GENERATOR_SPECS` + `generate.py` 存在 + readiness 未封鎖"
    )
    lines.append(
        "- 冊別「可用題型數」彙總＝**各 Skill 可用題型數加總**（非跨 Skill 去重）；"
        f"跨 Skill 去重唯一可用題型數＝`{len(cross_unique)}`"
    )
    lines.append("")
    lines.append("## 各冊彙總")
    lines.append("")
    lines.append("| 冊別 | Skill 總數 | 可執行 Skill | Outline | Generator 實作數加總 | 可用題型數加總（逐 Skill） |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for code in ("B1", "B2", "B3", "B4"):
        s = volume_summary.get(code, {})
        lines.append(
            f"| {code} | {s.get('skill_total', 0)} | {s.get('executable_skill_total', 0)} | "
            f"{s.get('outline_skill_total', 0)} | {s.get('generator_impl_sum', 0)} | "
            f"{s.get('usable_problem_type_sum_per_skill', 0)} |"
        )
    tot = payload["system_totals"]
    lines.append(
        f"| 合計 | {tot['skill_total']} | {tot['executable_skill_total']} | "
        f"{tot['outline_skill_total']} | {tot['generator_impl_sum']} | "
        f"{tot['usable_problem_type_sum_per_skill']} |"
    )
    lines.append("")
    lines.append("## 異常清單摘要")
    lines.append("")
    lines.append(f"- 沒有 Generator 的可執行 Skill：`{len(no_generator)}`")
    lines.append(f"- 題型／Registry 異常（WARN/FAIL/UNKNOWN）：`{len(type_anomalies)}`")
    lines.append(f"- 有 Generator 但未完全接入 Runtime：`{len(generators_not_runtime)}`")
    lines.append(f"- 健康狀態分布：`{dict(health_counts)}`")
    lines.append("")
    lines.append("### src_4584 / SlopeOfALine 靜態回歸")
    lines.append("")
    reg = payload["static_regressions"]["src_4584_point_line_not_parallel"]
    lines.append(
        f"- src_4584 ∈ PointAndLine：`{reg['src_4584_in_point']}`；"
        f"∈ ParallelLines：`{reg['src_4584_in_parallel']}`"
    )
    slope = regressions.get("vh_數學B1_SlopeOfALine") or {}
    lines.append(
        f"- SlopeOfALine 可用題型數：`{slope.get('usable_problem_type_count')}` "
        f"實作數：`{slope.get('generator_impl_count')}` 健康：`{slope.get('health')}`"
    )
    lines.append("")
    lines.append("## Skill 明細")
    lines.append("")
    lines.append(
        "| 冊別 | Skill ID | 中文名稱 | 實作數 | 可用題型數 | Family 數 | "
        "教材題數 | Eligible | V3 | Runtime published | 健康 | 異常 |"
    )
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---|---:|---|---|")
    for r in details:
        usable = r["usable_problem_type_count"]
        usable_s = "—" if usable is None else str(usable)
        anomalies = "; ".join(r["anomalies"][:3]) if r["anomalies"] else ""
        lines.append(
            f"| {r['volume']} | `{r['skill_id']}` | {r['skill_ch_name']} | "
            f"{r['generator_impl_count']} | {usable_s} | {r['family_count']} | "
            f"{r['textbook_example_count']} | {r['eligible_example_count']} | "
            f"{r['v3_status_label'] or r['v3_capability_status'] or ''} | "
            f"{r['runtime_published_count']} | {r['health']} | {anomalies} |"
        )

    lines.append("")
    lines.append("## 題型識別清單（逐 Skill）")
    lines.append("")
    for r in details:
        if r["is_outline"]:
            continue
        lines.append(f"### `{r['skill_id']}` — {r['skill_ch_name']}")
        lines.append(f"- 可用：{', '.join(r['usable_problem_type_ids']) or '（無）'}")
        if r["not_runtime_problem_type_ids"]:
            lines.append(
                f"- 已定義但未接入 Runtime：{', '.join(r['not_runtime_problem_type_ids'])}"
            )
        if r["family_ids"]:
            lines.append(f"- Family/line_type：{', '.join(r['family_ids'])}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        "totals",
        tot["executable_skill_total"],
        "impl",
        tot["generator_impl_sum"],
        "usable_sum",
        tot["usable_problem_type_sum_per_skill"],
        "cross_unique",
        tot["cross_skill_unique_usable_problem_types"],
    )
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
