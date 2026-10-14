# -*- coding: utf-8 -*-
"""Shared practice answer strip: student-facing multipart labels, internal keys,
field order, and the single left-aligned strip layout for fields + submit."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "static" / "js" / "multipart_field_renderer.js"
FEEDBACK = ROOT / "static" / "js" / "correct_answer_feedback.js"
LAYOUT_CSS = ROOT / "static" / "css" / "practice_answer_layout.css"
INDEX = ROOT / "templates" / "index.html"

_DOM_SHIM = r"""
function El(tag){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attrs={};
  this.textContent='';const self=this;this.classList={add(c){self.className=((self.className||'')+' '+c).trim();},
  remove(c){self.className=(self.className||'').split(' ').filter(x=>x!==c).join(' ');}};}
El.prototype.appendChild=function(c){this.children.push(c);return c;};
El.prototype.setAttribute=function(k,v){this.attrs[k]=String(v);};
El.prototype.getAttribute=function(k){return k==='type'?(this.type||null):(this.attrs[k]??null);};
Object.defineProperty(El.prototype,'innerHTML',{set(){this.children=[];},get(){return '';}});
global.document={createElement:(t)=>new El(t)};
global.window=global;
const R=require(process.argv[1]);
global.MultipartFieldRenderer=R;
require(process.argv[2]);
const input=JSON.parse(process.argv[3]);
const out={render:[],kinds:{},feedback:[]};
for(const payload of input.payloads){
  const root=new El('div');R.render(root,payload);
  const rows=[];const walk=(n,group)=>{for(const c of n.children){
    if(c.className==='multi-part-group-label'){group=c.textContent;}
    if(c.className==='multi-part-row'){const label=c.children.find(x=>x.tagName==='LABEL');
      const ctl=c.children.find(x=>x.tagName==='INPUT'||x.tagName==='SELECT');
      rows.push({group,label:label?label.textContent:'',aria:ctl?(ctl.attrs['aria-label']||''):'',
        key:ctl?ctl.dataset.fieldKey:'',order:ctl?ctl.dataset.answerOrder:'',cls:ctl?ctl.className:''});}
    walk(c,group);}};
  walk(root,'');out.render.push(rows);}
for(const [name,part] of Object.entries(input.kinds)){out.kinds[name]=R.controlKind(part);}
for(const display of input.feedback){
  const root=new El('div');window.CorrectAnswerFeedback.appendDisplay(root,display);
  const labels=[];const walk=(n)=>{for(const c of n.children){
    if(c.className==='correct-answer-item-label'){labels.push(c.textContent);} walk(c);}};
  walk(root);out.feedback.push(labels);}
