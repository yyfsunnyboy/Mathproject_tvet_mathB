from __future__ import annotations

from typing import Any

# Verified template families for short_answer + symbolic_condition + coordinate_point.
SYMBOLIC_QUADRANT_SHORT_ANSWER_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "A",
        "condition_text": "a<b<0",
        "stem_prefix": "若 $a<b<0$，且 $Q(ab,a+b)$",
        "target_label": "Q",
        "x_expr": "ab",
        "y_expr": "a+b",
        "answer": "第四象限",
        "derivation": [
            "a<0 且 b<0",
            "ab>0",
            "a+b<0",
            "所以 Q(ab,a+b) 在第四象限",
        ],
    },
    {
        "template_id": "B",
        "condition_text": "a<b<0",
        "stem_prefix": "若 $a<b<0$，且 $Q(a-b,ab)$",
        "target_label": "Q",
        "x_expr": "a-b",
        "y_expr": "ab",
        "answer": "第二象限",
        "derivation": [
            "a<0 且 b<0",
            "a-b<0",
            "ab>0",
            "所以 Q(a-b,ab) 在第二象限",
        ],
    },
    {
        "template_id": "C",
        "condition_text": "0<a<b",
        "stem_prefix": "若 $0<a<b$，且 $Q(a-b,ab)$",
        "target_label": "Q",
        "x_expr": "a-b",
        "y_expr": "ab",
        "answer": "第二象限",
        "derivation": [
            "0<a<b",
            "a-b<0",
            "ab>0",
            "所以 Q(a-b,ab) 在第二象限",
        ],
    },
    {
        "template_id": "D",
        "condition_text": "點 P(a,b) 位於第一象限且 a<b",
        "stem_prefix": "若點 $P(a,b)$ 位於第一象限且 $a<b$，則 $Q(a-b,a^2b)$",
        "target_label": "Q",
        "x_expr": "a-b",
        "y_expr": "a^2b",
        "answer": "第二象限",
        "derivation": [
            "a>0 且 b>0",
            "a<b",
            "a-b<0",
            "a^2b>0",
            "所以 Q(a-b,a^2b) 在第二象限",
        ],
    },
]


def build_symbolic_quadrant_metadata(template: dict[str, Any]) -> dict[str, Any]:
    variables = sorted({v for v in ("a", "b") if v in template["condition_text"] or v in template["x_expr"] or v in template["y_expr"]})
    return {
        "givens": [
            {
                "type": "symbolic_condition",
                "text": template["condition_text"],
                "variables": variables,
            }
        ],
        "target": {
            "type": "coordinate_point",
            "label": template["target_label"],
            "x_expr": template["x_expr"],
            "y_expr": template["y_expr"],
            "variables": variables,
        },
        "derivation": list(template["derivation"]),
    }


def build_symbolic_quadrant_question_text(template: dict[str, Any]) -> str:
    return f"{template['stem_prefix']}，請判斷 ${template['target_label']}$ 位於哪一象限？"


# Single-choice: quadrant statement judgment (source-style, symbolic labels only).
SYMBOLIC_STATEMENT_CHOICE_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "S1",
        "stem": "已知點 $P(a-b,ab)$ 在坐標平面的第四象限，下列敘述何者正確？",
        "correct": "$A(-a,b)$ 在第一象限",
        "wrongs": [
            "$B(|a|,b)$ 在第二象限",
            "$C(a,-b)$ 在第三象限",
            "$D(-a,-b)$ 在第四象限",
        ],
        "metadata": {
            "givens": [
                {
                    "type": "coordinate_point",
                    "text": "P(a-b,ab) 在第四象限",
                    "variables": ["a", "b"],
                }
            ],
            "target": {
                "type": "statement",
                "label": "A",
                "x_expr": "-a",
                "y_expr": "b",
                "variables": ["a", "b"],
            },
            "derivation": [
                "P 在第四象限 => a-b>0, ab<0",
                "a<0, b>0",
                "故 A(-a,b) 在第一象限",
            ],
        },
    },
    {
        "template_id": "S2",
        "stem": "若 $a<b<0$，下列關於點 $Q(ab,a+b)$ 的敘述何者正確？",
        "correct": "$Q(ab,a+b)$ 在第四象限",
        "wrongs": [
            "$Q(ab,a+b)$ 在第一象限",
            "$Q(ab,a+b)$ 在第二象限",
            "$Q(ab,a+b)$ 在第三象限",
        ],
        "metadata": {
            "givens": [
                {"type": "symbolic_condition", "text": "a<b<0", "variables": ["a", "b"]},
            ],
            "target": {
                "type": "coordinate_point",
                "label": "Q",
                "x_expr": "ab",
                "y_expr": "a+b",
                "variables": ["a", "b"],
            },
            "derivation": ["a<0,b<0", "ab>0,a+b<0", "故在第四象限"],
        },
    },
]
