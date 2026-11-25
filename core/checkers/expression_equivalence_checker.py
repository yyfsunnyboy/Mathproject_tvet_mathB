from __future__ import annotations

import logging
import math
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

MAX_INPUT_LEN = 200
_SAFE_CHARS = re.compile(r"^[0-9a-zA-Z+\-*/^=().,_\s\\{}$√]+$")

_FRAC_LATEX = re.compile(r"\\?frac\s*\{([^{}]+)\}\{([^{}]+)\}", re.IGNORECASE)
_SQRT_LATEX_BRACE = re.compile(r"\\sqrt\s*\{([^{}]+)\}", re.IGNORECASE)
_SQRT_LATEX_PAREN = re.compile(r"\\sqrt\s*\(([^()]+)\)", re.IGNORECASE)
_SQRT_LATEX_DIGIT = re.compile(r"\\sqrt\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
_SQRT_UNICODE = re.compile(r"√\(([^()]+)\)")
_SQRT_UNICODE_DIGIT = re.compile(r"√([0-9]+(?:\.[0-9]+)?)")
_SQRT_ASCII_BRACE = re.compile(r"sqrt\s*\{([^{}]+)\}", re.IGNORECASE)
_IMPLICIT_COEF = re.compile(r"(\d)\s*sqrt", re.IGNORECASE)
_IMPLICIT_AFTER_PAREN = re.compile(r"\)\s*sqrt", re.IGNORECASE)
_DEGREE_MARK = r"(?:°|∘|\^\s*\{?\s*\\circ\s*\}?)"
_TRIG_DEGREE_PAREN = re.compile(
    r"(sin|cos|tan|cot|sec|csc)\s*\(\s*(-?\d+(?:\.\d+)?)\s*" + _DEGREE_MARK + r"\s*\)", re.IGNORECASE
)
_TRIG_DEGREE_BARE = re.compile(
    r"(sin|cos|tan|cot|sec|csc)\s*(-?\d+(?:\.\d+)?)\s*" + _DEGREE_MARK, re.IGNORECASE
)
# Trailing semantic units (only after a digit or closing paren; never strip identifiers).
_UNIT_TAIL = re.compile(r"(?<=[\d)\]])\s*(?:公尺|米|次|度|°|∘|m)\s*$", re.IGNORECASE)
_SINGLE_ASSIGNMENT = re.compile(
    r"^\s*([A-Za-z])\s*=\s*(.+?)\s*$",
)


def normalize_math_expression(text: object) -> str:
    """Normalize LaTeX / ascii / unicode radical forms to sympy-friendly text."""
    from core.checkers.math_input_normalization import latex_to_plain

    s = unicodedata.normalize("NFKC", latex_to_plain(text))
    if not s:
        return ""
    # Degree marks are dropped below (degree-valued answers); trig arguments in
    # degrees must become radians first or `tan20°` would mean tan(20 rad).
    s = _TRIG_DEGREE_PAREN.sub(r"\1((\2)*pi/180)", s)
    s = _TRIG_DEGREE_BARE.sub(r"\1((\2)*pi/180)", s)
    s = (
        s.replace("$", "")
        .replace("−", "-")
        .replace("－", "-")
        .replace("×", "*")
        .replace("·", "*")
        .replace("（", "(")
        .replace("）", ")")
        .replace("＝", "=")
        .replace("，", ",")
        .replace("π", "pi")
        .replace("𝜋", "pi")
        .replace("°", "")
        .replace("∘", "")
        .replace("{}^\\circ", "")
        .replace("^\\circ", "")
        .replace("^{\\circ}", "")
    )
    if s.endswith("度"):
        s = s[:-1]
    s = _UNIT_TAIL.sub("", s)
    for _ in range(3):
        s = _FRAC_LATEX.sub(r"((\1)/(\2))", s)
        s = _SQRT_LATEX_BRACE.sub(r"sqrt(\1)", s)
        s = _SQRT_LATEX_PAREN.sub(r"sqrt(\1)", s)
        s = _SQRT_LATEX_DIGIT.sub(r"sqrt(\1)", s)
        s = _SQRT_UNICODE.sub(r"sqrt(\1)", s)
        s = _SQRT_UNICODE_DIGIT.sub(r"sqrt(\1)", s)
        s = _SQRT_ASCII_BRACE.sub(r"sqrt(\1)", s)
    s = s.replace("{", "(").replace("}", ")")
    s = s.replace("\\", "")
    s = _IMPLICIT_COEF.sub(r"\1*sqrt", s)
    s = _IMPLICIT_AFTER_PAREN.sub(r")*sqrt", s)
    s = re.sub(r"\s+", "", s)
    s = s.lower()
    s = re.sub(r"(\d)pi", r"\1*pi", s)
    s = re.sub(r"pi(\d)", r"pi*\1", s)
    return s


def _looks_safe(text: str) -> bool:
    t = str(text or "").strip()
    if not t or len(t) > MAX_INPUT_LEN:
        return False
    if not _SAFE_CHARS.match(t):
        return False
    balance = 0
    for ch in t:
        if ch == "(":
            balance += 1
        elif ch == ")":
            balance -= 1
            if balance < 0:
                return False
    return balance == 0


def _parse_sympy(text: str) -> Any:
    from sympy import Rational, sqrt, sympify
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )

    norm = normalize_math_expression(text)
    if not norm or not _looks_safe(norm):
        raise ValueError("unsafe_or_empty_expression")
    local_dict = {"sqrt": sqrt, "pi": sympify("pi")}
    transformations = standard_transformations + (
        convert_xor,
        implicit_multiplication_application,
    )
    return parse_expr(norm, local_dict=local_dict, transformations=transformations, evaluate=True)


