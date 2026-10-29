"""Read-only evidence for the 普高數學2 Unit 5 teacher acceptance page (no rebuild, no GenCode run, no write outside this folder).

* integrity: bundle SHA-256, review status, package files == candidate sources, rehearsal-published generate.py == rehearsal report
* representative questions: stem / answer / explanation from the rehearsal-published sandbox generators (seed 0 = textbook parameters)
* grading samples through the shared runtime checker (equivalent accepted, wrong rejected)
* the four ○× components: every variant (seeds 0..19), the variation audit's own per-payload checks replayed rule by rule
Writes teacher_acceptance_evidence.json next to this script.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.combinations.sandbox_harness import register_candidate_in_memory  # noqa: E402

WORKSPACE = ROOT / "reports/domain_operation_workspaces/capability_discrete_combinations_5ba1971d/revision_0001"
PROJECT = ROOT / "tmp/gh_math2u5_rehearsal/run/project"
SKILL_OF = {cid: "gh_Combination" for cid in range(12812, 12834)} | {cid: "gh_BinomialTheorem" for cid in range(12835, 12849)}
REPRESENTATIVE = (12813, 12822, 12828, 12833, 12835, 12836, 12837, 12843, 12846, 12848)
TRUE_FALSE = (12823, 12824, 12825, 12840)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(cid: int):
    path = PROJECT / "agent_skills_v3" / SKILL_OF[cid] / "components" / f"src_{cid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"accept_{uuid.uuid4().hex}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return path, module.generate


def main() -> None:
    register_candidate_in_memory()
    from core.gencode.runtime_skill_wrapper import check_answer

    bundle_path = WORKSPACE / "promotion_bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    rehearsal = json.loads((HERE / "rehearsal_unit5_report.json").read_text(encoding="utf-8"))
    integrity = {
        "bundle_sha256": sha(bundle_path),
        "review_status": bundle["review"]["status"],
        "operations": len(bundle["operations"]),
        "skill_bindings": {k: len(v["allowed_operations"]) for k, v in bundle["skill_bindings"].items()},
        "package_matches_bundle": all(sha(WORKSPACE / "production_package" / n) == h for n, h in bundle["files"].items()),
        "package_matches_candidate": all(sha(ROOT / "agent_domains_candidate/combinations" / n) == h for n, h in bundle["files"].items()),
        "published_generators_match_rehearsal": all(
            sha(PROJECT / "agent_skills_v3" / item["skill"] / "components" / f"src_{cid}" / "generate.py") == item["verify"]["generate_sha256"]
            for cid, item in rehearsal["rebuild"].items()),
        "rehearsal_tracker_verified": sum(1 for item in rehearsal["rebuild"].values() if (item.get("tracker") or [None, None])[1] == "verified"),
        "rehearsal_production_paths_written": rehearsal["production_paths_written"],
    }

    representative = {}
    for cid in REPRESENTATIVE:
        _path, generate = load(cid)
        p = generate(seed=0, component_id=f"src_{cid}")
        representative[cid] = {"skill": SKILL_OF[cid], "question_text": p["question_text"], "correct_answer": p["correct_answer"],
                               "display_answer": p.get("display_answer"), "explanation_steps": p.get("explanation_steps"),
                               "answer_type": p["answer_contract"]["answer_type"], "checker": p["answer_contract"]["checker_key"]}

    def grade(cid, answer, seed=0):
        _path, generate = load(cid)
        p = generate(seed=seed, component_id=f"src_{cid}")
        return bool(check_answer(answer, p["correct_answer"], payload=p))

    grading = [
        {"id": 12835, "answer": "y^5+5xy^4+10x^2y^3+10x^3y^2+5x^4y+x^5", "kind": "展開式重排", "want": True},
        {"id": 12835, "answer": "x^5+5*x^4*y+10*x^3*y^2+10*x^2*y^3+5*x*y^4+y^5", "kind": "顯式乘號", "want": True},
        {"id": 12835, "answer": "(x+y)^5", "kind": "未展開", "want": False},
        {"id": 12835, "answer": "x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4", "kind": "缺項", "want": False},
        {"id": 12836, "answer": "16x^4+32x^3y+24x^2y^2+8xy^3+y^4", "kind": "符號錯", "want": False},
        {"id": 12813, "answer": {"part_1": "120", "part_2": "56"}, "kind": "多小題全對", "want": True},
        {"id": 12813, "answer": {"part_1": "120", "part_2": "55"}, "kind": "多小題一題錯", "want": False},
        {"id": 12813, "answer": {"part_1": "120", "part_2": ""}, "kind": "多小題漏答", "want": False},
        {"id": 12843, "answer": {"part_1": "-41", "part_2": "29"}, "kind": "a, b 全對", "want": True},
        {"id": 12843, "answer": {"part_1": "29", "part_2": "-41"}, "kind": "a, b 對調", "want": False},
        {"id": 12822, "answer": "1,3,4,5", "kind": "複選全對", "want": True},
        {"id": 12822, "answer": "5, 4, 3, 1", "kind": "複選順序不同", "want": True},
        {"id": 12822, "answer": "1,3,4", "kind": "複選漏選", "want": False},
        {"id": 12822, "answer": "1,2,3,4,5", "kind": "複選多選", "want": False},
        {"id": 12848, "answer": "-1", "kind": "數值", "want": True},
        {"id": 12848, "answer": "-2/2", "kind": "等值分數", "want": True},
        {"id": 12848, "answer": "1", "kind": "數值錯", "want": False},
    ]
    for g in grading:
        g["got"] = grade(g["id"], g["answer"])
        g["ok"] = g["got"] == g["want"]

    true_false = {}
    for cid in TRUE_FALSE:
        _path, generate = load(cid)
        stems, labels, rules, problems = set(), {"A": 0, "B": 0}, {}, []
        for seed in range(20):
            p = generate(seed=seed, component_id=f"src_{cid}")
            ans = p["correct_answer"]
            choices = p.get("choices") or []
            stems.add(p["question_text"])
            labels[ans] = labels.get(ans, 0) + 1
            replay = {
                "required_keys": bool(p.get("question_text") and ans is not None and p.get("answer_contract") and p.get("presentation_mode")),
                "self_check": bool(check_answer(ans, ans, payload=p)),
                "four_choices": len(choices) == 4,
                "distinct_choices": len({c.get("text") or c.get("value") for c in choices}) == len(choices),
                "label_in_choices": ans in {c.get("label") for c in choices},
                "opposite_rejected": not check_answer("B" if ans == "A" else "A", ans, payload=p),
                "no_answer_in_stem": (p.get("display_answer") or "") not in p["question_text"].replace("「○」", "").replace("「×」", ""),
            }
            for k, v in replay.items():
                rules.setdefault(k, 0)
                rules[k] += int(v)
            if p["answer_contract"]["checker_key"] != "choice_label_checker" or [c.get("label") for c in choices] != ["A", "B"]:
                problems.append(f"seed{seed}:contract")
        true_false[cid] = {"presentation_mode": p["presentation_mode"], "checker": p["answer_contract"]["checker_key"],
                           "choices": [{k: c.get(k) for k in ("label", "value", "text") if c.get(k)} for c in choices],
                           "seeds": 20, "distinct_stems": len(stems), "answers": labels, "rules_passed_of_20": rules, "problems": problems,
                           "sample_true": next((s for s in stems), "")}
        true_false[cid]["samples"] = []
        for seed in range(20):
            p = generate(seed=seed, component_id=f"src_{cid}")
            if len(true_false[cid]["samples"]) < 2 and p["correct_answer"] not in [s["answer"] for s in true_false[cid]["samples"]]:
                true_false[cid]["samples"].append({"seed": seed, "stem": p["question_text"], "answer": p["correct_answer"],
                                                   "display": p.get("display_answer"), "explanation_steps": p.get("explanation_steps")})
        del true_false[cid]["sample_true"]

    out = {"integrity": integrity, "representative": representative, "grading": grading, "true_false": true_false}
    (HERE / "teacher_acceptance_evidence.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"integrity": integrity, "grading_ok": all(g["ok"] for g in grading),
                      "grading_bad": [g for g in grading if not g["ok"]],
                      "true_false": {k: {x: v[x] for x in ("presentation_mode", "checker", "choices", "distinct_stems", "answers", "rules_passed_of_20", "problems")}
                                     for k, v in true_false.items()}}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
