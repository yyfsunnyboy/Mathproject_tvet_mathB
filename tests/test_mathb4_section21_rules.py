from core.textbook_processor import remap_mathb21_non_skill_examples, validate_problem_block_purity


def test_mathb21_set_basic_concepts_mapping():
    ex = {"problem_text": "設集合A、B，判斷元素是否屬於與子集關係"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "SetBasicConcepts"


def test_mathb21_set_operations_mapping():
    ex = {"problem_text": "求A與B的聯集、交集與補集"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "SetOperations"


def test_mathb21_counting_inclusion_exclusion_mapping():
    ex = {"problem_text": "調查有A或B、有兩者與兩者都沒有的人數"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "SetCountingInclusionExclusion"


def test_mathb21_sample_space_mapping():
    ex = {"problem_text": "擲兩枚硬幣，列出樣本空間S與所有樣本點"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "SampleSpace"


def test_mathb21_event_concepts_mapping():
    ex = {"problem_text": "說明事件、基本事件、全事件與餘事件"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "EventConcepts"


def test_mathb21_event_operations_mapping():
    ex = {"problem_text": "判斷A與B是否互斥，並求和事件與積事件"}
    out = remap_mathb21_non_skill_examples("2-1 樣本空間與事件", "綜合題", "review", ex)
    assert out == "EventOperations"


def test_set_question_missing_notation_marked_formula_missing():
    p = {"problem_text": "設集合，則下列敘述何者錯誤？(A) (B) (C)"}
    out = validate_problem_block_purity(p)
    assert out.get("needs_review") is True
    assert out.get("formula_missing") is True