def _numeric_equal(lhs: Any, rhs: Any, *, tol: float = 1e-9) -> bool:
    try:
        from sympy import N

        a = complex(N(lhs))
        b = complex(N(rhs))
        if math.isfinite(a.real) and math.isfinite(b.real) and abs(a.imag) < tol and abs(b.imag) < tol:
            return math.isclose(float(a.real), float(b.real), rel_tol=tol, abs_tol=tol)
        return math.isclose(a.real, b.real, rel_tol=tol, abs_tol=tol) and math.isclose(
            a.imag, b.imag, rel_tol=tol, abs_tol=tol
        )
    except Exception:
        return False


_FULLY_FACTORIZED_FORMS = frozenset({"fully_factorized", "completely_factorized"})
_FACTORIZED_FORMS = frozenset(
    {"factorized", "factored", "factorization", "factored_expression", "factorized_expression"}
    | _FULLY_FACTORIZED_FORMS
)
_FACTORIZED_EQUIVS = frozenset({"factorized_form", "required_factorized_form"})
_PI_FORMS = frozenset({"pi_expression", "radian_pi", "contains_pi", "pi_form"})
_SIMPLIFIED_TRIG_FORMS = frozenset({"simplified_trig", "fundamental_trig_simplified"})
_EXPANDED_FORMS = frozenset({"expanded", "expanded_polynomial"})
_SIMPLEST_RADICAL_FORMS = frozenset({"simplest_radical", "simplified_radical"})
_RADICAL_NOTATION_FORMS = frozenset({"radical_notation", "radical_form"})
_SCIENTIFIC_NOTATION_FORMS = frozenset({"scientific_notation", "scientific_form"})
_SCI_NOTATION_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?)\s*(?:\\times|\\cdot|×|\*|x)\s*10\s*\^\s*(?:\{\s*[+-]?\d+\s*\}|[+-]?\d+)\s*$"
)


def _is_scientific_notation_answer(user_raw: str, significant_digits: Any = None) -> bool:
    """a×10^n with 1 <= |a| < 10 and, when the contract gives it, exactly that many significant digits."""
    match = _SCI_NOTATION_RE.match(str(user_raw or ""))
    if not match:
        return False
    mantissa = match.group(1).lstrip("+-")
    if not (1 <= float(mantissa) < 10):
        return False
    if significant_digits in (None, ""):
        return True
    return len(mantissa.replace(".", "")) == int(significant_digits)


def _is_radical_notation_answer(user_raw: str) -> bool:
    """Written with radical signs only: no fractional/decimal exponent such as ``3^{1/2}``."""
    text = str(user_raw or "")
    for match in re.finditer(r"\^|\*\*", text):
        rest = text[match.end():].lstrip()
        if rest.startswith("{"):
            depth, end = 0, 0
            for i, ch in enumerate(rest):
                depth += (ch == "{") - (ch == "}")
                if depth == 0:
                    end = i
                    break
            exponent = rest[1:end] if end else rest[1:]
        elif rest.startswith("("):
            end = rest.find(")")
            exponent = rest[1:end] if end > 0 else rest[1:]
        else:
            exponent = re.match(r"[-+]?[\w.\\]*", rest).group(0)
        if re.search(r"[/.]|\\frac|\\sqrt|sqrt", exponent):
            return False
    return True


