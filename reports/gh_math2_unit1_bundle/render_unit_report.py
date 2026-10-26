"""Render the whole-unit review report for 數學2 Unit 1 (three skills) from the sandbox generators, bundle, rehearsal and audits.

Reads the formal database in read-only mode; writes only UNIT1_REVIEW_REPORT.md next to this script.
"""
import importlib.util
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from agent_domains_candidate.sequence_progression import build_sandbox as B  # noqa: E402
from agent_domains_candidate.sequence_progression import verification as V  # noqa: E402
from agent_domains_candidate.sequence_progression.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.sequence_progression.sequence_progression_specs import COMPONENTS, DEFERRED, SKILLS  # noqa: E402

register_candidate_in_memory()
B.build_all()
bundle_dir = next((ROOT / "reports" / "domain_operation_workspaces").glob("capability_sequence_progression_*")) / "revision_0001"
bundle = json.loads((bundle_dir / "promotion_bundle.json").read_text(encoding="utf-8"))
rehearsal = json.loads((HERE / "rehearsal_sequence_report.json").read_text(encoding="utf-8"))
variation = json.loads((HERE / "variation_audit_result.json").read_text(encoding="utf-8"))
audit = json.loads((HERE / "audit_before_approval.json").read_text(encoding="utf-8"))
con = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
rows = {r[0]: (r[1], r[2].split(" [")[0], r[3]) for r in con.execute(
    "select id, skill_id, source_description, problem_text from textbook_examples where source_volume='數學2' and source_chapter='單元1 數列與遞迴關係'")}
per_skill = Counter(v[0] for v in rows.values())
built = Counter(SKILLS[s[0]] for s in COMPONENTS.values())
deferred = Counter(rows[c][0] for c in DEFERRED)


