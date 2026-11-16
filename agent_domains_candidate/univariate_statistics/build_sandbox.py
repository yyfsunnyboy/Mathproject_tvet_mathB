"""Build the 數學2 Unit 8 dry-run components.

Writes only under ``tmp/gh_math2_unit8_sandbox_dryrun_r4`` (revision_0001／0002／0003 output in ``..._dryrun``／``..._dryrun_r2``／``..._dryrun_r3`` is kept as is).
Formal DB is opened read-only for a private snapshot.
"""

from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.univariate_statistics.univariate_statistics_specs import COMPONENTS, FIXED_ROWS, OP, SKILLS

DOMAIN_KEY = "statistics.univariate_descriptive"
ROOT = Path(__file__).resolve().parents[2]
DRYRUN = ROOT / "tmp" / "gh_math2_unit8_sandbox_dryrun_r4"
FORMAL_DB = ROOT / "instance" / "kumon_math.db"
SNAPSHOT_DB = ROOT / "tmp" / "gh_math2_unit8_isolated" / "unit8_snapshot.db"
MODULE = "agent_domains_candidate.univariate_statistics.univariate_statistics_domain"
VARIANTS = 20


def isolated_db() -> Path:
    if not SNAPSHOT_DB.exists():
        SNAPSHOT_DB.parent.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(f"file:{FORMAL_DB.as_posix()}?mode=ro", uri=True)
        target = sqlite3.connect(SNAPSHOT_DB)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
    return SNAPSHOT_DB


def _textbook_row(example_id: int) -> dict:
    con = sqlite3.connect(f"file:{isolated_db().as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute("select * from textbook_examples where id=?", (example_id,)).fetchone()
        return dict(row)
    finally:
        con.close()


def _question_of(op: str, givens: dict) -> str | None:
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    try:
        _m, payload = dispatch_registered_operation(DOMAIN_KEY, OP[op], seed=0, constraints=dict(givens))
        surface = [payload["question_text"], payload["correct_answer"]]
        if payload.get("chart_data"):
            surface.append([panel["percent"] for panel in payload["chart_data"]["panels"]])
        return json.dumps(surface, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        return None


def collect_variants(cid: int, op: str, source: dict, sampler) -> list[dict]:
    first = _question_of(op, source)
    if first is None:
        raise RuntimeError(f"source variant invalid for src_{cid}")
    out, seen, questions = [source], {json.dumps(source, sort_keys=True, default=str)}, {first}
    rng = random.Random(f"math2u8:{cid}")
    for _ in range(4000):
        if len(out) >= VARIANTS:
            break
        try:
            cand = sampler(rng)
        except Exception:
            continue
        try:
            key = json.dumps(cand, sort_keys=True)
        except TypeError:
            continue
        if key in seen:
            continue
        question = _question_of(op, cand)
        if question is None or question in questions:
            continue
        seen.add(key)
        questions.add(question)
        out.append(cand)
    return out


def _payload_meta(op: str, payload: dict, variants: list[dict], example_id: int) -> dict:
    from core.gencode.checker_registry import CHECKER_CAPABILITIES

    contract = payload["answer_contract"]
    mode = payload["presentation_mode"]
    answer_type = "choice_label" if mode == "single_choice" else contract["answer_type"]
    checker = contract["checker_key"]
    module = CHECKER_CAPABILITIES.get(checker, {}).get("module", "pipeline")
    return {
        "problem_type_id": OP[op], "domain_operation": OP[op], "line_type": OP[op], "target_task": OP[op],
        "template_slot": OP[op], "presentation_mode": mode, "answer_type": answer_type,
        "fixed_domain_key": DOMAIN_KEY, "textbook_example_id": example_id,
        "checker_key": checker, "equivalence_type": contract["equivalence_type"], "checker_module": module,
        "curriculum_profile": "general_high",
        "constraints": {"generation_constraints": {"variants": variants}},
    }


def build_all(only: set[int] | None = None) -> dict:
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation
    from core.gencode.v3_component_scaffold_builder import build_component_files_from_domain_payload

    report: dict[int, dict] = {}
    for cid, (skill_key, op, source, sampler) in COMPONENTS.items():
        if only and cid not in only:
            continue
        if cid in FIXED_ROWS:
            continue
        skill_id = SKILLS[skill_key]
        variants = collect_variants(cid, op, source, sampler)
        _m, payload = dispatch_registered_operation(DOMAIN_KEY, OP[op], seed=0, constraints=dict(source))
        domain_meta = {
            "fixed_domain_key": DOMAIN_KEY, "domain_module": MODULE,
            "entrypoint": "build_univariate_statistics_matrix", "registered_payload_adapter": True,
            "default_curriculum_profile": "general_high",
        }
        files = build_component_files_from_domain_payload(
            skill_id, f"src_{cid}", "example", domain_meta, _payload_meta(op, payload, variants, cid),
            textbook_example_id=cid, textbook_row=_textbook_row(cid),
        )
        target = DRYRUN / skill_id / "components" / f"src_{cid}"
        target.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (target / name).write_text(text, encoding="utf-8", newline="\n")
        report[cid] = {"skill": skill_id, "op": OP[op], "variants": len(variants)}
    return report


if __name__ == "__main__":
    import sys

    result = build_all({int(x) for x in sys.argv[1:]} or None)
    short = {cid: item["variants"] for cid, item in result.items()}
    print(json.dumps(short, ensure_ascii=False))
    if short:
        print("components:", len(result), "min variants:", min(short.values()))