def contract_requires_pi_form(
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """AST-based π required-form is contract-driven, not a string substring test."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    required = str(ac.get("required_form") or pl.get("required_form") or "").strip().lower()
    if required in _PI_FORMS:
        return True
    shape = str(ac.get("answer_shape") or pl.get("answer_shape") or "").strip().lower()
    return shape in _PI_FORMS


def contract_requires_factorized_form(
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Required-form is contract-driven, not skill/example specific."""
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    pl = payload if isinstance(payload, dict) else {}
    required = str(ac.get("required_form") or pl.get("required_form") or "").strip().lower()
    if required in _FACTORIZED_FORMS:
        return True
    shape = str(ac.get("answer_shape") or pl.get("answer_shape") or "").strip().lower()
    if shape in _FACTORIZED_FORMS:
        return True
    equiv = str(
        ac.get("answer_equivalence")
        or ac.get("equivalence_type")
        or pl.get("equivalence")
        or pl.get("equivalence_type")
        or ""
    ).strip().lower()
    if equiv in _FACTORIZED_EQUIVS:
        return True
    problem_type = str(
        ac.get("problem_type_id") or pl.get("problem_type_id") or ""
    ).strip().lower()
    return "factoring" in problem_type or "factorization" in problem_type


_ASSIGNMENT_JOINERS = re.compile(r"\s*(?:且|、|;|；|\band\b)\s*", re.IGNORECASE)
_VALUE_LIST_SEPARATORS = ("或", ",", "、", ";")
_SAME_VAR_PREFIX = re.compile(r"^([A-Za-z])\s*=\s*(.+)$")
# Space / fullwidth-space between adjacent `name=value` pairs (before space stripping).
_ASSIGNMENT_SPACE_GAP = re.compile(r"([^=,\s])\s+([A-Za-z]+\s*=)")
# Ordered unlabeled numeric/rational tokens (negatives, decimals, fractions).
_ORDERED_VALUE_TOKEN = re.compile(
    r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:\s*/\s*\d+(?:\.\d+)?)?"
)


def _split_value_list(text: object) -> tuple[list[str], set[str]] | None:
    """Split a multi-valued answer (`1 或 21`, `[-9, 3]`, `x=±13`) into value strings.

    Returns None for single values and for lists naming different variables
    (those are assignment lists, handled separately).
    """
    from core.checkers.inequality_solution_checker import _split_top_level
    from core.checkers.math_input_normalization import latex_to_plain

    s = latex_to_plain(text)
    s = re.sub(r"(?i)\s+or\s+", " 或 ", s).strip()
    if len(s) >= 2 and s[0] == "[" and s[-1] == "]":
        s = s[1:-1].strip()
    parts = _split_top_level(s, _VALUE_LIST_SEPARATORS) or ([s] if s else [])
    values: list[str] = []
    names: set[str] = set()
    for part in parts:
        part = part.strip()
        m = _SAME_VAR_PREFIX.match(part)
        if m:
            names.add(m.group(1).lower())
            part = m.group(2).strip()
        if "=" in part or not part:
            return None
        if part.count("±") == 1:
            head, tail = part.split("±")
            head, tail = head.strip(), tail.strip()
            if not tail:
                return None
            values.extend([f"{head}+({tail})", f"{head}-({tail})"] if head else [tail, f"-({tail})"])
        else:
            values.append(part)
    if len(values) < 2 or len(names) > 1:
        return None
    return values, names


def _strip_trailing_units(text: object) -> str:
    """Drop trailing 度／公尺／m／次 when attached to a numeric/expression token."""
    from core.checkers.math_input_normalization import latex_to_plain

    s = unicodedata.normalize("NFKC", latex_to_plain(text)).strip()
    if not s:
        return ""
    prev = None
    while prev != s:
        prev = s
        s = _UNIT_TAIL.sub("", s).rstrip()
        if s.endswith("度"):
            s = s[:-1].rstrip()
    return s


