"""B3 Chapter 2 live presentation audit.

Payload checks run here. Interactive control counts are filled from a real
DOM render of ``scratch/b3_ch2_live_presentation_fixture.html``.
"""

from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent_skills_v3"
REPORT_JSON = ROOT / "reports" / "b3_ch2_live_presentation_audit.json"
REPORT_MD = ROOT / "reports" / "b3_ch2_live_presentation_audit.md"
FIXTURE_HTML = ROOT / "scratch" / "b3_ch2_live_presentation_fixture.html"
DOM_JSON = ROOT / "scratch" / "b3_ch2_live_dom_counts.json"

BAD_LABELS = ("第一個未知數", "第二個未知數", "第一個數量", "第二個數量")
FORMAT_PATTERNS = (
    ("double_delimiter", re.compile(r"\$\s*\\[\(\[]")),
    ("missing_operator", re.compile(r"x\^\{?2\}?(?!\s*[+\-=])\s+\d")),
    ("ugly_signed_paren", re.compile(r"\+\s*\(\s*-")),
    ("plus_minus", re.compile(r"\+\-|\-\+")),
    ("raw_python", re.compile(r"Fraction\(|\*\*|None|null")),
    ("double_minus", re.compile(r"(?<![\\a-zA-Z])--")),
)


