from __future__ import annotations

import random
from typing import Any


def validate_choices_unique(choices: list[str]) -> bool:
    return len(choices) == len(set(choices))


def validate_answer_in_choices(answer: str, choices: list[str]) -> bool:
    return answer in choices


def build_choice_payload(correct_text: str, distractors: list[str], labels: tuple[str, ...] = ("A", "B", "C", "D")) -> dict[str, Any]:
    choices = [correct_text] + list(distractors)
    if len(choices) != len(labels):
        raise ValueError("choices and labels length mismatch")
    if not validate_choices_unique(choices):
        raise ValueError("choices must be unique")
    if not validate_answer_in_choices(correct_text, choices):
        raise ValueError("correct answer must exist in choices")
    labeled = [{"label": labels[i], "text": choices[i]} for i in range(len(labels))]
    answer_label = labels[choices.index(correct_text)]
    return {"choices": labeled, "answer_label": answer_label}


def build_shuffled_choice_payload(
    correct_text: str,
    distractors: list[str],
    seed: int | None = None,
    labels: tuple[str, ...] = ("A", "B", "C", "D"),
) -> dict[str, Any]:
    choices = [str(correct_text)] + [str(x) for x in distractors]
    if len(choices) != len(labels):
        raise ValueError("choices and labels length mismatch")
    if not validate_choices_unique(choices):
        raise ValueError("choices must be unique")
    rng = random.Random(seed)
    rng.shuffle(choices)
    answer_label = labels[choices.index(str(correct_text))]
    return {
        "choices": [{"label": labels[i], "text": choices[i]} for i in range(len(labels))],
        "answer": answer_label,
        "correct_answer": answer_label,
        "correct_text": str(correct_text),
    }


def repair_choice_payload(payload: dict[str, Any], seed: int | None = None) -> dict[str, Any]:
    labels = ("A", "B", "C", "D")
    raw_choices = list(payload.get("choices") or [])
    if not raw_choices:
        raise ValueError("choices_missing")
    choice_texts: list[str] = []
    for ch in raw_choices:
        if isinstance(ch, dict):
            text = str(ch.get("text", "")).strip()
        else:
            text = str(ch).strip()
        if text:
            choice_texts.append(text)
    if not choice_texts:
        raise ValueError("choices_text_missing")

    correct_text = str(payload.get("correct_text", "")).strip()
    answer = str(payload.get("answer", "")).strip()
    correct_answer = str(payload.get("correct_answer", "")).strip()
    by_label = {labels[i]: choice_texts[i] for i in range(min(len(labels), len(choice_texts)))}

    if not correct_text:
        for token in (correct_answer, answer):
            up = token.upper().strip("()[] .")
            if up in by_label:
                correct_text = by_label[up]
                break
        if not correct_text:
            for token in (correct_answer, answer):
                if token in choice_texts:
                    correct_text = token
                    break
    if not correct_text:
        raise ValueError("correct_text_unresolved")
    if correct_text not in choice_texts:
        raise ValueError("choice_correct_answer_not_in_choices")

    deduped: list[str] = []
    seen: set[str] = set()
    for text in choice_texts:
        if text not in seen:
            deduped.append(text)
            seen.add(text)
    distractors = [x for x in deduped if x != correct_text]
    if len(distractors) < 3:
        raise ValueError("duplicate_choices_unrepairable")
    built = build_shuffled_choice_payload(correct_text, distractors[:3], seed=seed, labels=labels)
    payload["choices"] = [item["text"] for item in built["choices"]]
    payload["answer"] = built["answer"]
    payload["correct_answer"] = built["correct_answer"]
    payload["correct_text"] = built["correct_text"]
    return payload
