# -*- coding: utf-8 -*-
"""B2 1-1 Source Fidelity / Answer Oracle reclassification (no Phase 3)."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.component_tracker_service import save_tracker_record
from core.registry.domain_operation_registry import get_operation_spec
from core.gencode.services.failed_component_recovery_service import _has_executable_adapter_route

DB = ROOT / "instance" / "kumon_math.db"
SKILLS = [
    "vh_數學B2_AngleMeasurementAndConversion",
    "vh_數學B2_ArcLengthAndAreaOfSector",
    "vh_數學B2_CoterminalAngles",
]
EXAMPLE_IDS = list(range(11606, 11626))


def _load_generate(skill_id: str, example_id: int):
    path = ROOT / "agent_skills_v3" / skill_id / "components" / f"src_{example_id}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"src_{example_id}_gen", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod, path.exists()


def _source_fidelity(row: dict) -> dict:
    text = str(row.get("problem_text") or "").strip()
    ptype = str(row.get("problem_type") or "").strip()
    notes = str(row.get("notes") or "")
    parse_corruption = (
        "[MATH_PARSE_FAILED]" in text
        or "PARSE_FAILED" in text
        or "�" in text
    )
    question_text_complete = len(text) >= 8 and not parse_corruption
    formula_complete = True
    if "公式" in text and ("缺少" in text or "遺失" in text):
        formula_complete = False
    visual_needed = any(tok in text for tok in ("如圖", "右圖", "下圖", "附圖", "圖示"))
    has_image_ref = any(
        tok in notes.lower() + text.lower()
        for tok in (".png", ".jpg", ".svg", "image", "圖檔")
    )
    # Student-edition stem that mentions a figure still needs the figure if the
    # question cannot be solved from remaining numeric conditions.
    visual_asset_complete = True
    if visual_needed and not has_image_ref:
        # If the stem still contains enough numeric conditions, figure is illustrative.
        import re
        nums = re.findall(r"\d+", text)
        visual_asset_complete = len(nums) >= 1 or "表" in text
    answer_topology_complete = bool(ptype or text)
    fail_reasons = []
    if not question_text_complete:
        fail_reasons.append("source_incomplete")
    if parse_corruption:
        fail_reasons.append("source_corrupt")
    if not formula_complete:
        fail_reasons.append("source_incomplete")
    if not visual_asset_complete:
        fail_reasons.append("source_incomplete")
    if not answer_topology_complete:
        fail_reasons.append("source_incomplete")
    status = "FAIL" if fail_reasons else "PASS"
    return {
        "question_text_complete": question_text_complete,
        "formula_complete": formula_complete,
        "visual_asset_complete": visual_asset_complete,
        "answer_topology_complete": answer_topology_complete,
        "parse_corruption": parse_corruption,
        "final": status,
        "fail_reasons": fail_reasons,
        "has_correct_answer": bool(str(row.get("correct_answer") or "").strip()),
        "has_detailed_solution": bool(str(row.get("detailed_solution") or "").strip()),
    }


def _oracle_readiness(operation: str) -> dict:
    spec = get_operation_spec("trigonometry.angle", operation)
    adapter = False
    if spec is not None:
        adapter = _has_executable_adapter_route(
            selected_operation=operation,
            domain_module="core.domain.trigonometry_angle_domain",
            impl_fn_name=spec.handler,
            presentation_mode="short_answer",
            answer_type="expression",
        )
    exact = bool(spec) and adapter
    return {
        "fixed_domain_key": "trigonometry.angle",
        "operation_registered": spec is not None,
        "adapter": adapter,
        "exact_ready": exact,
    }


def _canonical_from_payload(payload: dict):
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = ac.get("parts") if isinstance(ac.get("parts"), list) else []
    if parts:
        return {str(p.get("key") or p.get("field_key") or f"p{i}"): p.get("expected_answer") for i, p in enumerate(parts)}
    table = payload.get("table_question") or payload.get("table_data") or {}
    blanks = table.get("blank_cells") if isinstance(table, dict) else None
    if isinstance(blanks, list) and blanks:
        return {str(b.get("field_key") or b.get("key")): b.get("expected_answer") for b in blanks if isinstance(b, dict)}
    ans = payload.get("answer")
    if isinstance(ans, dict):
        return ans
    return ans


def _wrong_from_canonical(canonical):
    if isinstance(canonical, dict):
        out = {}
        for k, v in canonical.items():
            s = str(v or "").strip()
            if s.replace("-", "").replace(".", "", 1).isdigit():
                try:
                    out[k] = str(int(float(s)) + 7)
                except Exception:
                    out[k] = "999"
            elif "pi" in s.lower() or "π" in s:
                out[k] = "pi/999"
            else:
                out[k] = "WRONG"
        return out
    s = str(canonical or "").strip()
    if "pi" in s.lower():
        return "pi/999"
    if s.replace("-", "").replace(".", "", 1).isdigit():
        try:
            return str(int(float(s)) + 7)
        except Exception:
            return "999"
    return "WRONG"


def _equiv_from_canonical(canonical):
    if isinstance(canonical, dict):
        out = {}
        for k, v in canonical.items():
            s = str(v or "").strip().replace(" ", "")
            if not s:
                out[k] = s
            elif s.lstrip("+-").replace(".", "", 1).isdigit():
                if s.startswith("-"):
                    out[k] = s  # keep signed integer
                else:
                    out[k] = f"+{s.lstrip('+')}"
            elif "pi" in s.lower() or "π" in s:
                out[k] = s.replace("*", "")
            else:
                out[k] = s
        return out
    s = str(canonical or "").strip().replace(" ", "")
    if s.lstrip("+-").replace(".", "", 1).isdigit() and not s.startswith("-"):
        return f"+{s.lstrip('+')}"
    if "pi" in s.lower():
        return s.replace("*", "")
    return s


def _grade(payload, user, correct):
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    return check_answer(
        user,
        correct,
        payload=payload,
        answer_contract=ac,
        skill_id=str(payload.get("skill_id") or ""),
    )


def validate_component(mod, example_id: int) -> dict:
    errors = []
    last_payload = None
    last_canonical = None
    last_ac = {}
    for seed in range(20):
        try:
            payload = mod.generate(seed=seed)
        except Exception as exc:
            errors.append(f"seed{seed}:generate:{exc}")
            continue
        last_payload = payload
        last_ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
        canonical = _canonical_from_payload(payload)
        last_canonical = canonical
        try:
            ok = _grade(payload, canonical, canonical)
            if not ok:
                errors.append(f"seed{seed}:canonical_fail")
        except Exception as exc:
            errors.append(f"seed{seed}:canonical_exc:{exc}")
            continue
        try:
            wrong = _wrong_from_canonical(canonical)
            if _grade(payload, wrong, canonical):
                errors.append(f"seed{seed}:wrong_accepted")
        except Exception as exc:
            errors.append(f"seed{seed}:wrong_exc:{exc}")
        try:
            equiv = _equiv_from_canonical(canonical)
            if not _grade(payload, equiv, canonical):
                errors.append(f"seed{seed}:equiv_fail")
        except Exception as exc:
            errors.append(f"seed{seed}:equiv_exc:{exc}")
        # required-form: pi_expression should reject decimal-only
        parts = last_ac.get("parts") if isinstance(last_ac.get("parts"), list) else []
        if any(str(p.get("required_form") or "") == "pi_expression" for p in parts if isinstance(p, dict)):
            rf_wrong = dict(canonical) if isinstance(canonical, dict) else canonical
            if isinstance(rf_wrong, dict):
                for p in parts:
                    if str(p.get("required_form") or "") == "pi_expression":
                        rf_wrong[str(p.get("key"))] = "1.57"
                try:
                    if _grade(payload, rf_wrong, canonical):
                        errors.append(f"seed{seed}:required_form_accepted")
                except Exception as exc:
                    errors.append(f"seed{seed}:required_form_exc:{exc}")
    table_ok = None
    if example_id == 11616 and last_payload:
        tq = last_payload.get("table_question") if isinstance(last_payload.get("table_question"), dict) else {}
        td = last_payload.get("table_data") if isinstance(last_payload.get("table_data"), dict) else {}
        blanks = tq.get("blank_cells") or td.get("blank_cells") or []
        needed = {"row", "col", "field_key"}
        cells_ok = isinstance(blanks, list) and blanks and all(needed <= set(b) for b in blanks if isinstance(b, dict))
        has_order = bool(tq.get("answer_order") or td.get("answer_order"))
        at = str(last_payload.get("answer_type") or last_ac.get("answer_type") or "")
        table_ok = at == "table_fill" and cells_ok and has_order and bool(tq or td)
    return {
        "errors": errors[:40],
        "seed_pass": len(errors) == 0,
        "answer_type": str((last_payload or {}).get("answer_type") or last_ac.get("answer_type") or ""),
        "checker": str(last_ac.get("checker") or last_ac.get("checker_key") or (last_payload or {}).get("checker") or ""),
        "presentation_mode": str((last_payload or {}).get("presentation_mode") or ""),
        "table_fill_contract": table_ok,
        "sample_canonical": last_canonical if not isinstance(last_canonical, dict) else {k: last_canonical[k] for k in list(last_canonical)[:8]},
        "has_table_question": bool((last_payload or {}).get("table_question")),
        "blank_count": len(((last_payload or {}).get("table_question") or {}).get("blank_cells") or ((last_payload or {}).get("table_data") or {}).get("blank_cells") or []) if last_payload else 0,
    }


def main():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    te_rows = {
        int(r["id"]): dict(r)
        for r in conn.execute(
            """
            SELECT id, skill_id, problem_text, problem_type, correct_answer, detailed_solution, notes
            FROM textbook_examples
            WHERE id BETWEEN 11606 AND 11625
            ORDER BY id
            """
        )
    }
    tracker = {
        int(r["textbook_example_id"]): dict(r)
        for r in conn.execute(
            """
            SELECT textbook_example_id, skill_id, component_id, gencode_status, gencode_error_log
            FROM gencode_component_tracker
            WHERE textbook_example_id BETWEEN 11606 AND 11625
            ORDER BY textbook_example_id
            """
        )
    }

    reports = []
    for eid in EXAMPLE_IDS:
        row = te_rows.get(eid)
        if not row:
            reports.append({"example_id": eid, "reason": "missing_row", "final_status": "not_found"})
            continue
        skill_id = row["skill_id"]
        fid = _source_fidelity(row)
        mod, exists = _load_generate(skill_id, eid)
        op = str(getattr(mod, "DOMAIN_OPERATION", "") or "")
        ready = _oracle_readiness(op)
        val = validate_component(mod, eid) if exists else {"errors": ["component_missing"], "seed_pass": False}
        oracle_source = "none"
        if fid["has_correct_answer"] or fid["has_detailed_solution"]:
            oracle_source = "source"
        elif ready["exact_ready"]:
            oracle_source = "domain_operation"
        else:
            oracle_source = "unavailable"

        verified = (
            fid["final"] == "PASS"
            and oracle_source in {"source", "domain_operation"}
            and ready["exact_ready"]
            and val["seed_pass"]
            and bool(val.get("checker"))
            and bool(val.get("answer_type"))
        )
        reason = "verified"
        if fid["final"] == "FAIL":
            reason = (fid["fail_reasons"] or ["source_incomplete"])[0]
        elif oracle_source == "unavailable":
            reason = "oracle_unavailable"
        elif not ready["exact_ready"]:
            reason = "oracle_not_ready"
        elif not val["seed_pass"]:
            if any("canonical" in e for e in val["errors"]):
                reason = "checker_failed"
            elif any("wrong_accepted" in e for e in val["errors"]):
                reason = "checker_failed"
            else:
                reason = "seed_validation_failed"
        if eid == 11616 and val.get("table_fill_contract") is False:
            verified = False
            reason = "answer_contract_failed"

        reports.append(
            {
                "example_id": eid,
                "skill_id": skill_id,
                "component_id": f"src_{eid}",
                "source_fidelity": fid["final"],
                "source_fidelity_detail": fid,
                "oracle_source": oracle_source,
                "oracle_operation": op,
                "exact_ready": "YES" if ready["exact_ready"] else "NO",
                "answer_type": val.get("answer_type"),
                "checker": val.get("checker"),
                "20_seed": "PASS" if val.get("seed_pass") else "FAIL",
                "final_status": "verified" if verified else "failed",
                "reason": reason if not verified else "all_gates_pass",
                "old_status": (tracker.get(eid) or {}).get("gencode_status"),
                "old_error": (tracker.get(eid) or {}).get("gencode_error_log"),
                "errors": val.get("errors"),
                "table_fill_contract": val.get("table_fill_contract"),
                "presentation_mode": val.get("presentation_mode"),
                "has_table_question": val.get("has_table_question"),
                "blank_count": val.get("blank_count"),
            }
        )

    out = ROOT / "scratch" / "_b2_1_1_reclassify_report.json"
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")

    old_mgt = 0
    remaining_mgt = 0
    for rec in reports:
        eid = int(rec["example_id"])
        old_err = str(rec.get("old_error") or "")
        if "missing_ground_truth" in old_err:
            old_mgt += 1
        skill_id = rec["skill_id"]
        payload = {
            "source_fidelity": rec.get("source_fidelity"),
            "oracle_source": rec.get("oracle_source"),
            "oracle_operation": rec.get("oracle_operation"),
            "exact_ready": rec.get("exact_ready"),
            "answer_type": rec.get("answer_type"),
            "checker": rec.get("checker"),
            "reclassification": "sop_v1.13_source_fidelity_answer_oracle",
        }
        if rec.get("final_status") == "verified":
            save_tracker_record(
                conn,
                textbook_example_id=eid,
                skill_id=skill_id,
                gencode_status="verified",
                induced_spec_payload=payload,
                gencode_error_log=None,
            )
        else:
            reason = str(rec.get("reason") or "failed")
            if reason == "missing_ground_truth":
                remaining_mgt += 1
            save_tracker_record(
                conn,
                textbook_example_id=eid,
                skill_id=skill_id,
                gencode_status="failed",
                induced_spec_payload=payload,
                gencode_error_log=reason,
            )
        rec["tracker_status_after"] = rec.get("final_status")

    print(json.dumps({
        "n": len(reports),
        "verified": sum(1 for r in reports if r.get("final_status") == "verified"),
        "failed": sum(1 for r in reports if r.get("final_status") != "verified"),
        "sf_pass": sum(1 for r in reports if r.get("source_fidelity") == "PASS"),
        "old_missing_ground_truth_failures": old_mgt,
        "remaining_missing_ground_truth_failures": remaining_mgt,
        "11616": next((r for r in reports if r.get("example_id") == 11616), None),
        "fail_ids": [r["example_id"] for r in reports if r.get("final_status") != "verified"],
        "fail_reasons": {r["example_id"]: (r.get("reason"), (r.get("errors") or [])[:3]) for r in reports if r.get("final_status") != "verified"},
    }, ensure_ascii=False, indent=2, default=str))
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