def _load_generate(source_id: int):
    matches = list(AGENT.glob(f"**/src_{source_id}/generate.py"))
    if len(matches) != 1:
        raise FileNotFoundError(f"generate.py for {source_id}: {matches}")
    spec = importlib.util.spec_from_file_location(f"ch2_src_{source_id}", matches[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _skill_modules() -> dict[str, Any]:
    out = {}
    for path in sorted((ROOT / "skills").glob("vh_數學B3_SubSection_2_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        out[module.SKILL_ID] = module
    return out


def _truthy_check(result: Any) -> bool:
    if isinstance(result, bool):
        return result
    if isinstance(result, dict):
        if "correct" in result:
            return bool(result["correct"])
        if "is_correct" in result:
            return bool(result["is_correct"])
    return bool(result)


def _logical_answer_count(payload: dict[str, Any]) -> int:
    answer_type = str(payload.get("answer_type") or "")
    if answer_type == "single_choice":
        return 1
    parts = ((payload.get("answer_contract") or {}).get("parts") or [])
    if parts:
        return len(parts)
    return 1


def _expected_visible_controls(payload: dict[str, Any]) -> int:
    answer_type = str(payload.get("answer_type") or "")
    if answer_type == "single_choice":
        return len(payload.get("choices") or [])
    return _logical_answer_count(payload)


def _format_hits(text: str) -> list[str]:
    hits = []
    for name, pattern in FORMAT_PATTERNS:
        if pattern.search(text or ""):
            hits.append(name)
    opens = (text or "").count("{")
    closes = (text or "").count("}")
    if opens != closes:
        hits.append("unmatched_braces")
    return hits


def _choice_delimiter_fail(choices: list[dict[str, Any]]) -> bool:
    for choice in choices:
        text = str(choice.get("text") or "")
        if r"\(" in text or r"\)" in text or r"\[" in text:
            return True
        if text.count("$") >= 2 and r"\(" in text:
            return True
    return False


def _semantic_label_fail(labels: list[str]) -> bool:
    for label in labels:
        if any(token in label for token in BAD_LABELS):
            return True
        # Repeating the stem equation as the answer label.
        if "=" in label and "x" in label and len(label) > 12:
            return True
        if any(op in label for op in (">=", "<=", ">", "<")) and "x" in label and len(label) > 16:
            return True
    return False


def classify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    parts = ((payload.get("answer_contract") or {}).get("parts") or [])
    labels = [str(part.get("display_label") or part.get("label") or "") for part in parts]
    choices = list(payload.get("choices") or [])
    question = str(payload.get("question_text") or "")
    format_hits = _format_hits(question)
    for choice in choices:
        format_hits.extend(_format_hits(str(choice.get("text") or "")))
    answer_type = str(payload.get("answer_type") or "")
    statuses = []
    if _choice_delimiter_fail(choices) or any(hit == "double_delimiter" for hit in format_hits):
        statuses.append("LATEX_RENDER_FAIL")
        if answer_type == "single_choice":
            statuses.append("MCQ_RENDER_FAIL")
    if any(hit != "double_delimiter" for hit in format_hits):
        statuses.append("QUESTION_FORMAT_FAIL")
    if _semantic_label_fail(labels):
        statuses.append("SEMANTIC_LABEL_FAIL")
    logical = _logical_answer_count(payload)
    if answer_type == "single_choice":
        groups = 1 if choices else 0
    else:
        groups = logical
    return {
        "source_id": int(payload.get("textbook_example_id") or 0),
        "skill_id": payload.get("skill_id"),
        "family": payload.get("problem_type_id") or payload.get("domain_operation"),
        "answer_type": answer_type,
        "logical_answer_count": logical,
        "api_part_count": len(parts) if parts else (0 if answer_type == "single_choice" else 1),
        "field_group_count": groups,
        "expected_visible_controls": _expected_visible_controls(payload),
        "labels": labels,
        "presentation_type": answer_type or "short_answer",
        "question_text": question,
        "choices": [{"label": c.get("label"), "text": c.get("text")} for c in choices],
        "format_hits": sorted(set(format_hits)),
        "status": statuses[0] if statuses else "PASS",
        "statuses": statuses,
    }


def _student_answer(payload: dict[str, Any]) -> Any:
    if str(payload.get("answer_type") or "") == "single_choice":
        return payload.get("correct_answer") or payload.get("correct_label")
    parts = ((payload.get("answer_contract") or {}).get("parts") or [])
    if parts:
        return {str(part["key"]): part.get("expected_answer") for part in parts}
    contract = payload.get("answer_contract") or {}
    return contract.get("semantic_answer") or payload.get("correct_answer")


def _wrong_answer(payload: dict[str, Any], correct: Any) -> Any:
    if str(payload.get("answer_type") or "") == "single_choice":
        label = str(correct or "A")
        return "B" if label != "B" else "C"
    if isinstance(correct, dict) and correct:
        wrong = dict(correct)
        first = next(iter(wrong))
        wrong[first] = "999999"
        return wrong
    return "999999"


def iter_source_ids() -> list[int]:
    from core.domain.equation_solving_domain import SOURCE_SPECS

    return sorted(SOURCE_SPECS)


def build_rows(seed: int = 3) -> list[dict[str, Any]]:
    rows = []
    for source_id in iter_source_ids():
        module = _load_generate(source_id)
        payload = module.generate(level=1, seed=seed)
        row = classify_payload(payload)
        row["source_id"] = source_id
        if not row.get("skill_id"):
            row["skill_id"] = Path(module.__file__).parents[2].name
        row["payload"] = {
            "answer_type": payload.get("answer_type"),
            "answer_contract": payload.get("answer_contract"),
            "choices": payload.get("choices"),
            "question_text": payload.get("question_text"),
            "ui_contract": (payload.get("answer_contract") or {}).get("ui_contract"),
        }
        rows.append(row)
    return rows


def sample_skills(per_skill: int = 30) -> dict[str, Any]:
    skills = _skill_modules()
    summary = {}
    for skill_id, module in skills.items():
        counters = Counter()
        keys = list(module.GENERATOR_KEYS)
        for index in range(per_skill):
            component = keys[index % len(keys)]
            payload = module.generate(level=1, seed=1000 + index, component_id=component)
            row = classify_payload(payload)
            if row["status"] != "PASS":
                counters[row["status"].lower()] += 1
            if "LATEX_RENDER_FAIL" in row["statuses"] or "MCQ_RENDER_FAIL" in row["statuses"]:
                counters["latex_failure"] += 1
            if "QUESTION_FORMAT_FAIL" in row["statuses"]:
                counters["question_format_failure"] += 1
            if "SEMANTIC_LABEL_FAIL" in row["statuses"]:
                counters["label_only"] += 1
            correct = _student_answer(payload)
            try:
                good = _truthy_check(module.check(correct, correct, payload))
                bad = _truthy_check(module.check(_wrong_answer(payload, correct), correct, payload))
            except Exception:
                good, bad = False, True
            if not good or bad:
                counters["checker_failure"] += 1
            if row["logical_answer_count"] <= 0:
                counters["answer_schema_failure"] += 1
        summary[skill_id] = {
            "samples": per_skill,
            "missing_input": counters["missing_input"],
            "hidden_input": counters["hidden_input"],
            "label_only": counters["label_only"],
            "latex_failure": counters["latex_failure"],
            "question_format_failure": counters["question_format_failure"],
            "answer_schema_failure": counters["answer_schema_failure"],
            "checker_failure": counters["checker_failure"],
        }
    return summary


def write_fixture(rows: list[dict[str, Any]]) -> None:
    cases = []
    for row in rows:
        cases.append({
            "source_id": row["source_id"],
            "answer_type": row["answer_type"],
            "expected_visible_controls": row["expected_visible_controls"],
            "logical_answer_count": row["logical_answer_count"],
            "payload": row["payload"],
        })
    FIXTURE_HTML.parent.mkdir(parents=True, exist_ok=True)
    payload_json = json.dumps(cases, ensure_ascii=False)
    FIXTURE_HTML.write_text(
        """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <title>B3 Ch2 live presentation DOM</title>
  <link rel="stylesheet" href="/static/css/practice_math_typography.css" />
  <style>
    body { font-family: "Noto Sans TC", sans-serif; margin: 16px; background: #fff; color: #111; }
    section { border-bottom: 1px solid #e2e8f0; margin-bottom: 12px; padding-bottom: 8px; max-width: 720px; }
    .practice-math-surface { line-height: 1.75; }
    .multi-part-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; max-width: 100%; }
    .multi-part-row label { flex: 1 1 auto; min-width: 0; max-width: calc(100% - 9rem); overflow: hidden; font-weight: 600; }
    .multi-part-input, #single-answer { position: relative; z-index: 2; flex: 0 0 8rem; width: 8rem; min-width: 8rem; min-height: 2.25rem; background: #fff; border: 1px solid #334155; }
    .choice-option { display: block; margin: 4px 0; min-height: 2rem; }
    .subquestions-container { display: block; }
  </style>
  <script>
    window.MathJax = { tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }, svg: { fontCache: 'global' } };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <script src="/static/js/multipart_field_renderer.js"></script>
</head>
<body>
  <div id="root"></div>
  <pre id="audit"></pre>
  <script>
    const cases = __CASES__;
    const root = document.getElementById('root');
    function renderChoice(parent, choices) {
      choices.forEach((choice, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'choice-option';
        const label = String.fromCharCode(65 + index);
        button.innerHTML = '<span class="choice-label">(' + label + ')</span><span class="choice-text">' + String(choice.text || '') + '</span>';
        parent.appendChild(button);
      });
    }
    cases.forEach((item) => {
      const section = document.createElement('section');
      section.id = 'src-' + item.source_id;
      section.className = 'practice-math-surface';
      const stem = document.createElement('div');
      stem.className = 'stem';
      stem.textContent = (item.payload && item.payload.question_text) || '';
      const box = document.createElement('div');
      box.className = 'subquestions-container practice-math-surface multi-part-list';
      const answerType = item.answer_type;
      if (answerType === 'single_choice') {
        renderChoice(box, (item.payload && item.payload.choices) || []);
      } else if (((item.payload.answer_contract || {}).parts || []).length) {
        window.MultipartFieldRenderer.render(box, item.payload);
      } else {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'single-answer';
        input.className = 'multi-part-input';
        box.appendChild(input);
      }
      section.appendChild(stem);
      section.appendChild(box);
      root.appendChild(section);
    });
    function collect() {
      const rows = cases.map((item) => {
        const section = document.getElementById('src-' + item.source_id);
        const box = section.querySelector('.subquestions-container');
        const counts = window.MultipartFieldRenderer.countControls(box);
        const choices = Array.from(box.querySelectorAll('.choice-option'));
        const choiceText = choices.map((node) => node.textContent || '').join(' ');
        const rawDelimiter = choiceText.indexOf('\\\\(') >= 0 || choiceText.indexOf('\\\\)') >= 0 || choiceText.indexOf('\\\\frac') >= 0;
        return {
          source_id: item.source_id,
          input_element_count: counts.input_element_count,
          visible_input_element_count: counts.visible_input_element_count,
          choice_button_count: choices.length,
          choice_text_has_raw_delimiter: item.answer_type === 'single_choice' ? rawDelimiter : false,
        };
      });
      const blob = JSON.stringify(rows);
      document.getElementById('audit').textContent = blob;
      window.__DOM_AUDIT = rows;
    }
    const ready = (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) || Promise.resolve();
    ready.then(() => {
      const nodes = Array.from(document.querySelectorAll('.practice-math-surface'));
      const typeset = (window.MathJax && window.MathJax.typesetPromise) ? window.MathJax.typesetPromise(nodes) : Promise.resolve();
      return typeset;
    }).then(() => collect()).catch(() => collect());
  </script>
</body>
</html>
""".replace("__CASES__", payload_json),
        encoding="utf-8",
    )


def merge_dom(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not DOM_JSON.exists():
        return rows
    counts = {int(item["source_id"]): item for item in json.loads(DOM_JSON.read_text(encoding="utf-8"))}
    for row in rows:
        found = counts.get(int(row["source_id"]))
        if not found:
            row["visible_interactive_control_count"] = None
            if row["status"] == "PASS":
                row["status"] = "MISSING_INPUT"
            continue
        visible = int(found.get("visible_input_element_count") or 0)
        choices = int(found.get("choice_button_count") or 0)
        if row["answer_type"] == "single_choice":
            visible_controls = choices
        else:
            visible_controls = visible
        row["visible_interactive_control_count"] = visible_controls
        row["dom_input_element_count"] = int(found.get("input_element_count") or 0)
        row["dom_visible_input_element_count"] = visible
        row["dom_choice_button_count"] = choices
        if found.get("choice_text_has_raw_delimiter"):
            row["statuses"] = list(row.get("statuses") or []) + ["LATEX_RENDER_FAIL", "MCQ_RENDER_FAIL"]
        expected = int(row["expected_visible_controls"])
        if visible_controls <= 0 and expected > 0:
            row["statuses"] = ["MISSING_INPUT"] + list(row.get("statuses") or [])
        elif visible_controls < expected:
            created = int(found.get("input_element_count") or 0) + choices
            kind = "HIDDEN_INPUT" if created >= expected else "MISSING_INPUT"
            row["statuses"] = [kind] + list(row.get("statuses") or [])
        elif row["answer_type"] != "single_choice" and visible > 0 and int(found.get("input_element_count") or 0) == 0:
            row["statuses"] = ["LABEL_ONLY"] + list(row.get("statuses") or [])
        deduped = []
        for status in row.get("statuses") or []:
            if status not in deduped:
                deduped.append(status)
        row["statuses"] = deduped
        row["status"] = deduped[0] if deduped else "PASS"
    return rows


def write_reports(rows: list[dict[str, Any]], sampling: dict[str, Any]) -> None:
    public = []
    for row in rows:
        public.append({key: value for key, value in row.items() if key != "payload"})
    passed = sum(1 for row in public if row["status"] == "PASS")
    report = {
        "package_status": "PENDING_LIVE_PRESENTATION_ACCEPTANCE",
        "mathematical_coverage": "68/68",
        "keys": len(public),
        "pass": passed,
        "fail": len(public) - passed,
        "dom_counts_present": DOM_JSON.exists(),
        "rows": public,
        "sampling": sampling,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# B3 Ch2 Live Presentation Audit",
        "",
        f"- package_status: PENDING_LIVE_PRESENTATION_ACCEPTANCE",
        f"- keys: {len(public)}",
        f"- pass: {passed}",
        f"- fail: {len(public) - passed}",
        f"- dom_counts_present: {DOM_JSON.exists()}",
        "",
        "| source_id | skill | answer_type | logical | visible controls | status | labels |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in public:
        labels = "、".join(row.get("labels") or [])
        lines.append(
            f"| {row['source_id']} | {row['skill_id']} | {row['answer_type']} | {row['logical_answer_count']} | {row.get('visible_interactive_control_count')} | {row['status']} | {labels} |"
        )
    lines.extend(["", "## Sampling", ""])
    for skill_id, counters in sampling.items():
        lines.append(f"- `{skill_id}`: {json.dumps(counters, ensure_ascii=False)}")
    failed = [row for row in public if row["status"] != "PASS"]
    lines.extend(["", "## Failed", ""])
    if not failed:
        lines.append("無")
    else:
        for row in failed:
            lines.append(f"- {row['source_id']} {row['status']} {row.get('format_hits')}")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_fixture(rows)
    sampling = sample_skills(30)
    rows = merge_dom(rows)
    write_reports(rows, sampling)
    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"rows={len(rows)} fail={len(failed)} dom={DOM_JSON.exists()}")
    for row in failed[:20]:
        print(row["source_id"], row["status"], row.get("format_hits"), row.get("labels"))


if __name__ == "__main__":
    main()
