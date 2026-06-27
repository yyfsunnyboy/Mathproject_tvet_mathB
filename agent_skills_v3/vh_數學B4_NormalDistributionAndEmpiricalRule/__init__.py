from __future__ import annotations
import importlib.util, math, random
from functools import reduce
from pathlib import Path
from typing import Any

SKILL_ID = "vh_數學B4_NormalDistributionAndEmpiricalRule"
GENERATOR_KEYS = ["src_3856","src_3857","src_3858","src_3859","src_3897","src_3898"]
GENERATOR_SPECS = [
    {"textbook_example_id":3856,"component_id":"src_3856","generator_key":"src_3856","presentation_mode":"multi_blank","response_mode":"multi_blank","interaction_type":"multi_blank","source_kind":"example","line_type":"empirical_rule_population_count","answer_type":"multi_part","answer_value_type":"multi_part","problem_type_id":"empirical_rule_population_count","display_order":3856,"source_order":3856,"sampling_weight":10.0},
    {"textbook_example_id":3857,"component_id":"src_3857","generator_key":"src_3857","presentation_mode":"multi_blank","response_mode":"multi_blank","interaction_type":"multi_blank","source_kind":"quiz","line_type":"empirical_rule_population_count","answer_type":"multi_part","answer_value_type":"multi_part","problem_type_id":"empirical_rule_population_count","display_order":3857,"source_order":3857,"sampling_weight":10.0},
    {"textbook_example_id":3858,"component_id":"src_3858","generator_key":"src_3858","presentation_mode":"multi_blank","response_mode":"multi_blank","interaction_type":"multi_blank","source_kind":"example","line_type":"empirical_rule_population_count","answer_type":"multi_part","answer_value_type":"multi_part","problem_type_id":"empirical_rule_population_count","display_order":3858,"source_order":3858,"sampling_weight":10.0},
    {"textbook_example_id":3859,"component_id":"src_3859","generator_key":"src_3859","presentation_mode":"single_choice","response_mode":"single_choice","interaction_type":"single_choice","source_kind":"example","line_type":"compare_distribution_spread","answer_type":"choice_label","answer_value_type":"choice_label","problem_type_id":"compare_distribution_spread","display_order":3859,"source_order":3859,"sampling_weight":10.0},
    {"textbook_example_id":3897,"component_id":"src_3897","generator_key":"src_3897","presentation_mode":"single_choice","response_mode":"single_choice","interaction_type":"single_choice","source_kind":"test","line_type":"empirical_rule_population_count","answer_type":"choice_label","answer_value_type":"choice_label","problem_type_id":"empirical_rule_population_count","display_order":3897,"source_order":3897,"sampling_weight":10.0},
    {"textbook_example_id":3898,"component_id":"src_3898","generator_key":"src_3898","presentation_mode":"single_choice","response_mode":"single_choice","interaction_type":"single_choice","source_kind":"test","line_type":"empirical_rule_population_count","answer_type":"choice_label","answer_value_type":"choice_label","problem_type_id":"empirical_rule_population_count","display_order":3898,"source_order":3898,"sampling_weight":10.0},
]
_COMPONENT_DISPATCH = {k: f"components/{k}/generate.py" for k in GENERATOR_KEYS}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _weight(cid: str) -> float:
    for r in GENERATOR_SPECS:
        if isinstance(r, dict) and str(r.get("component_id","")) == cid:
            return float(r.get("sampling_weight",1) or 1)
    return 1.0


def _ordered_keys() -> list:
    spec_map = {str(r.get("component_id","")): r for r in GENERATOR_SPECS if isinstance(r,dict) and r.get("component_id")}
    return sorted(GENERATOR_KEYS, key=lambda k: (int((spec_map.get(k) or {}).get("display_order",0)), k))


