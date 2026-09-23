from __future__ import annotations

import pytest

from core.gencode.choice_contract_validator import normalize_canonical_choices
from core.gencode.choice_math_display import (
    format_choice_math_display,
    normalize_choice_displays,
)
from core.routes.practice import _finalize_practice_question_api_fields


def test_fraction_radical_and_coefficient_radical_display() -> None:
    assert format_choice_math_display("19/2") == r"\(\frac{19}{2}\)"
    assert format_choice_math_display("sqrt(91)") == r"\(\sqrt{91}\)"
    assert format_choice_math_display("6*sqrt(10)") == r"\(6\sqrt{10}\)"
    assert format_choice_math_display("13*sqrt(2)/2") == r"\(\frac{13\sqrt{2}}{2}\)"


def test_integer_decimal_coordinate_and_text_are_unchanged() -> None:
    for value in ("7", "-3", "2.5", "(4,-2)", "以上皆非"):
        assert format_choice_math_display(value) == value


def test_choice_value_and_label_remain_canonical() -> None:
    choices = normalize_choice_displays(
        [
            {"label": "A", "text": "19/2", "value": "19/2"},
            {"label": "B", "text": "sqrt(91)", "value": "sqrt(91)"},
        ]
    )
    assert choices[0]["label"] == "A"
    assert choices[0]["value"] == "19/2"
    assert choices[0]["display"] == r"\(\frac{19}{2}\)"
    assert choices[1]["label"] == "B"
    assert choices[1]["value"] == "sqrt(91)"
    assert choices[1]["display"] == r"\(\sqrt{91}\)"


def test_choice_contract_and_practice_api_include_display_without_changing_values() -> None:
    canonical = normalize_canonical_choices(["19/2", "sqrt(91)", "6*sqrt(10)", "純文字"])
    assert [choice["value"] for choice in canonical] == [
        "19/2",
        "sqrt(91)",
        "6*sqrt(10)",
        "純文字",
    ]
    payload = _finalize_practice_question_api_fields(
        {
            "question_text": "選出正確答案",
            "choices": canonical,
            "correct_answer": "C",
            "answer": "C",
            "presentation_mode": "single_choice",
        }
    )
    assert payload["correct_answer"] == "C"
    assert payload["choices"][2]["value"] == "6*sqrt(10)"
    assert payload["choices"][2]["display"] == r"\(6\sqrt{10}\)"


@pytest.mark.parametrize(('source', 'latex'), [
    ('sqrt(2)', r'\sqrt{2}'),
    ('3*sqrt(2)', r'3\sqrt{2}'),
    ('3*sqrt(2)/2', r'\frac{3\sqrt{2}}{2}'),
    ('20 + 20*sqrt(3)', r'20 + 20\sqrt{3}'),
    ('-20 + 20*sqrt(3)', r'-20 + 20\sqrt{3}'),
    ('20 - 20*sqrt(3)', r'20 - 20\sqrt{3}'),
    ('3/2', r'\frac{3}{2}'),
    ('-3/2', r'\frac{-3}{2}'),
    ('1 + sqrt(2)', r'1 + \sqrt{2}'),
    ('1 - sqrt(2)', r'1 - \sqrt{2}'),
    ('2*(1 + sqrt(3))', r'2\left(1 + \sqrt{3}\right)'),
    ('(1+sqrt(2))/(3-sqrt(2))', r'\frac{1 + \sqrt{2}}{3 - \sqrt{2}}'),
    ('2*3', r'2 \times 3'),
    ('sqrt(1+sqrt(2))', r'\sqrt{1 + \sqrt{2}}'),
])
def test_numeric_expression_display(source, latex):
    assert format_choice_math_display(source) == r'\(' + latex + r'\)'


@pytest.mark.parametrize('source', [
    r'\(\sqrt{2}\)', r'\(\frac{3}{2}\)', r'$\sqrt{2}$', r'$\frac{3}{2}$',
    r'\sqrt{2}', '以上皆非', '已知 a = 3*sqrt(2)/2，求角度',
    '__import__("os").system("whoami")', 'sqrt.__class__', 'sqrt(2,3)',
    'sqrt(x)', '2**100000000', '3//2', 'sqrt(', 'True', '2'*513,
])
def test_existing_tex_text_and_unsupported_syntax_passthrough(source):
    assert format_choice_math_display(source) == source

def test_adaptive_response_matches_practice_and_preserves_canonical_input():
    from core.routes.adaptive_api import _response_for_frontend
    q = {'question_text': '選出答案', 'choices': [
        {'label': 'A', 'text': '20 + 20*sqrt(3)', 'value': '20 + 20*sqrt(3)',
         'display': '20 + 20*sqrt(3)'},
        '-20 + 20*sqrt(3)', '以上皆非', r'\(\sqrt{2}\)'], 'correct_answer': 'A'}
    adaptive = _response_for_frontend({'new_question_data': q})['new_question_data']
    practice = _finalize_practice_question_api_fields(q)
    assert adaptive['choices'] == practice['choices']
    assert adaptive['choices'][0]['display'] == r'\(20 + 20\sqrt{3}\)'
    assert adaptive['choices'][0]['text'] == '20 + 20*sqrt(3)'
    assert q['choices'][0]['display'] == '20 + 20*sqrt(3)'
    assert 'correct_answer' not in adaptive

def test_adaptive_http_response_uses_shared_choice_display(monkeypatch):
    from types import SimpleNamespace
    from flask import Flask
    from core.routes import adaptive_api
    app = Flask(__name__)
    app.config.update(SECRET_KEY='display-test', LOGIN_DISABLED=True)
    monkeypatch.setattr(adaptive_api, 'current_user', SimpleNamespace(id=1))
    raw = {'session_id': 'display-test', 'new_question_data': {
        'question_text': '選出正確答案', 'choices': ['20 + 20*sqrt(3)', '-20 + 20*sqrt(3)'],
        'correct_answer': 'A'}}
    monkeypatch.setattr(adaptive_api, 'submit_and_get_next', lambda payload: raw)
    app.add_url_rule('/api/adaptive/submit_and_get_next', view_func=adaptive_api.adaptive_submit_and_get_next, methods=['POST'])
    result = app.test_client().post('/api/adaptive/submit_and_get_next', json={'step_number': 0, 'skill_id': 'test'})
    assert result.status_code == 200
    q = result.get_json()['new_question_data']
    assert q['choices'] == normalize_choice_displays(raw['new_question_data']['choices'])
    assert q['choices'][1]['value'] == '-20 + 20*sqrt(3)'
    assert 'correct_answer' not in q

def test_shared_normalization_preserves_zero_and_adaptive_content_alias():
    choices = normalize_choice_displays([0, {'text': '0', 'value': 0}, {'content': '以上皆非'}])
    assert [c['text'] for c in choices] == ['0', '0', '以上皆非']
    assert [c['value'] for c in choices] == ['0', '0', '以上皆非']
    assert [c['display'] for c in choices] == ['0', '0', '以上皆非']
