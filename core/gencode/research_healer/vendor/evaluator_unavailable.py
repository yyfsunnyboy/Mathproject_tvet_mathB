# -*- coding: utf-8 -*-
"""Stand-in for the research evaluators, which do not exist in this repository.

The vendored runner wraps evaluator calls and turns this error into a
fail-closed ``evaluator_error``; the V3 adapter never supplies the research
``task`` / ``frozen`` context that would reach these functions.
"""

from __future__ import annotations

from typing import Any


class ResearchEvaluatorUnavailable(RuntimeError):
    pass


def classify_response(*_args: Any, **_kwargs: Any) -> Any:
    raise ResearchEvaluatorUnavailable("research math_boundary_pilot evaluator is not part of GenCode V3")


def classify_math16_response(*_args: Any, **_kwargs: Any) -> Any:
    raise ResearchEvaluatorUnavailable("research Math16 evaluator is not part of GenCode V3")
