from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = ROOT / "static" / "js" / "math_display_normalizer.js"


def _normalize(values: list[str]) -> list[str]:
    script = (
        "const n=require(process.argv[1]);"
        "const values=JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(values.map(v=>n.normalizeMathText(v))));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(NORMALIZER), json.dumps(values, ensure_ascii=False)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_slash_pi_negative_parenthesized_and_trig_fractions_become_latex():
    assert _normalize(["3/5", "19π/4", "-5π/6", "(3/4)π", "-(3/5)", "sin(19π/4)"]) == [
        r"\(\frac{3}{5}\)", r"\(\frac{19\pi}{4}\)", r"\(-\frac{5\pi}{6}\)",
        r"\(\frac{3}{4}\pi\)", r"\(-\frac{3}{5}\)",
        r"\(\sin\left(\frac{19\pi}{4}\right)\)",
    ]


def test_existing_latex_is_preserved():
    existing = r"\(\frac{3\pi}{4}\)"
    assert _normalize([existing]) == [existing]


def test_ascii_sympy_pi_fractions_use_stacked_latex_without_touching_paths():
    assert _normalize(["2*pi/3", "-pi/2", "sin(3*pi/4)"]) == [
        r"\(\frac{2\pi}{3}\)", r"\(-\frac{\pi}{2}\)",
        r"\(\sin\left(\frac{3\pi}{4}\right)\)",
    ]


def test_plain_dates_urls_and_paths_are_not_converted():
    values = ["日期 2026/9/11", "https://example.test/a/3/5", r"C:\tmp\3/5", "純文字說明"]
    assert _normalize(values) == values


def test_practice_question_subquestion_and_table_paths_use_shared_normalizer():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement(element" in source
    assert "MathDisplayNormalizer.normalizeMathText(text" in source
    assert "renderMathContent(subquestionsContainer)" in source


def test_adaptive_question_choice_and_hint_typesetting_uses_shared_normalizer():
    source = (ROOT / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement(element" in source
    assert "await typesetMath(choiceList)" in source
    assert "await typesetMath(hintBox)" in source


def test_correct_answer_display_delegates_to_shared_normalizer_and_mathjax():
    source = (ROOT / "static" / "js" / "correct_answer_feedback.js").read_text(encoding="utf-8")
    assert "MathDisplayNormalizer.normalizeMathText" in source
    assert "MathJax.typesetPromise" in source


def test_textbook_example_preview_uses_same_shared_renderer():
    source = (ROOT / "templates" / "admin_v3_example_preview.html").read_text(encoding="utf-8")
    assert "math_display_normalizer.js" in source
    assert "MathDisplayNormalizer.normalizeElement" in source
    assert "await triggerMathJax([contentBlock])" in source

def test_compound_radicals_and_explicit_stem_math():
    assert _normalize(['20 + 20*sqrt(3)', '-20 + 20*sqrt(3)',
                       '3*sqrt(2)/2', r'已知 \(a = 3 * sqrt(2) / 2\)，求角度']) == [
        r'\(20 + 20\sqrt{3}\)', r'\(-20 + 20\sqrt{3}\)',
        r'\(\frac{3\sqrt{2}}{2}\)', r'已知 \(a = \frac{3\sqrt{2}}{2}\)，求角度']


def test_choice_fallback_with_present_but_noop_normalizer():
    script = r'''
      globalThis.MathDisplayNormalizer = { normalizeMathText: x => x };
      const c = require('./static/js/choice_math.js');
      process.stdout.write(c.choiceDisplay({text:'3*sqrt(2)'}));
    '''
    result = subprocess.run(['node', '-e', script], cwd=ROOT, capture_output=True, text=True, check=True)
    assert result.stdout == r'\(3\sqrt{2}\)'


def test_adaptive_display_is_preserved_and_escaped():
    source = (ROOT / 'templates/adaptive_practice_v2.html').read_text(encoding='utf-8')
    assert 'display: choice.display' in source
    assert 'escapeHtml(renderChoiceText(`(${choice.label}) ${choice.display || choice.text}`' in source

def test_adaptive_render_uses_display_without_html_injection():
    script = r"""
      const fs = require('fs'), vm = require('vm');
      const source = fs.readFileSync('templates/adaptive_practice_v2.html', 'utf8');
      const start = source.indexOf('    const CHOICE_LABELS =');
      const end = source.indexOf('    function renderTrajectory()', start);
      const choiceList = {innerHTML:'', classList:{add(){},remove(){}}, querySelectorAll(){return []}};
      let typeset = 0;
      const context = vm.createContext({choiceList,
        typesetMath: async () => {typeset++},
        escapeHtml: s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')});
      vm.runInContext(source.slice(start, end), context);
      (async () => {
        await context.renderChoiceOptions([{label:'A',text:'20 + 20*sqrt(3)',display:'\\(20 + 20\\sqrt{3}\\)'},
          {label:'B',text:'以上皆非'}, {label:'C',text:'test',display:'<img src=x onerror=alert(1)>'}]);
        process.stdout.write(JSON.stringify({html:choiceList.innerHTML,typeset}));
      })();
    """
    result = subprocess.run(['node', '-e', script], cwd=ROOT, check=True, capture_output=True, text=True, encoding='utf-8')
    out = json.loads(result.stdout)
    assert r'\(20 + 20\sqrt{3}\)' in out['html']
    assert 'data-choice-text="20 + 20*sqrt(3)"' in out['html']
    assert '以上皆非' in out['html']
    assert '<img' not in out['html']
    assert '&lt;img' in out['html']
    assert out['typeset'] == 1
