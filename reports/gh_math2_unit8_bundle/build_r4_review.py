"""Static teacher-review checklist for revision_0004 built from the existing r4 dry-run components (nothing is built or published).

Reads the formal DB read-only for the textbook stems; writes only
``reports/gh_math2_unit8_bundle/revision_0004_teacher_review.html`` and ``revision_0004_teacher_review.json``.
Checker columns reuse the sandbox gate helpers (``verify_payload`` / ``grade`` / ``wrong_value``); they are technical evidence,
not a teacher sign-off.
"""

from __future__ import annotations

import html
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.univariate_statistics.univariate_statistics_specs import COMPONENTS, SKILLS  # noqa: E402
from agent_domains_candidate.univariate_statistics.verification import grade, parts_of, verify_payload, wrong_value  # noqa: E402

DRYRUN = ROOT / "tmp" / "gh_math2_unit8_sandbox_dryrun_r4"
OUT = ROOT / "reports" / "gh_math2_unit8_bundle" / "revision_0004_teacher_review.html"
OUT_JSON = OUT.with_suffix(".json")
DB = ROOT / "instance" / "kumon_math.db"
BUNDLE_SHA256 = "d6b6310c279d5b7dfcf131d3695948db0647b50b186e86c766a656cef274ee3a"
SEEDS = (0, 3, 7)
CHECK_SEEDS = tuple(range(20))
PENDING = "待教師確認"
TEACHER_ITEMS = {
    12934: ("語意改寫，" + PENDING + "（不得視為通過）",
            "原題考「中位數一定 ≥ 平均數」的全稱敘述（答 ×，兩者無固定大小關係，舉一反例即可否定）。只有 seed 0（20 個變體中的 1 個）"
            "保留原題；其餘 19 個拿掉「一定」，改成「數據 … 的中位數大於或等於它的平均數」的具體計算判斷，○／× 約各半。答案經獨立計算 19/19 "
            "正確，但考點由全稱敘述的反例判斷變成計算比較，與 12935 計算題重疊，且常答 ○ 可能讓學生誤以為「中位數 ≥ 平均數」通常成立。"
            "可選：接受現況／改為只出原題的固定概念題／改寫為保留「一定」的變體（後兩者需新 revision）。"),
    12932: (PENDING,
            "原題「數據全部相等時標準差為 0」（○）。只有 seed 0 保留原題，其餘為「數據 c, c, …, c 的標準差為 s」的具體判斷，○／× 各半。"
            "考點仍是常數資料標準差為 0，偏離較 12934 小。"),
    12923: (PENDING,
            "多選題，教材答案 (1)(3)：40 人時 Q1 為第 10、11 筆平均，第 11 筆以上 30 人皆 ≥ Q1；中位數介於 Q1、Q3 之間；"
            "總時數 40×8.5=340 未超過 350。請確認「約有 10 名超過 Q3」判為無法推論，以及變體的敘述與數值。"),
    12941: (PENDING,
            "多選題，教材答案 (1)(2)(4)：原平均 2×(66−40)=52、原標準差 2×5=10；調整後低於 60 對應原分數低於 40（非 20）；"
            "調整後不低於原分數等價於原分數 ≤ 80。請確認變體的敘述數值設計。"),
    12946: (PENDING,
            "多選題，教材答案 (1)(2)：乘正數或平移時百分位數隨之變換；合併兩組不是相加；「必小於平均數」不成立。"
            "變體會出現乘以負數、平方、「介於最小與最大值之間」等敘述，請確認是否超出教材範圍。"),
    12926: (PENDING,
            "例題9：教材為 109 學測國文／數學級分百分比長條圖。V3 以兩張動態長條圖呈現（seed 0 用教材百分比資料，其他 seed 為模擬資料並標示），"
            "請確認圖形可讀、模擬資料標示清楚、敘述判斷與圖一致。"),
    12930: (PENDING,
            "隨堂練習10（承例題9）：前標（第 75 百分位數）比較，同樣使用動態長條圖。請確認同上。"),
}
ALL_VARIANT_SEEDS = tuple(range(20))
DEFAULT_SEMANTICS = "保留（Agent 初判：同題型、同數學結構，只換參數；" + PENDING + "）"


