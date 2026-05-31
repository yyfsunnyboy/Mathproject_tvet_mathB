from __future__ import annotations

from typing import Any
import random

from core.gencode.absolute_value_latex import (
    format_abs_inequality_op,
    format_linear_abs_expr,
)

SKILL_ID = 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning'
GENERATOR_KEYS = ['vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning:absolute_value_inequality_linear_expression_basic:draft_v1', 'vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning:absolute_value_inequality_geometric_meaning:draft_v1']

GENERATOR_SPECS = [{'problem_type_id': 'absolute_value_inequality_linear_expression_basic', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_set'}, {'problem_type_id': 'absolute_value_inequality_geometric_meaning', 'checker_key': 'choice_label_checker', 'equivalence_type': 'choice_label'}]

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
    a = random.randint(-5, 5)
    r = random.randint(1, 6)
    op = random.choice(['<', '<=', '>', '>='])
    left = a - r
    right = a + r
    if op == '<':
        ans = f'({left}, {right})'
    elif op == '<=':
        ans = f'[{left}, {right}]'
    elif op == '>':
        ans = f'(-∞, {left}) ∪ ({right}, ∞)'
    else:
        ans = f'(-∞, {left}] ∪ [{right}, ∞)'
    expr = format_linear_abs_expr(a)
    op_latex = format_abs_inequality_op(op)
    q = f'解不等式 ${expr} {op_latex} {r}$。'
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
        'explanation': f'${expr} {op_latex} {r}$ 表示 x 與 {a} 的距離，解集為 {ans}。',
        'source': 'gencode_phase3_template',
    }

def _gen_choice_problem(pt: str) -> dict[str, Any]:
    a = random.randint(-5, 5)
    r = random.randint(1, 6)
    op = random.choice(['<', '>'])
    expr = format_linear_abs_expr(a)
    op_latex = format_abs_inequality_op(op)
    if op == '<':
        stem = f'不等式 ${expr} {op_latex} {r}$ 的幾何意義，下列何者正確？'
        correct_text = f'x 與 {a} 的距離小於 {r}'
        wrong = [
            f'x 與 {a} 的距離大於 {r}',
            f'x = {a + r}',
            f'x = {a - r}',
        ]
    else:
        stem = f'不等式 ${expr} {op_latex} {r}$ 的幾何意義，下列何者正確？'
        correct_text = f'x 與 {a} 的距離大於 {r}'
        wrong = [
            f'x 與 {a} 的距離小於 {r}',
            f'x = {a + r}',
            f'x = {a - r}',
        ]
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
        'explanation': f'${expr} {op_latex} {r}$ 的幾何意義為點 x 與 {a} 的距離與 {r} 的比較。',
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