def _split_single_assignment(text: object) -> tuple[str, str] | None:
    """Return (lhs_var, rhs) for a single `x=...` / `y=...` assignment; else None."""
    raw = _strip_trailing_units(text)
    if not raw or raw.count("=") != 1:
        return None
    m = _SINGLE_ASSIGNMENT.match(raw)
    if not m:
        return None
    rhs = m.group(2).strip()
    if not rhs or "=" in rhs:
        return None
    return m.group(1).lower(), rhs


def _scalar_assignment_or_rhs_equivalent(user_answer: object, correct_answer: object) -> bool | None:
    """Accept bare value / RHS-only when canonical is a single-variable assignment.

    Examples that PASS: ``2`` vs ``x=2``, ``a=1`` vs ``1``,
    ``2(x+1)^2-3`` vs ``y=2(x+1)^2-3``.
    Returns None when this rule does not apply.
    """
    ua = _strip_trailing_units(user_answer)
    ca = _strip_trailing_units(correct_answer)
    if not ua or not ca:
        return None
    user_asg = _split_single_assignment(ua)
    correct_asg = _split_single_assignment(ca)
    # Both bare (no assignment) → leave to generic expression compare.
    if user_asg is None and correct_asg is None:
        return None
    # Both assignments with different variables → not this rule
    # (e.g. a=1 vs b=1 should not silently pass here).
    if user_asg is not None and correct_asg is not None and user_asg[0] != correct_asg[0]:
        return False
    user_rhs = user_asg[1] if user_asg else ua
    correct_rhs = correct_asg[1] if correct_asg else ca
    # If the non-assignment side still contains '=', it is a full equation — not RHS-only.
    if (user_asg is None and "=" in ua) or (correct_asg is None and "=" in ca):
        return None
    try:
        from sympy import simplify

        diff = simplify(_parse_sympy(user_rhs) - _parse_sympy(correct_rhs))
        return bool(diff == 0 or _numeric_equal(_parse_sympy(user_rhs), _parse_sympy(correct_rhs)))
    except Exception:
        return None


def _value_list_equivalent(user_answer: object, correct_answer: object) -> bool | None:
    """Unordered multiset comparison for multi-valued answers; None if not a value list."""
    correct = _split_value_list(correct_answer)
    if correct is None:
        return None
    user = _split_value_list(user_answer)
    if user is None:
        return False
    user_vals, user_names = user
    correct_vals, correct_names = correct
    if user_names and correct_names and user_names != correct_names:
        return False
    if len(user_vals) != len(correct_vals):
        return False
    from sympy import simplify

    try:
        user_exprs = [_parse_sympy(v) for v in user_vals]
        remaining = [_parse_sympy(v) for v in correct_vals]
    except Exception:
        return None
    for expr in user_exprs:
        for idx, target in enumerate(remaining):
            if simplify(expr - target) == 0 or _numeric_equal(expr, target):
                remaining.pop(idx)
                break
        else:
            return False
    return True


def _preprocess_assignment_text(text: object) -> str:
    """Normalize punctuation / joiners while keeping assignment boundaries."""
    from core.checkers.math_input_normalization import latex_to_plain

    raw = unicodedata.normalize("NFKC", latex_to_plain(text)).strip()
    if not raw:
        return ""
    raw = (
        raw.replace("（", "(")
        .replace("）", ")")
        .replace("，", ",")
        .replace("、", ",")
        .replace("；", ";")
        .replace("＝", "=")
        .replace("−", "-")
        .replace("－", "-")
    )
    raw = _ASSIGNMENT_JOINERS.sub(",", raw)
    raw = _ASSIGNMENT_SPACE_GAP.sub(r"\1,\2", raw)
    return raw.strip()


