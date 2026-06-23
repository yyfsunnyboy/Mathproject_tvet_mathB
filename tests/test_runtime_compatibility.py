import pytest
from fractions import Fraction
from decimal import Decimal
from core.legacy_generator_adapter import (
    invoke_skill_generate,
    format_math_value,
    normalize_runtime_value
)

# Mock Modules to simulate various generate signatures

class MockZeroArgModule:
    @staticmethod
    def generate():
        return {"question_text": "Zero Args", "answer": 42}

class MockLevelArgModule:
    @staticmethod
    def generate(level):
        return {"question_text": f"Level {level}", "answer": 42}

class MockComponentArgModule:
    @staticmethod
    def generate(component_id):
        return {"question_text": f"Component {component_id}", "answer": 42}

class MockMultiArgModule:
    @staticmethod
    def generate(level, component_id=None):
        return {"question_text": f"Level {level} Component {component_id}", "answer": 42}

class MockKwargsModule:
    @staticmethod
    def generate(**kwargs):
        return {"question_text": "Kwargs", "kwargs": kwargs}

class MockTypeErrorInsideModule:
    @staticmethod
    def generate():
        # Raise real TypeError inside generate logic
        return "not a dict".split(1)  # splits on int, raises TypeError

def test_invoke_skill_generate_signatures():
    # Test zero args
    res_zero = invoke_skill_generate(MockZeroArgModule, level=2, component_id="comp_123", seed=42)
    assert res_zero["question_text"] == "Zero Args"

    # Test level arg
    res_level = invoke_skill_generate(MockLevelArgModule, level=3, component_id="comp_123", seed=42)
    assert res_level["question_text"] == "Level 3"

    # Test component arg
    res_comp = invoke_skill_generate(MockComponentArgModule, level=3, component_id="comp_456", seed=42)
    assert res_comp["question_text"] == "Component comp_456"

    # Test multi args
    res_multi = invoke_skill_generate(MockMultiArgModule, level=5, component_id="comp_789", seed=42)
    assert res_multi["question_text"] == "Level 5 Component comp_789"

    # Test kwargs
    res_kwargs = invoke_skill_generate(MockKwargsModule, level=4, component_id="comp_000", seed=123)
    assert res_kwargs["question_text"] == "Kwargs"
    assert res_kwargs["kwargs"]["level"] == 4
    assert res_kwargs["kwargs"]["component_id"] == "comp_000"
    assert res_kwargs["kwargs"]["seed"] == 123

    # Test TypeError preservation
    with pytest.raises(TypeError) as excinfo:
        invoke_skill_generate(MockTypeErrorInsideModule, level=1)
    # The TypeError should be from the splitting or arg mismatch inside generate logic, not adapter arg checking
    assert "descriptor 'split'" in str(excinfo.value) or "must be str" in str(excinfo.value) or "split" in str(excinfo.value)

def test_format_math_value():
    # Fractions
    assert format_math_value(Fraction(5, 1)) == "5"
    assert format_math_value(Fraction(3, 4)) == "3/4"
    assert format_math_value(Fraction(3, 4), decimal_places=2) == "0.75"

    # Decimal
    assert format_math_value(Decimal("1.5")) == "1.5"
    assert format_math_value(Decimal("1.5"), decimal_places=2) == "1.50"

    # Int & Float & Str
    assert format_math_value(42) == "42"
    assert format_math_value(3.14) == "3.14"
    assert format_math_value(3.14, decimal_places=1) == "3.1"
    assert format_math_value("raw string") == "raw string"

def test_normalize_runtime_value():
    payload = {
        "question_text": "Calculate",
        "answer": Fraction(3, 2),
        "choices": [Fraction(1, 2), Fraction(3, 2), Fraction(5, 2)],
        "details": {
            "val": Decimal("1.25")
        }
    }
    norm = normalize_runtime_value(payload)
    assert norm["answer"] == "3/2"
    assert norm["choices"] == ["1/2", "3/2", "5/2"]
    assert norm["details"]["val"] == 1.25
