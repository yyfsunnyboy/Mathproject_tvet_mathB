# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("ft", ROOT / "skills" / "vh_數學B1_FactorTheorem.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

keys = list(mod.GENERATOR_KEYS)
print("KEYS", keys)

hits = []
for key in keys:
    gen_path = ROOT / "agent_skills_v3" / "vh_數學B1_FactorTheorem" / "components" / key / "generate.py"
    text = gen_path.read_text(encoding="utf-8")
    pres = "single_choice" if 'PRESENTATION_MODE = "single_choice"' in text or "PRESENTATION_MODE = 'single_choice'" in text else "other"
    for seed in range(0, 80):
        try:
            pl = mod.generate(seed=seed, component_id=key)
        except TypeError:
            pl = mod.generate(seed=seed)
        cid = str(pl.get("component_id") or "")
        if cid and cid != key:
            continue
        q = str(pl.get("question_text") or pl.get("question") or "")
        choices = pl.get("choices") or []
        texts = []
        for ch in choices:
            if isinstance(ch, dict):
                texts.append(str(ch.get("text") or ""))
            else:
                texts.append(str(ch))
        joined = " | ".join(texts)
        if "驗證" in q and "因式分解" in q:
            rec = {
                "component_id": cid or key,
                "seed": seed,
                "answer_type": pl.get("answer_type"),
                "presentation_mode": pl.get("presentation_mode"),
                "pres_in_file": pres,
                "question": q,
                "answer": pl.get("answer"),
                "choices": texts,
                "has_suffix": any(t.endswith(("_1", "_2", "_3")) or "_1" in t or "_2" in t or "_3" in t for t in texts),
            }
            hits.append(rec)
            print("HIT", rec["component_id"], "seed", seed, "at", rec["answer_type"], "suffix", rec["has_suffix"])
            print(" Q", q)
            print(" C", texts)
            print(" A", pl.get("answer"))
            break

print("HIT_COUNT", len(hits))
(ROOT / "scratch" / "_locate_factor_suffix_choice.json").write_text(
    json.dumps(hits, ensure_ascii=False, indent=2), encoding="utf-8"
)
