# -*- coding: utf-8 -*-
import argparse
import re

import pandas as pd

from app import app
from models import db, SkillInfo


def load_skills_from_backup(filepath):
    xls = pd.read_excel(filepath, sheet_name=None, engine="openpyxl")
    if "skills_info" not in xls:
        raise ValueError("backup missing skills_info sheet")
    df = xls["skills_info"].where(pd.notnull(xls["skills_info"]), None)
    if "skill_id" not in df.columns:
        raise ValueError("skills_info sheet missing skill_id column")
    return df


def is_b1_skill(skill_id):
    sid = str(skill_id or "")
    return bool(re.match(r"^vh_.*B1_", sid) or re.match(r"^outline_vocational_.*B1_", sid))


def _is_blank(val):
    if val is None:
        return True
    if isinstance(val, float) and pd.isna(val):
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def _to_int_bool(val, default=1):
    if _is_blank(val):
        return int(default)
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return 1 if int(val) != 0 else 0
    s = str(val).strip().lower()
    if s in {"true", "t", "yes", "y", "1"}:
        return 1
    if s in {"false", "f", "no", "n", "0"}:
        return 0
    return int(default)


def normalize_skills_info_row(raw):
    cols = SkillInfo.__table__.columns.keys()
    out = {}
    for col in cols:
        if col in raw:
            v = raw[col]
            if isinstance(v, float) and pd.isna(v):
                v = None
            out[col] = v

    if _is_blank(out.get("gemini_prompt")):
        out["gemini_prompt"] = ""
    if _is_blank(out.get("input_type")):
        out["input_type"] = "text"
    if _is_blank(out.get("consecutive_correct_required")):
        out["consecutive_correct_required"] = 3
    if _is_blank(out.get("order_index")):
        out["order_index"] = 0
    if _is_blank(out.get("importance")):
        out["importance"] = 1

    # Preserve explicit FALSE for outline rows and all rows.
    out["is_active"] = _to_int_bool(out.get("is_active"), default=1)

    if "description" in cols and _is_blank(out.get("description")):
        desc_col = SkillInfo.__table__.columns.get("description")
        if desc_col is not None and not getattr(desc_col, "nullable", True):
            out["description"] = ""

    for name in ("suggested_prompt_1", "suggested_prompt_2", "suggested_prompt_3"):
        col = SkillInfo.__table__.columns.get(name)
        if col is None:
            continue
        if _is_blank(out.get(name)) and not getattr(col, "nullable", True):
            out[name] = ""
    return out


def main():
    parser = argparse.ArgumentParser(description="Repair missing skills_info rows from backup")
    parser.add_argument("--file", required=True, help="Path to backup xlsx")
    parser.add_argument("--apply", action="store_true", help="Apply upsert for missing rows")
    args = parser.parse_args()

    with app.app_context():
        df = load_skills_from_backup(args.file)
        backup_rows = len(df)
        backup_by_id = {}
        for _, row in df.iterrows():
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                backup_by_id[sid] = row.to_dict()

        db_ids = {sid for (sid,) in db.session.query(SkillInfo.skill_id).all()}
        missing_ids = sorted([sid for sid in backup_by_id.keys() if sid not in db_ids])
        missing_b1 = [sid for sid in missing_ids if is_b1_skill(sid)]

        print(f"backup skills_info rows: {backup_rows}")
        print(f"backup unique skill_id: {len(backup_by_id)}")
        print(f"DB skills_info rows: {len(db_ids)}")
        print(f"missing rows: {len(missing_ids)}")
        print(f"missing B1 rows: {len(missing_b1)}")

        missing_rows = [backup_by_id[sid] for sid in missing_ids]
        gemini_blank = sum(1 for r in missing_rows if _is_blank(r.get("gemini_prompt")))
        input_type_blank = sum(1 for r in missing_rows if _is_blank(r.get("input_type")))
        ccr_blank = sum(1 for r in missing_rows if _is_blank(r.get("consecutive_correct_required")))
        is_active_blank = sum(1 for r in missing_rows if _is_blank(r.get("is_active")))
        order_blank = sum(1 for r in missing_rows if _is_blank(r.get("order_index")))
        importance_blank = sum(1 for r in missing_rows if _is_blank(r.get("importance")))
        print(f"gemini_prompt blank rows = {gemini_blank} -> will fill \"\"")
        print(f"input_type blank rows = {input_type_blank} -> will fill \"text\"")
        print(f"consecutive_correct_required blank rows = {ccr_blank} -> will fill 3")
        print(f"is_active blank rows = {is_active_blank} -> will fill 1")
        print(f"order_index blank rows = {order_blank} -> will fill 0")
        print(f"importance blank rows = {importance_blank} -> will fill 1")

        print("missing skill_id preview (top 30):")
        for sid in missing_ids[:30]:
            print(f"  - {sid}")

        if not args.apply:
            print("dry-run only. use --apply to upsert missing skills_info rows.")
            return

        inserted = 0
        failed = 0
        for sid in missing_ids:
            raw = dict(backup_by_id[sid])
            clean = normalize_skills_info_row(raw)
            try:
                row = SkillInfo(**clean)
                db.session.add(row)
                db.session.commit()
                inserted += 1
            except Exception as e:
                db.session.rollback()
                failed += 1
                print(f"FAILED skill_id={sid}: {e}")

        print(f"apply done: inserted={inserted}, failed={failed}")


if __name__ == "__main__":
    main()
