import core.textbook_processor as processor


def test_mathb31_remap_statistical_basic_concepts():
    ex = {"problem_text": "請說明敘述統計與推論統計的差異"}
    out = processor.remap_mathb31_non_skill_examples("3-1 統計的基本概念", "綜合題", "review", ex)
    assert out == "MeaningOfStatistics"


def test_mathb31_remap_sampling_survey():
    ex = {"problem_text": "母群體、樣本、母群體數與樣本數的定義"}
    out = processor.remap_mathb31_non_skill_examples("3-1 統計的基本概念", "綜合題", "review", ex)
    assert out == "SamplingSurvey"


def test_mathb31_remap_sampling_methods():
    ex = {"problem_text": "此情境應採用分層隨機抽樣或系統抽樣？"}
    out = processor.remap_mathb31_non_skill_examples("3-1 統計的基本概念", "綜合題", "review", ex)
    assert out == "SamplingMethods"


def test_source_type_handwork_is_textbook_practice():
    item = {"title": "動動手 1"}
    assert processor.normalize_source_type_by_title(item, default_source_type="in_class_practice") == "textbook_practice"
