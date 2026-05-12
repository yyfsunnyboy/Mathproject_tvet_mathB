import os
from collections import defaultdict
import traceback

from core.vocational_math_b4.services.question_router import (
    generate_for_skill,
    generate_for_chap2_skill,
)

SKILLS_TO_TEST = [
    ("vh_數學B4_AdditionPrinciple", 1),
    ("vh_數學B4_MultiplicationPrinciple", 1),
    ("vh_數學B4_SampleSpaceAndEvents", 2),
    ("vh_數學B4_FactorialNotation", 1),
    ("vh_數學B4_PermutationOfDistinctObjects", 1),
    ("vh_數學B4_Combination", 1),
    ("vh_數學B4_RepeatedPermutation", 1),
    ("vh_數學B4_PermutationOfNonDistinctObjects", 1),
    ("vh_數學B4_BinomialTheorem", 1),
    ("vh_數學B4_BinomialCoefficientIdentities", 1),
]

def main():
    report_lines = [
        "# B4 Ch1 Choices Policy Smoke Test",
        "",
        "| skill_id | problem_type_id / problem_type | answer_type | choices_count | question_text 前 80 字 | status |",
        "|---|---|---|---|---|---|",
    ]
    
    all_pass = True
    
    for skill_id, chap in SKILLS_TO_TEST:
        for seed in [101, 202]:
            try:
                if chap == 1:
                    payload = generate_for_skill(skill_id=skill_id, level=1, seed=seed)
                else:
                    payload = generate_for_chap2_skill(skill_id=skill_id, level=1, seed=seed)
                
                pt_id = str(
                    payload.get("problem_type_id")
                    or payload.get("problem_type")
                    or payload.get("type")
                    or payload.get("generator_key")
                    or "unknown"
                )
                
                ans_type = str(payload.get("answer_type", "unknown"))
                choices = payload.get("choices", [])
                choices_count = len(choices)
                
                question_text = str(payload.get("question_text", ""))
                q_preview = question_text[:80].replace("\n", " ").replace("|", "｜")
                
                status = "PASS" if choices_count == 0 else "FAIL"
                if status == "FAIL":
                    all_pass = False
                    
                report_lines.append(
                    f"| {skill_id} | {pt_id} | {ans_type} | {choices_count} | {q_preview} | {status} |"
                )
                
            except Exception as e:
                status = "ERROR"
                all_pass = False
                err_msg = str(e)[:80].replace("\n", " ").replace("|", "｜")
                report_lines.append(
                    f"| {skill_id} | N/A | N/A | N/A | Error: {err_msg} | {status} |"
                )

    report_lines.append("")
    if all_pass:
        report_lines.append("## Conclusion: All tested skills PASSED (choices_count = 0).")
    else:
        report_lines.append("## Conclusion: FAIL. Some skills returned choices.")
        
    os.makedirs("reports/b4_generator_planning", exist_ok=True)
    out_path = "reports/b4_generator_planning/b4_ch1_choices_policy_smoke.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Smoke test completed. All pass: {all_pass}")

if __name__ == "__main__":
    main()
