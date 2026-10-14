# -*- coding: utf-8 -*-
"""Section practice-type rotation (題型全覆蓋 + 動態補弱).

A section (one runtime skill) exposes several generator components.  Components
that share the same practice type (e.g. 例題1 and 隨堂練習1) are candidates of a
single type.  The first round serves exactly one question per unique type, so the
round length is ``len(unique type keys)`` and never a configured count.  Types
answered incorrectly become ``weak`` and are re-served in later rounds, preferring
a different candidate, until every type is ``passed``.

Type key resolution order (first non-empty wins):
    problem_type_id > family_id > pattern_id > practice_type_key

Example numbers, question ids and question text are never used as type identity.

The rotation state lives in the cookie session, so it is stored compactly: types
and candidates are addressed by their index in the (deterministic) pool order.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import random
import re
from typing import Any, Callable, Iterable

STATUS_UNSEEN = "unseen"
STATUS_PASSED = "passed"
STATUS_WEAK = "weak"
_STATUS_CODE = {STATUS_UNSEEN: "u", STATUS_PASSED: "p", STATUS_WEAK: "w"}
_CODE_STATUS = {v: k for k, v in _STATUS_CODE.items()}

TYPE_KEY_FIELDS: tuple[str, ...] = ("problem_type_id", "family_id", "pattern_id", "practice_type_key")

SESSION_KEY = "practice_type_rotation"
_MAX_PENDING = 4


def _candidate_id(spec: dict[str, Any]) -> str:
    return str(spec.get("component_id") or spec.get("generator_key") or "").strip()


def resolve_type_key(spec: dict[str, Any]) -> tuple[str, str]:
    """Return ``(type_key, source_field)``; ``("", "")`` when no reliable metadata exists."""
    for field in TYPE_KEY_FIELDS:
        value = str(spec.get(field) or "").strip()
        if value:
            return value, field
    return "", ""


def _runtime_specs(module: Any) -> list[dict[str, Any]]:
    specs = [dict(s) for s in (getattr(module, "GENERATOR_SPECS", None) or []) if isinstance(s, dict)]
    keys = [str(k) for k in (getattr(module, "GENERATOR_KEYS", None) or [])]
    if keys:
        allowed = set(keys)
        specs = [s for s in specs if _candidate_id(s) in allowed]
    return specs


def build_type_pool(specs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Group generator specs by practice type.

    Components without reliable type metadata become singleton types keyed by their
    component id and make the pool ``reliable=False``.
    """
    types: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    for spec in specs:
        cid = _candidate_id(spec)
        if not cid:
            continue
        type_key, source = resolve_type_key(spec)
        if not type_key:
            unresolved.append(cid)
            type_key, source = f"component:{cid}", "component_singleton"
        types.setdefault(type_key, []).append(
            {
                "component_id": cid,
                "generator_key": str(spec.get("generator_key") or cid),
                "source_kind": str(spec.get("source_kind") or ""),
                "textbook_example_id": spec.get("textbook_example_id"),
                "type_key_source": source,
            }
        )
    return {"types": types, "reliable": bool(types) and not unresolved, "unresolved_components": unresolved}


