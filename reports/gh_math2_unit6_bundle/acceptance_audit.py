"""Read-only acceptance audit for 普高數學2 Unit 6.

Does not rebuild generators, does not write the formal database, and does not approve or publish.
Writes acceptance_audit.json and acceptance_review.md in this folder.
"""

from __future__ import annotations

import json
import random
import sqlite3
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.classical_probability.classical_probability_specs import COMPONENTS, FAMILY, SKILLS  # noqa: E402
from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.classical_probability.verification import (  # noqa: E402
    equivalent_value,
    grade,
    parts_of,
    verify_payload,
    wrong_value,
)

HERE = Path(__file__).resolve().parent
MATRIX = ROOT / "reports/domain_operation_workspaces/capability_discrete_classical_probability_f8c6199f/revision_0001/coverage_matrix.json"
BUNDLE = MATRIX.parent / "promotion_bundle.json"
FORMAL = ROOT / "instance/kumon_math.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/07199f701f24_單元06-古典機率.pdf"
DOCX = ROOT / "textbook_import/uploaded_sources/general/數學2/08141f321b73_單元06-古典機率.docx"
CUES = ("如圖", "右圖", "下圖", "左圖", "上圖", "見圖", "圖（", "圖(", "下表", "如表", "附表")
SPOTLIGHT = (12849, 12852, 12859, 12864, 12871, 12872, 12883, 12884, 12885, 12887, 12890)
HUMAN = {
    12849: "樣本點編成整數：正面為 1、反面為 0，最先擲出的是最高位。學生寫的是編碼後的集合，不是「正正、正反」四個詞。",
    12852: "三種抽法都編成十進位碼。要確認題幹把不放回、放回、不計順序分開，學生不會把三種樣本空間混成一種。",
    12859: "互斥以 A＝是、B＝否作答。第一粒是偶數且點數和是奇數可以同時發生，所以答案是 B。",
    12864: "依序不放回是 6/20＝3/10，同時取出是 3/10。兩種數法的分母不同，約分後機率相同。",
    12871: "教材寫「三粒相同的公正骰子」。元件把骰子編號，樣本空間是 216。恰有一粒 6 點的有利結果是 75，機率 75/216＝25/72。若改成不區分骰子，各結果就不再等可能。",
    12872: "「各若干顆」沒有給出紅白球的顆數，不能推出機率是 1/2。答案是 ×，選項 B。",
    12883: "一次猜中：24 個排列中有利 1 個，機率 1/24。連續三次互不相同的錯誤密碼就鎖定：有利 21 個，機率 21/24＝7/8。",
    12884: "所求是黑球顆數 n＝10，不是機率。白球 5 顆、兩白球機率 2/21 時，正整數解只有 10。",
    12885: "第三小題的交集機率是 0。判分接受 0，也接受等價的 0.0。",
    12887: "至少兩粒點數相同：已編號的 216 個樣本點中有 96 個，96/216＝4/9。這與教材補事件 1−5/9 相同。",
    12890: "四人各自從 6 個社團選一個，樣本點 6^4＝1296。至少兩人相同的有利結果是 936，936/1296＝13/18。",
}


def _show(value) -> str:
    if isinstance(value, dict):
        return "；".join(f"{key}={_show(value[key])}" for key in sorted(value, key=lambda item: int(item.split('_')[1])))
    if isinstance(value, list):
        return "{" + ", ".join(str(item) for item in value) + "}"
    return str(value)


