# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SKILL = ROOT / "agent_skills_v3" / "vh_數學B1_FactorTheorem"
KEYS = [
    "src_4646", "src_4647", "src_4648", "src_4649", "src_4650", "src_4651",
    "src_4652", "src_4653", "src_4654", "src_4655", "src_4660", "src_4661",
    "src_4662", "src_4663", "src_4710", "src_4711", "src_4712",
]


def _load(key: str):
    path = SKILL / "components" / key / "generate.py"
    spec = importlib.util.spec_from_file_location(f"gen_{key}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _choice_texts(pl: dict) -> list[str]:
    out = []
    for ch in pl.get("choices") or []:
        if isinstance(ch, dict):
            out.append(str(ch.get("text") or ""))
        else:
            out.append(str(ch))
    return out


suffix_re = re.compile(r"_(?:[123]|duplicate|copy)\b")

rows = []
for key in KEYS:
    mod = _load(key)
    samples = []
    hits_verify = []
    hits_suffix = []
    for seed in range(0, 120):
        pl = mod.generate(level=1, seed=seed, component_id=key)
        q = str(pl.get("question_text") or pl.get("question") or "")
        texts = _choice_texts(pl)
        rec = {
            "seed": seed,
            "answer_type": pl.get("answer_type"),
            "presentation_mode": pl.get("presentation_mode"),
            "question": q,
            "answer": pl.get("answer"),
            "display_answer": pl.get("display_answer"),
            "choices": texts,
        }
        if seed < 3:
            samples.append(rec)
        if "驗證" in q:
            hits_verify.append(rec)
        if any(suffix_re.search(t) for t in texts):
            hits_suffix.append(rec)
        if "2x^2-2x-12" in q.replace(" ", "") or "2x^{2}-2x-12" in q.replace(" ", ""):
            hits_verify.append({**rec, "poly_hit": True})
    print("=" * 60)
    print(key, "mode", samples[0]["presentation_mode"] if samples else None)
    print(" sample0 Q:", (samples[0]["question"] if samples else "")[:180])
    print(" sample0 C:", samples[0]["choices"] if samples else None)
    print(" sample0 A:", samples[0]["answer"] if samples else None)
    print(" verify_hits", len(hits_verify), "suffix_hits", len(hits_suffix))
    if hits_verify:
        print(" FIRST VERIFY seed", hits_verify[0]["seed"], hits_verify[0]["question"][:160])
        print("  choices", hits_verify[0]["choices"])
    if hits_suffix:
        print(" FIRST SUFFIX seed", hits_suffix[0]["seed"], hits_suffix[0]["choices"])
    rows.append({
        "component_id": key,
        "verify_count": len(hits_verify),
        "suffix_count": len(hits_suffix),
        "sample0": samples[0] if samples else None,
        "first_verify": hits_verify[0] if hits_verify else None,
        "first_suffix": hits_suffix[0] if hits_suffix else None,
    })

(ROOT / "scratch" / "_dump_factor_choice_payloads.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8",
)
print("DONE")