def _load(cid: str, fname: str) -> Any:
    path = _V3_ROOT / "components" / cid / fname
    mname = f"v3_{SKILL_ID}_{cid}_{fname.replace('.py','')}"
    spec = importlib.util.spec_from_file_location(mname, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{cid}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pick(seed=None, component_id=None) -> str:
    global _RR_CURSOR, _SHUFFLED_CYCLE
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    keys = _ordered_keys()
    raw_w = [max(1, int(_weight(k) or 1)) for k in keys]
    g = reduce(math.gcd, raw_w) if raw_w else 1
    cycle = []
    for k, w in zip(keys, raw_w):
        cycle.extend([k] * (w // g))
    if seed is None:
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            _SHUFFLED_CYCLE = list(cycle); random.shuffle(_SHUFFLED_CYCLE); _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]; _RR_CURSOR += 1
        return picked
    clen = len(cycle)
    sh = list(cycle); random.Random(int(seed) // clen).shuffle(sh)
    return sh[int(seed) % clen]


def _spec(cid: str) -> dict:
    for r in GENERATOR_SPECS:
        if isinstance(r,dict) and str(r.get("component_id","")) == cid:
            return dict(r)
    return {}


def _minimal_contract(payload: dict, spec: dict) -> dict:
    embedded = payload.get("answer_contract")
    if isinstance(embedded,dict) and embedded.get("answer_type"):
        return dict(embedded)
    mode = str(payload.get("presentation_mode") or spec.get("presentation_mode") or "short_answer").strip()
    sem = str(payload.get("semantic_answer") or payload.get("display_answer") or payload.get("correct_answer") or "").strip()
    if mode == "single_choice":
        return {"presentation_mode":"single_choice","answer_type":"single_choice","checker":"choice_label_checker","checker_key":"choice_label_checker","answer_equivalence":"choice_label","equivalence":"choice_label","semantic_answer":sem}
    if mode == "multi_blank":
        return {"presentation_mode":"multi_blank","answer_type":"multi_part","checker":"multi_part_answer_checker","checker_key":"multi_part_answer_checker","answer_equivalence":"multi_part_answer","equivalence":"multi_part_answer","semantic_answer":sem}
    return {"presentation_mode":"short_answer","answer_type":"expression","checker":"linear_equation_equivalent_checker","checker_key":"linear_equation_equivalent_checker","answer_equivalence":"linear_equation_equivalent","equivalence":"linear_equation_equivalent","semantic_answer":sem}


def _merge(payload: dict, cid: str) -> dict:
    if not isinstance(payload, dict): return payload
    sp = _spec(cid); out = dict(payload)
    for k in ("textbook_example_id","component_id","generator_key","presentation_mode","answer_type","problem_type_id","source_kind","line_type","display_order","source_order","sampling_weight"):
        if sp.get(k) is not None: out[k] = sp[k]
    out.setdefault("component_id", cid); out.setdefault("generator_key", cid)
    meta = dict(out.get("metadata") or {}) if isinstance(out.get("metadata"), dict) else {}
    for k in ("textbook_example_id","component_id","presentation_mode","answer_type","problem_type_id","source_kind","line_type"):
        v = out.get(k) or sp.get(k)
        if v is not None: meta.setdefault(k, v)
    out["metadata"] = meta
    if not isinstance(out.get("answer_contract"),dict) or not out.get("answer_contract"):
        out["answer_contract"] = _minimal_contract(out, sp)
    ac = out["answer_contract"]
    if ac.get("checker"): out["checker"] = ac["checker"]; out.setdefault("checker_type", ac["checker"])
    if ac.get("answer_equivalence"): out["equivalence"] = ac["answer_equivalence"]
    return out


def generate(level: int = 1, seed=None, component_id=None, **kwargs) -> dict:
    picked = _pick(seed=seed, component_id=component_id)
    mod = _load(picked, "generate.py")
    fn = getattr(mod, "generate", None)
    if not callable(fn): raise RuntimeError(f"component_generate_missing:{picked}")
    payload = fn(level=level, seed=seed, **kwargs)
    if isinstance(payload, dict):
        if not payload.get("component_id"): payload["component_id"] = picked
        return _merge(payload, picked)
    return payload


def check(user_answer, correct_answer, question_payload=None) -> Any:
    payload = dict(question_payload or {})
    cid = str(payload.get("component_id") or "")
    if cid and cid in _COMPONENT_DISPATCH:
        mod = _load(cid, "generate.py")
        fn = getattr(mod, "check", None)
        if callable(fn): return fn(user_answer, correct_answer, payload)
    from core.gencode.runtime_skill_wrapper import check_answer
    return check_answer(user_answer, correct_answer, payload=payload)


def get_hint(step: int, question_payload=None) -> str:
    payload = dict(question_payload or {})
    cid = str(payload.get("component_id") or "")
    if cid and cid in _COMPONENT_DISPATCH:
        try:
            mod = _load(cid, "get_hint.py")
            fn = getattr(mod, "get_hint", None)
            if callable(fn): return str(fn(step, payload) or "")
        except Exception:
            pass
    return ""