def _card(cid: int, payload: dict, skill: str, family: str, operation: str, *, seed_label: str) -> dict:
    contract = payload["answer_contract"]
    problems = verify_payload(payload, skill, f"src_{cid}")
    parts = parts_of(payload)
    wrong_ok = True
    equivalent_note = "此答案型別沒有另一種自動等價寫法"
    if contract["answer_type"] in {"multi_part", "table_fill"}:
        for part in parts:
            bad = dict(payload["correct_answer"])
            bad[part["key"]] = wrong_value(part)
            if grade(payload, bad, skill):
                wrong_ok = False
            equivalent = equivalent_value(part)
            if equivalent is not None:
                good = dict(payload["correct_answer"])
                good[part["key"]] = equivalent
                equivalent_note = f"{part['key']} 等價寫法 {_show(equivalent)}：{'接受' if grade(payload, good, skill) else '拒絕'}"
    else:
        if grade(payload, wrong_value(parts[0]), skill):
            wrong_ok = False
        equivalent = equivalent_value(parts[0])
        if equivalent is not None:
            equivalent_note = f"等價寫法 {_show(equivalent)}：{'接受' if grade(payload, equivalent, skill) else '拒絕'}"
    text = payload["question_text"]
    mathjax = text.count("$") % 2 == 0 and "$$" not in text and all(
        segment.count("{") == segment.count("}") for index, segment in enumerate(text.split("$")) if index % 2 == 1
    )
    return {
        "skill_id": skill,
        "textbook_example_id": cid,
        "seed": seed_label,
        "family": family,
        "problem_type": operation,
        "question_text": text,
        "correct_answer": _show(payload["correct_answer"]),
        "explanation_steps": payload.get("explanation_steps") or [],
        "checker": {
            "key": contract["checker_key"],
            "verify_payload": problems,
            "canonical_accepted": grade(payload, payload["correct_answer"], skill),
            "wrong_rejected": wrong_ok,
            "equivalent": equivalent_note,
        },
        "answer_format": {
            "answer_type": contract["answer_type"],
            "presentation_mode": payload["presentation_mode"],
            "equivalence_type": contract["equivalence_type"],
        },
        "mathjax_inline_balanced": mathjax,
        "figure_cue_in_stem": any(cue in text for cue in CUES),
        "human_check": HUMAN.get(cid, "確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。"),
    }


def _figures(rows: list[sqlite3.Row]) -> dict:
    cue_rows = []
    asset_rows = []
    statuses = defaultdict(int)
    for row in rows:
        text = row["problem_text"] or ""
        hits = [cue for cue in CUES if cue in text]
        if hits:
            cue_rows.append({"id": row["id"], "cues": hits})
        notes = json.loads(row["notes"] or "{}")
        assets = notes.get("image_assets") or []
        status = str(notes.get("pdf_visual_status") or "")
        statuses[status or "(none)"] += 1
        if assets:
            asset_rows.append({"id": row["id"], "count": len(assets), "status": status})
    docx_media: dict[str, int] = {}
    docx_blips = 0
    if DOCX.is_file():
        with zipfile.ZipFile(DOCX) as package:
            suffixes = [Path(name).suffix.lower() for name in package.namelist() if name.startswith("word/media/")]
            docx_media = dict(__import__("collections").Counter(suffixes))
            xml = package.read("word/document.xml")
            docx_blips = xml.count(b"<a:blip ") + xml.count(b"<w:drawing") + xml.count(b"<w:pict")
    pdf_pages = []
    if PDF.is_file():
        import fitz

        with fitz.open(PDF) as doc:
            for index, page in enumerate(doc, 1):
                images = page.get_images()
                drawings = page.get_drawings()
                text = page.get_text("text")
                if images or drawings or any(cue in text for cue in CUES):
                    pdf_pages.append({
                        "page": index,
                        "embedded_images": len(images),
                        "vector_drawings": len(drawings),
                        "stem_cues_on_page": [cue for cue in CUES if cue in text],
                    })
    return {
        "formal_rows": len(rows),
        "stem_cue_rows": cue_rows,
        "rows_with_image_assets": asset_rows,
        "pdf_visual_status_counts": dict(statuses),
        "docx_media_by_suffix": docx_media,
        "docx_drawing_markers": docx_blips,
        "pdf_embedded_image_pages": [
            {"page": item["page"], "embedded_images": item["embedded_images"]}
            for item in pdf_pages if item["embedded_images"]
        ],
        "pdf_phrase_hits": [
            {"page": item["page"], "cues": item["stem_cues_on_page"]}
            for item in pdf_pages if item["stem_cues_on_page"]
        ],
        "conclusion": (
            "42 題入庫題幹都沒有「如圖／下表」，正式列的 image_assets 為 0。"
            "DOCX 的 170 個 wmf 與 2 個 emf 是 MathType 方程式，不是題圖。"
            "另外 6 張 jpeg（郵票人像、撲克牌、球袋、水餃、慶生）是課文插圖，題幹已經寫出計算所需的數字，解題不必讀圖。"
            "PDF 只有第 1、9、12 頁出現「如圖／右圖」，分別在章首灑藍釉缽、課文把白球編號的說明，以及例題9詳解的編號示意，不在 42 題題幹裡。"
            "PDF 上大量向量是方程式字形，不是缺漏的數據圖或表格。"
        ),
    }


