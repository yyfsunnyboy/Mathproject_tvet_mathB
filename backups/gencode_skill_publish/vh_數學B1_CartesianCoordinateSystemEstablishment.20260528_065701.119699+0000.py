from __future__ import annotations

from typing import Any
import random
import re

SKILL_ID = 'vh_數學B1_CartesianCoordinateSystemEstablishment'
GENERATOR_KEYS = ['vh_數學B1_CartesianCoordinateSystemEstablishment:cartesian_coordinate_quadrant_symbol_reasoning:draft_v1']

GENERATOR_SPECS = [{'problem_type_id': 'cartesian_coordinate_quadrant_symbol_reasoning', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}]

def _normalize_interval(s: Any) -> str:
    t = str(s or '').strip().lower().replace(' ', '')
    t = t.replace('∞', 'inf').replace('infty', 'inf').replace('infinity', 'inf')
    t = t.replace('-oo', '-inf').replace('+oo', 'inf').replace('oo', 'inf')
    t = t.replace('∪', 'u')
    return t

def _choice_label(s: Any) -> str:
    t = str(s or '').strip().upper()
    return t[:1] if t else ''

def _gen_interval_problem(pt: str) -> dict[str, Any]:
    q = '設點 A 的座標為 (4, -3)，則 A 位於第幾象限？'
    ans = '第四象限'
    return {
        'skill_id': SKILL_ID,
        'problem_type_id': pt,
        'question_text': q,
        'question': q,
        'answer': ans,
        'correct_answer': ans,
        'answer_type': 'choice',
        'question_type': 'choice',
        'checker': 'choice_label_checker',
        'checker_type': 'choice_label_checker',
        'choices': [
            {'label': 'A', 'text': '第一象限'},
            {'label': 'B', 'text': '第二象限'},
            {'label': 'C', 'text': '第三象限'},
            {'label': 'D', 'text': '第四象限'},
        ],
        'explanation': '依座標符號判斷所在象限。',
        'source': 'gencode_phase3_template',
    }

def _is_cartesian_problem_type(pt: str) -> bool:
    p = str(pt or '').lower()
    return any(k in p for k in ['cartesian_coordinate', 'quadrant', 'coordinate', 'position_reasoning'])

def _gen_choice_problem(pt: str) -> dict[str, Any]:
    a = random.randint(-6, -1)
    b = random.randint(a + 1, -1)
    x = a * b
    y = a + b
    stem = f'設 $a,b$ 為實數，且 $a<b<0$，則點 $Q({x},{y})$ 位於第幾象限？'
    correct_text = '第四象限'
    wrong = ['第一象限', '第二象限', '第三象限']
    option_pool = [
        {'is_correct': True, 'text': correct_text},
        {'is_correct': False, 'text': wrong[0]},
        {'is_correct': False, 'text': wrong[1]},
        {'is_correct': False, 'text': wrong[2]},
    ]
    random.shuffle(option_pool)
    choices = []
    ans = 'A'
    for i, opt in enumerate(option_pool):
        label = chr(ord('A') + i)
        choices.append({'label': label, 'text': str(opt.get('text', ''))})
        if opt.get('is_correct'):
            ans = label
    q = stem + '\n' + '\n'.join([f"({c['label']}) {c['text']}" for c in choices])
    return {
        'skill_id': SKILL_ID,
        'problem_type_id': pt,
        'question_text': q,
        'question': q,
        'choices': choices,
        'options': [f"({c['label']}) {c['text']}" for c in choices],
        'answer': ans,
        'correct_answer': ans,
        'answer_type': 'choice',
        'question_type': 'choice',
        'checker': 'choice_label_checker',
        'checker_type': 'choice_label_checker',
        'explanation': '由座標符號判斷所在象限。',
        'source': 'gencode_phase3_template',
    }

def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    if seed is not None:
        random.seed(seed)
    if not GENERATOR_SPECS:
        return {
            'skill_id': SKILL_ID,
            'problem_type_id': 'no_usable_problem_type',
            'question_text': '1 + 1 = ? (fallback)',
            'question': '1 + 1 = ? (fallback)',
            'answer': '2',
            'correct_answer': '2',
            'explanation': 'fallback deterministic item',
            'source': 'gencode_phase3_fallback',
        }
    spec = random.choice(GENERATOR_SPECS)
    pt = str(spec.get('problem_type_id', '')).strip() or 'unknown_problem_type'
    checker = str(spec.get('checker_key', '')).strip()
    eq = str(spec.get('equivalence_type', '')).strip()
    if _is_cartesian_problem_type(pt):
        return _gen_choice_problem(pt)
    if checker == 'choice_label_checker' or eq == 'choice_label' or 'geometric_meaning' in pt:
        return _gen_choice_problem(pt)
    if checker == 'interval_checker' or eq == 'interval_set' or 'inequality' in pt:
        return _gen_interval_problem(pt)
    return _gen_interval_problem(pt)

def check(user_answer: Any, correct_answer: Any):
    ua = str(user_answer or '')
    ca = str(correct_answer or '')
    if not ua.strip() or not ca.strip():
        return False
    ua_label = _choice_label(ua)
    ca_label = _choice_label(ca)
    if ua_label in {'A','B','C','D'} and ca_label in {'A','B','C','D'}:
        return ua_label == ca_label
    return _normalize_interval(ua) == _normalize_interval(ca)
