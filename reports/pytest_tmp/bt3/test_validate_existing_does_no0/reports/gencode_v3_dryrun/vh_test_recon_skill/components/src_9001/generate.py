def generate(level=1, seed=None, component_id=None, **kwargs):
    return {
        'question_text': '解 $|x|=3$',
        'answer': 'x=3或x=-3',
        'correct_answer': 'x=3或x=-3',
        'answer_type': 'expression',
        'presentation_mode': 'short_answer',
        'problem_type_id': 'solve_basic_absolute_value_equation',
        'choices': [],
        'explanation': '',
        'component_id': component_id or 'src_9001',
        'answer_contract': {
            'answer_type': 'expression',
            'checker_key': 'linear_equation_equivalent_checker',
            'equivalence_type': 'linear_equation_equivalent',
        },
        'metadata': {'semantic_answer': 'x=3或x=-3'},
    }