def load_section_pool(
    section: str,
    *,
    module: Any | None = None,
    specs: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if specs is None:
        if module is None:
            module = importlib.import_module(f"skills.{section}")
        specs = _runtime_specs(module)
    return build_type_pool(specs)


def get_practice_type_pool(
    section: str,
    *,
    module: Any | None = None,
    specs: Iterable[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """``{type_key: [candidate generators...]}`` for one section (runtime skill id)."""
    return load_section_pool(section, module=module, specs=specs)["types"]


def _type_keys(types: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(types)


def _signature(section: str, types: dict[str, list[dict[str, Any]]]) -> str:
    shape = [section, [[k, [c["component_id"] for c in types[k]]] for k in _type_keys(types)]]
    return hashlib.sha1(json.dumps(shape, ensure_ascii=False).encode("utf-8")).hexdigest()[:10]


def _uid_token(question_uid: str) -> str:
    return hashlib.sha1(str(question_uid).encode("utf-8")).hexdigest()[:8]


def new_state(section: str, types: dict[str, list[dict[str, Any]]], rng: random.Random | None = None) -> dict[str, Any]:
    rng = rng or random.Random()
    queue = list(range(len(types)))
    rng.shuffle(queue)
    return {
        "sig": _signature(section, types),
        "r": 1,
        "n": len(types),
        "q": queue,
        "st": _STATUS_CODE[STATUS_UNSEEN] * len(types),
        "sv": {},
        "p": [],
        "c": 0,
    }


def ensure_state(
    state: dict[str, Any] | None,
    section: str,
    types: dict[str, list[dict[str, Any]]],
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Reuse ``state`` for the same section/pool; otherwise start the section fresh."""
    if (
        isinstance(state, dict)
        and state.get("sig") == _signature(section, types)
        and not state.get("c")
        and len(str(state.get("st", ""))) == len(types)
    ):
        return state
    return new_state(section, types, rng)


def matches(state: dict[str, Any] | None, section: str, types: dict[str, list[dict[str, Any]]]) -> bool:
    return isinstance(state, dict) and state.get("sig") == _signature(section, types)


def type_status(state: dict[str, Any], types: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    codes = str(state.get("st", ""))
    return {k: _CODE_STATUS.get(codes[i:i + 1], STATUS_UNSEEN) for i, k in enumerate(_type_keys(types))}


def _set_status(state: dict[str, Any], idx: int, status: str) -> None:
    codes = list(str(state.get("st", "")))
    codes[idx] = _STATUS_CODE[status]
    state["st"] = "".join(codes)


def _pick_candidate(state: dict[str, Any], idx: int, candidates: list[dict[str, Any]], rng: random.Random) -> str:
    served_map = dict(state.get("sv") or {})
    served = [int(i) for i in served_map.get(str(idx), [])]
    fresh = [i for i in range(len(candidates)) if i not in served]
    if not fresh:
        last = served[-1] if served else -1
        fresh = [i for i in range(len(candidates)) if i != last] or list(range(len(candidates)))
        served = []
    picked = rng.choice(fresh)
    served.append(picked)
    served_map[str(idx)] = served
    state["sv"] = served_map
    return candidates[picked]["component_id"]


def next_pick(
    state: dict[str, Any],
    types: dict[str, list[dict[str, Any]]],
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    """Pop the next type from the current round and choose a candidate generator.

    When the round queue is exhausted, a new round is built from every type that is
    not yet ``passed`` (weak, or served but never answered).  Returns ``None`` once
    every type is passed.
    """
    rng = rng or random.Random()
    keys = _type_keys(types)
    codes = str(state.get("st", ""))
    passed = _STATUS_CODE[STATUS_PASSED]
    queue = [int(i) for i in state.get("q", []) if 0 <= int(i) < len(keys) and codes[int(i)] != passed]
    if not queue:
        remaining = [i for i in range(len(keys)) if codes[i] != passed]
        if not remaining:
            state["q"] = []
            state["c"] = 1
            return None
        rng.shuffle(remaining)
        queue = remaining
        state["r"] = int(state.get("r", 1)) + 1
    idx = queue.pop(0)
    state["q"] = queue
    type_key = keys[idx]
    component_id = _pick_candidate(state, idx, types[type_key], rng)
    return {"type_key": type_key, "component_id": component_id, "round": state["r"]}


def register_served_question(
    state: dict[str, Any],
    types: dict[str, list[dict[str, Any]]],
    question_uid: str,
    type_key: str,
) -> None:
    if not question_uid or type_key not in types:
        return
    idx = _type_keys(types).index(type_key)
    token = _uid_token(question_uid)
    pending = [p for p in (state.get("p") or []) if p and p[0] != token]
    pending.append([token, idx])
    state["p"] = pending[-_MAX_PENDING:]


def record_result(
    state: dict[str, Any],
    types: dict[str, list[dict[str, Any]]],
    question_uid: str,
    is_correct: bool,
) -> str | None:
    """Apply the first verdict of a served question; re-submits of the same uid are ignored."""
    token = _uid_token(question_uid or "")
    pending = list(state.get("p") or [])
    hit = next((p for p in pending if p and p[0] == token), None)
    if hit is None:
        return None
    state["p"] = [p for p in pending if p is not hit]
    keys = _type_keys(types)
    idx = int(hit[1])
    if not 0 <= idx < len(keys):
        return None
    _set_status(state, idx, STATUS_PASSED if is_correct else STATUS_WEAK)
    if set(str(state.get("st", ""))) == {_STATUS_CODE[STATUS_PASSED]}:
        state["c"] = 1
        state["q"] = []
    return keys[idx]


def apply_statuses(state: dict[str, Any], types: dict[str, list[dict[str, Any]]], statuses: dict[str, str]) -> None:
    """Overwrite type statuses from an authoritative source (e.g. persisted attempts)."""
    keys = _type_keys(types)
    state["st"] = "".join(_STATUS_CODE[statuses.get(k, STATUS_UNSEEN)] for k in keys)
    passed = _STATUS_CODE[STATUS_PASSED]
    state["q"] = [int(i) for i in state.get("q", []) if 0 <= int(i) < len(keys) and state["st"][int(i)] != passed]
    state["c"] = 1 if keys and set(state["st"]) == {passed} else 0
    if state["c"]:
        state["q"] = []


def restore_state(
    section: str,
    types: dict[str, list[dict[str, Any]]],
    statuses: dict[str, str],
    seed: str,
) -> dict[str, Any]:
    """Rebuild a section state from persisted type statuses: unseen types first, then weak ones."""
    rng = random.Random(seed)
    state = new_state(section, types, rng)
    keys = _type_keys(types)
    unseen = [i for i, k in enumerate(keys) if statuses.get(k, STATUS_UNSEEN) == STATUS_UNSEEN]
    weak = [i for i, k in enumerate(keys) if statuses.get(k) == STATUS_WEAK]
    rng.shuffle(unseen)
    rng.shuffle(weak)
    state["q"] = unseen + weak
    apply_statuses(state, types, statuses)
    if weak and not unseen:
        state["r"] = 2
    return state


def summarize(state: dict[str, Any], types: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    status = type_status(state, types)
    counts = {s: sum(1 for v in status.values() if v == s) for s in (STATUS_UNSEEN, STATUS_PASSED, STATUS_WEAK)}
    return {
        "round": int(state.get("r", 1)),
        "total_types": len(status),
        "first_round_size": int(state.get("n", len(status))),
        "status_counts": counts,
        "weak_types": sorted(k for k, v in status.items() if v == STATUS_WEAK),
        "section_completed": bool(state.get("c")),
    }


def _leading_numbers(text: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", str(text or ""))[:3])


def resolve_next_section(
    section: str,
    curriculum_rows: Iterable[Any],
    *,
    is_available: Callable[[str], bool] | None = None,
) -> str:
    """Next section skill id within the same chapter, in textbook order.

    ``curriculum_rows`` are SkillCurriculum-like objects (curriculum, volume, chapter,
    section, display_order, skill_id).  Returns ``""`` after the chapter's last
    available section; progression never crosses into another chapter.
    """
    rows = list(curriculum_rows)
    anchor = next((r for r in rows if r.skill_id == section), None)
    if anchor is None:
        return ""
    same_chapter = [
        r for r in rows
        if r.curriculum == anchor.curriculum and r.volume == anchor.volume and r.chapter == anchor.chapter
    ]
    same_chapter.sort(
        key=lambda r: (
            _leading_numbers(r.section),
            int(r.display_order or 0),
            str(r.skill_id),
        )
    )
    ordered: list[str] = []
    for r in same_chapter:
        if r.skill_id not in ordered:
            ordered.append(r.skill_id)
    for skill_id in ordered[ordered.index(section) + 1:]:
        if is_available is None or is_available(skill_id):
            return skill_id
    return ""


CHAPTER_SESSION_KEY = "practice_chapter_progress"


def chapter_key(curriculum: str, volume: str, chapter: str) -> str:
    raw = json.dumps([curriculum or "", volume or "", chapter or ""], ensure_ascii=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def section_token(section: str) -> str:
    return hashlib.sha1(str(section).encode("utf-8")).hexdigest()[:8]


def ensure_chapter_progress(progress: dict[str, Any] | None, key: str) -> dict[str, Any]:
    """Counters for the current chapter run; a new chapter or a finished run starts fresh."""
    if isinstance(progress, dict) and progress.get("ch") == key and not progress.get("done"):
        return progress
    return {"ch": key, "a": 0, "k": 0, "t": 0, "s": 0, "done": 0, "last": ""}


def record_chapter_verdict(
    progress: dict[str, Any],
    is_correct: bool,
    *,
    section_completed: bool,
) -> None:
    progress["a"] = int(progress.get("a", 0)) + 1
    if is_correct:
        progress["k"] = int(progress.get("k", 0)) + 1
        progress["t"] = int(progress.get("t", 0)) + 1
    if section_completed:
        progress["s"] = int(progress.get("s", 0)) + 1


def mark_chapter_completed(progress: dict[str, Any], section: str) -> None:
    progress["done"] = 1
    progress["last"] = section_token(section)


def chapter_summary(progress: dict[str, Any]) -> dict[str, Any]:
    answered = int(progress.get("a", 0))
    correct = int(progress.get("k", 0))
    return {
        "total_answered": answered,
        "correct": correct,
        "wrong": answered - correct,
        "accuracy": round(correct * 100.0 / answered, 1) if answered else 0.0,
        "types_completed": int(progress.get("t", 0)),
        "sections_completed": int(progress.get("s", 0)),
        "chapter_completed": bool(progress.get("done")),
    }
