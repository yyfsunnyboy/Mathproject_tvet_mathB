"""Smoke test for B4 Ch3 statistics runtime quality."""
import os
import sys

# Skills map: (display_key, router_fn_name, canonical_skill_id_suffix)
SKILLS = [
    ("Statisticalchartreading",          "chap3", "StatisticalChartReading"),
    ("Frequencydistributiontableconstruction", "chap3", "FrequencyDistributionTableConstruction"),
    ("Opinionpollinterpretation",         "chap3", "OpinionPollInterpretation"),
    ("Normaldistributionandempiricalrule","chap3", "NormalDistributionAndEmpiricalRule"),
]

N_SAMPLES = 5

def _generate(router_fn, skill_id_suffix, seed):
    from core.vocational_math_b4.services.question_router import (
        generate_for_chap3_skill,
    )
    # Try canonical CamelCase first, then lowercase fallback
    prefixes = ["vh_數學B4_", "vh_??B4_"]
    for prefix in prefixes:
        try:
            return generate_for_chap3_skill(
                skill_id=prefix + skill_id_suffix,
                level=1,
                seed=seed,
            )
        except ValueError:
            continue
    raise ValueError(f"Cannot find skill_id for suffix {skill_id_suffix}")


def _has_placeholder(text: str) -> bool:
    indicators = ["?????", "[FORMULA_MISSING]", "[IMAGE_MISSING]", "????", "???"]
    t = str(text)
    return any(ind in t for ind in indicators)


def main():
    rows = []
    skill_results = {}  # display_key -> list of (status, problem_type_id)

    for display_key, router_fn, suffix in SKILLS:
        payloads = []
        skill_results[display_key] = []
        for i in range(N_SAMPLES):
            seed = 100 + i * 17
            try:
                p = _generate(router_fn, suffix, seed)
                payloads.append(p)
            except Exception as e:
                rows.append({
                    "skill": display_key,
                    "seed": seed,
                    "problem_type_id": "N/A",
                    "answer": "N/A",
                    "answer_type": "N/A",
                    "choices_count": "N/A",
                    "q_preview": f"ERROR: {str(e)[:80]}",
                    "status": "ERROR",
                })
                skill_results[display_key].append(("ERROR", "N/A"))
                continue

            p_id = str(p.get("problem_type_id") or p.get("problem_type") or "unknown")
            answer = str(p.get("answer", ""))
            answer_type = str(p.get("answer_type", ""))
            choices = p.get("choices") or []
            choices_count = len(choices)
            qt = str(p.get("question_text", ""))
            q_preview = qt[:80].replace("\n", " ").replace("|", "｜")

            fail_reasons = []

            # Check placeholder
            if _has_placeholder(qt):
                fail_reasons.append("question_text contains ?????")
            for ch in choices:
                if _has_placeholder(str(ch)):
                    fail_reasons.append("choices contain ?????")
                    break

            # FrequencyDistribution must have table_data or be single-bin count
            if "FrequencyDistribution" in display_key:
                if not p.get("table_data") and p_id not in ("frequency_table_single_bin_count",):
                    fail_reasons.append("FrequencyDistribution: missing table_data and not single-bin")

            # deterministic types must have answer and answer_type
            if not answer and p.get("runtime_mode", "") not in ("teacher_review", "review_mode"):
                fail_reasons.append("no answer")
            if not answer_type:
                fail_reasons.append("no answer_type")

            status = "PASS" if not fail_reasons else "FAIL: " + "; ".join(fail_reasons)
            rows.append({
                "skill": display_key,
                "seed": seed,
                "problem_type_id": p_id,
                "answer": answer[:30],
                "answer_type": answer_type,
                "choices_count": choices_count,
                "q_preview": q_preview,
                "status": status,
            })
            skill_results[display_key].append((status, p_id))

    # Extra checks
    extra_notes = []

    # Opinionpoll: 5 questions must not all be identical
    op_q_texts = [
        r["q_preview"]
        for r in rows
        if r["skill"] == "Opinionpollinterpretation"
    ]
    if len(set(op_q_texts)) < 2:
        extra_notes.append("FAIL: OpinionPollInterpretation 5 題全部相同")
    else:
        extra_notes.append(f"PASS: OpinionPollInterpretation 5 題中有 {len(set(op_q_texts))} 種不同題目")

    # NormalDistribution: at least 2 distinct problem_type_ids
    nd_pt_ids = set(
        pt for (st, pt) in skill_results.get("Normaldistributionandempiricalrule", [])
        if st != "ERROR"
    )
    if len(nd_pt_ids) >= 2:
        extra_notes.append(f"PASS: NormalDistribution 5 題出現 {len(nd_pt_ids)} 種 problem_type: {', '.join(sorted(nd_pt_ids))}")
    else:
        extra_notes.append(f"FAIL: NormalDistribution 5 題只出現 {len(nd_pt_ids)} 種 problem_type: {', '.join(sorted(nd_pt_ids))}")

    # Build report
    pass_count = sum(1 for r in rows if r["status"] == "PASS")
    fail_count = sum(1 for r in rows if r["status"] != "PASS")

    lines = [
        "# B4 Ch3 Statistics Runtime Quality Smoke Report",
        "",
        f"總計：{len(rows)} 題，PASS：{pass_count}，FAIL/ERROR：{fail_count}",
        "",
    ]
    for note in extra_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("| skill | seed | problem_type_id | answer | answer_type | choices_count | question_text 前80字 | status |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['skill']} | {r['seed']} | {r['problem_type_id']} | {r['answer']} | "
            f"{r['answer_type']} | {r['choices_count']} | {r['q_preview']} | {r['status']} |"
        )

    os.makedirs("reports/b4_generator_planning", exist_ok=True)
    out_path = "reports/b4_generator_planning/b4_ch3_statistics_runtime_quality_smoke.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Smoke done. PASS={pass_count} FAIL/ERROR={fail_count}")
    for note in extra_notes:
        print(" ", note)


if __name__ == "__main__":
    main()