def _strip_wrapping_group(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == "(" and text[-1] == ")":
        return text[1:-1].strip()
    return text


def _parse_assignment_map(text: object) -> dict[str, Any] | None:
    """Parse labeled assignment lists like `a=0,b=3` / `a=0 b=3` / `a=0 且 b=3`."""
    prepared = _preprocess_assignment_text(text)
    if not prepared or "=" not in prepared:
        return None
    norm = normalize_math_expression(prepared)
    if "=" not in norm:
        return None
    # Single assignment still counts when contract expects only one name, but
    # multipart "a,b 之值" answers are multi-key; require at least one `=`.
    mapping: dict[str, Any] = {}
    chunks = norm.split(",") if "," in norm else [norm]
    if len(chunks) < 2 and "," not in prepared and not re.search(r"[A-Za-z]+\s*=.+=", prepared):
        # Keep two-or-more variable lists as the authoritative assignment shape.
        # A lone `a=0` is not an ordered multi-value answer for this path.
        if len(chunks) == 1 and chunks[0].count("=") == 1:
            return None
    for chunk in chunks:
        if "=" not in chunk:
            return None
        key, raw_val = chunk.split("=", 1)
        if not re.fullmatch(r"[a-z]+", key) or not raw_val or key in mapping:
            return None
        mapping[key] = _parse_sympy(raw_val)
    return mapping or None


def _parse_ordered_value_list(text: object, *, expected_len: int) -> list[Any] | None:
    """Parse unlabeled ordered multi-values: `0,3` / `0 3` / `(0,3)` / fullwidth spaces.

    Only returns a list when the entire input is exactly `expected_len` scalar tokens.
    Does not split general algebra (`4x^2+4x-2`) or equations.
    """
    if expected_len < 2:
        return None
    prepared = _strip_wrapping_group(_preprocess_assignment_text(text))
    if not prepared or "=" in prepared:
        return None
    # Reject equation / inequality / set markers that are not ordered scalars.
    if any(ch in prepared for ch in ("<", ">", "{", "}", ":", "；", ";")):
        return None

    tokens: list[str]
    if "," in prepared:
        tokens = [part.strip() for part in prepared.split(",") if part.strip()]
    else:
        # Whitespace-separated only when there is no comma. Keep fractions intact.
        tokens = [part.strip() for part in re.split(r"\s+", prepared) if part.strip()]

    if len(tokens) != expected_len:
        return None
    values: list[Any] = []
    for token in tokens:
        compact = re.sub(r"\s+", "", token)
        if not _ORDERED_VALUE_TOKEN.fullmatch(compact):
            return None
        values.append(_parse_sympy(compact))
    return values


def _exprs_equivalent(lhs: Any, rhs: Any) -> bool:
    from sympy import simplify

    try:
        return simplify(lhs - rhs) == 0 or _numeric_equal(lhs, rhs)
    except Exception:
        return False


def ordered_variable_names_from_expected(text: object) -> list[str] | None:
    """Return ordered variable names when `text` is a labeled multi-assignment answer."""
    mapping = _parse_assignment_map(text)
    if mapping is None or len(mapping) < 2:
        return None
    prepared = _preprocess_assignment_text(text)
    names = [name.lower() for name in re.findall(r"([A-Za-z]+)\s*=", prepared)]
    if set(names) != set(mapping) or len(names) != len(mapping):
        return sorted(mapping.keys())
    return names


def _contract_variable_order(answer_contract: dict[str, Any] | None) -> list[str] | None:
    if not isinstance(answer_contract, dict):
        return None
    raw = (
        answer_contract.get("variable_order")
        or answer_contract.get("ordered_variable_names")
        or answer_contract.get("ordered_variables")
    )
    if not isinstance(raw, (list, tuple)) or len(raw) < 2:
        return None
    names = [str(item).strip().lower() for item in raw]
    if not all(re.fullmatch(r"[a-z]+", name or "") for name in names):
        return None
    if len(set(names)) != len(names):
        return None
    return names


def _assignment_lists_equivalent(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
) -> bool | None:
    """Compare ordered named multi-value answers.

    Activated when the canonical answer is a labeled assignment list
    (`a=0,b=3`) and/or `answer_contract.variable_order` is present.

    Accepts student forms:
      - labeled by name: `a=0,b=3`, `b=3,a=0`, `a=0 b=3`
      - unlabeled ordered by contract/canonical variable order: `0,3`, `0 3`, `(0,3)`

    Rejects reversed unlabeled order, wrong arity, and unknown labels.
    Does not treat the answer as an unordered set.
    """
    try:
        correct_map = _parse_assignment_map(correct_answer)
        contract_order = _contract_variable_order(answer_contract)
        if correct_map is None and contract_order is None:
            return None

        if correct_map is None:
            correct_values = _parse_ordered_value_list(correct_answer, expected_len=len(contract_order or []))
            if correct_values is None or not contract_order:
                return None
            correct_map = dict(zip(contract_order, correct_values))
            ordered_names = list(contract_order)
        else:
            if contract_order and set(contract_order) == set(correct_map):
                ordered_names = list(contract_order)
            else:
                # Preserve canonical textual order of variables.
                prepared = _preprocess_assignment_text(correct_answer)
                ordered_names = [name.lower() for name in re.findall(r"([A-Za-z]+)\s*=", prepared)]
                if set(ordered_names) != set(correct_map) or len(ordered_names) != len(correct_map):
                    ordered_names = sorted(correct_map.keys())

        user_map = _parse_assignment_map(user_answer)
        if user_map is not None:
            if set(user_map) != set(correct_map):
                return False
            return all(_exprs_equivalent(user_map[key], correct_map[key]) for key in correct_map)

        user_values = _parse_ordered_value_list(user_answer, expected_len=len(ordered_names))
        if user_values is None:
            # Canonical is an ordered multi-value answer; unmatched student form is wrong.
            return False
        return all(
            _exprs_equivalent(actual, correct_map[name])
            for actual, name in zip(user_values, ordered_names)
        )
    except Exception:
        return None


def _has_pi_symbol(expr: Any) -> bool:
    """True when the parsed expression contains sympy.pi (AST), not a 'pi' substring."""
    try:
        from sympy import pi as sympy_pi

        return bool(getattr(expr, "has", lambda _x: False)(sympy_pi))
    except Exception:
        return False


def _is_factorized_expression(expr: Any) -> bool:
    """True when the parsed expression is already a product of non-constant factors."""
    try:
        if expr is None:
            return False
        if not getattr(expr, "free_symbols", None):
            return True
        if expr.is_Mul:
            nonconst = [arg for arg in expr.args if getattr(arg, "free_symbols", None)]
            if len(nonconst) >= 2:
                return True
            return any(getattr(arg, "is_Pow", False) and arg.exp != 1 for arg in nonconst)
        if expr.is_Pow and expr.exp != 1:
            return True
        if expr.is_Add:
            try:
                from sympy import degree, Poly

                symbols = list(expr.free_symbols)
                if len(symbols) == 1:
                    return int(degree(Poly(expr, symbols[0]))) <= 1
            except Exception:
                return False
            return False
        return False
    except Exception:
        return False


def _is_fully_factorized_expression(expr: Any) -> bool:
    """Factorized and every non-constant factor is irreducible over the rationals."""
    if not _is_factorized_expression(expr):
        return False
    try:
        from sympy import Mul, factor_list

        for factor in Mul.make_args(expr):
            base = factor.base if factor.is_Pow else factor
            if not base.free_symbols:
                continue
            _, factors = factor_list(base)
            if len(factors) != 1 or factors[0][1] != 1:
                return False
        return True
    except Exception:
        return False


def _is_expanded_answer(user_raw: str, evaluated: Any) -> bool:
    """Written form has no product or power of a sum and its like terms are combined."""
    try:
        from sympy import Add, expand, preorder_traversal

        tree = _parse_sympy_unevaluated(user_raw)
        if any(
            (node.is_Mul or node.is_Pow) and any(arg.is_Add for arg in node.args)
            for node in preorder_traversal(tree)
        ):
            return False
        return len(Add.make_args(tree)) == len(Add.make_args(expand(evaluated)))
    except Exception:
        return False


def _parse_sympy_unevaluated(text: str) -> Any:
    """Parse without automatic simplification, so the written form is preserved."""
    from sympy import sqrt, sympify
    from sympy.core.parameters import evaluate
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )

    norm = normalize_math_expression(text)
    if not norm or not _looks_safe(norm):
        raise ValueError("unsafe_or_empty_expression")
    transformations = standard_transformations + (convert_xor, implicit_multiplication_application)
    with evaluate(False):
        return parse_expr(
            norm,
            local_dict={"sqrt": sqrt, "pi": sympify("pi")},
            transformations=transformations,
            evaluate=False,
        )


