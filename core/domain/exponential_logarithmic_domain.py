# -*- coding: utf-8 -*-
"""B3 Chapter 4 exponential / logarithmic domain entrypoint.

Maps every imported source row (textbook_example_id) to one family
operation plus its variant slots, and dispatches to the family builders.
All mathematical truth lives in ``exponential_logarithmic_math`` and the
family builders; generators only call ``build_exponential_logarithmic_matrix``.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from core.domain import exponential_logarithmic_exp_builders as E
from core.domain import exponential_logarithmic_log_builders as L
from core.domain.exponential_logarithmic_render import (
    BARE_LOG_RE,
    DOMAIN_KEY,
    EQ_RESIDUE_RE,
    SOLUTION_MARKER_RE,
    SOURCE_LABEL_RE,
)

# ------------------------------------------------------------ operations
EXP_INTEGER_POWER_EVAL = "exp_integer_power_eval"
EXP_PRIME_FACTOR_EXPONENT = "exp_prime_factor_exponent"
EXP_LAW_PRODUCT_CHOICE = "exp_law_product_choice"
EXP_INTEGER_EXPONENT_SIMPLIFY = "exp_integer_exponent_simplify"
EXP_FILL_INTEGER_EXPONENT = "exp_fill_integer_exponent"
EXP_ZERO_NEGATIVE_EVAL = "exp_zero_negative_eval"
EXP_RATIONAL_POWER_EVAL = "exp_rational_power_eval"
EXP_RATIONAL_EXPONENT_SIMPLIFY = "exp_rational_exponent_simplify"
EXP_RATIONAL_POWER_COMBO = "exp_rational_power_combo"
EXP_GROWTH_DECAY_MODEL_CHOICE = "exp_growth_decay_model_choice"
EXP_SOLVE_EXPONENT_RADICAL = "exp_solve_exponent_radical"
GRAPH_SKETCH_TABLE = "graph_sketch_table"
EXP_COMPARE_SAME_BASE = "exp_compare_same_base"
EXP_MODEL_FROM_GRAPH = "exp_model_from_graph"
GRAPH_PROPERTY_CHOICE = "graph_property_choice"
EXP_GRAPH_IDENTIFY_CHOICE = "exp_graph_identify_choice"
EXP_EQUATION_SAME_BASE = "exp_equation_same_base"
EXP_EQUATION_CONVERT_BASE = "exp_equation_convert_base"
EXP_EQUATION_QUADRATIC_SUB = "exp_equation_quadratic_sub"
EXP_EQUATION_FACTOR_COMMON = "exp_equation_factor_common"
EXP_POWER_SUBSTITUTION_VALUE = "exp_power_substitution_value"
LOG_DEFINITION_EVAL = "log_definition_eval"
LOG_DOMAIN_VALIDITY_CHOICE = "log_domain_validity_choice"
LOG_BASIC_PROPERTY_EVAL = "log_basic_property_eval"
LOG_RATIONAL_VALUE_EVAL = "log_rational_value_eval"
LOG_PRODUCT_QUOTIENT_EVAL = "log_product_quotient_eval"
LOG_LINEAR_COMBINATION_EVAL = "log_linear_combination_eval"
LOG_CHANGE_BASE_CHAIN_EVAL = "log_change_base_chain_eval"
LOG_CHANGE_BASE_PRODUCT_EVAL = "log_change_base_product_eval"
LOG_EXPRESS_IN_AB = "log_express_in_ab"
LOG_APPLICATION_STATEMENT_CHOICE = "log_application_statement_choice"
LOG_RECIPROCAL_SUM_PARAM = "log_reciprocal_sum_param"
LOG_DEFINITION_INVERSE_EVAL = "log_definition_inverse_eval"
LOG_COMPARE_VALUES = "log_compare_values"
LOG_DECIBEL_APPLICATION = "log_decibel_application"
LOG_EQUATION_LINEAR_ARG = "log_equation_linear_arg"
LOG_EQUATION_PRODUCT_QUADRATIC = "log_equation_product_quadratic"
LOG_EQUATION_QUADRATIC_ARG = "log_equation_quadratic_arg"
LOG_EQUATION_SOLVE_BASE = "log_equation_solve_base"
LOG_CURVE_THROUGH_POINTS = "log_curve_through_points"
LOG_THRESHOLD_APPLICATION_CHOICE = "log_threshold_application_choice"
COMMON_LOG_TABLE_LOOKUP = "common_log_table_lookup"
COMMON_LOG_GIVEN_APPROX_EVAL = "common_log_given_approx_eval"
LOG_CHARACTERISTIC_MANTISSA = "log_characteristic_mantissa"
LOG_CHARACTERISTIC_RULE = "log_characteristic_rule"
LOG_SCIENTIFIC_SHIFT = "log_scientific_shift"
LOG_POWER_DIGIT_COUNT = "log_power_digit_count"
LOG_POWER_FIRST_NONZERO = "log_power_first_nonzero"
LOG_GROWTH_YEARS = "log_growth_years"

_BUILDERS: dict[str, Callable[[random.Random, dict[str, Any]], dict[str, Any]]] = {
    EXP_INTEGER_POWER_EVAL: E.build_exp_integer_power_eval,
    EXP_PRIME_FACTOR_EXPONENT: E.build_exp_prime_factor_exponent,
    EXP_LAW_PRODUCT_CHOICE: E.build_exp_law_product_choice,
    EXP_INTEGER_EXPONENT_SIMPLIFY: E.build_exp_integer_exponent_simplify,
    EXP_FILL_INTEGER_EXPONENT: E.build_exp_fill_integer_exponent,
    EXP_ZERO_NEGATIVE_EVAL: E.build_exp_zero_negative_eval,
    EXP_RATIONAL_POWER_EVAL: E.build_exp_rational_power_eval,
    EXP_RATIONAL_EXPONENT_SIMPLIFY: E.build_exp_rational_exponent_simplify,
    EXP_RATIONAL_POWER_COMBO: E.build_exp_rational_power_combo,
    EXP_GROWTH_DECAY_MODEL_CHOICE: E.build_exp_growth_decay_model_choice,
    EXP_SOLVE_EXPONENT_RADICAL: E.build_exp_solve_exponent_radical,
    GRAPH_SKETCH_TABLE: E.build_graph_sketch_table,
    EXP_COMPARE_SAME_BASE: E.build_exp_compare_same_base,
    EXP_MODEL_FROM_GRAPH: E.build_exp_model_from_graph,
    GRAPH_PROPERTY_CHOICE: E.build_graph_property_choice,
    EXP_GRAPH_IDENTIFY_CHOICE: E.build_exp_graph_identify_choice,
    EXP_EQUATION_SAME_BASE: E.build_exp_equation_same_base,
    EXP_EQUATION_CONVERT_BASE: E.build_exp_equation_convert_base,
    EXP_EQUATION_QUADRATIC_SUB: E.build_exp_equation_quadratic_sub,
    EXP_EQUATION_FACTOR_COMMON: E.build_exp_equation_factor_common,
    EXP_POWER_SUBSTITUTION_VALUE: E.build_exp_power_substitution_value,
    LOG_DEFINITION_EVAL: L.build_log_definition_eval,
    LOG_DOMAIN_VALIDITY_CHOICE: L.build_log_domain_validity_choice,
    LOG_BASIC_PROPERTY_EVAL: L.build_log_basic_property_eval,
    LOG_RATIONAL_VALUE_EVAL: L.build_log_rational_value_eval,
    LOG_PRODUCT_QUOTIENT_EVAL: L.build_log_product_quotient_eval,
    LOG_LINEAR_COMBINATION_EVAL: L.build_log_linear_combination_eval,
    LOG_CHANGE_BASE_CHAIN_EVAL: L.build_log_change_base_chain_eval,
    LOG_CHANGE_BASE_PRODUCT_EVAL: L.build_log_change_base_product_eval,
    LOG_EXPRESS_IN_AB: L.build_log_express_in_ab,
    LOG_APPLICATION_STATEMENT_CHOICE: L.build_log_application_statement_choice,
    LOG_RECIPROCAL_SUM_PARAM: L.build_log_reciprocal_sum_param,
    LOG_DEFINITION_INVERSE_EVAL: L.build_log_definition_inverse_eval,
    LOG_COMPARE_VALUES: L.build_log_compare_values,
    LOG_DECIBEL_APPLICATION: L.build_log_decibel_application,
    LOG_EQUATION_LINEAR_ARG: L.build_log_equation_linear_arg,
    LOG_EQUATION_PRODUCT_QUADRATIC: L.build_log_equation_product_quadratic,
    LOG_EQUATION_QUADRATIC_ARG: L.build_log_equation_quadratic_arg,
    LOG_EQUATION_SOLVE_BASE: L.build_log_equation_solve_base,
    LOG_CURVE_THROUGH_POINTS: L.build_log_curve_through_points,
    LOG_THRESHOLD_APPLICATION_CHOICE: L.build_log_threshold_application_choice,
    COMMON_LOG_TABLE_LOOKUP: L.build_common_log_table_lookup,
    COMMON_LOG_GIVEN_APPROX_EVAL: L.build_common_log_given_approx_eval,
    LOG_CHARACTERISTIC_MANTISSA: L.build_log_characteristic_mantissa,
    LOG_CHARACTERISTIC_RULE: L.build_log_characteristic_rule,
    LOG_SCIENTIFIC_SHIFT: L.build_log_scientific_shift,
    LOG_POWER_DIGIT_COUNT: L.build_log_power_digit_count,
    LOG_POWER_FIRST_NONZERO: L.build_log_power_first_nonzero,
    LOG_GROWTH_YEARS: L.build_log_growth_years,
}

OPS = frozenset(_BUILDERS)

# ---------------------------------------------------------------- skills
SKILL_411 = "vh_數學B3_SubSection_4_1_1"
SKILL_412 = "vh_數學B3_SubSection_4_1_2"
SKILL_413 = "vh_數學B3_SubSection_4_1_3"
SKILL_421 = "vh_數學B3_SubSection_4_2_1"
SKILL_422 = "vh_數學B3_SubSection_4_2_2"
SKILL_431 = "vh_數學B3_SubSection_4_3_1"
SKILL_432 = "vh_數學B3_SubSection_4_3_2"
SKILL_441 = "vh_數學B3_SubSection_4_4_1"
SKILL_442 = "vh_數學B3_SubSection_4_4_2"
SKILL_451 = "vh_數學B3_SubSection_4_5_1"
SKILL_452 = "vh_數學B3_SubSection_4_5_2"
SKILL_453 = "vh_數學B3_SubSection_4_5_3"

# Formal skill with no legal imported source (calculator-key usage); kept
# without a generator on purpose.
ZERO_SOURCE_SKILLS = frozenset({SKILL_452})

_EXAMPLE = "textbook_example"
_PRACTICE = "in_class_practice"
_EXERCISE = "textbook_exercise"
_ADVANCED = "advanced_exercise"
_EXAM = "exam_practice"
_SELF = "self_assessment"

_SOURCE_KIND: dict[int, str] = {
    **{i: _EXAMPLE for i in (12127, 12129, 12131, 12133, 12146, 12148, 12150, 12152, 12154, 12156, 12158,
                            12171, 12173, 12175, 12177, 12179, 12181, 12183, 12185, 12198, 12200, 12202,
                            12204, 12206, 12208, 12221, 12223, 12225, 12227, 12229, 12231, 12233, 12235)},
    **{i: _PRACTICE for i in (12128, 12130, 12132, 12134, 12147, 12149, 12151, 12153, 12155, 12157, 12159,
                             12172, 12174, 12176, 12178, 12180, 12182, 12184, 12186, 12199, 12201, 12203,
                             12205, 12207, 12209, 12222, 12224, 12226, 12228, 12230, 12232, 12234, 12236)},
    **{i: _EXERCISE for i in (12136, 12137, 12138, 12139, 12140, 12141, 12142, 12143, 12161, 12162, 12163,
                             12164, 12165, 12166, 12167, 12168, 12188, 12189, 12190, 12191, 12192, 12193,
                             12194, 12195, 12211, 12212, 12213, 12214, 12215, 12216, 12217, 12218, 12238,
                             12239, 12240, 12241, 12242, 12243, 12244, 12245)},
    **{i: _ADVANCED for i in (12144, 12145, 12169, 12170, 12196, 12197, 12219, 12220, 12246, 12247)},
    **{i: _EXAM for i in (12135, 12160, 12187, 12210, 12237)},
    **{i: _SELF for i in range(12248, 12273)},
}

SOURCE_SPECS: dict[int, dict[str, Any]] = {}


def _bind(example_id: int, skill_id: str, op: str, presentation: str = "short_answer", **slots: Any) -> None:
    if example_id in SOURCE_SPECS:
        raise ValueError(f"duplicate_source_spec:{example_id}")
    SOURCE_SPECS[example_id] = {
        "skill_id": skill_id,
        "op": op,
        "presentation": presentation,
        "source_kind": _SOURCE_KIND[example_id],
        "slots": dict(slots),
    }


MC = "single_choice"

# 4-1-1 integer exponent laws
_bind(12127, SKILL_411, EXP_INTEGER_POWER_EVAL)
_bind(12128, SKILL_411, EXP_INTEGER_POWER_EVAL)
_bind(12136, SKILL_411, EXP_INTEGER_POWER_EVAL, kinds=["power_of_power", "product_power"])
_bind(12145, SKILL_411, EXP_PRIME_FACTOR_EXPONENT)
_bind(12248, SKILL_411, EXP_LAW_PRODUCT_CHOICE, MC)
# 4-1-2 zero / negative exponents
_bind(12129, SKILL_412, EXP_INTEGER_EXPONENT_SIMPLIFY, kinds=["numeric", "monomial2"])
_bind(12130, SKILL_412, EXP_INTEGER_EXPONENT_SIMPLIFY, kinds=["numeric", "monomial1"])
_bind(12139, SKILL_412, EXP_INTEGER_EXPONENT_SIMPLIFY, kinds=["monomial_frac", "monomial2"])
_bind(12137, SKILL_412, EXP_FILL_INTEGER_EXPONENT)
_bind(12138, SKILL_412, EXP_ZERO_NEGATIVE_EVAL)
# 4-1-3 rational exponents
for _id in (12131, 12132):
    _bind(_id, SKILL_413, EXP_RATIONAL_POWER_EVAL, kinds=["int_neg_frac", "frac_root", "decimal_base"])
_bind(12140, SKILL_413, EXP_RATIONAL_POWER_EVAL, kinds=["decimal_base", "frac_root", "frac_root"])
for _id in (12133, 12134):
    _bind(_id, SKILL_413, EXP_RATIONAL_EXPONENT_SIMPLIFY, kinds=["power_product", "radical_quotient"])
_bind(12141, SKILL_413, EXP_RATIONAL_EXPONENT_SIMPLIFY, kinds=["bracket_half", "bracket_half"])
_bind(12142, SKILL_413, EXP_RATIONAL_EXPONENT_SIMPLIFY, kinds=["three_var"])
_bind(12143, SKILL_413, EXP_RATIONAL_EXPONENT_SIMPLIFY, kinds=["radical_product", "radical_product"])
_bind(12144, SKILL_413, EXP_RATIONAL_POWER_COMBO, variant="sum3")
_bind(12259, SKILL_413, EXP_RATIONAL_POWER_COMBO, MC, variant="sum2")
_bind(12258, SKILL_413, EXP_RATIONAL_POWER_COMBO, MC, variant="same_base")
_bind(12135, SKILL_413, EXP_GROWTH_DECAY_MODEL_CHOICE, MC)
_bind(12260, SKILL_413, EXP_SOLVE_EXPONENT_RADICAL, MC, variant="two")
_bind(12268, SKILL_413, EXP_SOLVE_EXPONENT_RADICAL, MC, variant="nested")
# 4-2-1 exponential functions and graphs
for _id in (12146, 12147):
    _bind(_id, SKILL_421, GRAPH_SKETCH_TABLE, fn="exp", base="up")
for _id in (12148, 12149):
    _bind(_id, SKILL_421, GRAPH_SKETCH_TABLE, fn="exp", base="down")
_bind(12161, SKILL_421, GRAPH_SKETCH_TABLE, fn="exp", mode="pair")
_bind(12150, SKILL_421, EXP_COMPARE_SAME_BASE, parts=[("up", 3), ("down", 3)])
_bind(12151, SKILL_421, EXP_COMPARE_SAME_BASE, parts=[("sqrt", 3), ("down", 3)])
_bind(12163, SKILL_421, EXP_COMPARE_SAME_BASE, parts=[("down", 4), ("sqrt", 4)])
_bind(12249, SKILL_421, EXP_COMPARE_SAME_BASE, MC)
_bind(12152, SKILL_421, EXP_MODEL_FROM_GRAPH, variant="growth")
_bind(12153, SKILL_421, EXP_MODEL_FROM_GRAPH, variant="decay")
_bind(12162, SKILL_421, GRAPH_PROPERTY_CHOICE, MC, pool="exp")
_bind(12170, SKILL_421, GRAPH_PROPERTY_CHOICE, MC, pool="exp", fname="f")
_bind(12269, SKILL_421, GRAPH_PROPERTY_CHOICE, MC, pool="pair")
# 4-2-2 exponential equations
for _id in (12154, 12155):
    _bind(_id, SKILL_422, EXP_EQUATION_SAME_BASE, kinds=["linear_exp", "linear_exp"])
_bind(12164, SKILL_422, EXP_EQUATION_SAME_BASE, kinds=["power_base", "linear_exp"])
for _id in (12156, 12157, 12165):
    _bind(_id, SKILL_422, EXP_EQUATION_CONVERT_BASE, variant="reciprocal")
_bind(12166, SKILL_422, EXP_EQUATION_CONVERT_BASE, variant="inverse_square")
_bind(12271, SKILL_422, EXP_EQUATION_CONVERT_BASE, MC, variant="square_reciprocal")
_bind(12158, SKILL_422, EXP_EQUATION_QUADRATIC_SUB, variant="basic")
_bind(12159, SKILL_422, EXP_EQUATION_QUADRATIC_SUB, variant="shifted")
_bind(12168, SKILL_422, EXP_EQUATION_QUADRATIC_SUB, variant="two_roots")
_bind(12169, SKILL_422, EXP_EQUATION_QUADRATIC_SUB, variant="divide")
_bind(12272, SKILL_422, EXP_EQUATION_QUADRATIC_SUB, MC, variant="square_base")
_bind(12167, SKILL_422, EXP_EQUATION_FACTOR_COMMON)
_bind(12270, SKILL_422, EXP_POWER_SUBSTITUTION_VALUE, MC)
_bind(12160, SKILL_422, EXP_GRAPH_IDENTIFY_CHOICE, MC)
# 4-3-1 logarithm definition
for _id in (12171, 12172):
    _bind(_id, SKILL_431, LOG_DEFINITION_EVAL)
_bind(12188, SKILL_431, LOG_DOMAIN_VALIDITY_CHOICE)
_bind(12250, SKILL_431, LOG_DOMAIN_VALIDITY_CHOICE, MC)
# 4-3-2 logarithm properties
for _id in (12173, 12174):
    _bind(_id, SKILL_432, LOG_BASIC_PROPERTY_EVAL, kinds=["log_one", "log_self", "log_power", "exp_log"])
_bind(12189, SKILL_432, LOG_BASIC_PROPERTY_EVAL, kinds=["log_power", "exp_log"])
for _id in (12175, 12176):
    _bind(_id, SKILL_432, LOG_RATIONAL_VALUE_EVAL, kinds=["int", "radical_arg", "radical_base"])
_bind(12253, SKILL_432, LOG_RATIONAL_VALUE_EVAL, MC)
for _id in (12177, 12178, 12190):
    _bind(_id, SKILL_432, LOG_PRODUCT_QUOTIENT_EVAL)
for _id in (12179, 12180):
    _bind(_id, SKILL_432, LOG_LINEAR_COMBINATION_EVAL, kinds=["combo3"])
_bind(12191, SKILL_432, LOG_LINEAR_COMBINATION_EVAL, kinds=["combo3", "combo3"])
_bind(12192, SKILL_432, LOG_LINEAR_COMBINATION_EVAL, kinds=["surd", "half"])
_bind(12251, SKILL_432, LOG_LINEAR_COMBINATION_EVAL, MC)
for _id in (12181, 12182):
    _bind(_id, SKILL_432, LOG_CHANGE_BASE_CHAIN_EVAL, kinds=["reciprocal", "chain"])
_bind(12193, SKILL_432, LOG_CHANGE_BASE_CHAIN_EVAL, kinds=["chain", "exp_ratio"])
_bind(12254, SKILL_432, LOG_CHANGE_BASE_CHAIN_EVAL, MC)
for _id in (12183, 12184, 12194):
    _bind(_id, SKILL_432, LOG_CHANGE_BASE_PRODUCT_EVAL)
_bind(12252, SKILL_432, LOG_CHANGE_BASE_PRODUCT_EVAL, MC)
_bind(12185, SKILL_432, LOG_EXPRESS_IN_AB, setting="base3", parts=["log", "ratio"])
_bind(12186, SKILL_432, LOG_EXPRESS_IN_AB, setting="base10", parts=["log", "ratio"])
_bind(12195, SKILL_432, LOG_EXPRESS_IN_AB, setting="base10", parts=["ratio", "ratio"])
_bind(12196, SKILL_432, LOG_EXPRESS_IN_AB, setting="mixed", parts=["log", "ratio"])
_bind(12256, SKILL_432, LOG_EXPRESS_IN_AB, MC, setting="base10")
_bind(12187, SKILL_432, LOG_APPLICATION_STATEMENT_CHOICE, MC)
_bind(12197, SKILL_432, LOG_RECIPROCAL_SUM_PARAM)
_bind(12255, SKILL_432, LOG_DEFINITION_INVERSE_EVAL, MC)
# 4-4-1 logarithmic functions and graphs
for _id in (12198, 12199):
    _bind(_id, SKILL_441, GRAPH_SKETCH_TABLE, fn="log", base="up")
for _id in (12200, 12201):
    _bind(_id, SKILL_441, GRAPH_SKETCH_TABLE, fn="log", base="down")
_bind(12211, SKILL_441, GRAPH_SKETCH_TABLE, fn="log", mode="pair")
_bind(12202, SKILL_441, LOG_COMPARE_VALUES, parts=["up", "down"])
_bind(12203, SKILL_441, LOG_COMPARE_VALUES, parts=["sqrt_up", "down"])
_bind(12213, SKILL_441, LOG_COMPARE_VALUES, parts=["pi", "down_frac", "self_down"])
_bind(12219, SKILL_441, LOG_COMPARE_VALUES, parts=["convert", "convert"])
_bind(12261, SKILL_441, LOG_COMPARE_VALUES, MC)
_bind(12204, SKILL_441, LOG_DECIBEL_APPLICATION, mode="both")
_bind(12205, SKILL_441, LOG_DECIBEL_APPLICATION, mode="forward")
_bind(12212, SKILL_441, GRAPH_PROPERTY_CHOICE, MC, pool="log")
_bind(12257, SKILL_441, GRAPH_PROPERTY_CHOICE, MC, pool="mixed", mode="incorrect")
# 4-4-2 logarithmic equations
for _id in (12206, 12207, 12214):
    _bind(_id, SKILL_442, LOG_EQUATION_LINEAR_ARG)
_bind(12262, SKILL_442, LOG_EQUATION_LINEAR_ARG, MC)
for _id in (12208, 12209, 12217):
    _bind(_id, SKILL_442, LOG_EQUATION_PRODUCT_QUADRATIC, variant="const")
_bind(12218, SKILL_442, LOG_EQUATION_PRODUCT_QUADRATIC, variant="log_rhs")
_bind(12263, SKILL_442, LOG_EQUATION_PRODUCT_QUADRATIC, MC, variant="const")
_bind(12215, SKILL_442, LOG_EQUATION_QUADRATIC_ARG)
_bind(12216, SKILL_442, LOG_EQUATION_SOLVE_BASE)
_bind(12220, SKILL_442, LOG_CURVE_THROUGH_POINTS)
_bind(12210, SKILL_442, LOG_THRESHOLD_APPLICATION_CHOICE, MC)
# 4-5-1 common logarithm table
for _id in (12221, 12222):
    _bind(_id, SKILL_451, COMMON_LOG_TABLE_LOOKUP, kinds=["3", "3"])
for _id in (12223, 12224):
    _bind(_id, SKILL_451, COMMON_LOG_TABLE_LOOKUP, kinds=["4", "4"])
_bind(12238, SKILL_451, COMMON_LOG_TABLE_LOOKUP, kinds=["3", "4"])
_bind(12265, SKILL_451, COMMON_LOG_GIVEN_APPROX_EVAL)
# 4-5-3 characteristic, mantissa and applications
for _id in (12225, 12226, 12239):
    _bind(_id, SKILL_453, LOG_CHARACTERISTIC_MANTISSA, sign="pos")
for _id in (12227, 12228, 12240):
    _bind(_id, SKILL_453, LOG_CHARACTERISTIC_MANTISSA, sign="neg")
_bind(12264, SKILL_453, LOG_CHARACTERISTIC_MANTISSA, MC, sign="neg")
_bind(12241, SKILL_453, LOG_CHARACTERISTIC_RULE)
for _id in (12229, 12230):
    _bind(_id, SKILL_453, LOG_SCIENTIFIC_SHIFT, variant="forward_inverse")
_bind(12242, SKILL_453, LOG_SCIENTIFIC_SHIFT, variant="reverse")
_bind(12246, SKILL_453, LOG_SCIENTIFIC_SHIFT, variant="neg_single")
for _id in (12231, 12232, 12243, 12244):
    _bind(_id, SKILL_453, LOG_POWER_DIGIT_COUNT)
_bind(12266, SKILL_453, LOG_POWER_DIGIT_COUNT, MC)
for _id in (12233, 12234, 12245):
    _bind(_id, SKILL_453, LOG_POWER_FIRST_NONZERO)
for _id in (12235, 12236):
    _bind(_id, SKILL_453, LOG_GROWTH_YEARS, variant="dep")
_bind(12247, SKILL_453, LOG_GROWTH_YEARS, variant="grow")
_bind(12267, SKILL_453, LOG_GROWTH_YEARS, MC, variant="dep")
_bind(12237, SKILL_453, LOG_GROWTH_YEARS, MC, variant="closest")

SOURCE_IDS = frozenset(SOURCE_SPECS)

HINTS: dict[str, tuple[str, ...]] = {
    "exp": (
        "先把每個底數化成質數或同一底數的次方。",
        "依指數律合併：同底相乘指數相加、乘冪的乘冪指數相乘、負指數取倒數。",
        "最後化成最簡分數或最簡指數形式，再檢查答案。",
    ),
    "graph": (
        "先判斷底數大於 1 還是介於 0 與 1 之間。",
        "指數函數恆過 (0,1) 且在 x 軸上方；對數函數恆過 (1,0) 且在 y 軸右方。",
        "代入題目給的點或比較同底數的指數／真數大小。",
    ),
    "exp_equation": (
        "把方程式兩邊化成同底數的次方。",
        "指數相等時列出一次或二次方程式；必要時令 t=a^x>0。",
        "解出後捨去使 a^x 不為正的根，再代回檢查。",
    ),
    "log": (
        "由定義 a^y=x 與 y=log_a x 互換，並確認底數與真數的條件。",
        "用乘法、除法、次方與換底公式把式子合併成單一對數。",
        "把真數寫成底數的次方求值，或以題目給定的符號表示。",
    ),
    "log_equation": (
        "先寫出真數大於 0 的條件。",
        "合併對數後由定義化成代數方程式並求解。",
        "逐一檢查每個根是否使所有真數大於 0，不合的要捨去。",
    ),
    "common_log": (
        "常用對數以 10 為底；先把數寫成 a×10^n（1≤a<10）。",
        "首數由 n 決定，尾數由 log a 決定；只使用題目給的近似值。",
        "依首數判斷位數或第幾位出現不為 0 的數字；應用題先列式再取對數。",
    ),
}

_HINT_GROUP = {
    **{op: "exp" for op in (
        EXP_INTEGER_POWER_EVAL, EXP_PRIME_FACTOR_EXPONENT, EXP_LAW_PRODUCT_CHOICE, EXP_INTEGER_EXPONENT_SIMPLIFY,
        EXP_FILL_INTEGER_EXPONENT, EXP_ZERO_NEGATIVE_EVAL, EXP_RATIONAL_POWER_EVAL, EXP_RATIONAL_EXPONENT_SIMPLIFY,
        EXP_RATIONAL_POWER_COMBO, EXP_GROWTH_DECAY_MODEL_CHOICE, EXP_SOLVE_EXPONENT_RADICAL, EXP_POWER_SUBSTITUTION_VALUE,
    )},
    **{op: "graph" for op in (
        GRAPH_SKETCH_TABLE, EXP_COMPARE_SAME_BASE, EXP_MODEL_FROM_GRAPH, GRAPH_PROPERTY_CHOICE,
        EXP_GRAPH_IDENTIFY_CHOICE, LOG_COMPARE_VALUES,
    )},
    **{op: "exp_equation" for op in (
        EXP_EQUATION_SAME_BASE, EXP_EQUATION_CONVERT_BASE, EXP_EQUATION_QUADRATIC_SUB, EXP_EQUATION_FACTOR_COMMON,
    )},
    **{op: "log" for op in (
        LOG_DEFINITION_EVAL, LOG_DOMAIN_VALIDITY_CHOICE, LOG_BASIC_PROPERTY_EVAL, LOG_RATIONAL_VALUE_EVAL,
        LOG_PRODUCT_QUOTIENT_EVAL, LOG_LINEAR_COMBINATION_EVAL, LOG_CHANGE_BASE_CHAIN_EVAL,
        LOG_CHANGE_BASE_PRODUCT_EVAL, LOG_EXPRESS_IN_AB, LOG_APPLICATION_STATEMENT_CHOICE, LOG_RECIPROCAL_SUM_PARAM,
        LOG_DEFINITION_INVERSE_EVAL, LOG_DECIBEL_APPLICATION, LOG_THRESHOLD_APPLICATION_CHOICE,
    )},
    **{op: "log_equation" for op in (
        LOG_EQUATION_LINEAR_ARG, LOG_EQUATION_PRODUCT_QUADRATIC, LOG_EQUATION_QUADRATIC_ARG,
        LOG_EQUATION_SOLVE_BASE, LOG_CURVE_THROUGH_POINTS,
    )},
    **{op: "common_log" for op in (
        COMMON_LOG_TABLE_LOOKUP, COMMON_LOG_GIVEN_APPROX_EVAL, LOG_CHARACTERISTIC_MANTISSA, LOG_CHARACTERISTIC_RULE,
        LOG_SCIENTIFIC_SHIFT, LOG_POWER_DIGIT_COUNT, LOG_POWER_FIRST_NONZERO, LOG_GROWTH_YEARS,
    )},
}


def hint_steps(op: str) -> tuple[str, ...]:
    return HINTS[_HINT_GROUP[op]]


_MAX_ATTEMPTS = 40


def build_exponential_logarithmic_matrix(seed: int | None = None, constraints: dict | None = None) -> dict[str, Any]:
    constraints = dict(constraints or {})
    example_id = constraints.get("textbook_example_id")
    spec = SOURCE_SPECS.get(int(example_id)) if example_id is not None else None
    op = str(constraints.get("op") or (spec or {}).get("op") or constraints.get("problem_type_id") or "")
    if op not in _BUILDERS:
        raise ValueError(f"unknown_op:{op}")
    slots = dict((spec or {}).get("slots") or {})
    slots.update(constraints.get("slots") or {})
    slots["op"] = op
    slots["presentation"] = str(constraints.get("presentation") or (spec or {}).get("presentation") or "short_answer")
    base_seed = 0 if seed is None else int(seed)
    salt = int(example_id) if spec else 0
    last_error: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        rng = random.Random(base_seed * 1009 + attempt + salt * 7919)
        try:
            matrix = _BUILDERS[op](rng, slots)
        except ValueError as exc:
            last_error = exc
            continue
        if not validate_exponential_logarithmic_matrix(matrix):
            last_error = ValueError(f"invalid_matrix:{op}")
            continue
        if spec:
            matrix["givens"]["textbook_example_id"] = int(example_id)
            matrix["givens"]["skill_id"] = spec["skill_id"]
        matrix["generation_attempt"] = attempt
        return matrix
    raise ValueError(f"exponential_logarithmic_generation_failed:{op}:{last_error}")


def validate_exponential_logarithmic_matrix(matrix: dict[str, Any]) -> bool:
    if matrix.get("domain_key") != DOMAIN_KEY or matrix.get("domain_operation") not in OPS:
        return False
    text = str(matrix.get("question_text") or "").strip()
    if not text:
        return False
    if SOURCE_LABEL_RE.search(text) or SOLUTION_MARKER_RE.search(text) or EQ_RESIDUE_RE.search(text):
        return False
    facts = matrix.get("validation_facts") or {}
    if facts.get("log_notation") != "common" and BARE_LOG_RE.search(text):
        return False
    answer = matrix.get("answer") if isinstance(matrix.get("answer"), dict) else {}
    value = answer.get("value")
    if isinstance(value, dict):
        if len(value) < 2 or any(not str(v).strip() for v in value.values()):
            return False
    elif not str(value or "").strip():
        return False
    if matrix.get("presentation_mode") == "single_choice":
        values = [row.get("value") for row in matrix.get("choices") or []]
        if len(values) != 4 or len(set(values)) != 4 or value not in values:
            return False
        label = matrix.get("correct_label")
        if [row.get("value") for row in matrix["choices"] if row.get("label") == label] != [value]:
            return False
    return True