def _load(cid: int):
    path = DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"r4_{cid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _image_src(item) -> str:
    if isinstance(item, dict):
        item = item.get("value") or item.get("src") or item.get("url") or ""
    item = str(item or "")
    if item.startswith(("data:", "/", "http")):
        return item
    return "data:image/png;base64," + item if item else ""


def _images(payload: dict) -> str:
    return "".join(f'<img src="{html.escape(s)}" alt="chart">'
                   for s in (_image_src(v) for v in payload.get("visual_aids") or []) if s)


def _checker(payload: dict, skill_id: str, cid: int) -> dict:
    issues = verify_payload(payload, skill_id, f"src_{cid}")
    accepted = grade(payload, payload["correct_answer"], skill_id) is True
    rejected = total = 0
    for part in parts_of(payload):
        bad = wrong_value(part)
        if isinstance(payload["correct_answer"], dict):
            bad = {**payload["correct_answer"], part["key"]: bad}
        total += 1
        rejected += grade(payload, bad, skill_id) is False
    return {"payload_issues": len(issues), "correct_accepted": accepted, "wrong_rejected": rejected, "wrong_total": total,
            "pass": not issues and accepted and rejected == total}


def _checker_text(c: dict) -> str:
    return (f'Checker：{"PASS" if c["pass"] else "FAIL"}（payload 檢查 {c["payload_issues"]} 項問題；正解{"接受" if c["correct_accepted"] else "未接受"}；'
            f'錯解拒絕 {c["wrong_rejected"]}/{c["wrong_total"]}）')


def _variant(seed: int, payload: dict, check: dict) -> str:
    stem = html.escape(payload["question_text"]).replace("\n", "<br>")
    steps = "；".join(payload.get("explanation_steps") or [])
    dataset = ((payload.get("math_core") or {}).get("givens") or {}).get("dataset")
    return (f'<div class="variant"><h4>seed {seed}{"（教材錨點）" if seed == 0 else ""}'
            f'{f"｜圖表資料：{html.escape(str(dataset))}" if dataset else ""}</h4><div class="stem">{stem}</div>{_images(payload)}'
            f'<p class="ans">答案：{html.escape(str(payload.get("display_answer")))}</p>'
            + (f'<p class="steps">詳解：{html.escape(steps)}</p>' if steps else "")
            + f'<p class="chk {"ok" if check["pass"] else "bad"}">{_checker_text(check)}</p></div>')