def _is_simplest_radical_answer(user_raw: str, evaluated: Any) -> bool:
    """Written form has squarefree integer radicands, no radical denominators,
    no unexpanded products of sums, and like terms already combined."""
    try:
        from sympy import Add, Rational, factorint, preorder_traversal

        tree = _parse_sympy_unevaluated(user_raw)
        if len(Add.make_args(tree)) != len(Add.make_args(evaluated)):
            return False
        for node in preorder_traversal(tree):
            if not (node.is_Mul or node.is_Pow):
                continue
            if any(arg.is_Add for arg in node.args):
                return False
            if not node.is_Pow:
                continue
            base, exponent = node.args
            if isinstance(exponent, Rational) and exponent.q == 2:
                if not (base.is_Integer and base > 1 and all(e == 1 for e in factorint(int(base)).values())):
                    return False
            elif exponent.is_negative and any(
                sub.is_Pow and isinstance(sub.args[1], Rational) and sub.args[1].q == 2
                for sub in preorder_traversal(base)
            ):
                return False
        return True
    except Exception:
        return False


def _is_simplified_trig_expression(expr: Any) -> bool:
    """AST/structural check that a trig expression is already simplified."""
    try:
        from sympy import trigsimp

        simplified = trigsimp(expr, method="fu")
        return bool(expr == simplified)
    except Exception:
        return False