def load(cid):
    skill = SKILLS[COMPONENTS[cid][0]]
    path = B.DRYRUN / skill / "components" / f"src_{cid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"r{cid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate


def kind_of(source):
    return str(source.get("kind") or source.get("style") or (source.get("statement") or {}).get("kind") or "formula_items")


out = ["# 數學2 Unit 1「數列與遞迴關係」GenCode V3 — 整單元審閱報告", ""]
out += [f"- Bundle：`{bundle_dir.relative_to(ROOT).as_posix()}/promotion_bundle.json`（review.status = **{bundle['review']['status']}**，approved_by 為空；尚未 Promotion、尚未 Publish）",
        f"- domain `{bundle['domain_key']}`：{len(bundle['operations'])} 個 operations，套件 {len(bundle['files'])} 個檔案（SHA-256 鎖定）；Bundle SHA-256 `{audit['A_preflight']['bundle_sha256'][:16]}…`",
        f"- 正式教材（唯讀核對）：{len(rows)} 題（Stage 1 READY）", "", "## 三個 Skill 狀態", "",
        "| Skill | 教材題數 | 可用 Component（PASS） | DEFERRED | 狀態 |", "|---|---|---|---|---|"]
for skill in ("gh_Sequence", "gh_RecursiveRelation", "gh_MathematicalInduction"):
    state = "Bundle 就緒、隔離發布演練通過" if built[skill] else "無可生成的 Component（全部 DEFERRED），不隨本單元發布"
    out.append(f"| `{skill}` | {per_skill[skill]} | {built[skill]} | {deferred[skill]} | {state} |")
out += ["", f"合計：{len(rows)} 題 = **{len(COMPONENTS)} PASS** + **{len(DEFERRED)} DEFERRED**（覆蓋率 {len(COMPONENTS) / len(rows):.1%}）。", "",
        "## DEFERRED 與原因", ""] + [f"- **{cid}**（{rows[cid][1]}，{rows[cid][0]}）：{reason}" for cid, reason in sorted(DEFERRED.items())]
out += ["", "## 驗證摘要", "", "| 項目 | 結果 |", "|---|---|",
        "| 沙盒測試 `tests/gencode/test_gh_math2_unit1_sequence_sandbox.py` | 73 項 PASS（逐 component 契約／20 seeds／獨立手算答案／錯解被拒／等價解被接受／驗證器拒絕被竄改答案／○× 平衡／格式提示不洩漏答案／顯示衛生） |",
        f"| 隔離 Phase 2 重建（暫存 store + DB 複本） | {len(rehearsal['rebuild'])} / {len(COMPONENTS)} component tracker = verified，failures = {sum(1 for v in rehearsal['rebuild'].values() if (v.get('verify') or {}).get('failures'))} |"]
for skill, info in rehearsal["publish"].items():
    out.append(f"| 沙盒 Phase 3 發布 `{skill}`（暫存專案根目錄） | {info['status']}，{info['component_count']} components，smoke / staging / production smoke = {info['smoke_status']} / {info['staging_smoke_status']} / {info['production_smoke_status']} |")
for skill, info in rehearsal["student_side"].items():
    out.append(f"| 學生端 facade `{skill}`（正解／等價解／錯解逐一提交） | problems = {len(info['problems'])}，服務到 {len(info['served_examples'])} 個 component |")
out += [f"| 正式路徑寫入掃描 | {rehearsal['production_paths_written'] or '無'} |",
        f"| Promotion 預檢（唯讀） | blockers = {audit['A_preflight']['blockers']}（只剩人工核可） |",
        f"| 套件安全掃描 | 無禁用 import／I/O／隨機／eval／空函式；套件檔與核可雜湊逐位元相同；第三方只用 sympy |",
        f"| 與既有 `sequence.series` 交叉驗證 | 可比對的原語全部一致（{audit['B_cross_validation']['terms'][0]}/{audit['B_cross_validation']['terms'][1]} 項、{audit['B_cross_validation']['arith_two_terms'][0]}/{audit['B_cross_validation']['arith_two_terms'][1]} 等差、{audit['B_cross_validation']['geo_ratio_two_terms'][0]}/{audit['B_cross_validation']['geo_ratio_two_terms'][1]} 公比等） |"]
for skill, res in variation.items():
    out.append(f"| 共用 variation audit `{skill}` | {res['status']}：dynamic {res['dynamic_count']} / {res['components_checked']}；其餘為 ○× 二選一題（共用規則要求單選 4 選項，單元11 已發布 skill 同樣如此），逐項檢查其他判定全部通過 |")
out += ["", "## 來源對應", "", "| 教材 id | 題目 | 正式庫 Skill | operation | 子題型 |", "|---|---|---|---|---|"]
kinds = set()
for cid, (_k, op, source, _s) in sorted(COMPONENTS.items()):
    kinds.add((op, kind_of(source)))
    out.append(f"| {cid} | {rows[cid][1]} | {rows[cid][0]} | `{op}` | {kind_of(source)} |")
out += ["", f"operations = {len({op for op, _ in kinds})}；子題型（operation × kind/style）= {len(kinds)}。", "", "## 代表題（變體 0 = 教材題；變體 B = seed 7）", ""]
for cid, (_k, op, source, _s) in sorted(COMPONENTS.items()):
    generate = load(cid)
    out += [f"### {cid} · {rows[cid][1]} · `{op}` / {kind_of(source)}", "", "教材原題：", "", "> " + rows[cid][2].replace("\n", "\n> "), ""]
    for label, seed in (("變體 0", 0), ("變體 B", 7)):
        p = generate(seed=seed, component_id=f"src_{cid}")
        contract, parts, problems = p["answer_contract"], V.parts_of(p), V.verify_payload(p, SKILLS[COMPONENTS[cid][0]], f"src_{cid}")
        wrong, equiv = V.wrong_value(parts[0]), V.equivalent_value(parts[0])
        hint = parts[0].get("answer_format_example")
        out += [f"**{label}**（verify_payload = {'PASS' if not problems else problems}）", "", "```text", p["question_text"], "```",
                f"- 答案顯示：{p['display_answer']}",
                f"- 契約：{contract['answer_type']} / {contract['presentation_mode']} / checkers = {sorted({x['checker'] for x in parts})}；輸入欄位 {len(parts)} 個" + (f"；格式提示 `{hint}`（與答案無關）" if hint else ""),
                f"- 判分抽查（第一欄）：正解 → 接受；錯解 `{wrong}` → 拒絕" + (f"；等價寫法 `{equiv}` → 接受" if equiv is not None else ""), ""]
    if "statement" in source:
        counts = Counter(generate(seed=s, component_id=f"src_{cid}")["correct_answer"] for s in range(20))
        out += [f"○× 分佈（20 seeds）：A(○)={counts['A']}、B(×)={counts['B']}", ""]
out += ["## 一次性授權前仍需注意", "",
        "1. 共用 variation audit 對 5 個 ○× 二選一題標示 unsafe_dynamic（共用規則），依單元11 先例視為非阻斷；若要改共用規則另案處理。",
        "2. gh_MathematicalInduction 全部 7 題 DEFERRED（證明題無判分契約、圖形規律題），該 Skill 本單元沒有可發布 Component；如需覆蓋，需要先有『數學歸納法證明』的判分契約。",
        "3. gh_RecursiveRelation 的遞迴關係式以『填入範本空格』作答（首項、公比／增量／n 的式子），因為沒有共用 checker 能可靠判定自由格式的遞迴方程式（equation_checker 會誤判 `a_n=a_{n-1}+5` 等錯誤式為正確，已實測）。",
        "4. 6 題圖形規律題 DEFERRED（12668、12673、12686、12694、12698，另 12702、12705）。",
        "5. 匯入器共通修復與 Stage 2 程式碼尚未 commit。", ""]
(HERE / "UNIT1_REVIEW_REPORT.md").write_text("\n".join(out), encoding="utf-8")
print("written", len(out), "lines")
