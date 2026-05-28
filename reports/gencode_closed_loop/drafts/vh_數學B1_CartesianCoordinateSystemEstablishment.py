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
    left = random.randint(-8, 0)
    right = random.randint(1, 9)
    q = f'請寫出同時滿足 x > {left} 且 x < {right} 的解集合（區間表示）。'
    ans = f'({left}, {right})'
    return {
        'skill_id': SKILL_ID,
        'problem_type_id': pt,
        'question_text': q,
        'question': q,
        'answer': ans,
        'correct_answer': ans,
        'answer_type': 'text',
        'question_type': 'text',
        'checker': 'interval_checker',
        'checker_type': 'interval_checker',
        'explanation': '交集區間為兩端點之間的開區間。',
        'source': 'gencode_phase3_template',
    }

def _is_cartesian_problem_type(pt: str) -> bool:
    p = str(pt or '').lower()
    return any(k in p for k in ['cartesian_coordinate', 'quadrant', 'coordinate', 'position_reasoning'])

def _gen_cartesian_choice_problem(pt: str) -> dict[str, Any]:
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

def _gen_generic_choice_problem(pt: str) -> dict[str, Any]:
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    stem = f'已知 a={a}, b={b}，下列何者為 a+b？'
    correct_text = str(a + b)
    wrong = [str(a + b + 1), str(a + b - 1), str(a + b + 2)]
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
        'explanation': '以 choice label 比對正確選項。',
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
        return _gen_cartesian_choice_problem(pt)
    if 'cartesian_coordinate' in pt:
        return _gen_cartesian_choice_problem(pt)
    if checker == 'choice_label_checker' or eq == 'choice_label':
        return _gen_generic_choice_problem(pt)
    if checker == 'interval_checker' or eq == 'interval_set' or 'inequality' in pt:
        return _gen_interval_problem(pt)
    return {
        'skill_id': SKILL_ID,
        'problem_type_id': pt,
        'question_text': 'implementation pending',
        'question': 'implementation pending',
        'answer': 'implementation_pending',
        'correct_answer': 'implementation_pending',
        'answer_type': 'text',
        'question_type': 'text',
        'checker': checker or 'manual_review_checker',
        'checker_type': checker or 'manual_review_checker',
        'source': 'gencode_phase3_blocked',
        'block_reason': f'no_template_for:{pt}',
    }

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
