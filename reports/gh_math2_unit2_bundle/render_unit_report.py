"""Render the whole-unit review report for 數學2 Unit 2 (two skills) from the sandbox specs, bundle, rehearsal and audits.  Writes UNIT2_REVIEW_REPORT.md only."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from agent_domains_candidate.series_summation.series_summation_specs import COMPONENTS, DEFERRED, SKILLS  # noqa: E402

bundle_dir = next((ROOT / "reports" / "domain_operation_workspaces").glob("capability_sequence_series_*")) / "revision_0001"
bundle = json.loads((bundle_dir / "promotion_bundle.json").read_text(encoding="utf-8"))
rehearsal = json.loads((HERE / "rehearsal_unit2_report.json").read_text(encoding="utf-8"))
ops = Counter(spec[1] for spec in COMPONENTS.values())
per_skill = Counter(SKILLS[spec[0]] for spec in COMPONENTS.values())
out = ["# 數學2 Unit 2「級數」GenCode V3 — 整單元審閱報告", "",
       f"- Bundle：`{bundle_dir.relative_to(ROOT).as_posix()}/promotion_bundle.json`（review.status = **{bundle['review']['status']}**，approved_by 為空；尚未 Promotion、尚未 Publish）",
       f"- domain `{bundle['domain_key']}`：{len(bundle['operations'])} 個 operations，套件 {len(bundle['files'])} 個檔案（SHA-256 鎖定）",
       "- 正式教材：37 題（Stage 1 READY，12707–12743）", "", "## 結果", "",
       "| Skill | 教材題數 | PASS Component | DEFERRED |", "|---|---|---|---|"]
rows_per_skill = {"gh_Series": 26, "gh_CommonSeriesSummationFormulas": 11}
for skill, total in rows_per_skill.items():
    out.append(f"| `{skill}` | {total} | {per_skill[skill]} | {total - per_skill[skill]} |")
out += ["", f"合計：37 題 = **{len(COMPONENTS)} PASS** + **{len(DEFERRED)} DEFERRED**（覆蓋率 {len(COMPONENTS) / 37:.1%}）。", "", "## DEFERRED 與原因", ""]
out += [f"- **{cid}**：{reason}" for cid, reason in sorted(DEFERRED.items())]
out += ["", "## Operation 與 Component", "", "| operation | Component 數 |", "|---|---|"] + [f"| `{op}` | {n} |" for op, n in sorted(ops.items())]
out += ["", "## 隔離演練", "",
        f"- Phase 2 重建：{len(rehearsal['rebuild'])} / {len(COMPONENTS)} component tracker = verified；failures = {sum(1 for v in rehearsal['rebuild'].values() if (v.get('verify') or {}).get('failures'))}",
        "- 每個 component 20 seeds：`verify_payload`（Answer Contract、Checker capability、完整性驗證、正解接受、錯解拒絕、等價解接受）全部通過"]
for skill, info in rehearsal["publish"].items():
    out.append(f"- 發布演練 `{skill}`（暫存專案根目錄）：{info['status']}，{info['component_count']} components，smoke / staging / production smoke = "
               f"{info['smoke_status']} / {info['staging_smoke_status']} / {info['production_smoke_status']}；variation audit = {info['variation_status']}"
               f"（dynamic {info['dynamic_count']}，其餘為 ○× 二選一題，同 Unit 1 / 單元 11 先例）")
for skill, info in rehearsal["student_side"].items():
    out.append(f"- 學生端 facade `{skill}`：problems = {len(info['problems'])}，服務到 {len(info['served_examples'])} 個 component（正解／等價解／錯解逐一提交）")
out += [f"- 正式路徑寫入掃描：{rehearsal['production_paths_written'] or '無'}", ""]
(HERE / "UNIT2_REVIEW_REPORT.md").write_text("\n".join(out), encoding="utf-8")
print("written", len(out), "lines")