def check_expression_equivalence_debug(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    require_factorized: bool | None = None,
) -> dict[str, Any]:
    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    out: dict[str, Any] = {
        "correct": False,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
        "error_code": "",
        "required_form_failed": False,
    }
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out

    # Vector-valued oracles: accept keyboard-friendly forms before generic math parse.
    from core.checkers.vector_answer_normalization import try_check_vector_answer

    vector_debug = try_check_vector_answer(
        ua_raw,
        ca_raw,
        answer_contract=answer_contract,
        payload=payload,
    )
    if vector_debug is not None:
        out.update({k: v for k, v in vector_debug.items() if k != "correct"})
        out["correct"] = bool(vector_debug.get("correct"))
        if vector_debug.get("format_hint"):
            out["format_hint"] = vector_debug.get("format_hint")
        return out

    out["normalized_user_expression"] = normalize_math_expression(ua_raw)
    out["normalized_correct_expression"] = normalize_math_expression(ca_raw)
    need_form = (
        require_factorized
        if require_factorized is not None
        else contract_requires_factorized_form(answer_contract, payload)
    )
    need_pi_form = contract_requires_pi_form(answer_contract, payload)
    required_form = str(
        (answer_contract or {}).get("required_form")
        or (payload or {}).get("required_form")
        or ""
    ).strip().lower()
    need_simplified_trig = required_form in _SIMPLIFIED_TRIG_FORMS

    assign_eq = _assignment_lists_equivalent(
        ua_raw,
        ca_raw,
        answer_contract=answer_contract if isinstance(answer_contract, dict) else None,
    )
    if assign_eq is True:
        out["correct"] = True
        out["simplify_result"] = "assignment_list_equivalent"
        return out
    if assign_eq is False:
        out["correct"] = False
        out["simplify_result"] = "assignment_list_mismatch"
        return out

    list_eq = _value_list_equivalent(ua_raw, ca_raw)
    if list_eq is not None:
        out["correct"] = list_eq
        out["simplify_result"] = "value_list_equivalent" if list_eq else "value_list_mismatch"
        return out

    # Units / single-var assignment / RHS-only (求 x、求函數式右側).
    ua_units = _strip_trailing_units(ua_raw)
    ca_units = _strip_trailing_units(ca_raw)
    if ua_units != ua_raw or ca_units != ca_raw:
        out["normalized_user_expression"] = normalize_math_expression(ua_units)
        out["normalized_correct_expression"] = normalize_math_expression(ca_units)
        ua_raw, ca_raw = ua_units, ca_units

    asg_eq = _scalar_assignment_or_rhs_equivalent(ua_raw, ca_raw)
    if asg_eq is not None:
        out["correct"] = bool(asg_eq)
        out["simplify_result"] = (
            "scalar_assignment_or_rhs_equivalent" if asg_eq else "scalar_assignment_or_rhs_mismatch"
        )
        return out

    # Full equations (incl. circle / unicode superscripts already normalized).
    if "=" in normalize_math_expression(ua_raw) and "=" in normalize_math_expression(ca_raw):
        eq_dbg = check_equation_equivalence_debug(ua_raw, ca_raw)
        out.update({k: v for k, v in eq_dbg.items() if k in out or k in ("correct", "simplify_result", "parser_error", "error_code")})
        out["correct"] = bool(eq_dbg.get("correct"))
        if eq_dbg.get("simplify_result"):
            out["simplify_result"] = eq_dbg["simplify_result"]
        return out

    try:
        user_expr = _parse_sympy(ua_raw)
        correct_expr = _parse_sympy(ca_raw)
        from sympy import simplify

        diff = simplify(user_expr - correct_expr)
        out["simplify_result"] = str(diff)
        algebraically_equal = diff == 0 or _numeric_equal(user_expr, correct_expr)
        if not algebraically_equal:
            out["correct"] = False
            return out
        if need_form and not _is_factorized_expression(user_expr):
            out["correct"] = False
            out["required_form_failed"] = True
            out["simplify_result"] = "required_form_failed"
            return out
        if need_pi_form and not _has_pi_symbol(user_expr):
            out["correct"] = False
            out["required_form_failed"] = True
            out["simplify_result"] = "required_form_failed"
            return out
        if need_simplified_trig and not _is_simplified_trig_expression(user_expr):
            out["correct"] = False
            out["required_form_failed"] = True
            out["simplify_result"] = "required_form_failed"
            return out
        if (
            (required_form in _FULLY_FACTORIZED_FORMS and not _is_fully_factorized_expression(user_expr))
            or (required_form in _EXPANDED_FORMS and not _is_expanded_answer(ua_raw, user_expr))
            or (required_form in _SIMPLEST_RADICAL_FORMS and not _is_simplest_radical_answer(ua_raw, user_expr))
            or (required_form in _RADICAL_NOTATION_FORMS and not _is_radical_notation_answer(ua_raw))
            or (
                required_form in _SCIENTIFIC_NOTATION_FORMS
                and not _is_scientific_notation_answer(
                    ua_raw,
                    (answer_contract or {}).get("significant_digits") or (payload or {}).get("significant_digits"),
                )
            )
        ):
            out["correct"] = False
            out["required_form_failed"] = True
            out["simplify_result"] = "required_form_failed"
            return out
        out["correct"] = True
        return out
    except Exception as ex:
        if out["normalized_user_expression"] == out["normalized_correct_expression"]:
            out["correct"] = True
            out["simplify_result"] = "normalized_identity"
            return out
        out["parser_error"] = str(ex)
        out["error_code"] = "ANSWER_PARSE_FAILED"
        out["correct"] = False
        return out


