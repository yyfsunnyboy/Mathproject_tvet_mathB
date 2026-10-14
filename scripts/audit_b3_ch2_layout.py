"""B3 Chapter 2 answer-field layout audit.

Payload inventory is written here. Alignment, width, and mobile overflow
come from a browser render of the shared practice answer layout.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "b3_ch2_layout_audit.json"
REPORT_MD = ROOT / "reports" / "b3_ch2_layout_audit.md"
FIXTURE_HTML = ROOT / "scratch" / "b3_ch2_layout_fixture.html"
DOM_JSON = ROOT / "scratch" / "b3_ch2_layout_dom.json"


def _live_module():
    spec = importlib.util.spec_from_file_location(
        "b3_ch2_live_presentation",
        ROOT / "scripts" / "audit_b3_ch2_live_presentation.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _layout_type(answer_type: str, logical: int) -> str:
    if answer_type == "single_choice":
        return "mcq"
    if logical >= 4:
        return "multipart_4plus"
    if logical == 3:
        return "multipart_3"
    if logical == 2:
        return "multipart_2"
    return "single"


def _label_duplicated(labels: list[str]) -> bool:
    for label in labels:
        if "=" in label and "x" in label and len(label) > 12:
            return True
        if any(token in label for token in ("第一個未知數", "第二個未知數", "第一個數量")):
            return True
    return False


def build_inventory() -> list[dict]:
    live = _live_module()
    rows = []
    for source_id in live.iter_source_ids():
        module = live._load_generate(source_id)
        payload = module.generate(level=1, seed=3)
        classified = live.classify_payload(payload)
        classified["source_id"] = source_id
        if not classified.get("skill_id"):
            classified["skill_id"] = Path(module.__file__).parents[2].name
        logical = classified["logical_answer_count"]
        answer_type = classified["answer_type"]
        parts = ((payload.get("answer_contract") or {}).get("parts") or [])
        rows.append({
            "source_id": source_id,
            "skill_id": classified["skill_id"],
            "family": classified["family"],
            "answer_type": answer_type,
            "question_type": payload.get("problem_type_id") or classified["family"],
            "logical_answer_count": logical,
            "layout_type": _layout_type(answer_type, logical),
            "labels": classified["labels"],
            "input_type": "choice" if answer_type == "single_choice" else "text",
            "css_class": "choice-list" if answer_type == "single_choice" else "multi-part-row",
            "label_duplicated": _label_duplicated(classified["labels"]),
            "payload": {
                "answer_type": answer_type,
                "answer_contract": payload.get("answer_contract"),
                "choices": payload.get("choices"),
                "question_text": payload.get("question_text"),
                "checker": payload.get("checker"),
                "correct_answer": payload.get("correct_answer"),
                "display_answer": payload.get("display_answer"),
            },
            "part_checkers": [part.get("checker") for part in parts],
        })
    return rows


def write_fixture(rows: list[dict]) -> None:
    cases = []
    for row in rows:
        cases.append({
            "source_id": row["source_id"],
            "layout_type": row["layout_type"],
            "answer_type": row["answer_type"],
            "payload": row["payload"],
        })
    FIXTURE_HTML.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_HTML.write_text(
        """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <title>B3 Ch2 layout</title>
  <link rel="stylesheet" href="/static/css/practice_answer_layout.css" />
  <style>
    body { margin: 16px; background: #fff; color: #111; font-family: "Noto Sans TC", sans-serif; }
    section { width: 720px; max-width: 100%; border-bottom: 1px solid #e2e8f0; margin-bottom: 16px; padding-bottom: 8px; }
    .choice-list { display: flex; flex-direction: column; gap: 8px; align-items: stretch; }
    .choice-option { display: flex; justify-content: flex-start; min-height: 38px; padding: 8px 12px; border: 1px solid #d8e2dc; border-radius: 10px; background: #fff; }
  </style>
  <script src="/static/js/multipart_field_renderer.js"></script>
</head>
<body>
  <div id="root"></div>
  <pre id="audit"></pre>
  <script>
    const cases = __CASES__;
    const root = document.getElementById('root');
    const bands = {
      numeric: [140, 180],
      fraction: [160, 200],
      expression: [240, 320],
      equation: [280, 360],
      inequality: [280, 360],
      radical: [220, 300],
    };
    cases.forEach((item) => {
      const section = document.createElement('section');
      section.id = 'src-' + item.source_id;
      section.className = 'practice-answer-block';
      if (item.answer_type === 'single_choice') {
        const list = document.createElement('div');
        list.className = 'choice-list';
        (item.payload.choices || []).forEach((choice, index) => {
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'choice-option';
          button.innerHTML = '<span>(' + String.fromCharCode(65 + index) + ')</span><span class="choice-text">' + String(choice.text || '') + '</span>';
          list.appendChild(button);
        });
        section.appendChild(list);
      } else if (((item.payload.answer_contract || {}).parts || []).length) {
        const box = document.createElement('div');
        box.className = 'subquestions-container';
        window.MultipartFieldRenderer.render(box, item.payload);
        section.appendChild(box);
      } else {
        const group = document.createElement('div');
        group.className = 'input-group';
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'answer-input';
        window.MultipartFieldRenderer.applyControlKind(input, window.MultipartFieldRenderer.controlKindFromPayload(item.payload));
        group.appendChild(input);
        section.appendChild(group);
      }
      root.appendChild(section);
    });
    function measure(mobile) {
      return cases.map((item) => {
        const section = document.getElementById('src-' + item.source_id);
        const overflow = section.scrollWidth > section.clientWidth + 2;
        if (item.answer_type === 'single_choice') {
          const buttons = Array.from(section.querySelectorAll('.choice-option'));
          const text = buttons.map((node) => node.textContent || '').join(' ');
          const inputs = section.querySelectorAll('input, select, textarea');
          return {
            source_id: item.source_id,
            mobile: mobile,
            choice_count: buttons.length,
            raw_delimiter: text.indexOf('\\\\(') >= 0 || text.indexOf('\\\\)') >= 0,
            text_input_count: inputs.length,
            overflow: overflow,
          };
        }
        const controls = Array.from(section.querySelectorAll('input, select, textarea'));
        const details = controls.map((node) => {
          const row = node.closest('.multi-part-row') || node.parentElement;
          const label = row ? row.querySelector('label') : null;
          const rowStyle = row ? getComputedStyle(row) : null;
          const nodeRect = node.getBoundingClientRect();
          const sectionRect = section.getBoundingClientRect();
          const labelRect = label ? label.getBoundingClientRect() : null;
          const kind = (node.className.match(/control-[a-z]+/) || ['control-expression'])[0].replace('control-', '');
          const band = bands[kind] || bands.expression;
          const gap = labelRect ? nodeRect.left - labelRect.right : nodeRect.left - sectionRect.left;
          return {
            kind: kind,
            width: Math.round(nodeRect.width),
            justify: rowStyle ? rowStyle.justifyContent : '',
            gap: Math.round(gap),
            right_slack: Math.round(sectionRect.right - nodeRect.right),
            band: band,
          };
        });
        return { source_id: item.source_id, mobile: mobile, overflow: overflow, controls: details };
      });
    }
    window.__LAYOUT_DESKTOP = measure(false);
    document.getElementById('audit').textContent = JSON.stringify(window.__LAYOUT_DESKTOP);
  </script>
</body>
</html>
""".replace("__CASES__", json.dumps(cases, ensure_ascii=False)),
        encoding="utf-8",
    )


def _status_for(row: dict, desktop: dict | None, mobile: dict | None) -> str:
    if row["label_duplicated"]:
        return "LABEL_DUPLICATED"
    if not desktop:
        return "MISALIGNED"
    if row["layout_type"] == "mcq":
        if desktop.get("choice_count") != 4 or desktop.get("raw_delimiter") or desktop.get("text_input_count"):
            return "MCQ_LAYOUT_FAIL"
        if (mobile or {}).get("overflow") or desktop.get("overflow"):
            return "MOBILE_OVERFLOW"
        return "PASS"
    controls = desktop.get("controls") or []
    if len(controls) != row["logical_answer_count"]:
        return "MISALIGNED"
    for control in controls:
        if control.get("justify") not in {"flex-start", "start", "left", "normal"}:
            return "MISALIGNED"
        if control.get("gap", 99) > 28 or control.get("gap", -99) < -4:
            return "MISALIGNED"
        if control.get("right_slack", 0) < 24 and control.get("width", 0) < 300:
            return "MISALIGNED"
        low, high = control.get("band") or [140, 360]
        width = control.get("width") or 0
        if width > high + 8:
            return "TOO_WIDE"
        if width < low - 8:
            return "TOO_NARROW"
    if (mobile or {}).get("overflow") or desktop.get("overflow"):
        return "MOBILE_OVERFLOW"
    return "PASS"


def merge_dom(rows: list[dict]) -> list[dict]:
    if not DOM_JSON.exists():
        for row in rows:
            row["status"] = "MISALIGNED"
        return rows
    blob = json.loads(DOM_JSON.read_text(encoding="utf-8"))
    desktop = {int(item["source_id"]): item for item in blob.get("desktop") or []}
    mobile = {int(item["source_id"]): item for item in blob.get("mobile") or []}
    for row in rows:
        found = desktop.get(row["source_id"])
        phone = mobile.get(row["source_id"])
        row["status"] = _status_for(row, found, phone)
        if found and found.get("controls"):
            row["control_kind"] = found["controls"][0]["kind"]
            row["control_width"] = found["controls"][0]["width"]
            row["label_alignment"] = "left"
            row["control_alignment"] = "left" if row["status"] == "PASS" else "check"
        elif row["layout_type"] == "mcq":
            row["control_kind"] = "choice"
            row["control_width"] = None
            row["label_alignment"] = "choice"
            row["control_alignment"] = "choice"
        row["mobile_wrap"] = "column" if phone else "unknown"
    return rows


def write_reports(rows: list[dict]) -> None:
    public = []
    for row in rows:
        public.append({key: value for key, value in row.items() if key != "payload"})
    passed = sum(1 for row in public if row.get("status") == "PASS")
    inventory = {}
    for row in public:
        inventory[row["layout_type"]] = inventory.get(row["layout_type"], 0) + 1
    report = {
        "keys": len(public),
        "pass": passed,
        "fail": len(public) - passed,
        "inventory": inventory,
        "dom_present": DOM_JSON.exists(),
        "rows": public,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# B3 Ch2 Layout Audit",
        "",
        f"- keys: {len(public)}",
        f"- pass: {passed}",
        f"- fail: {len(public) - passed}",
        f"- inventory: {json.dumps(inventory, ensure_ascii=False)}",
        "",
        "| source_id | skill | layout | logical | kind | width | status | labels |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in public:
        labels = "、".join(row.get("labels") or [])
        lines.append(
            f"| {row['source_id']} | {row['skill_id']} | {row['layout_type']} | {row['logical_answer_count']} | {row.get('control_kind')} | {row.get('control_width')} | {row.get('status')} | {labels} |"
        )
    failed = [row for row in public if row.get("status") != "PASS"]
    lines.extend(["", "## Failed", ""])
    lines.append("無" if not failed else "")
    for row in failed:
        lines.append(f"- {row['source_id']} {row.get('status')} {row.get('labels')}")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_inventory()
    write_fixture(rows)
    rows = merge_dom(rows)
    write_reports(rows)
    failed = [row for row in rows if row.get("status") != "PASS"]
    print(f"rows={len(rows)} fail={len(failed)} dom={DOM_JSON.exists()}")
    for row in failed[:15]:
        print(row["source_id"], row.get("status"), row.get("layout_type"), row.get("labels"))


if __name__ == "__main__":
    main()
