# -*- coding: utf-8 -*-
"""A/B evaluation: raw AI Python (A) vs legacy healer chain (B) vs V3 Research Healer adapter (C).

The same saved AI responses feed all three groups; no model is called (the
legacy semantic-heal LLM hook is replaced by a recorder that raises).  Scoring
uses the research repository's authoritative observational evaluator, run in
a subprocess with the research repository as working directory.

Usage:
  python scripts/gencode_v3_research_healer_ab.py run --corpus DIR --research-root DIR --work-dir DIR
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_v3_research_healer_ab"
V3_SAMPLES = [PROJECT_ROOT / "tests/gencode/fixtures/incompatible_slope_of_a_line_33147281/slope_calculator_engine.py"]
GUARD_KEYS = ("math_operator_changed", "control_flow_changed", "function_names_changed", "constants_changed", "code_deleted")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Phase 1: production context (A / B / C outputs)
# ---------------------------------------------------------------------------


class _RecordingClient:
    max_tokens = 0

    def __init__(self) -> None:
        self.calls = 0

    def generate_content(self, *args: Any, **kwargs: Any):
        self.calls += 1
        raise RuntimeError("ab_eval_no_model_calls")


def _legacy(raw: str, skill_id: str) -> dict[str, Any]:
    import core.ai_wrapper as ai_wrapper
    from core.code_generator import _advanced_healer, _basic_cleanup

    client = _RecordingClient()
    attempted = {"n": 0}

    def _recorder(*args: Any, **kwargs: Any):
        attempted["n"] += 1
        raise RuntimeError("ab_eval_no_model_calls")

    original = ai_wrapper.call_ai_with_retry
    ai_wrapper.call_ai_with_retry = _recorder
    started = time.perf_counter()
    out: dict[str, Any] = {"rejected": None}
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            clean, _ = _basic_cleanup(raw)
            healed, regex_fixes, ast_fixes, *_rest = _advanced_healer(clean, 3, skill_id, ai_client=client)
        out.update(code=healed, regex_fixes=regex_fixes, ast_fixes=ast_fixes)
    except ValueError as exc:
        out.update(code=None, rejected=f"legacy_gate:{str(exc)[:120]}")
    except Exception as exc:  # noqa: BLE001
        out.update(code=None, rejected=f"legacy_error:{type(exc).__name__}")
    finally:
        ai_wrapper.call_ai_with_retry = original
    out["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
    out["llm_calls_attempted"] = attempted["n"] + client.calls
    return out


def _group_record(reference: str, raw: str, code: str | None) -> dict[str, Any]:
    from core.gencode.research_healer.structure import parse_status, structural_diff

    if code is None:
        return {"code": None, "sha256": None, "parses": False, "modified": True, "diff": {}}
    diff = structural_diff(reference, code)
    return {
        "code": code,
        "sha256": _sha(code),
        "parses": parse_status(code)["parses"],
        "modified": code != raw,
        "diff": {k: bool(diff.get(k)) for k in (*GUARD_KEYS, "changed", "ast_compared", "delimiter_only")},
    }


def _produce_one(raw: str, skill_id: str) -> dict[str, Any]:
    from core.gencode.research_healer.adapter import extract_unique_python_fence, heal_ai_python_source

    inner, _, _ = extract_unique_python_fence(raw)
    reference = inner if inner is not None else raw
    started = time.perf_counter()
    c = heal_ai_python_source(raw, skill_id=skill_id, component_id="ab", mode="repair")
    c_ms = round((time.perf_counter() - started) * 1000, 3)
    b = _legacy(raw, skill_id)
    probe = [
        {k: p.get(k) for k in ("rule_id", "would_change", "grouping_alternatives", "proposed_parses")}
        for p in c.probe
        if p.get("would_change")
    ]
    return {
        "reference_is_fence": inner is not None,
        "A": {**_group_record(reference, raw, raw), "duration_ms": 0.0},
        "B": {
            **_group_record(reference, raw, b.get("code")),
            "duration_ms": b["duration_ms"],
            "rejected": b["rejected"],
            "llm_calls_attempted": b["llm_calls_attempted"],
            "fixes": (b.get("regex_fixes") or 0) + (b.get("ast_fixes") or 0),
        },
        "C": {
            **_group_record(reference, raw, c.final_code),
            "duration_ms": c_ms,
            "status": c.status,
            "reason": c.reason,
            "eligible": c.rounds >= 1,
            "rules_applied": [r["rule_id"] for r in c.rules_applied],
            "semantic_preservation_proven": c.semantic_preservation_proven,
            "probe_would_change": probe,
            "real_model_calls": c.real_model_calls,
        },
    }


def produce(corpus: Path, out_path: Path) -> int:
    os.environ.setdefault("HEALER_VERBOSE", "0")
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    cells = sorted(corpus.rglob("raw_response.txt"))
    n = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for raw_path in cells:
            cell_dir = raw_path.parent
            artifact = json.loads((cell_dir / "artifact.json").read_text(encoding="utf-8"))
            raw = raw_path.read_text(encoding="utf-8")
            record = {
                "kind": "research_corpus",
                "cell_id": artifact["cell_id"],
                "task_id": artifact["task_id"],
                "model_key": artifact.get("model_key"),
                "condition": artifact.get("condition"),
                "sealed_outcome": artifact.get("outcome"),
                "raw_sha256": _sha(raw),
                **_produce_one(raw, artifact["task_id"]),
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
        for sample in V3_SAMPLES:
            raw = sample.read_text(encoding="utf-8")
            record = {
                "kind": "v3_ai_sample",
                "cell_id": sample.name,
                "task_id": None,
                "raw_sha256": _sha(raw),
                **_produce_one(raw, "vh_數學B1_SlopeOfALine"),
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return n


# ---------------------------------------------------------------------------
# Phase 2: research context (authoritative observational evaluator)
# ---------------------------------------------------------------------------


def evaluate(in_path: Path, out_path: Path, research_root: Path) -> int:
    sys.path[:] = [str(research_root)] + [p for p in sys.path if Path(p or ".").resolve() != Path(__file__).parent]
    from agent_tools.finals_rebuild.math16_observational_evaluator_v1 import (  # type: ignore
        resolve_task_and_api_policy,
        score_source,
    )
    from agent_tools.finals_rebuild.math16_pool import frozen_for_prompt  # type: ignore

    cache: dict[tuple[str, str], dict[str, Any]] = {}
    tasks: dict[str, tuple[Any, str, Any]] = {}
    n = 0
    with in_path.open(encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as dst:
        for line in src:
            record = json.loads(line)
            if record["kind"] != "research_corpus":
                continue
            task_id = record["task_id"]
            if task_id not in tasks:
                task, policy = resolve_task_and_api_policy(task_id)
                tasks[task_id] = (task, policy, frozen_for_prompt(task)["oracle_payload"])
            task, policy, frozen = tasks[task_id]
            scores = {}
            for group in ("A", "B", "C"):
                g = record[group]
                if g["code"] is None:
                    scores[group] = {"status": "FAILED", "classifier_outcome": "legacy_rejected", "primary_failure_layer": "legacy_gate", "failure_subtype": None}
                    continue
                key = (task_id, g["sha256"])
                if key not in cache:
                    with contextlib.redirect_stdout(io.StringIO()):
                        cache[key] = score_source(g["code"], task=task, frozen_params=frozen, api_policy=policy)
                scores[group] = cache[key]
            dst.write(json.dumps({"cell_id": record["cell_id"], "scores": scores}, ensure_ascii=False) + "\n")
            n += 1
    return n


# ---------------------------------------------------------------------------
# Phase 3: aggregate
# ---------------------------------------------------------------------------


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def aggregate(produced: Path, scored: Path) -> dict[str, Any]:
    records = [json.loads(x) for x in produced.read_text(encoding="utf-8").splitlines()]
    scores = {
        json.loads(x)["cell_id"]: json.loads(x)["scores"] for x in scored.read_text(encoding="utf-8").splitlines()
    }
    corpus = [r for r in records if r["kind"] == "research_corpus"]
    groups: dict[str, Any] = {}
    for group in ("A", "B", "C"):
        m: Counter = Counter()
        outcomes: Counter = Counter()
        layers: Counter = Counter()
        durations: list[float] = []
        for r in corpus:
            g = r[group]
            sa, sg = scores[r["cell_id"]]["A"], scores[r["cell_id"]][group]
            a_pass, g_pass = sa["status"] == "PASSED", sg["status"] == "PASSED"
            eligible = not r["A"]["parses"]
            m["total"] += 1
            m["baseline_pass"] += a_pass
            m["baseline_fail"] += not a_pass
            m["eligible"] += eligible
            m["pass"] += g_pass
            m["rescue"] += (not a_pass) and g_pass
            m["regression"] += a_pass and not g_pass
            m["modified"] += bool(g["modified"])
            m["parse_gain"] += eligible and g["parses"]
            a_layer, g_layer = sa["primary_failure_layer"], sg["primary_failure_layer"]
            m["runtime_gain"] += (a_layer in ("runtime", "execution")) and g_layer not in ("runtime", "execution", "parse", "legacy_gate")
            m["contract_mismatch"] += (g_layer or "") in ("contract", "schema", "output_contract")
            for key in GUARD_KEYS:
                if g["modified"] and g["diff"].get(key):
                    m[f"modified_{key}"] += 1
            m["unauthorized_math_change"] += bool(g["modified"] and g["diff"].get("math_operator_changed"))
            m["unauthorized_control_flow_change"] += bool(g["modified"] and g["diff"].get("control_flow_changed"))
            outcomes[sg["classifier_outcome"]] += 1
            layers[str(g_layer)] += 1
            durations.append(float(g.get("duration_ms") or 0.0))
            if group == "B":
                m["legacy_rejected"] += bool(g.get("rejected"))
                m["legacy_triggered"] += bool(g.get("fixes"))
                m["llm_calls_attempted"] += int(g.get("llm_calls_attempted") or 0)
                m["cells_with_llm_semantic_heal_attempt"] += bool(g.get("llm_calls_attempted"))
            if group == "C":
                m["triggered"] += bool(g.get("eligible"))
                m["repaired"] += g.get("status") == "REPAIRED"
                m["abstained"] += g.get("status") in ("ABSTAINED", "REJECTED")
                m["semantic_preservation_proven"] += bool(g.get("semantic_preservation_proven"))
                m["real_model_calls"] += int(g.get("real_model_calls") or 0)
                for p in g.get("probe_would_change") or []:
                    m[f"probe_would_change:{p['rule_id']}"] += 1
                    if p.get("grouping_alternatives") not in (None, 1):
                        m[f"probe_grouping_ambiguous:{p['rule_id']}"] += 1
        groups[group] = {
            **dict(sorted(m.items())),
            "avg_duration_ms": _mean(durations),
            "classifier_outcomes": dict(outcomes.most_common()),
            "failure_layers": dict(layers.most_common()),
        }
    v3 = [
        {
            "sample": r["cell_id"],
            **{
                g: {k: r[g].get(k) for k in ("parses", "modified", "status", "reason", "rejected", "llm_calls_attempted", "diff") if k in r[g]}
                for g in ("A", "B", "C")
            },
        }
        for r in records
        if r["kind"] == "v3_ai_sample"
    ]
    return {"corpus_cells": len(corpus), "groups": groups, "v3_ai_samples": v3}


def _git_status(root: Path) -> str:
    return subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--corpus", required=True, type=Path)
    run.add_argument("--research-root", required=True, type=Path)
    run.add_argument("--work-dir", required=True, type=Path)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--in", dest="in_path", required=True, type=Path)
    ev.add_argument("--out", required=True, type=Path)
    ev.add_argument("--research-root", required=True, type=Path)
    args = parser.parse_args()

    if args.cmd == "evaluate":
        print(evaluate(args.in_path, args.out, args.research_root))
        return 0

    args.work_dir.mkdir(parents=True, exist_ok=True)
    produced = args.work_dir / "ab_produced.jsonl"
    scored = args.work_dir / "ab_scored.jsonl"
    research_before = _git_status(args.research_root)
    started = time.time()
    n = produce(args.corpus, produced)
    print(f"produced {n} corpus cells in {time.time() - started:.1f}s", flush=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "evaluate", "--in", str(produced), "--out", str(scored), "--research-root", str(args.research_root)],
        cwd=args.research_root,
        env=env,
        check=True,
    )
    print(f"scored in {time.time() - started:.1f}s", flush=True)
    summary = aggregate(produced, scored)
    summary["research_repo_clean_after"] = _git_status(args.research_root) == research_before
    summary["corpus"] = str(args.corpus)
    summary["artifacts"] = {"produced": str(produced), "scored": str(scored)}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "ab_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("corpus_cells", "research_repo_clean_after")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