def check_expression_equivalence_answer(
    user_answer: object,
    correct_answer: object,
    *,
    answer_contract: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    require_factorized: bool | None = None,
) -> bool:
    return bool(
        check_expression_equivalence_debug(
            user_answer,
            correct_answer,
            answer_contract=answer_contract,
            payload=payload,
            require_factorized=require_factorized,
        ).get("correct")
    )


def check_equation_equivalence_debug(
    user_answer: object,
    correct_answer: object,
) -> dict[str, Any]:
    """Equation equivalence: same solution set / constant-multiple of (lhs-rhs)."""
    out: dict[str, Any] = {
        "correct": False,
        "normalized_user_expression": "",
        "normalized_correct_expression": "",
        "parser_error": "",
        "simplify_result": "",
        "error_code": "",
    }
    ua_raw = str(user_answer or "").strip()
    ca_raw = str(correct_answer or "").strip()
    if not ua_raw or not ca_raw:
        out["parser_error"] = "empty_answer"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out
    out["normalized_user_expression"] = normalize_math_expression(ua_raw)
    out["normalized_correct_expression"] = normalize_math_expression(ca_raw)
    if "=" not in out["normalized_user_expression"] or "=" not in out["normalized_correct_expression"]:
        out["parser_error"] = "not_an_equation"
        out["error_code"] = "ANSWER_PARSE_FAILED"
        return out

    try:
        from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer

        if check_linear_equation_equivalent_answer(user_answer, correct_answer):
            out["correct"] = True
            out["simplify_result"] = "linear_equation_equivalent"
            return out
    except Exception:
        pass

    try:
        from sympy import simplify

        def _diff_poly(text: str) -> Any:
            left, right = normalize_math_expression(text).split("=", 1)
            return _parse_sympy(left) - _parse_sympy(right)

        user_diff = _diff_poly(ua_raw)
        correct_diff = _diff_poly(ca_raw)
        if simplify(correct_diff) == 0:
            out["correct"] = bool(simplify(user_diff) == 0)
            out["simplify_result"] = "identity_equation"
            return out
        ratio = simplify(user_diff / correct_diff)
        out["simplify_result"] = str(ratio)
        out["correct"] = bool(getattr(ratio, "is_number", False) and ratio != 0)
        return out
    except Exception as ex:
        out["parser_error"] = str(ex)
        out["error_code"] = "ANSWER_PARSE_FAILED"
        out["correct"] = False
        return out


def check_equation_equivalence_answer(user_answer: object, correct_answer: object) -> bool:
    return bool(check_equation_equivalence_debug(user_answer, correct_answer).get("correct"))