def main() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    by_skill_family = defaultdict(set)
    by_skill_type = defaultdict(set)
    families = set()
    types = set()
    operations = set()
    generators = []
    for row in matrix:
        families.add(row["family"])
        types.add(row["problem_type"])
        operations.add(row["domain_function"])
        generators.append(row["generator"])
        by_skill_family[row["skill_id"]].add(row["family"])
        by_skill_type[row["skill_id"]].add(row["problem_type"])
    per_skill = []
    for skill in (
        "gh_SampleSpace",
        "gh_Event",
        "gh_DefinitionOfClassicalProbability",
        "gh_PropertiesOfProbability",
    ):
        rows = [row for row in matrix if row["skill_id"] == skill]
        per_skill.append({
            "skill_id": skill,
            "questions": len(rows),
            "families_within_skill": sorted(by_skill_family[skill]),
            "problem_types_within_skill": sorted(by_skill_type[skill]),
            "generators": len(rows),
        })
    shared = sorted(family for family in families if sum(family in item["families_within_skill"] for item in per_skill) > 1)
    stats = {
        "questions": len(matrix),
        "generators": len(generators),
        "unique_generators": len(set(generators)),
        "problem_types": len(types),
        "families_deduped": len(families),
        "family_memberships_if_counted_inside_each_skill": sum(len(item["families_within_skill"]) for item in per_skill),
        "domain_operations": len(operations),
        "problem_type_equals_domain_operation": types == operations,
        "families_shared_by_more_than_one_skill": shared,
        "per_skill": per_skill,
        "why_17_and_14": "3+2+8+4 把跨技能共用的 3 個 family 各算了兩次。去重後是 14。Problem Type 與 Domain Operation 在這份矩陣裡是同一個名稱，也是 14。",
    }

    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    con = sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    db_rows = list(con.execute(
        "select id, skill_id, ifnull(correct_answer, '') as correct_answer, problem_text, source_description, notes "
        "from textbook_examples where id between 12849 and 12890 order by id"
    ))
    con.close()
    by_id = {row["id"]: row for row in db_rows}
    formal = {
        "row_count": len(db_rows),
        "empty_correct_answer": sum(1 for row in db_rows if not str(row["correct_answer"]).strip()),
        "skill_counts": dict(__import__("collections").Counter(row["skill_id"] for row in db_rows)),
        "ids": [row["id"] for row in db_rows],
        "runtime": (
            "學生端判分讀的是 Generator payload 的 correct_answer 與 answer_contract，"
            "不是 textbook_examples.correct_answer。正式庫這 42 格維持空白，不會參與這批候選題的出題或判分。"
            "元件尚未發布，所以現在的練習路由還不會載入它們。"
        ),
    }
    figures = _figures(db_rows)

    cards = []
    index = []
    seen_family = set()
    full_ids = set(SPOTLIGHT)
    drift = []
    staged_loaded = 0
    for row in matrix:
        cid = row["textbook_example_id"]
        if row["family"] not in seen_family:
            seen_family.add(row["family"])
            full_ids.add(cid)
    for row in matrix:
        cid = row["textbook_example_id"]
        skill_key, operation, source, sampler = COMPONENTS[cid]
        _matrix, payload = dispatch_registered_operation(
            "discrete.classical_probability", operation, seed=0, constraints=dict(source)
        )
        card = _card(cid, payload, row["skill_id"], row["family"], operation, seed_label="0（教材參數）")
        staged_path = ROOT / "tmp/gh_math2_unit6_sandbox_dryrun" / SKILLS[skill_key] / "components" / f"src_{cid}" / "generate.py"
        if staged_path.is_file():
            import importlib.util

            spec = importlib.util.spec_from_file_location(f"staged_{cid}", staged_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            staged = module.generate(seed=0)
            staged_loaded += 1
            if staged.get("question_text") != payload["question_text"] or staged.get("correct_answer") != payload["correct_answer"]:
                drift.append(cid)
        variant = None
        rng = random.Random(f"math2u6:{cid}")
        for _ in range(40):
            try:
                candidate = sampler(rng)
            except Exception:
                continue
            try:
                _m2, other = dispatch_registered_operation(
                    "discrete.classical_probability", operation, seed=1, constraints=candidate
                )
            except Exception:
                continue
            if other["question_text"] != payload["question_text"]:
                variant = _card(cid, other, row["skill_id"], row["family"], operation, seed_label="另一個抽樣")
                break
        index.append({
            "textbook_example_id": cid,
            "source_description": by_id[cid]["source_description"],
            "skill_id": row["skill_id"],
            "family": row["family"],
            "problem_type": operation,
            "generator": row["generator"],
            "formal_correct_answer_empty": not str(by_id[cid]["correct_answer"]).strip(),
            "answer_type": card["answer_format"]["answer_type"],
            "presentation_mode": card["answer_format"]["presentation_mode"],
            "checker_key": card["checker"]["key"],
            "seed0_answer": card["correct_answer"],
            "verify_payload": card["checker"]["verify_payload"],
            "canonical_accepted": card["checker"]["canonical_accepted"],
            "wrong_rejected": card["checker"]["wrong_rejected"],
            "mathjax_inline_balanced": card["mathjax_inline_balanced"],
            "variant_answer_differs": variant is not None and variant["correct_answer"] != card["correct_answer"],
            "variant_stem_differs": variant is not None,
        })
        if cid in full_ids:
            cards.append({"textbook": card, "variant": variant})

    staging = {
        "component_generate_py_loaded": staged_loaded,
        "component_generate_py_drift": drift,
        "bundle_review_status": json.loads(BUNDLE.read_text(encoding="utf-8"))["review"]["status"],
        "browser_mathjax": "尚未驗證。元件未發布，這輪沒有打開練習頁。",
        "in_memory_dispatch_of_42_sources": all(not item["verify_payload"] and item["canonical_accepted"] and item["wrong_rejected"] for item in index),
        "published_skill_packages_present": any((ROOT / "agent_skills_v3" / skill).exists() for skill in (
            "gh_SampleSpace", "gh_Event", "gh_DefinitionOfClassicalProbability", "gh_PropertiesOfProbability"
        )),
    }
    audit = {
        "statistics": stats,
        "formal_database": formal,
        "figures": figures,
        "staging": staging,
        "checklist": index,
        "family_cards": cards,
    }
    (HERE / "acceptance_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 單元06 古典機率人工驗收",
        "",
        stats["why_17_and_14"],
        "",
        f"題目 {stats['questions']}、Generator 元件 {stats['generators']}、去重 Family {stats['families_deduped']}、"
        f"Domain Operation {stats['domain_operations']}。跨技能各算一次時 family 成員數是 "
        f"{stats['family_memberships_if_counted_inside_each_skill']}。",
        "",
        "共用 family：" + ("、".join(shared) if shared else "無"),
        "",
        "## 教師須確認",
        "",
        "下列項目答案可判，作答形式或模型需要教師點頭。瀏覽器上的 MathJax 尚未驗證，不視為 Runtime PASS。",
        "",
        "- 數字編碼：硬幣與出生順序用 0/1 整數，抽取結果用十進位碼，不是文字列舉。",
        "- 相同骰子：題幹與詳解都把骰子編號。12871 是 216 個樣本點、有利 75 個、機率 75/216＝25/72。",
        "- 放回與不放回：12864 依序不放回是 6/20，同時取出是 3/10，約分後相同。12852 三種抽法分開計數。",
        "- 機率 0：12885 第三小題是 0，Checker 接受 0 與 0.0。",
        "- 整數答案：12884 所求是黑球顆數 10，不是機率。",
        "",
        "## 42 題清單",
        "",
        "| ID | 教材 | Skill | Family | 作答 | 標準答案 | Checker |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in index:
        flag = "PASS" if item["canonical_accepted"] and item["wrong_rejected"] and not item["verify_payload"] else "FAIL"
        lines.append(
            f"| {item['textbook_example_id']} | {item['source_description'].split('[')[0].strip()} | `{item['skill_id']}` | "
            f"`{item['family']}` | {item['answer_type']} / {item['presentation_mode']} | {item['seed0_answer']} | {flag} |"
        )
    lines += ["", "## 代表題（每個 Family 的教材參數，以及另一個抽樣）", ""]
    for pair in cards:
        card = pair["textbook"]
        lines += [
            f"### {card['textbook_example_id']} `{card['family']}`",
            "",
            f"- Skill：`{card['skill_id']}`",
            f"- Problem Type / Domain Operation：`{card['problem_type']}`",
            f"- 作答：{card['answer_format']['answer_type']}，{card['answer_format']['presentation_mode']}，checker `{card['checker']['key']}`",
            f"- Checker：標準答案 {'接受' if card['checker']['canonical_accepted'] else '拒絕'}；錯誤答案 {'拒絕' if card['checker']['wrong_rejected'] else '接受'}；{card['checker']['equivalent']}",
            f"- MathJax 括號：{'成對' if card['mathjax_inline_balanced'] else '不成對'}",
            "",
            card["question_text"],
            "",
            f"標準答案：{card['correct_answer']}",
            "",
            "解題：",
            *[f"- {step}" for step in card["explanation_steps"]],
            "",
            f"請人工確認：{card['human_check']}",
            "",
        ]
        variant = pair["variant"]
        if variant:
            lines += [
                "另一個抽樣：",
                "",
                variant["question_text"],
                "",
                f"標準答案：{variant['correct_answer']}",
                "",
            ]
    lines += [
        "## 圖形",
        "",
        figures["conclusion"],
        "",
        f"DOCX 媒體 {figures['docx_media_by_suffix']}，drawing 標記 {figures['docx_drawing_markers']}。",
        f"PDF 嵌入影像頁：{figures['pdf_embedded_image_pages']}。圖形用語：{figures['pdf_phrase_hits']}。",
        "",
        "## 尚未驗證",
        "",
        "tmp 裡的 42 個 generate.py 有載入 "
        f"{staging['component_generate_py_loaded']} 個，與目前 domain 的教材參數不一致的有 {staging['component_generate_py_drift'] or '無'}。"
        "瀏覽器 MathJax 尚未驗證。",
        "",
    ]
    (HERE / "acceptance_review.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "stats": {k: stats[k] for k in (
            "questions", "generators", "problem_types", "families_deduped",
            "family_memberships_if_counted_inside_each_skill", "domain_operations",
        )},
        "shared_families": shared,
        "empty_answers": formal["empty_correct_answer"],
        "checker_failures": [item["textbook_example_id"] for item in index if item["verify_payload"] or not item["wrong_rejected"]],
        "mathjax_failures": [item["textbook_example_id"] for item in index if not item["mathjax_inline_balanced"]],
        "figures": figures["conclusion"],
        "docx_media": figures["docx_media_by_suffix"],
        "pdf_images": figures["pdf_embedded_image_pages"],
        "pdf_phrases": figures["pdf_phrase_hits"],
        "cards": len(cards),
        "staged_loaded": staging["component_generate_py_loaded"],
        "staged_drift": staging["component_generate_py_drift"],
        "published_packages": staging["published_skill_packages_present"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