def main() -> Path:
    register_candidate_in_memory()
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    src = {r[0]: (r[1], r[2]) for r in con.execute(
        "select id, source_description, problem_text from textbook_examples where id between 12912 and 12946")}
    con.close()
    order = sorted(COMPONENTS, key=lambda c: (list(SKILLS).index(COMPONENTS[c][0]), c))
    rows, summary, sections = [], [], []
    for cid in order:
        skill = SKILLS[COMPONENTS[cid][0]]
        module = _load(cid)
        payloads = {s: module.generate(seed=s) for s in sorted(set(CHECK_SEEDS) | set(SEEDS))}
        checks = {s: _checker(p, skill, cid) for s, p in payloads.items()}
        n_pass = sum(c["pass"] for s, c in checks.items() if s in CHECK_SEEDS)
        stems = len({payloads[s]["question_text"] for s in CHECK_SEEDS})
        answers = len({json.dumps(payloads[s]["correct_answer"], sort_keys=True, ensure_ascii=False) for s in CHECK_SEEDS})
        semantics, note = TEACHER_ITEMS.get(cid, (DEFAULT_SEMANTICS, ""))
        desc, stem = src.get(cid, ("", ""))
        label = desc.split(" [")[0]
        has_table = "begin{array}" in payloads[0]["question_text"]
        n_img = len(payloads[0].get("visual_aids") or [])
        rows.append({"id": cid, "skill": skill, "source": label, "operation": COMPONENTS[cid][1], "table": has_table, "charts": n_img,
                     "checker_pass_seeds_0_19": f"{n_pass}/{len(CHECK_SEEDS)}", "distinct_stems": stems, "distinct_answers": answers,
                     "seed0_answer": payloads[0].get("display_answer"), "semantics": semantics, "teacher_note": note,
                     "teacher_review": "pending"})
        star = cid in TEACHER_ITEMS
        summary.append(
            f'<tr class="{"star" if star else ""}"><td><a href="#c{cid}">{cid}</a></td><td>{html.escape(skill)}</td><td>{html.escape(label)}</td>'
            f'<td>{"表格" if has_table else ""}{" 長條圖×" + str(n_img) if n_img else ""}</td><td>{n_pass}/{len(CHECK_SEEDS)}</td>'
            f'<td>{stems}／{answers}</td><td>{html.escape(semantics)}</td><td>☐ 核可 ☐ 退回</td></tr>')
        seeds = ALL_VARIANT_SEEDS if star else SEEDS
        variants = "".join(_variant(s, payloads[s], checks[s]) for s in seeds)
        flag = f'<p class="flag"><b>{html.escape(semantics)}</b>：{html.escape(note)}</p>' if note else f'<p class="sem">原題語意：{html.escape(semantics)}</p>'
        sections.append(
            f'<section id="c{cid}"><h3>src_{cid}｜{html.escape(skill)}｜{html.escape(label)}｜operation {COMPONENTS[cid][1]}</h3>{flag}'
            f'<p>seeds 0–19：Checker PASS {n_pass}/{len(CHECK_SEEDS)}；不同題幹 {stems}、不同答案 {answers}</p>'
            f'<details open><summary>教材原題（正式 DB）</summary><div class="stem orig">{html.escape(stem).replace(chr(10), "<br>")}</div></details>'
            f'{variants}<p class="review">教師審核：☐ 核可　☐ 退回　意見：＿＿＿＿＿＿＿＿</p></section>')
    head = (f"<p>Bundle <code>revision_0004</code>（bundle_sha256 <code>{BUNDLE_SHA256}</code>），狀態 ready_for_human_review，"
            "尚未 Promotion／Publish。Checker 欄為技術驗證（sandbox gate 的 verify_payload／grade／wrong_value），"
            "<b>不等於教師人工審核通過</b>。「語意」欄除 ★ 題外為 Agent 初判，仍需教師確認。★ 題列 seed 0–19，其餘列 seed 0／3／7。"
            "答案與詳解僅供審核，學生端提交前不顯示。公式以 MathJax CDN 排版（需網路）。</p>")
    table = ("<table><tr><th>id</th><th>Skill</th><th>教材來源</th><th>表格／圖</th><th>Checker（seed 0–19）</th><th>題幹／答案變化數</th>"
             "<th>原題數學語意</th><th>教師審核</th></tr>" + "".join(summary) + "</table>")
    OUT.write_text(
        "<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'><title>Unit 8 revision_0004 教師審核清單</title>"
        "<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']]}};</script>"
        "<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script>"
        "<style>body{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;max-width:1150px;margin:auto;color:#1f2937}"
        "table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #d1d5db;padding:3px 5px}tr.star{background:#fef3c7}"
        "section{border-top:2px solid #9ca3af;padding:8px 0}.variant{border-left:3px solid #d1d5db;margin:8px 0;padding:4px 10px}"
        ".orig{background:#f3f4f6;padding:6px}.ans{color:#065f46}.steps{color:#4b5563;font-size:14px}.chk{font-size:13px}"
        ".ok{color:#047857}.bad{color:#b91c1c;font-weight:bold}.flag{background:#fef3c7;padding:6px;border-radius:4px}.sem{color:#4b5563}"
        "img{max-width:100%;border:1px solid #d1d5db;margin:4px 0}.review{color:#6b7280}</style></head><body>"
        "<h1>普高數學2 Unit 8 一維數據分析 — revision_0004 教師審核清單</h1>" + head + table + "".join(sections) + "</body></html>",
        encoding="utf-8",
    )
    OUT_JSON.write_text(json.dumps({"bundle_sha256": BUNDLE_SHA256, "revision": 4, "review_status": "pending_teacher_review",
                                    "checker_is_not_teacher_approval": True, "reviewer": "", "reviewed_at": "",
                                    "instructions": "teacher sets every components[].teacher_review to approved or rejected, "
                                                    "fills reviewer / reviewed_at; rejected components are not published",
                                    "components": rows}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(main())