out.messages=(input.messages||[]).map(d=>window.CorrectAnswerFeedback.studentGradingMessage(d,d.result));
process.stdout.write(JSON.stringify(out));
"""


def _node() -> str:
    node = shutil.which("node")
    if not node:
        candidates = sorted((Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe"))
        node = str(candidates[0]) if candidates else None
    if not node:
        pytest.skip("Node.js runtime is required for shared renderer DOM tests")
    return node


def _run(payloads=(), kinds=None, feedback=(), messages=()):
    data = {"payloads": list(payloads), "kinds": kinds or {}, "feedback": list(feedback), "messages": list(messages)}
    completed = subprocess.run(
        [_node(), "-e", _DOM_SHIM, str(RENDERER), str(FEEDBACK), json.dumps(data, ensure_ascii=False)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(completed.stdout)


def _parts(*labels):
    return {"answer_contract": {"parts": [
        {"key": f"part_{i + 1}", "label": label, "expected_answer": str(i + 2)} for i, label in enumerate(labels)
    ]}}


def test_generic_multipart_labels_show_numbers_but_keep_internal_keys_and_order() -> None:
    payloads = [
        _parts("part_1", "part_2"),
        _parts("Part 1", "part 2", "第（3）小題", "欄位 4"),
        {"subquestions": [{"part": "part_1"}, {"part": "part_2"}, {"part": "part_3"}]},
        {"answer_contract": {"parts": [{"key": "part_1"}, {"key": "part_2"}]}},
    ]
    rendered = _run(payloads)["render"]
    expected_keys = [["part_1", "part_2"], ["part_1", "part_2", "part_3", "part_4"],
                     ["part_1", "part_2", "part_3"], ["part_1", "part_2"]]
    for rows, keys in zip(rendered, expected_keys):
        assert [row["key"] for row in rows] == keys
        assert [row["order"] for row in rows] == [str(i) for i in range(len(keys))]
        assert [row["label"] for row in rows] == [f"({i + 1})" for i in range(len(keys))]
        for row in rows:
            assert not re.search(r"(?i)part", row["label"] + row["group"])


def test_signed_generic_labels_keep_sign_meaning() -> None:
    payload = {"answer_contract": {"parts": [
        {"key": k, "label": k} for k in ("part_1_pos", "part_1_neg", "part_2_pos", "part_2_neg")
    ]}}
    rows = _run([payload])["render"][0]
    assert [row["label"] for row in rows] == ["(1) 正", "(1) 負", "(2) 正", "(2) 負"]
    assert [row["key"] for row in rows] == ["part_1_pos", "part_1_neg", "part_2_pos", "part_2_neg"]


def test_semantic_labels_are_preserved() -> None:
    labels = ["x 截距", "y =", "斜率", "機率"]
    rows = _run([_parts(*labels)])["render"][0]
    assert [row["label"] for row in rows] == labels
    assert [row["key"] for row in rows] == ["part_1", "part_2", "part_3", "part_4"]


def test_group_marker_is_not_repeated_on_its_single_field() -> None:
    payload = {"answer_contract": {
        "parts": [{"key": "part_1", "label": "part_1", "group_label": "(1)"},
                  {"key": "part_2", "label": "part_2", "group_label": "(2)"}],
    }}
    rows = _run([payload])["render"][0]
    assert [row["group"] for row in rows] == ["(1)", "(2)"]
    assert [row["label"] for row in rows] == ["", ""]
    assert [row["aria"] for row in rows] == ["(1)", "(2)"]
    assert [row["key"] for row in rows] == ["part_1", "part_2"]


def test_control_width_kind_follows_answer_type() -> None:
    kinds = _run(kinds={
        "numeric": {"expected_answer": "12"},
        "coordinate": {"expected_answer": "(1,-2)"},
        "fraction": {"expected_answer": "-3/4"},
        "expression": {"expected_answer": "(x-2)(x+3)"},
        "equation": {"expected_answer": "y=2x+1"},
        "inequality": {"expected_answer": "-1<x<3"},
        "text": {"expected_answer": "向右 1、向下 4"},
    })["kinds"]
    assert kinds == {name: name for name in kinds}


def test_feedback_uses_student_labels_for_generic_parts() -> None:
    display = {"answer_type": "multi_part", "items": [
        {"key": "part_1", "label": "part_1", "value": "3"},
        {"key": "part_2", "label": "斜率", "value": "2"},
    ]}
    assert _run(feedback=[display])["feedback"] == [["(1)", "斜率"]]


def test_grading_summary_uses_student_labels_only_when_it_matches_per_part_results() -> None:
    rows = [{"key": "part_1", "label": "part_1", "correct": True},
            {"key": "part_2", "label": "part_2", "correct": False},
            {"key": "part_3", "label": "x =", "correct": False}]
    summary = "部分小題答錯。\npart_1：正確\npart_2：錯誤\nx =：錯誤"
    edited = "部分小題答錯。請檢查 part_2。"
    out = _run(messages=[
        {"result": summary, "per_part_results": rows},
        {"result": edited, "per_part_results": rows},
        {"result": "答對了！", "per_part_results": rows},
        {"result": summary},
    ])["messages"]
    assert out[0] == "部分小題答錯。\n(1)：正確\n(2)：錯誤\nx =：錯誤"
    assert out[1:] == [edited, "答對了！", summary]


def test_math_normalizer_keeps_subquestion_markers_as_text() -> None:
    script = (
        "const n=require(process.argv[1]);"
        "process.stdout.write(JSON.stringify(JSON.parse(process.argv[2]).map(v=>n.normalizeMathText(v))));"
    )
    values = ["(1)", "（2）", " (3) ", "(1+2)/3", "3/4"]
    completed = subprocess.run(
        [_node(), "-e", script, str(ROOT / "static" / "js" / "math_display_normalizer.js"), json.dumps(values)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    out = json.loads(completed.stdout)
    assert out[:3] == values[:3]
    assert out[3] == r"\(\frac{1 + 2}{3}\)"
    assert out[4] == r"\(\frac{3}{4}\)"


def test_fields_and_submit_share_one_left_aligned_strip() -> None:
    html = INDEX.read_text(encoding="utf-8")
    block = re.search(r'<div class="practice-answer-block">(.*?)<div id="result-display"', html, re.S).group(1)
    assert 'id="subquestions-container"' in block
    group = re.search(r'<div class="input-group">(.*?)</div>', block, re.S).group(1)
    assert 'id="answer-input"' in group and 'id="submit-button"' in group
    assert "answerBlock.classList.toggle('has-multi-part-fields', multi && !tableFill)" in html

    css = LAYOUT_CSS.read_text(encoding="utf-8")
    compact = re.sub(r"\s+", " ", css)
    assert re.search(r"\.practice-answer-block \{[^}]*flex-direction: row;[^}]*flex-wrap: wrap;"
                     r"[^}]*justify-content: flex-start;", compact)
    assert re.search(r"\.practice-answer-block\.has-multi-part-fields > \.subquestions-container"
                     r"\.multi-part-list \{ display: contents !important;", compact)
    assert re.search(r"\.practice-answer-block > \.input-group > #submit-button \{[^}]*flex: 0 0 auto;", compact)
    # Inputs size by answer kind; no control is stretched to the full row.
    for rule in re.findall(r"([^{}]*(?:multi-part-input|#answer-input)[^{}]*)\{([^}]*)\}", css):
        assert not re.search(r"(?<![-\w])width:\s*100%", rule[1]), rule[0]
    # Only the narrow-screen fallback may stack the strip; tablets keep rows.
    assert "flex-direction: column" not in css
    # MCQ choice buttons keep their own layout.
    assert "choice-option" not in css and "choice-list" not in css


def test_short_question_inline_row_is_measured_not_length_based() -> None:
    css = re.sub(r"\s+", " ", LAYOUT_CSS.read_text(encoding="utf-8"))
    inline = re.search(
        r"@media \(min-width: 900px\) \{ \.practice-area\.question-answer-inline"
        r":not\(:has\(#result-display:not\(:empty\)\)\) \{([^}]*)\}", css)
    assert inline, "inline row must be desktop-only and drop out while feedback is shown"
    assert 'grid-template-areas: "header header" "question answer" "canvas canvas";' in inline.group(1)
    assert "var(--question-inline-width" in inline.group(1)

    html = INDEX.read_text(encoding="utf-8")
    start = html.index("function fitQuestionAnswerRow()")
    body = html[start:html.index("function scheduleQuestionAnswerRowFit()", start)]
    assert "question_text" not in body and ".length <" not in body
    assert "getBoundingClientRect" in body and "createRange" in body
    assert "has-multi-part-fields" in body
    assert "questionChoices" in body and "subquestionsContainer" in body
    assert "question-media-container" in body
    assert "getComputedStyle(area).display !== 'grid'" in body
    # Falls back to the stacked layout when the measured row does not fit.
    assert body.count("classList.remove('question-answer-inline')") >= 2
    loader = html[html.index("function scheduleQuestionAnswerRowFit()"):]
    assert "fitQuestionAnswerRow();" in loader
    assert html.count("scheduleQuestionAnswerRowFit()") >= 3
