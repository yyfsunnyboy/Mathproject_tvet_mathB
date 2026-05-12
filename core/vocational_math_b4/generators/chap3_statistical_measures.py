"""Generators for B4 Chapter 3 Statistical Measures (Phase 7B/Graph-1)."""

import random
import math
import io
import base64
import json
import hashlib
from typing import Dict, Any, Optional, Set, Tuple, List
import matplotlib.pyplot as plt

from core.vocational_math_b4.domain.b4_validators import validate_parameter_tuple_not_seen

_LAST_SAMPLING_METHODS_PARAMETER_SIGNATURE: Optional[str] = None
_LAST_STATISTICAL_BASIC_CONCEPT_SCENARIO_ID: Optional[str] = None
_LAST_SAMPLING_SURVEY_SCENARIO_ID: Optional[str] = None
_LAST_SAMPLING_SURVEY_PARAMETER_SIGNATURE: Optional[str] = None
_LAST_DATA_ORG_SCENARIO_ID: Optional[str] = None
_LAST_DATA_ORG_PARAMETER_SIGNATURE: Optional[str] = None
_LAST_TREE_DIAGRAM_SCENARIO_ID: Optional[str] = None
_LAST_TREE_DIAGRAM_PARAMETER_SIGNATURE: Optional[str] = None

SAMPLING_METHODS_CHOICES = [
    "1. 簡單隨機抽樣",
    "2. 系統抽樣",
    "3. 分層隨機抽樣",
    "4. 部落抽樣",
]

SAMPLING_METHODS_CLASSIFICATION_CONTEXTS: Dict[str, List[Dict[str, str]]] = {
    "simple_random": [
        {
            "scenario_id": "sampling_method_identification_random_lottery",
            "template_id": "classification_simple_random_lottery",
            "stem": "學校要抽查學生問卷，先將全校學生編號後以抽籤方式抽出受訪者。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "1",
        },
        {
            "scenario_id": "sampling_method_identification_random_ticket_draw",
            "template_id": "classification_simple_random_ticket_draw",
            "stem": "活動主辦單位把所有參加者名字放入箱中，隨機摸出若干人做滿意度訪談。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "1",
        },
        {
            "scenario_id": "sampling_method_identification_random_number_table",
            "template_id": "classification_simple_random_number_table",
            "stem": "研究者先將名單編號，再用亂數表抽出樣本。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "1",
        },
    ],
    "systematic": [
        {
            "scenario_id": "sampling_method_identification_systematic_interval",
            "template_id": "classification_systematic_interval",
            "stem": "{context}從第 {start} 個開始，每隔 {interval} 個抽 1 個{target}檢查。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "2",
        },
        {
            "scenario_id": "sampling_method_identification_systematic_page",
            "template_id": "classification_systematic_page",
            "stem": "出版社檢查印刷品質時，從第 {start} 本開始，每隔 {interval} 本抽 1 本。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "2",
        },
        {
            "scenario_id": "sampling_method_identification_systematic_vehicle",
            "template_id": "classification_systematic_vehicle",
            "stem": "交通調查時，從第 {start} 輛車開始，每隔 {interval} 輛車攔檢一輛。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "2",
        },
    ],
    "stratified": [
        {
            "scenario_id": "sampling_method_identification_stratified_grade",
            "template_id": "classification_stratified_grade",
            "stem": "調查學生升學意向時，先按年級分層，再依各層人數比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "3",
        },
        {
            "scenario_id": "sampling_method_identification_stratified_gender",
            "template_id": "classification_stratified_gender",
            "stem": "調查通勤習慣時，先按性別分層，再依各層比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "3",
        },
        {
            "scenario_id": "sampling_method_identification_stratified_income",
            "template_id": "classification_stratified_income",
            "stem": "調查消費行為時，先按收入層級分層，再做比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "3",
        },
    ],
    "cluster": [
        {
            "scenario_id": "sampling_method_identification_cluster_class",
            "template_id": "classification_cluster_class",
            "stem": "研究者先抽出若干班級，再調查被抽中班級內所有學生。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "4",
        },
        {
            "scenario_id": "sampling_method_identification_cluster_community",
            "template_id": "classification_cluster_community",
            "stem": "研究者先抽出若干社區，再調查被抽中社區內所有住戶。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "4",
        },
        {
            "scenario_id": "sampling_method_identification_cluster_department",
            "template_id": "classification_cluster_department",
            "stem": "公司先抽出若干部門，再調查被抽中部門的全部員工。這屬於哪一種抽樣方法？請輸入選項代號。",
            "answer": "4",
        },
    ],
}

SYSTEMATIC_IDENTIFICATION_CONTEXTS: List[Dict[str, str]] = [
    {"context": "工廠品管", "target": "產品"},
    {"context": "出版社抽查", "target": "書本"},
    {"context": "學校作業抽查", "target": "作業"},
    {"context": "電話簿調查", "target": "電話號碼"},
    {"context": "車輛攔檢", "target": "汽車"},
]

SYSTEMATIC_INTERVAL_NUMERIC_POOL: List[Tuple[int, int]] = [
    (300, 30),
    (600, 60),
    (800, 40),
    (1000, 50),
    (1200, 40),
    (1500, 50),
    (2000, 100),
]

STRATIFIED_ALLOCATION_NUMERIC_POOL: List[Dict[str, Any]] = [
    {"scenario_id": "stratified_allocation_grade_120_80_100", "layers": [("一年級", 120), ("二年級", 80), ("三年級", 100)], "sample_total": 30, "target_idx": 0},
    {"scenario_id": "stratified_allocation_grade_150_90_60", "layers": [("一年級", 150), ("二年級", 90), ("三年級", 60)], "sample_total": 60, "target_idx": 1},
    {"scenario_id": "stratified_allocation_gender_180_120", "layers": [("男生", 180), ("女生", 120)], "sample_total": 50, "target_idx": 1},
    {"scenario_id": "stratified_allocation_department_200_160_140", "layers": [("商業群", 200), ("工業群", 160), ("設計群", 140)], "sample_total": 50, "target_idx": 2},
    {"scenario_id": "stratified_allocation_income_240_180_180", "layers": [("低收入層", 240), ("中收入層", 180), ("高收入層", 180)], "sample_total": 60, "target_idx": 0},
    {"scenario_id": "stratified_allocation_region_300_180_120", "layers": [("北區", 300), ("中區", 180), ("南區", 120)], "sample_total": 60, "target_idx": 1},
]

STATISTICAL_BASIC_CONCEPT_SCENARIOS: List[Dict[str, Any]] = [
    {
        "scenario_id": "descriptive_statistics_identification",
        "question_text": "計算一組資料的平均數、中位數、標準差，用來描述這組資料的特性，屬於何者？請輸入選項代號。",
        "answer": "1",
        "choices": ["1. 敘述統計", "2. 推論統計", "3. 普查", "4. 抽查"],
        "explanation": "題目只在描述已取得資料的特性，沒有由部分資料推估整體，因此屬於敘述統計。",
    },
    {
        "scenario_id": "inferential_statistics_identification",
        "question_text": "根據抽出的 200 位學生資料，推估全校學生平均身高，這屬於敘述統計或推論統計中的何者？請輸入選項代號。",
        "answer": "2",
        "choices": ["1. 敘述統計", "2. 推論統計", "3. 資料陳示", "4. 資料整理"],
        "explanation": "由部分學生資料推估全校情況，是由部分資料推論整體，屬於推論統計。",
    },
    {
        "scenario_id": "statistics_process_collect_data",
        "question_text": "統計研究通常包含蒐集、整理、陳示、分析、解釋。取得原始資料屬於哪一步？請輸入選項代號。",
        "answer": "1",
        "choices": ["1. 蒐集", "2. 整理", "3. 分析", "4. 解釋"],
        "explanation": "取得原始資料是統計流程起點，屬於蒐集。",
    },
    {
        "scenario_id": "statistics_process_organize_data",
        "question_text": "將問卷得到的原始資料分組並整理成一覽資料，屬於統計研究的哪一步？請輸入選項代號。",
        "answer": "2",
        "choices": ["1. 蒐集", "2. 整理", "3. 分析", "4. 解釋"],
        "explanation": "把資料分類、分組、整理，是整理資料。",
    },
    {
        "scenario_id": "statistics_process_present_data",
        "question_text": "把整理後資料畫成長條圖或折線圖，屬於統計研究的哪一步？請輸入選項代號。",
        "answer": "3",
        "choices": ["1. 蒐集", "2. 整理", "3. 陳示", "4. 解釋"],
        "explanation": "用圖表呈現資料屬於陳示。",
    },
    {
        "scenario_id": "statistics_process_analyze_data",
        "question_text": "根據平均數與標準差比較兩組資料差異，屬於統計研究的哪一步？請輸入選項代號。",
        "answer": "3",
        "choices": ["1. 蒐集", "2. 陳示", "3. 分析", "4. 普查"],
        "explanation": "利用統計量比較資料特性屬於分析。",
    },
    {
        "scenario_id": "statistics_process_interpret_data",
        "question_text": "根據分析結果說明可能原因並提出結論，屬於統計研究的哪一步？請輸入選項代號。",
        "answer": "4",
        "choices": ["1. 蒐集", "2. 整理", "3. 陳示", "4. 解釋"],
        "explanation": "對分析結果做判讀並形成結論屬於解釋。",
    },
    {
        "scenario_id": "census_vs_sample_survey_census",
        "question_text": "若學校想了解全校學生通勤方式，直接詢問每一位學生，這屬於何者？請輸入選項代號。",
        "answer": "1",
        "choices": ["1. 普查", "2. 抽查", "3. 推論統計", "4. 陳示資料"],
        "explanation": "調查全部對象屬於普查。",
    },
    {
        "scenario_id": "census_vs_sample_survey_sample",
        "question_text": "若學校只訪問部分學生來了解通勤方式，這屬於何者？請輸入選項代號。",
        "answer": "2",
        "choices": ["1. 普查", "2. 抽查", "3. 資料整理", "4. 資料陳示"],
        "explanation": "只調查部分對象屬於抽查。",
    },
    {
        "scenario_id": "statistics_purpose_identification",
        "question_text": "下列何者最能說明統計研究的主要目的？請輸入選項代號。",
        "answer": "2",
        "choices": ["1. 只記錄數字", "2. 從資料整理資訊並協助判斷", "3. 只畫圖不分析", "4. 只背誦公式"],
        "explanation": "統計重點是整理、分析與解釋資料以協助判斷。",
    },
    {
        "scenario_id": "descriptive_not_generalized",
        "question_text": "某班把全班成績整理成表格並描述分布情形，主要屬於何者？請輸入選項代號。",
        "answer": "1",
        "choices": ["1. 敘述統計", "2. 推論統計", "3. 抽查", "4. 解釋資料"],
        "explanation": "只描述已知班級資料狀況，屬於敘述統計。",
    },
    {
        "scenario_id": "inferential_generalized_to_population",
        "question_text": "根據抽訪部分住戶資料推估整個社區支持比例，主要屬於何者？請輸入選項代號。",
        "answer": "2",
        "choices": ["1. 敘述統計", "2. 推論統計", "3. 普查", "4. 資料整理"],
        "explanation": "由部分資料推估整體屬於推論統計。",
    },
]


def _build_chart_png_base64(
    x_labels: List[str],
    y_values: List[int],
    *,
    chart_kind: str,
    title: str,
) -> str:
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=120)
    try:
        if chart_kind == "line":
            ax.plot(x_labels, y_values, marker="o", linewidth=2)
        else:
            ax.bar(x_labels, y_values)
        ax.set_title(title)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        return base64.b64encode(buf.getvalue()).decode("ascii")
    finally:
        plt.close(fig)


def _build_table_png_base64(
    headers: List[str],
    rows: List[List[str]],
    *,
    title: str,
) -> str:
    fig, ax = plt.subplots(figsize=(5.8, 3.2), dpi=120)
    try:
        ax.axis("off")
        ax.set_title(title)
        tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        tbl.scale(1.1, 1.5)
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png")
        return base64.b64encode(buf.getvalue()).decode("ascii")
    finally:
        plt.close(fig)


def chart_mode_bar_reading(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (["甲", "乙", "丙", "丁"], [6, 9, 9, 5], "閱讀長條圖，求眾數值（次數最多的值）"),
        (["A", "B", "C", "D"], [11, 8, 7, 11], "閱讀長條圖，求眾數值（次數最多的值）"),
        (["一組", "二組", "三組", "四組"], [4, 10, 6, 10], "閱讀長條圖，求眾數值（次數最多的值）"),
    ]
    labels, values, stem = rng.choice(scenarios)
    param_tuple = ("chart_mode_bar_reading", tuple(labels), tuple(values))
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    mode_value = max(values)
    image_b64 = _build_chart_png_base64(labels, values, chart_kind="bar", title="長條圖")
    return {
        "question_text": f"{stem}。請輸入對應的次數。",
        "answer": str(mode_value),
        "correct_answer": str(mode_value),
        "choices": [str(mode_value)],
        "explanation": f"圖中最大次數為 {mode_value}，因此答案為 {mode_value}。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_mode_bar_reading",
        "generator_key": "b4.chap3.chart_mode_bar_reading",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "mode"],
        "remediation_candidates": ["vh_數學B4_CentralTendencyMeasures"],
        "source_style_refs": ["B4_Ch3_chart"],
        "parameters": {"scenario": "bar_mode", "labels": labels, "values": values},
        "image_base64": image_b64,
        "visual_aids": [
            {"type": "chart", "chart_kind": "bar", "x_labels": labels, "y_values": values}
        ],
        "visual_backed": True,
        "visual_asset_type": "chart",
        "runtime_mode": "visual_backed",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic_auto_checked",
    }


def chart_range_line_reading(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (["週一", "週二", "週三", "週四", "週五"], [13, 18, 15, 20, 16]),
        (["1", "2", "3", "4", "5"], [9, 14, 12, 17, 11]),
        (["甲", "乙", "丙", "丁", "戊"], [22, 19, 24, 18, 21]),
    ]
    labels, values = rng.choice(scenarios)
    param_tuple = ("chart_range_line_reading", tuple(labels), tuple(values))
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    expected_range = max(values) - min(values)
    image_b64 = _build_chart_png_base64(labels, values, chart_kind="line", title="折線圖")
    return {
        "question_text": "請看折線圖資料，求最大值與最小值的差（全距）。",
        "answer": str(expected_range),
        "correct_answer": str(expected_range),
        "choices": [str(expected_range)],
        "explanation": f"最大值為 {max(values)}，最小值為 {min(values)}，全距為 {expected_range}。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_range_line_reading",
        "generator_key": "b4.chap3.chart_range_line_reading",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "range"],
        "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
        "source_style_refs": ["B4_Ch3_chart"],
        "parameters": {"scenario": "line_range", "labels": labels, "values": values},
        "image_base64": image_b64,
        "visual_aids": [
            {"type": "chart", "chart_kind": "line", "x_labels": labels, "y_values": values}
        ],
        "visual_backed": True,
        "visual_asset_type": "chart",
        "runtime_mode": "visual_backed",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic_auto_checked",
    }


def frequency_table_mean_reading(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        ([2, 3, 4, 5], [1, 2, 3, 2]),
        ([10, 12, 14, 16], [2, 1, 2, 1]),
        ([6, 7, 8, 9], [1, 3, 2, 2]),
    ]
    x_vals, freqs = rng.choice(scenarios)
    param_tuple = ("frequency_table_mean_reading", tuple(x_vals), tuple(freqs))
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    total_n = sum(freqs)
    weighted_sum = sum(x * f for x, f in zip(x_vals, freqs))
    mean_value = weighted_sum // total_n
    headers = ["數值", "次數"]
    table_rows = [[str(x), str(f)] for x, f in zip(x_vals, freqs)]
    table_title = "次數分配表"
    image_b64 = _build_table_png_base64(headers, table_rows, title=table_title)
    return {
        "question_text": "閱讀下列次數分配表，求資料的算術平均數。",
        "answer": str(mean_value),
        "correct_answer": str(mean_value),
        "choices": [str(mean_value)],
        "explanation": f"算術平均數 = {weighted_sum} ÷ {total_n} = {mean_value}。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "frequency_table_mean_reading",
        "scenario_family": "frequency_table_mean",
        "generator_key": "b4.chap3.frequency_table_mean_reading",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["table_reading", "mean"],
        "remediation_candidates": ["vh_數學B4_CentralTendencyMeasures"],
        "source_style_refs": ["B4_Ch3_table"],
        "parameters": {
            "scenario_id": "freq_mean",
            "scenario_family": "frequency_table_mean",
            "values": x_vals,
            "frequencies": freqs,
        },
        "table_title": table_title,
        "image_base64": image_b64,
        "visual_aids": [
            {
                "type": "table",
                "title": table_title,
                "caption": table_title,
                "alt_text": table_title,
                "headers": headers,
                "rows": table_rows,
                "table_kind": "frequency",
            }
        ],
        "visual_backed": True,
        "visual_asset_type": "table",
        "runtime_mode": "visual_reading_with_short_answer",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def frequency_table_range_reading(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        ([4, 5, 6, 7, 8], [1, 2, 1, 3, 1]),
        ([12, 15, 18, 21], [2, 1, 2, 1]),
        ([30, 35, 40, 45], [1, 1, 2, 1]),
    ]
    x_vals, freqs = rng.choice(scenarios)
    param_tuple = ("frequency_table_range_reading", tuple(x_vals), tuple(freqs))
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    expected_range = max(x_vals) - min(x_vals)
    headers = ["數值", "次數"]
    table_rows = [[str(x), str(f)] for x, f in zip(x_vals, freqs)]
    table_title = "次數分配表"
    image_b64 = _build_table_png_base64(headers, table_rows, title=table_title)
    return {
        "question_text": "閱讀下列次數分配表，求資料的全距。",
        "answer": str(expected_range),
        "correct_answer": str(expected_range),
        "choices": [str(expected_range)],
        "explanation": f"全距 = 最大值 {max(x_vals)} - 最小值 {min(x_vals)} = {expected_range}。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "frequency_table_range_reading",
        "scenario_family": "frequency_table_range",
        "generator_key": "b4.chap3.frequency_table_range_reading",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["table_reading", "range"],
        "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
        "source_style_refs": ["B4_Ch3_table"],
        "parameters": {
            "scenario_id": "freq_range",
            "scenario_family": "frequency_table_range",
            "values": x_vals,
            "frequencies": freqs,
        },
        "table_title": table_title,
        "image_base64": image_b64,
        "visual_aids": [
            {
                "type": "table",
                "title": table_title,
                "caption": table_title,
                "alt_text": table_title,
                "headers": headers,
                "rows": table_rows,
                "table_kind": "frequency",
            }
        ],
        "visual_backed": True,
        "visual_asset_type": "table",
        "runtime_mode": "visual_reading_with_short_answer",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def histogram_reading(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        {
            "scenario_id": "histogram_group_frequency",
            "bins": ["40-49", "50-59", "60-69", "70-79", "80-89"],
            "freqs": [2, 5, 8, 6, 3],
            "target_idx": 2,
            "question_text": "閱讀下列直方圖，求 60-69 分這一組的人數。",
        },
        {
            "scenario_id": "histogram_total_frequency",
            "bins": ["10-19", "20-29", "30-39", "40-49", "50-59"],
            "freqs": [3, 4, 7, 5, 1],
            "target_idx": None,
            "question_text": "閱讀下列直方圖，求全部資料的總人數。",
        },
        {
            "scenario_id": "histogram_group_frequency_alt",
            "bins": ["0-9", "10-19", "20-29", "30-39", "40-49"],
            "freqs": [1, 3, 6, 4, 2],
            "target_idx": 3,
            "question_text": "閱讀下列直方圖，求 30-39 組別的次數。",
        },
    ]
    sc = rng.choice(scenarios)
    bins = sc["bins"]
    freqs = sc["freqs"]
    param_tuple = ("histogram_reading", sc["scenario_id"], tuple(bins), tuple(freqs))
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)

    chart_title = "直方圖"
    x_label = "分數區間"
    y_label = "人數"
    image_b64 = _build_chart_png_base64(bins, freqs, chart_kind="bar", title=chart_title)

    if sc["target_idx"] is None:
        answer_value = sum(freqs)
        explanation = f"將各組人數相加：{' + '.join(str(v) for v in freqs)} = {answer_value}。"
    else:
        answer_value = freqs[int(sc["target_idx"])]
        target_bin = bins[int(sc["target_idx"])]
        explanation = f"由直方圖可讀得 {target_bin} 這一組的人數為 {answer_value}。"

    return {
        "question_text": sc["question_text"],
        "answer": str(answer_value),
        "correct_answer": str(answer_value),
        "choices": [str(answer_value)],
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "histogram_reading",
        "scenario_family": "histogram_reading_short_answer",
        "generator_key": "b4.chap3.histogram_reading",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["histogram_reading", "chart_reading"],
        "remediation_candidates": ["vh_數學B4_HistogramsAndFrequencyPolygons"],
        "source_style_refs": ["B4_Ch3_histogram"],
        "parameters": {
            "scenario_id": sc["scenario_id"],
            "scenario_family": "histogram_reading_short_answer",
            "bins": bins,
            "frequencies": freqs,
            "target_idx": sc["target_idx"],
        },
        "chart_title": chart_title,
        "image_base64": image_b64,
        "visual_aids": [
            {
                "type": "histogram",
                "title": chart_title,
                "caption": chart_title,
                "alt_text": chart_title,
                "x_label": x_label,
                "y_label": y_label,
                "bins": bins,
                "frequencies": freqs,
            }
        ],
        "visual_backed": True,
        "visual_asset_type": "histogram",
        "runtime_mode": "visual_reading_with_short_answer",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def normal_distribution_empirical_rule_basic(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        ("within_1sigma", "常態分配的經驗法則中，落在平均數正負 1 個標準差內的資料約占百分之幾？", "68"),
        ("within_2sigma", "常態分配的經驗法則中，落在平均數正負 2 個標準差內的資料約占百分之幾？", "95"),
        ("within_3sigma", "常態分配的經驗法則中，落在平均數正負 3 個標準差內的資料約占百分之幾（取整數近似）？", "99"),
    ]
    scenario_id, question_text, answer = rng.choice(scenarios)
    param_tuple = ("normal_distribution_empirical_rule_basic", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": ["68", "95", "99", "50"],
        "explanation": "經驗法則為 68-95-99.7，分別對應正負 1、2、3 個標準差區間。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "empirical_rule_interval_percentage",
        "scenario_family": "normal_distribution_empirical_rule",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.empirical_rule_interval_percentage",
        "answer_type": "rational_fraction",
        "difficulty": difficulty,
        "diagnosis_tags": ["normal_distribution", "empirical_rule"],
        "remediation_candidates": ["vh_數學B4_NormalDistributionAndEmpiricalRule"],
        "source_style_refs": ["B4_Ch3_normal_distribution"],
        "parameters": {"scenario_id": scenario_id, "scenario_family": "normal_distribution_empirical_rule"},
        "visual_backed": False,
        "runtime_mode": "deterministic_short_answer",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def sampling_methods_classification_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        ("sampling_method_identification_random", "教育局要抽查學生問卷，先把全市學生編號後用抽籤方式抽出 200 人。這屬於哪一種抽樣方法？", "1"),
        ("sampling_method_identification_systematic", "工廠品管從生產線第 5 件開始，每隔 20 件抽 1 件檢查。這屬於哪一種抽樣方法？", "2"),
        ("sampling_method_identification_stratified", "調查青年就業時，先按年級分層，再依各層人數比例抽樣。這屬於哪一種抽樣方法？", "3"),
        ("sampling_method_identification_cluster", "研究者先抽出 4 個社區，再調查這些社區內所有住戶。這屬於哪一種抽樣方法？", "4"),
        ("systematic_sampling_interval_or_probability", "共有 600 名員工，想用系統抽樣抽出 60 人，抽樣間距應為多少？", "2"),
        ("stratified_sampling_proportional_allocation", "某校一年級 120 人、二年級 80 人、三年級 100 人，共 300 人。若做分層隨機抽樣共抽 30 人，則一年級應抽幾人？", "3"),
    ]
    scenario_id, stem, answer = rng.choice(scenarios)
    param_tuple = ("sampling_methods_classification_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    choices_map = {
        "sampling_method_identification_random": [
            "1. 簡單隨機抽樣",
            "2. 系統抽樣",
            "3. 分層隨機抽樣",
            "4. 部落抽樣",
        ],
        "sampling_method_identification_systematic": [
            "1. 簡單隨機抽樣",
            "2. 系統抽樣",
            "3. 分層隨機抽樣",
            "4. 部落抽樣",
        ],
        "sampling_method_identification_stratified": [
            "1. 簡單隨機抽樣",
            "2. 系統抽樣",
            "3. 分層隨機抽樣",
            "4. 部落抽樣",
        ],
        "sampling_method_identification_cluster": [
            "1. 簡單隨機抽樣",
            "2. 系統抽樣",
            "3. 分層隨機抽樣",
            "4. 部落抽樣",
        ],
        "systematic_sampling_interval_or_probability": [
            "1. 抽樣間距為 6",
            "2. 抽樣間距為 10",
            "3. 抽樣間距為 12",
            "4. 抽樣間距為 20",
        ],
        "stratified_sampling_proportional_allocation": [
            "1. 一年級應抽 8 人",
            "2. 一年級應抽 10 人",
            "3. 一年級應抽 12 人",
            "4. 一年級應抽 15 人",
        ],
    }
    explanation_map = {
        "sampling_method_identification_random": "以抽籤或亂數直接從全體名單抽取，屬於簡單隨機抽樣。",
        "sampling_method_identification_systematic": "從固定起點後每隔固定件數抽取，屬於系統抽樣。",
        "sampling_method_identification_stratified": "先分層再依比例抽樣，屬於分層隨機抽樣。",
        "sampling_method_identification_cluster": "先抽群組（社區/班級）再調查群組內成員，屬於部落抽樣。",
        "systematic_sampling_interval_or_probability": "系統抽樣間距 = 母群體數 ÷ 樣本數 = 600 ÷ 60 = 10。",
        "stratified_sampling_proportional_allocation": "一年級比例為 120/300，因此應抽 30 × 120/300 = 12 人。",
    }
    return {
        "question_text": f"{stem} 請輸入選項代號。",
        "answer": answer,
        "correct_answer": answer,
        "choices": choices_map[scenario_id],
        "explanation": explanation_map.get(scenario_id, "依題意判斷抽樣方法與比例計算。"),
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "sampling_methods_classification_choice",
        "scenario_family": "sampling_methods_boundary_aligned",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.sampling_methods_classification_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["sampling_methods", "classification"],
        "remediation_candidates": ["vh_數學B4_SamplingMethods"],
        "source_style_refs": ["B4_Ch3_sampling"],
        "source_style_summary": "3-1 抽樣方法情境判斷與基礎比例計算題型。",
        "textbook_alignment_note": "對齊 3-1 抽樣方法：簡單隨機、系統、分層隨機、部落抽樣。",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "sampling_methods_boundary_aligned"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def sampling_methods_classification_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_SAMPLING_METHODS_PARAMETER_SIGNATURE
    rng = random.Random(seed)
    seed_val = int(seed) if seed is not None else rng.randint(1, 10_000_000)

    catalog: List[Dict[str, Any]] = []
    for family in ("simple_random", "systematic", "stratified", "cluster"):
        for context_tpl in SAMPLING_METHODS_CLASSIFICATION_CONTEXTS[family]:
            entry = dict(context_tpl)
            entry["family"] = family
            catalog.append(entry)
    catalog.append(
        {
            "scenario_id": "systematic_sampling_interval_calculation_parameterized",
            "template_id": "systematic_interval_calculation",
            "family": "systematic_interval",
        }
    )
    catalog.append(
        {
            "scenario_id": "stratified_sampling_proportional_allocation_parameterized",
            "template_id": "stratified_allocation_calculation",
            "family": "stratified_allocation",
        }
    )

    if seed is not None:
        base = catalog[(seed_val - 1) % len(catalog)]
    else:
        candidates = [
            item
            for item in catalog
            if f"{item['scenario_id']}::{item.get('template_id','')}"
            != _LAST_SAMPLING_METHODS_PARAMETER_SIGNATURE
        ]
        base = rng.choice(candidates or catalog)

    scenario_id = str(base["scenario_id"])
    template_id = str(base["template_id"])
    family = str(base["family"])
    numeric_params: Dict[str, Any] = {}
    context_params: Dict[str, Any] = {}
    question_text = ""
    answer = ""
    explanation = ""
    choices: List[str] = list(SAMPLING_METHODS_CHOICES)

    if family in {"simple_random", "stratified", "cluster"}:
        question_text = str(base["stem"])
        answer = str(base["answer"])
        explanation_map = {
            "simple_random": "以抽籤、摸彩券或亂數方式直接從全體名單抽取，屬於簡單隨機抽樣。",
            "stratified": "先依特徵分層，再按各層比例抽樣，屬於分層隨機抽樣。",
            "cluster": "先抽群組，再調查群組內成員，屬於部落抽樣。",
        }
        explanation = explanation_map[family]
        parameter_signature = f"{template_id}:context={family}"
    elif family == "systematic":
        context = SYSTEMATIC_IDENTIFICATION_CONTEXTS[(seed_val - 1) % len(SYSTEMATIC_IDENTIFICATION_CONTEXTS)]
        start_candidates = [1, 2, 3, 5, 8, 10, 12, 15, 20]
        interval_candidates = [5, 10, 20, 25, 50, 100]
        start = start_candidates[(seed_val + 1) % len(start_candidates)]
        interval = interval_candidates[(seed_val + 2) % len(interval_candidates)]
        question_text = str(base["stem"]).format(
            context=context["context"], start=start, interval=interval, target=context["target"]
        )
        answer = str(base["answer"])
        explanation = "先決定起點，再每隔固定件數抽取一次，屬於系統抽樣。"
        numeric_params = {"start": start, "interval": interval}
        context_params = {"context": context["context"], "target": context["target"]}
        parameter_signature = (
            f"{template_id}:start={start},interval={interval},context={context['context']}"
        )
    elif family == "systematic_interval":
        n_total, sample_n = SYSTEMATIC_INTERVAL_NUMERIC_POOL[
            (seed_val - 1) % len(SYSTEMATIC_INTERVAL_NUMERIC_POOL)
        ]
        k_interval = n_total // sample_n
        distractors = {max(1, k_interval - 5), max(1, k_interval + 5), max(1, k_interval * 2)}
        distractors.discard(k_interval)
        options = [k_interval] + sorted(distractors)[:3]
        while len(options) < 4:
            candidate = k_interval + len(options) * 3
            if candidate not in options:
                options.append(candidate)
        options = options[:4]
        rng.shuffle(options)
        choices = [f"{i + 1}. 抽樣間距為 {v}" for i, v in enumerate(options)]
        answer = str(options.index(k_interval) + 1)
        question_text = (
            f"共有 {n_total} 名對象，想用系統抽樣抽出 {sample_n} 名，抽樣間距 k 應為多少？請輸入選項代號。"
        )
        explanation = f"系統抽樣間距 k = 母體數 ÷ 樣本數 = {n_total} ÷ {sample_n} = {k_interval}。"
        numeric_params = {"N": n_total, "n": sample_n, "k": k_interval}
        parameter_signature = f"systematic_interval:N={n_total},n={sample_n},k={k_interval}"
    else:
        row = STRATIFIED_ALLOCATION_NUMERIC_POOL[(seed_val - 1) % len(STRATIFIED_ALLOCATION_NUMERIC_POOL)]
        layers = list(row["layers"])
        sample_total = int(row["sample_total"])
        target_idx = int(row["target_idx"])
        target_name = str(layers[target_idx][0])
        target_count = int(layers[target_idx][1])
        total_count = sum(int(x[1]) for x in layers)
        answer_people = sample_total * target_count // total_count
        layer_text = "、".join(f"{name} {count} 人" for name, count in layers)
        distractors = {max(1, answer_people - 2), answer_people + 2, answer_people + 4}
        distractors.discard(answer_people)
        options = [answer_people] + sorted(distractors)[:3]
        while len(options) < 4:
            candidate = answer_people + len(options)
            if candidate not in options:
                options.append(candidate)
        options = options[:4]
        rng.shuffle(options)
        choices = [f"{i + 1}. {target_name}應抽 {v} 人" for i, v in enumerate(options)]
        answer = str(options.index(answer_people) + 1)
        question_text = (
            f"某群體分層人數如下：{layer_text}，共 {total_count} 人。"
            f"若做分層隨機抽樣共抽 {sample_total} 人，則{target_name}應抽幾人？請輸入選項代號。"
        )
        explanation = f"{target_name}應抽人數 = {sample_total} × {target_count}/{total_count} = {answer_people}。"
        numeric_params = {
            "sample_total": sample_total,
            "layer_count": target_count,
            "population_total": total_count,
            "answer_people": answer_people,
        }
        context_params = {"target_layer": target_name, "layers": layers}
        scenario_id = str(row["scenario_id"])
        parameter_signature = (
            f"stratified_allocation:sample_total={sample_total},"
            f"layer_count={target_count},total={total_count},target={target_name}"
        )

    param_tuple = ("sampling_methods_classification_choice", scenario_id, template_id, parameter_signature)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)

    _LAST_SAMPLING_METHODS_PARAMETER_SIGNATURE = parameter_signature

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "sampling_methods_classification_choice",
        "scenario_family": "sampling_methods_boundary_aligned",
        "scenario_id": scenario_id,
        "parameter_signature": parameter_signature,
        "generator_key": "b4.chap3.sampling_methods_classification_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["sampling_methods", "classification", family],
        "remediation_candidates": ["vh_?詨飛B4_SamplingMethods"],
        "source_style_refs": ["B4_Ch3_sampling"],
        "source_style_summary": "3-1 抽樣方法：簡單隨機、系統、分層隨機、部落抽樣。",
        "textbook_alignment_note": "維持 3-1 抽樣方法骨架，僅做題幹參數化，不引入課本外新題型。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "sampling_methods_boundary_aligned",
            "template_id": template_id,
            "numeric_params": numeric_params,
            "context_params": context_params,
            "parameter_signature": parameter_signature,
        },
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def statistical_basic_concepts_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        ("descriptive_vs_inferential_statistics", "下列何者屬於敘述統計？", "1"),
        ("statistics_process_order_or_identification", "統計研究通常包含蒐集、整理、陳示、分析、解釋。下列何者是正確的第一步？", "2"),
        ("census_vs_sample_survey_basic", "若學校想了解全校學生通勤方式，直接詢問全校每一位學生，這屬於何者？", "3"),
    ]
    scenario_id, question_text, answer = rng.choice(scenarios)
    param_tuple = ("statistical_basic_concepts_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    choices_map = {
        "descriptive_vs_inferential_statistics": [
            "1. 統計某班本次測驗平均分數並用長條圖呈現",
            "2. 由樣本推估全市學生身高分布",
            "3. 依民調推論全國選民支持度",
            "4. 以樣本預測未來十年人口變化",
        ],
        "statistics_process_order_or_identification": [
            "1. 先解釋結論，再蒐集資料",
            "2. 先蒐集資料",
            "3. 先製作圖表，再蒐集資料",
            "4. 先分析結果，再整理資料",
        ],
        "census_vs_sample_survey_basic": [
            "1. 抽查",
            "2. 分層隨機抽樣",
            "3. 普查",
            "4. 系統抽樣",
        ],
    }
    explanation_map = {
        "descriptive_vs_inferential_statistics": "敘述統計重點是整理並呈現已蒐集到的資料，不進行母體推論。",
        "statistics_process_order_or_identification": "統計研究要先蒐集資料，再進行後續整理、陳示、分析與解釋。",
        "census_vs_sample_survey_basic": "對母群體每一個個體都進行調查，屬於普查。",
    }
    return {
        "question_text": f"{question_text} 請輸入選項代號。",
        "answer": answer,
        "correct_answer": answer,
        "choices": choices_map[scenario_id],
        "explanation": explanation_map[scenario_id],
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "statistical_basic_concepts_choice",
        "scenario_family": "statistical_basic_concepts_boundary_aligned",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_basic_concepts_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["statistics_basics", "terminology"],
        "remediation_candidates": ["vh_數學B4_StatisticalBasicConcepts"],
        "source_style_refs": ["B4_Ch3_statistical_basics"],
        "source_style_summary": "3-1 統計基本概念：統計意義、流程、敘述與推論、普查抽查。",
        "textbook_alignment_note": "避免樣本平均數/母體平均數名詞反覆題，改為 3-1 概念辨識題。",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "statistical_basic_concepts_boundary_aligned"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def statistical_basic_concepts_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_STATISTICAL_BASIC_CONCEPT_SCENARIO_ID
    scenarios = STATISTICAL_BASIC_CONCEPT_SCENARIOS
    if seed is not None:
        scenario = scenarios[(int(seed) - 1) % len(scenarios)]
    else:
        rng = random.Random()
        candidates = [
            s
            for s in scenarios
            if s["scenario_id"] != _LAST_STATISTICAL_BASIC_CONCEPT_SCENARIO_ID
        ]
        scenario = rng.choice(candidates or scenarios)

    scenario_id = str(scenario["scenario_id"])
    param_tuple = ("statistical_basic_concepts_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    _LAST_STATISTICAL_BASIC_CONCEPT_SCENARIO_ID = scenario_id

    choices = list(scenario["choices"])
    answer = str(scenario["answer"])
    return {
        "question_text": str(scenario["question_text"]),
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": str(scenario["explanation"]),
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "statistical_basic_concepts_choice",
        "scenario_family": "statistical_basic_concepts_boundary_aligned",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_basic_concepts_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["statistics_basics", "terminology", scenario_id],
        "remediation_candidates": ["vh_?詨飛B4_StatisticalBasicConcepts"],
        "source_style_refs": ["B4_Ch3_statistical_basics"],
        "source_style_summary": "3-1 統計基本概念：統計目的、資料處理流程、敘述統計、推論統計、普查與抽查。",
        "textbook_alignment_note": "限於 B4 3-1 統計基本概念範圍，不含抽樣方法分類、調查對象數量細節或統計量計算題。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "statistical_basic_concepts_boundary_aligned",
        },
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def tree_diagram_counting_runtime_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "tree_diagram_completion_runtime_shell"
    return {
        "question_text": "請以樹狀圖列出兩階段事件所有可能路徑，並在手寫區上傳你的作答。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "handwriting_tree_diagram",
            "required_elements": ["分支節點", "完整路徑", "每條路徑標示事件結果"],
        },
        "choices": [],
        "explanation": "此題為作圖/手寫型，請使用 AI 檢查或教師覆核，不走一般自動比對。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "tree_diagram_completion_or_listing",
        "scenario_family": "tree_diagram_counting",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.tree_diagram_counting_runtime_shell",
        "answer_type": "handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["tree_diagram", "counting"],
        "remediation_candidates": ["vh_數學B4_TreeDiagramCounting"],
        "source_style_refs": ["B4_Ch1_tree_diagram"],
        "parameters": {"scenario_id": scenario_id, "scenario_family": "tree_diagram_counting"},
        "visual_backed": True,
        "visual_asset_type": "tree_diagram_template",
        "requires_handwriting": True,
        "requires_teacher_review": False,
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "handwriting_ai_checked",
        "grading_mode": "ai_assisted_review",
    }

def frequency_distribution_table_construction_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    samples = [12, 15, 18, 18, 19, 20, 20, 21, 23, 24]
    if rng.randint(0, 1) == 1:
        samples = [8, 10, 10, 11, 13, 13, 14, 15, 15, 16]
    scenario_id = "frequency_distribution_table_completion"
    return {
        "question_text": f"請將下列資料整理成次數分配表，並在手寫區填入組別與次數：{samples}",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "frequency_table_completion",
            "required_columns": ["組別", "次數"],
            "minimum_rows": 4,
        },
        "choices": [],
        "explanation": "此題為補表/手寫型，請使用 AI 檢查或教師覆核，不走一般自動比對。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "table_completion_handwriting",
        "scenario_family": "frequency_distribution_table_construction",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.frequency_distribution_table_construction_shell",
        "answer_type": "handwriting",
        "answer_input_type": "handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["frequency_distribution_table", "table_construction"],
        "remediation_candidates": ["vh_數學B4_FrequencyDistributionTableConstruction"],
        "source_style_refs": ["B4_Ch3_frequency_table_construction"],
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "frequency_distribution_table_construction",
            "raw_data": samples,
        },
        "visual_backed": True,
        "visual_asset_type": "table_template",
        "requires_handwriting": True,
        "requires_teacher_review": True,
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "handwriting_ai_checked",
        "grading_mode": "ai_assisted_review",
    }

def sampling_survey_foundation_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (
            "population_sample_size_identification",
            "某技術高中有學生 1000 人，學校抽出 100 人做健康檢查。若問「樣本數是多少？」應選哪一項？",
            "2",
            [
                "1. 1000",
                "2. 100",
                "3. 900",
                "4. 無法判定",
            ],
            "樣本數是被抽出接受調查的人數，因此為 100。",
        ),
        (
            "population_sample_identification",
            "某城市共有 5000 位機車族，研究者抽出其中 250 位填寫問卷。下列何者是樣本？",
            "3",
            [
                "1. 全城市 5000 位機車族",
                "2. 全城市所有交通工具使用者",
                "3. 被抽出的 250 位機車族",
                "4. 問卷題目本身",
            ],
            "樣本是實際被抽出接受調查的對象，因此是 250 位機車族。",
        ),
        (
            "census_or_sample_survey_identification",
            "學校只訪問各班 5 位學生了解午餐滿意度，此作法屬於何者？",
            "4",
            [
                "1. 普查",
                "2. 母群體數",
                "3. 部落抽樣",
                "4. 抽查",
            ],
            "只調查母群體中的一部分個體，屬於抽查。",
        ),
    ]
    scenario_id, question_text, answer, choices, explanation = rng.choice(scenarios)
    param_tuple = ("sampling_survey_foundation_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": f"{question_text} 請輸入選項代號。",
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "sampling_survey_foundation_identification",
        "scenario_family": "sampling_survey_foundation_identification",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.sampling_survey_foundation_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["sampling_survey", "population_sample"],
        "remediation_candidates": ["vh_數學B4_SamplingSurvey"],
        "source_style_refs": ["B4_Ch3_sampling_survey"],
        "source_style_summary": "3-1 抽樣調查：母群體、樣本、母群體數、樣本數、普查與抽查。",
        "textbook_alignment_note": "採具體情境判斷題，避免抽象名詞定義堆疊。",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "sampling_survey_foundation_identification"},
        "visual_backed": False,
        "requires_teacher_review": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def sampling_survey_bias_review_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "sampling_survey_bias_explanation"
    return {
        "question_text": "某候選人為了了解支持度，只在自己的造勢晚會上發放問卷。請說明這個抽樣調查可能有哪些偏誤？",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "text_explanation",
            "required_points": ["樣本不具代表性", "取樣偏誤"],
        },
        "choices": [],
        "explanation": "在造勢晚會上發放問卷，受訪者多半已是支持者，導致樣本不具代表性，產生嚴重的取樣偏誤。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "sampling_survey_bias_review",
        "scenario_family": "sampling_survey_bias_review",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.sampling_survey_bias_review_shell",
        "answer_type": "handwriting",
        "answer_input_type": "handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["sampling_survey", "bias"],
        "remediation_candidates": ["vh_數學B4_SamplingSurvey"],
        "source_style_refs": ["B4_Ch3_sampling_survey"],
        "parameters": {"scenario_id": scenario_id},
        "visual_backed": False,
        "requires_teacher_review": True,
        "runtime_mode": "teacher_review",
        "check_mode": "review_mode",
        "grading_mode": "teacher_review",
    }

def cumulative_frequency_tables_graphs_review_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "cumulative_frequency_table_completion_review"
    headers = ["組別", "次數", "累積次數"]
    rows = [
        ["0-9", "3", "3"],
        ["10-19", "5", "8"],
        ["20-29", "4", "□"],
        ["30-39", "2", "□"],
    ]
    table_title = "累積次數分配表"
    image_b64 = _build_table_png_base64(headers, rows, title=table_title)
    return {
        "question_text": "請依下表補齊累積次數欄位，並簡述你如何由次數欄推得累積次數。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "table_completion_with_reasoning",
            "required_columns": headers,
            "minimum_rows": 4,
            "required_points": ["補齊累積次數", "由上而下累加說明"],
        },
        "choices": [],
        "explanation": "累積次數是由上而下逐列累加次數欄位得到，例如先有 3，再加 5 得 8，後續依序累加即可。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "cumulative_frequency_table_completion_review",
        "scenario_family": "cumulative_frequency_table_completion_review",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.cumulative_frequency_tables_graphs_review_shell",
        "answer_type": "handwriting",
        "answer_input_type": "free_response_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["cumulative_frequency", "table_completion"],
        "remediation_candidates": ["vh_數學B4_CumulativeFrequencyTablesAndGraphs"],
        "source_style_refs": ["B4_Ch3_cumulative_frequency"],
        "source_style_summary": "3-2 累積次數補表題，需依次數欄位逐列累加。",
        "textbook_alignment_note": "保留補表與說明作答型態，不轉為 deterministic 單值比對。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "cumulative_frequency_table_completion_review",
            "table_rows": rows,
        },
        "visual_backed": True,
        "visual_asset_type": "table",
        "table_title": table_title,
        "table": {
            "table_title": table_title,
            "headers": headers,
            "rows": rows,
        },
        "image_base64": image_b64,
        "visual_aids": [
            {
                "type": "table",
                "title": table_title,
                "caption": table_title,
                "alt_text": table_title,
                "headers": headers,
                "rows": rows,
            }
        ],
        "requires_handwriting": True,
        "requires_teacher_review": True,
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "review_mode",
        "grading_mode": "teacher_review",
    }

def data_organization_charts_review_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "data_organization_chart_selection_review"
    return {
        "question_text": "某社團記錄一週每日到課人數。請說明你會先如何整理資料，並選擇一種最適合呈現趨勢的圖表，簡述理由。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "workflow_and_chart_selection",
            "required_points": ["整理步驟", "圖表選擇", "選擇理由"],
        },
        "choices": [],
        "explanation": "此題重點在資料整理流程與圖表選擇判斷，需 review 判分。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "data_organization_chart_selection_review",
        "scenario_family": "data_organization_review",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.data_organization_charts_review_shell",
        "answer_type": "text",
        "answer_input_type": "text_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "chart_selection"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "parameters": {"scenario_id": scenario_id, "scenario_family": "data_organization_review"},
        "visual_backed": True,
        "visual_asset_type": "chart_planning_prompt",
        "requires_teacher_review": True,
        "runtime_mode": "teacher_review",
        "check_mode": "review_mode",
        "grading_mode": "teacher_review",
    }

def data_organization_chart_type_selection_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (
            "trend_line_chart",
            "某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 折線圖", "2. 圓形圖", "3. 直方圖", "4. 樹狀圖"],
            "1",
            "折線圖最適合呈現隨時間變化的趨勢。",
        ),
        (
            "category_comparison_bar_chart",
            "學校想比較甲乙丙丁四個班參加活動的人數差異，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 圓形圖", "2. 長條圖", "3. 折線圖", "4. 直方圖"],
            "2",
            "長條圖適合比較不同類別的數量差異。",
        ),
        (
            "proportion_pie_chart",
            "社團要呈現經費在交通、餐飲、器材與宣傳四項支出所占比例，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 直方圖", "2. 長條圖", "3. 圓形圖", "4. 折線圖"],
            "3",
            "圓形圖適合呈現各部分占整體的比例。",
        ),
        (
            "distribution_histogram",
            "要呈現段考分數區間（如 50-59、60-69）的人數分布，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 折線圖", "2. 圓形圖", "3. 直方圖", "4. 長條圖"],
            "3",
            "直方圖適合呈現連續資料在各區間的分布。",
        ),
    ]
    scenario_id, question_text, choices, answer, explanation = rng.choice(scenarios)
    param_tuple = ("data_organization_chart_type_selection_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_type_selection_by_purpose",
        "scenario_family": "chart_type_selection_by_purpose",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.data_organization_chart_type_selection_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "chart_selection", "chart_purpose"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "source_style_summary": "資料整理與圖表編製以情境選圖為核心，優先採課本式四選一。",
        "textbook_alignment_note": "對齊課本常見的「趨勢/比較/比例/分布」圖表用途判別。",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "chart_type_selection_by_purpose"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def data_organization_first_step_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (
            "commute_category_frequency_table",
            "某班記錄 40 位學生通勤方式，資料含步行、公車、機車、腳踏車等類別。若要比較各類別人數，應先如何整理？請輸入選項代號。",
            [
                "1. 統計各類別出現次數",
                "2. 直接計算標準差",
                "3. 畫累積次數折線圖",
                "4. 先假設資料服從常態分配",
            ],
            "1",
            "要比較類別人數，第一步是先整理成各類別次數（或次數分配）表。",
        ),
        (
            "snack_sales_category_count",
            "合作社記錄一週零食銷售品項（餅乾、飲料、麵包、飯糰），若要比較哪一類賣得最多，應先如何整理？請輸入選項代號。",
            [
                "1. 先求全體平均數",
                "2. 統計各品項出現次數",
                "3. 直接畫圓形圖不整理",
                "4. 先做常態分配檢定",
            ],
            "2",
            "先統計各品項次數，才能正確比較各類別數量。",
        ),
    ]
    scenario_id, question_text, choices, answer, explanation = rng.choice(scenarios)
    param_tuple = ("data_organization_first_step_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "data_organization_first_step",
        "scenario_family": "data_organization_first_step",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.data_organization_first_step_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "frequency_table", "chart_preparation"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "source_style_summary": "先整理資料再選圖，採明確可判分的四選一流程題。",
        "textbook_alignment_note": "對齊課本常見的資料整理第一步：先做類別統計或次數分配。",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "data_organization_first_step"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }



def statistical_chart_type_by_purpose_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (
            "chart_type_by_purpose_trend",
            "?????????????????????????????????????",
            ["1. ???", "2. ???", "3. ???", "4. ???"],
            "1",
            "???????????????????",
        ),
        (
            "chart_match_data_type_class_comparison",
            "?????????????????????????????????",
            ["1. ???", "2. ???", "3. ???", "4. ???"],
            "1",
            "?????????????????",
        ),
        (
            "chart_type_by_purpose_ratio",
            "???????????????????????????????????",
            ["1. ???", "2. ???", "3. ???", "4. ???"],
            "2",
            "??????????????????",
        ),
    ]
    scenario_id, question_text, choices, answer, explanation = rng.choice(scenarios)
    param_tuple = ("statistical_chart_type_by_purpose_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_type_by_purpose",
        "scenario_family": "chart_type_by_purpose",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_chart_type_by_purpose_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "chart_type_selection"],
        "remediation_candidates": ["vh_??B4_StatisticalChartReading"],
        "source_style_refs": ["B4_Ch3_statistical_chart_reading"],
        "source_style_summary": "????????????????????",
        "textbook_alignment_note": "???????????????????????",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "chart_type_by_purpose"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def statistical_chart_interpretation_caution_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "chart_interpretation_caution_axis_scale"
    param_tuple = ("statistical_chart_interpretation_caution_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": "???????????????????????????",
        "answer": "1",
        "correct_answer": "1",
        "choices": [
            "1. ?????????????",
            "2. ????????",
            "3. ????????",
            "4. ?????????",
        ],
        "explanation": "??????????????????????????????",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_interpretation_caution",
        "scenario_family": "chart_interpretation_caution",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_chart_interpretation_caution_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "interpretation_caution"],
        "remediation_candidates": ["vh_??B4_StatisticalChartReading"],
        "source_style_refs": ["B4_Ch3_statistical_chart_reading"],
        "source_style_summary": "????????????????????",
        "textbook_alignment_note": "??????????????????",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "chart_interpretation_caution"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def statistical_chart_match_data_type_choice(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    scenarios = [
        (
            "chart_match_data_type_class_count",
            "?????????????????????????????????",
            ["1. ???", "2. ???", "3. ???", "4. ???"],
            "1",
            "???????????????",
        ),
        (
            "chart_match_data_type_distribution",
            "?????????????????????????????????????",
            ["1. ???", "2. ???", "3. ???", "4. ???"],
            "3",
            "?????????????????",
        ),
    ]
    scenario_id, question_text, choices, answer, explanation = rng.choice(scenarios)
    param_tuple = ("statistical_chart_match_data_type_choice", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_match_data_type",
        "scenario_family": "chart_match_data_type",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_chart_match_data_type_choice",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "data_type_match"],
        "remediation_candidates": ["vh_??B4_StatisticalChartReading"],
        "source_style_refs": ["B4_Ch3_statistical_chart_reading"],
        "source_style_summary": "??????????????????????",
        "textbook_alignment_note": "??????????????????",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "chart_match_data_type"},
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

def statistical_chart_reading_visibility_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "statistical_chart_reading_visibility_review"
    chart_spec = {
        "x_labels": ["??", "??", "??", "??", "??"],
        "attendance": [28, 31, 29, 34, 32],
        "club_category_labels": ["??", "??", "??", "??"],
        "club_category_values": [18, 24, 15, 13],
    }
    expected_answer_schema = {
        "type": "chart_reading_open_response",
        "required_points": ["??????", "????????"],
        "rubric": {
            "trend": "????????????????",
            "caution": "??????????????????",
        },
    }
    return {
        "question_text": "??????????????????????????????????????????",
        "message": "????????????? AI/Review ???????????",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": expected_answer_schema,
        "choices": [],
        "explanation": "????????????????? review rubric ???????",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "statistical_chart_reading_visibility_review",
        "scenario_family": "statistical_chart_reading_visibility_review",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.statistical_chart_reading_visibility_shell",
        "answer_type": "text",
        "answer_input_type": "text_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["chart_reading", "interpretation"],
        "remediation_candidates": ["vh_??B4_StatisticalChartReading"],
        "source_style_refs": ["B4_Ch3_statistical_chart_reading"],
        "source_style_summary": "?????????????????????? rubric?",
        "textbook_alignment_note": "???????????????? review ?????",
        "parameters": {"scenario_id": scenario_id, "scenario_family": "statistical_chart_reading_visibility_review"},
        "visual_backed": True,
        "visual_asset_type": "chart",
        "chart_spec": chart_spec,
        "visual_aids": [
            {
                "type": "line_chart",
                "title": "????????",
                "x_labels": chart_spec["x_labels"],
                "y_values": chart_spec["attendance"],
            },
            {
                "type": "bar_chart",
                "title": "?????????",
                "x_labels": chart_spec["club_category_labels"],
                "y_values": chart_spec["club_category_values"],
            },
        ],
        "requires_teacher_review": True,
        "runtime_mode": "visibility_only",
        "check_mode": "review_mode",
        "grading_mode": "visibility_only",
    }


def opinion_poll_interpretation_review_shell(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    scenario_id = "opinion_poll_interpretation_review"
    poll = {"樣本數": 200, "贊成比例": "58%", "調查方式": "網路問卷"}
    return {
        "question_text": "某民調資料如下：樣本數 200、贊成比例 58%、調查方式為網路問卷。請說明此結果可如何解讀，並指出至少一項可能限制。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "poll_interpretation_review",
            "required_points": ["結果解讀", "限制或偏誤"],
        },
        "choices": [],
        "explanation": "民調解讀需評估樣本代表性與調查方式限制，建議 AI/教師覆核。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "opinion_poll_interpretation_review",
        "scenario_family": "opinion_poll_interpretation",
        "scenario_id": scenario_id,
        "generator_key": "b4.chap3.opinion_poll_interpretation_review_shell",
        "answer_type": "text",
        "answer_input_type": "text_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["opinion_poll", "interpretation"],
        "remediation_candidates": ["vh_數學B4_OpinionPollInterpretation"],
        "source_style_refs": ["B4_Ch3_opinion_poll"],
        "parameters": {"scenario_id": scenario_id, "scenario_family": "opinion_poll_interpretation", "poll": poll},
        "visual_backed": False,
        "requires_teacher_review": True,
        "runtime_mode": "teacher_review",
        "check_mode": "review_mode",
        "grading_mode": "teacher_review",
    }

def _generate_perfect_square_variance_dataset(rng: random.Random) -> Tuple[List[int], int, int]:
    """Generate a small dataset with integer mean and perfect square variance.
    Returns (dataset, mean, variance).
    """
    # Pre-calculated sets that have integer mean and perfect square variance
    # Variance here is population variance: V = sum((x-mu)^2)/N
    templates = [
        ([1, 3, 5, 7, 9], 5, 8), # variance = 8 (not perfect square)
        ([0, 3, 6], 3, 6), # variance = 6
        ([1, 2, 6, 7], 4, 6),
        ([1, 4, 4, 7], 4, 4), # variance = 4 (std=2)
        ([2, 5, 5, 8], 5, 4), # variance = 4
        ([1, 1, 7, 7], 4, 9), # variance = 9 (std=3)
        ([0, 0, 8, 8], 4, 16), # variance = 16 (std=4)
        ([2, 2, 8, 8], 5, 9), # variance = 9 (std=3)
    ]
    
    # Filter for perfect square variances
    perfect_squares = [t for t in templates if math.isqrt(t[2])**2 == t[2]]
    
    base_data, base_mean, base_var = rng.choice(perfect_squares)
    
    # Apply random shift to create variation
    shift = rng.randint(-5, 15)
    data = [x + shift for x in base_data]
    mean = base_mean + shift
    
    # Shuffle so it's not always sorted
    rng.shuffle(data)
    
    return data, mean, base_var

def mean_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        n = rng.randint(4, 6)
        data = [rng.randint(10, 50) for _ in range(n)]
        total = sum(data)
        
        # Adjust last element to make sum divisible by n
        rem = total % n
        if rem != 0:
            data[-1] += (n - rem)
            total = sum(data)
            
        mean = total // n
        
        param_tuple = tuple(sorted(data))
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        data_str = ", ".join(map(str, data))
        question_text = f"已知有 {n} 筆數據為 {data_str}，求這組數據的算術平均數。"
        
        explanation = (
            f"算術平均數的公式為總和除以資料個數。\n"
            f"資料總和 = ${' + '.join(map(str, data))} = {total}$\n"
            f"算術平均數 = $\\frac{{{total}}}{{{n}}} = {mean}$"
        )
        
        answer = str(mean)
        
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(mean + rng.randint(-5, 5))
            if fake_ans not in choices and int(fake_ans) > 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "mean_basic_numeric",
            "generator_key": "b4.chap3.mean_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["basic_arithmetic", "mean"],
            "remediation_candidates": ["vh_數學B4_CentralTendencyMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"data": data, "mean": mean},
        }
        
    raise RuntimeError("Failed to generate unique parameters")

def median_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        # Even or odd number of data points
        is_even = rng.choice([True, False])
        n = rng.randint(4, 6) if is_even else rng.randint(5, 7)
        if is_even and n % 2 != 0: n += 1
        if not is_even and n % 2 == 0: n += 1
        
        data = [rng.randint(10, 60) for _ in range(n)]
        
        # Force integer median for even case by making middle two have same parity
        sorted_data = sorted(data)
        if is_even:
            mid1, mid2 = n // 2 - 1, n // 2
            if (sorted_data[mid1] + sorted_data[mid2]) % 2 != 0:
                sorted_data[mid1] += 1
                data = sorted_data.copy()
        
        rng.shuffle(data)
        
        param_tuple = tuple(data)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        data_str = ", ".join(map(str, data))
        question_text = f"已知有一組數據為 {data_str}，求這組數據的中位數。"
        
        sorted_data_str = ", ".join(map(str, sorted(data)))
        
        if is_even:
            mid1, mid2 = n // 2 - 1, n // 2
            v1, v2 = sorted(data)[mid1], sorted(data)[mid2]
            median = (v1 + v2) // 2
            explanation = (
                f"首先將數據由小到大排列：\n"
                f"${sorted_data_str}$\n"
                f"共有 {n} 筆數據，中位數為第 {mid1 + 1} 筆與第 {mid2 + 1} 筆的平均值。\n"
                f"中位數 = $\\frac{{{v1} + {v2}}}{{2}} = {median}$"
            )
        else:
            mid = n // 2
            median = sorted(data)[mid]
            explanation = (
                f"首先將數據由小到大排列：\n"
                f"${sorted_data_str}$\n"
                f"共有 {n} 筆數據，中位數為正中間的第 {mid + 1} 筆數據。\n"
                f"中位數 = ${median}$"
            )
            
        answer = str(median)
        
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(median + rng.randint(-5, 5))
            if fake_ans not in choices and int(fake_ans) > 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "median_basic_numeric",
            "generator_key": "b4.chap3.median_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["median", "sorting"],
            "remediation_candidates": ["vh_數學B4_CentralTendencyMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"data": data, "median": median},
        }

    raise RuntimeError("Failed to generate unique parameters")

def mode_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        n = rng.randint(6, 8)
        base_vals = rng.sample(range(10, 30), 4)
        mode_val = base_vals[0]
        
        data = [mode_val, mode_val, mode_val]
        for v in base_vals[1:]:
            data.append(v)
            if rng.choice([True, False]) and len(data) < n:
                data.append(v)
                
        while len(data) < n:
            data.append(rng.choice(base_vals[1:]))
            
        # Ensure single mode
        counts = {}
        for d in data:
            counts[d] = counts.get(d, 0) + 1
        
        max_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_count]
        if len(modes) > 1:
            continue
            
        rng.shuffle(data)
        
        param_tuple = tuple(data)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        data_str = ", ".join(map(str, data))
        question_text = f"已知有一組數據為 {data_str}，求這組數據的眾數。"
        
        explanation = (
            f"眾數是數據中出現次數最多的數值。\n"
            f"觀察數據，可以發現：\n"
        )
        for val in sorted(counts.keys()):
            explanation += f"- {val} 出現了 {counts[val]} 次\n"
        
        explanation += f"因為 {mode_val} 出現次數最多（{max_count}次），所以眾數為 {mode_val}。"
        
        answer = str(mode_val)
        
        choices = [answer]
        for val in counts.keys():
            if str(val) not in choices:
                choices.append(str(val))
        while len(choices) < 4:
            fake_ans = str(mode_val + rng.randint(-5, 5))
            if fake_ans not in choices and int(fake_ans) > 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "mode_basic_numeric",
            "generator_key": "b4.chap3.mode_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["mode", "counting"],
            "remediation_candidates": ["vh_數學B4_CentralTendencyMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"data": data, "mode": mode_val},
        }

    raise RuntimeError("Failed to generate unique parameters")

def weighted_mean_basic(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        scenario = rng.randint(0, 3)
        
        if scenario == 0:
            subjects = [("國文", rng.randint(2, 4)), ("英文", rng.randint(2, 4)), ("數學", rng.randint(3, 4))]
            scores = [rng.randint(60, 95) for _ in range(3)]
            total_credits = sum(w for _, w in subjects)
            total_weighted_score = sum(s * w for s, (_, w) in zip(scores, subjects))
            
            question_text = (
                f"某學生的段考成績如下：\n"
                f"國文 {scores[0]} 分（{subjects[0][1]} 學分），"
                f"英文 {scores[1]} 分（{subjects[1][1]} 學分），"
                f"數學 {scores[2]} 分（{subjects[2][1]} 學分）。\n"
                f"求此學生的加權平均數。"
            )
            sum_str = " + ".join([f"{s} \\times {w}" for s, (_, w) in zip(scores, subjects)])
            weight_sum_str = " + ".join([str(w) for _, w in subjects])
            
        elif scenario == 1:
            w1 = rng.randint(3, 4) * 10
            w2 = 100 - w1
            s1 = rng.randint(70, 95)
            s2 = rng.randint(60, 90)
            total_credits = 100
            total_weighted_score = s1 * w1 + s2 * w2
            
            question_text = (
                f"某科目的學期成績計算方式為：平時成績佔 {w1}\\%，期末成績佔 {w2}\\%。\n"
                f"若小明的平時成績為 {s1} 分，期末成績為 {s2} 分，\n"
                f"求小明的學期加權平均分數。"
            )
            sum_str = f"{s1} \\times {w1} + {s2} \\times {w2}"
            weight_sum_str = f"{w1} + {w2}"
            
        elif scenario == 2:
            n1 = rng.choice([10, 15, 20])
            n2 = rng.choice([15, 20, 25])
            s1 = rng.randint(65, 85)
            s2 = rng.randint(60, 80)
            total_credits = n1 + n2
            total_weighted_score = s1 * n1 + s2 * n2
            
            question_text = (
                f"某班級分成 A、B 兩組進行測驗。\n"
                f"A 組有 {n1} 人，平均分數為 {s1} 分；\n"
                f"B 組有 {n2} 人，平均分數為 {s2} 分。\n"
                f"求全班的平均分數。"
            )
            sum_str = f"{s1} \\times {n1} + {s2} \\times {n2}"
            weight_sum_str = f"{n1} + {n2}"
            
        else:
            items = [("商品A", rng.randint(10, 50), rng.randint(2, 5)), 
                     ("商品B", rng.randint(20, 80), rng.randint(1, 4))]
            total_credits = sum(w for _, _, w in items)
            total_weighted_score = sum(p * w for _, p, w in items)
            
            question_text = (
                f"小華購買了 {items[0][2]} 件單價為 {items[0][1]} 元的{items[0][0]}，\n"
                f"以及 {items[1][2]} 件單價為 {items[1][1]} 元的{items[1][0]}。\n"
                f"求這些商品的平均單價。"
            )
            sum_str = " + ".join([f"{p} \\times {w}" for _, p, w in items])
            weight_sum_str = " + ".join([str(w) for _, _, w in items])
            
        from fractions import Fraction
        frac = Fraction(total_weighted_score, total_credits)
        if frac.denominator == 1:
            answer = str(frac.numerator)
            ans_latex = str(frac.numerator)
        else:
            answer = f"{frac.numerator}/{frac.denominator}"
            ans_latex = f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
            
        param_tuple = (scenario, total_weighted_score, total_credits)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        explanation = (
            f"加權平均數 = $\\frac{{\\text{{總值}}}}{{\\text{{總權數}}}}$\n\n"
            f"總值 = ${sum_str} = {total_weighted_score}$\n"
            f"總權數 = ${weight_sum_str} = {total_credits}$\n"
            f"加權平均數 = $\\frac{{{total_weighted_score}}}{{{total_credits}}} = {ans_latex}$"
        )
        
        choices = [answer]
        while len(choices) < 4:
            fake_num = total_weighted_score + rng.randint(-10, 10) * total_credits
            fake_frac = Fraction(fake_num, total_credits)
            fake_ans = str(fake_frac.numerator) if fake_frac.denominator == 1 else f"{fake_frac.numerator}/{fake_frac.denominator}"
            if fake_ans not in choices and fake_frac > 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "weighted_mean_basic",
            "generator_key": "b4.chap3.weighted_mean_basic",
            "answer_type": "rational_fraction",
            "difficulty": difficulty,
            "diagnosis_tags": ["weighted_mean"],
            "remediation_candidates": ["vh_數學B4_WeightedMean"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "total_weighted_score": total_weighted_score, "total_credits": total_credits},
        }

    raise RuntimeError("Failed to generate unique parameters")

def _generate_variance_std_scenario(rng: random.Random, is_variance: bool) -> Tuple[int, int, int, str, str]:
    scenario = rng.randint(0, 2)
    if scenario == 0:
        data, mean, pop_var = _generate_perfect_square_variance_dataset(rng)
        n = len(data)
        data_str = ", ".join(map(str, data))
        target = "變異數" if is_variance else "標準差"
        question_text = f"已知一組母體數據為 {data_str}，求這組數據的母體{target}。"
        dev_sum_str = " + ".join([f"({x} - {mean})^2" for x in data])
        dev_sum_val = sum((x - mean)**2 for x in data)
        explanation = (
            f"1. 先求算術平均數 $\\mu = \\frac{{{' + '.join(map(str, data))}}}{{{n}}} = {mean}$\n"
            f"2. 計算離均差平方和：\n"
            f"   $\\sum(x_i - \\mu)^2 = {dev_sum_str} = {dev_sum_val}$\n"
            f"3. 計算母體變異數 $\\sigma^2 = \\frac{{{dev_sum_val}}}{{{n}}} = {pop_var}\n"
        )
    elif scenario == 1:
        n = rng.randint(5, 20)
        mean = rng.randint(10, 50)
        var = rng.randint(2, 6)**2
        sum_sq = n * (var + mean**2)
        target = "變異數" if is_variance else "標準差"
        question_text = f"已知有 {n} 筆母體數據，其算術平均數為 {mean}，且這些數據的平方和為 {sum_sq}，求這組數據的母體{target}。"
        pop_var = var
        explanation = (
            f"利用變異數的快速公式：$\\sigma^2 = \\frac{{\\sum x_i^2}}{{N}} - \\mu^2$\n"
            f"已知 $N = {n}$，$\\mu = {mean}$，$\\sum x_i^2 = {sum_sq}$\n"
            f"代入公式得：$\\sigma^2 = \\frac{{{sum_sq}}}{{{n}}} - {mean}^2 = {sum_sq // n} - {mean**2} = {pop_var}\n"
        )
    else:
        n = rng.randint(10, 30)
        var = rng.randint(2, 6)**2
        dev_sum = n * var
        target = "變異數 $\\sigma^2$" if is_variance else "標準差 $\\sigma$"
        question_text = f"已知有 {n} 筆母體數據 $x_1, \\dots, x_{n}$，其算術平均數為 $\\mu$。若已知 $\\sum_{{i=1}}^{{{n}}}(x_i - \\mu)^2 = {dev_sum}$，求這組數據的母體{target}。"
        pop_var = var
        explanation = (
            f"根據母體變異數定義：$\\sigma^2 = \\frac{{\\sum (x_i - \\mu)^2}}{{N}}$\n"
            f"已知 $N = {n}$，離均差平方和為 {dev_sum}\n"
            f"代入公式得：$\\sigma^2 = \\frac{{{dev_sum}}}{{{n}}} = {pop_var}\n"
        )
        
    ans_val = pop_var if is_variance else math.isqrt(pop_var)
    if not is_variance:
        explanation += f"4. 計算標準差 $\\sigma = \\sqrt{{\\sigma^2}} = \\sqrt{{{pop_var}}} = {ans_val}$"
        
    return scenario, pop_var, ans_val, question_text, explanation

def variance_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        scenario, pop_var, ans_val, question_text, explanation = _generate_variance_std_scenario(rng, is_variance=True)
        
        param_tuple = (scenario, pop_var, ans_val)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        answer = str(ans_val)
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(ans_val + rng.randint(-3, 5))
            if fake_ans not in choices and int(fake_ans) >= 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "variance_basic_numeric",
            "generator_key": "b4.chap3.variance_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["variance"],
            "remediation_candidates": ["vh_數學B4_VarianceAndStandardDeviation"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "variance": pop_var},
        }

    raise RuntimeError("Failed to generate unique parameters")

def standard_deviation_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        scenario, pop_var, ans_val, question_text, explanation = _generate_variance_std_scenario(rng, is_variance=False)
        
        param_tuple = (scenario, pop_var, ans_val)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        answer = str(ans_val)
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(ans_val + rng.randint(-2, 3))
            if fake_ans not in choices and int(fake_ans) >= 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "standard_deviation_basic_numeric",
            "generator_key": "b4.chap3.standard_deviation_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["standard_deviation"],
            "remediation_candidates": ["vh_數學B4_VarianceAndStandardDeviation"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "std_dev": ans_val},
        }

    raise RuntimeError("Failed to generate unique parameters")

def linear_transform_mean(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        scenario = rng.randint(0, 2)
        
        if scenario == 0:
            mu_x = rng.randint(40, 70)
            a = rng.randint(2, 5)
            b = rng.randint(5, 20) * rng.choice([-1, 1])
            mu_y = a * mu_x + b
            sign = "+" if b > 0 else "-"
            abs_b = abs(b)
            question_text = f"已知一組數據 $x_1, \\dots, x_n$ 的算術平均數 $\\mu_x = {mu_x}$。若將每筆數據進行線性變換 $y_i = {a}x_i {sign} {abs_b}$，求新數據 $y_i$ 的算術平均數 $\\mu_y$。"
            explanation = f"根據線性變換性質，新平均數 $\\mu_y = a\\mu_x + b$。\n在此題中 $\\mu_y = {a} \\times {mu_x} {sign} {abs_b} = {a * mu_x} {sign} {abs_b} = {mu_y}$。"
            answer_val = mu_y
            
        elif scenario == 1:
            mu_x = rng.randint(40, 70)
            b = rng.randint(5, 20) * rng.choice([-1, 1])
            mu_y = mu_x + b
            sign = "+" if b > 0 else "-"
            abs_b = abs(b)
            question_text = f"某次考試全班平均分數為 {mu_x} 分。老師決定將每位同學的分數調整為「原分數 {sign} {abs_b} 分」，求調整後的全班平均分數。"
            explanation = f"將每筆數據平移，平均數也會跟著平移。\n調整後的平均分數 = {mu_x} {sign} {abs_b} = {mu_y} 分。"
            answer_val = mu_y
            
        else:
            is_add = rng.choice([True, False])
            if is_add:
                mu_x = rng.randint(40, 60)
                b = rng.randint(5, 15) * rng.choice([-1, 1])
                mu_y = mu_x + b
                question_text = f"某班級的平均成績原為 {mu_x} 分，經過成績調整後，全班每個人都加了 $b$ 分，新的平均成績變為 {mu_y} 分。求 $b$ 的值。"
                explanation = f"若每人加 $b$ 分，則新的平均數為原平均數加 $b$。\n即 ${mu_x} + b = {mu_y}$，可求得 $b = {b}$。"
                answer_val = b
            else:
                mu_x = rng.randint(10, 30)
                a = rng.randint(2, 5)
                mu_y = mu_x * a
                question_text = f"已知一組數據的平均數為 {mu_x}，若將每筆數據皆乘上一個常數 $a$ 後，新的平均數變為 {mu_y}，求常數 $a$ 的值。"
                explanation = f"若每筆數據乘上 $a$，則新平均數為原平均數的 $a$ 倍。\n即 ${mu_x} \\times a = {mu_y}$，可求得 $a = {a}$。"
                answer_val = a
                
        param_tuple = (scenario, answer_val)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        answer = str(answer_val)
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(answer_val + rng.randint(-10, 10))
            if fake_ans not in choices:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "linear_transform_mean",
            "generator_key": "b4.chap3.linear_transform_mean",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["linear_transformation", "mean"],
            "remediation_candidates": ["vh_數學B4_LinearTransformationOfData"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "answer": answer_val},
        }

    raise RuntimeError("Failed to generate unique parameters")

def linear_transform_std_variance(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        scenario = rng.randint(0, 2)
        ask_variance = rng.choice([True, False])
        std_x = rng.randint(2, 6)
        var_x = std_x ** 2
        
        if scenario == 0:
            a = rng.choice([-3, -2, 2, 3, 4])
            b = rng.randint(5, 20) * rng.choice([-1, 1])
            std_y = abs(a) * std_x
            var_y = (a ** 2) * var_x
            sign = "+" if b > 0 else "-"
            abs_b = abs(b)
            target = "變異數 $\\sigma_y^2$" if ask_variance else "標準差 $\\sigma_y$"
            question_text = f"已知一組數據 $x_1, \\dots, x_n$ 的標準差 $\\sigma_x = {std_x}$。若進行線性變換 $y_i = {a}x_i {sign} {abs_b}$，求新數據 $y_i$ 的{target}。"
            if ask_variance:
                explanation = f"根據線性變換性質，新變異數 $\\sigma_y^2 = a^2 \\sigma_x^2$。\n$\\sigma_x^2 = {var_x}$，所以 $\\sigma_y^2 = ({a})^2 \\times {var_x} = {var_y}$。"
                answer_val = var_y
            else:
                explanation = f"根據線性變換性質，新標準差 $\\sigma_y = |a| \\sigma_x$。\n$\\sigma_y = |{a}| \\times {std_x} = {std_y}$。"
                answer_val = std_y
                
        elif scenario == 1:
            b = rng.randint(5, 20) * rng.choice([-1, 1])
            std_y = std_x
            var_y = var_x
            sign = "+" if b > 0 else "-"
            abs_b = abs(b)
            target = "變異數" if ask_variance else "標準差"
            question_text = f"某次考試全班成績的{target}為 {var_x if ask_variance else std_x}。老師將每位同學的分數都 {sign} {abs_b} 分，求調整後全班成績的{target}。"
            if ask_variance:
                explanation = f"將數據平移不會改變數據的分散程度，因此變異數保持不變。\n新的變異數 = {var_y}。"
                answer_val = var_y
            else:
                explanation = f"將數據平移不會改變數據的分散程度，因此標準差保持不變。\n新的標準差 = {std_y}。"
                answer_val = std_y
                
        else:
            a = rng.choice([-4, -3, -2, 2, 3, 4])
            std_y = abs(a) * std_x
            var_y = (a ** 2) * var_x
            target = "變異數" if ask_variance else "標準差"
            question_text = f"有一組數據的{target}為 {var_x if ask_variance else std_x}。若將每筆數據皆乘以 {a} 倍，求新數據的{target}。"
            if ask_variance:
                explanation = f"將數據乘上 $a$ 倍，其變異數會變為 $a^2$ 倍。\n新的變異數 = $({a})^2 \\times {var_x} = {var_y}$。"
                answer_val = var_y
            else:
                explanation = f"將數據乘上 $a$ 倍，其標準差會變為 $|a|$ 倍。\n新的標準差 = $|{a}| \\times {std_x} = {std_y}$。"
                answer_val = std_y
                
        param_tuple = (scenario, ask_variance, answer_val)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        answer = str(answer_val)
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(int(answer) + rng.choice([-1, 1]) * rng.randint(1, 5) * (std_x if not ask_variance else var_x))
            if fake_ans not in choices and int(fake_ans) >= 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "linear_transform_std_variance",
            "generator_key": "b4.chap3.linear_transform_std_variance",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["linear_transformation", "variance_std"],
            "remediation_candidates": ["vh_數學B4_LinearTransformationOfData"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "ask_variance": ask_variance, "answer": answer_val},
        }

    raise RuntimeError("Failed to generate unique parameters")


from fractions import Fraction
import math

def _calculate_percentile(data: list[int], k: int) -> tuple[str, str, str, Fraction]:
    """Calculate the k-th percentile of a list of data. Returns (ans_str, ans_latex, explanation_steps, Fraction)."""
    n = len(data)
    i = n * k / 100
    sorted_data = sorted(data)
    
    if i.is_integer():
        idx = int(i) - 1
        x1 = sorted_data[idx]
        x2 = sorted_data[idx + 1]
        val = Fraction(x1 + x2, 2)
        step = (
            f"計算指標值 $i = N \times \frac{{k}}{{100}} = {n} \times \frac{{{k}}}{{100}} = {int(i)}$。\n"
            f"因為 $i$ 為整數，故第 {k} 百分位數為第 {int(i)} 筆與第 {int(i)+1} 筆資料的平均數。\n"
            f"$P_{{{k}}} = \frac{{x_{{{int(i)}}} + x_{{{int(i)+1}}}}}{{2}} = \frac{{{x1} + {x2}}}{{2}}"
        )
        if val.denominator == 1:
            ans_str = str(val.numerator)
            ans_latex = str(val.numerator)
            step += f" = {ans_latex}$"
        else:
            ans_str = f"{val.numerator}/{val.denominator}"
            ans_latex = f"\frac{{{val.numerator}}}{{{val.denominator}}}"
            if val.denominator == 2:
                ans_latex = str(val.numerator / 2) # Often displayed as decimal for x.5
                ans_str = str(val.numerator / 2)
            step += f" = {ans_latex}$"
    else:
        idx = math.floor(i)
        val = sorted_data[idx]
        ans_str = str(val)
        ans_latex = str(val)
        step = (
            f"計算指標值 $i = N \times \frac{{k}}{{100}} = {n} \times \frac{{{k}}}{{100}} = {i}$。\n"
            f"因為 $i$ 不為整數，故無條件進位取整數得 {idx + 1}。\n"
            f"第 {k} 百分位數即為第 {idx + 1} 筆資料：$P_{{{k}}} = x_{{{idx + 1}}} = {ans_latex}$"
        )
        val = Fraction(val, 1)
        
    return ans_str, ans_latex, step, val

def _generate_dispersion_context(rng: random.Random, n: int) -> tuple[int, list[int], str, str, str]:
    scenario = rng.randint(0, 2)
    if scenario == 0:
        data = [rng.randint(10, 99) for _ in range(n)]
        data_str = ", ".join(map(str, data))
        prefix = f"給定以下一組未排序的資料：\n{data_str}\n"
        context_desc = "這組資料"
        unit = ""
    elif scenario == 1:
        data = [rng.randint(40, 100) for _ in range(n)]
        data_str = ", ".join(map(str, data))
        prefix = f"某班 {n} 位學生的平時測驗分數如下：\n{data_str}\n"
        context_desc = "這組分數"
        unit = "分"
    else:
        data = [rng.randint(15, 35) for _ in range(n)]
        data_str = ", ".join(map(str, data))
        prefix = f"某手搖飲店連續 {n} 天的每日銷售杯數如下：\n{data_str}\n"
        context_desc = "這組銷售杯數"
        unit = "杯"
    return scenario, data, prefix, context_desc, unit

def range_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    
    for _ in range(50):
        n = rng.randint(7, 12)
        scenario, data, prefix, context_desc, unit = _generate_dispersion_context(rng, n)
        
        param_tuple = (scenario, tuple(sorted(data)))
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        data.sort()
        max_val = data[-1]
        min_val = data[0]
        ans_val = max_val - min_val
        
        question_text = f"{prefix}求{context_desc}的全距。"
        
        explanation = (
            f"全距 = 最大值 - 最小值\n\n"
            f"先找出{context_desc}的最大值與最小值：\n"
            f"最大值 = {max_val}\n"
            f"最小值 = {min_val}\n"
            f"全距 = {max_val} - ({min_val}) = {ans_val}"
        )
        
        answer = str(ans_val)
        choices = [answer]
        while len(choices) < 4:
            fake_ans = str(ans_val + rng.randint(-10, 10))
            if fake_ans not in choices and int(fake_ans) > 0:
                choices.append(fake_ans)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": answer,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "range_basic_numeric",
            "generator_key": "b4.chap3.range_basic_numeric",
            "answer_type": "integer",
            "difficulty": difficulty,
            "diagnosis_tags": ["range"],
            "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "range": ans_val},
        }

    raise RuntimeError("Failed to generate unique parameters")

def percentile_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    for _ in range(50):
        n = rng.choice([8, 10, 12, 15, 20])
        scenario, data, prefix, context_desc, unit = _generate_dispersion_context(rng, n)
        k = rng.choice([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90])
        
        param_tuple = (scenario, tuple(sorted(data)), k)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        question_text = f"{prefix}求{context_desc}的第 {k} 百分位數 $P_{{{k}}}$。"
        ans_str, ans_latex, step, ans_frac = _calculate_percentile(data, k)
        
        sorted_data_str = ", ".join(map(str, sorted(data)))
        explanation = (
            f"1. 先將數據由小到大排列：\n{sorted_data_str}\n\n"
            f"2. {step}"
        )
        
        choices = [ans_str]
        while len(choices) < 4:
            fake_k = rng.choice([x for x in [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90] if x != k])
            fake_ans, _, _, _ = _calculate_percentile(data, fake_k)
            if fake_ans not in choices:
                choices.append(fake_ans)
            if len(choices) < 4:
                fake_val = float(ans_frac) + rng.randint(-5, 5)
                fake_ans_fb = str(int(fake_val)) if fake_val.is_integer() else str(fake_val)
                if fake_ans_fb not in choices and fake_val > 0:
                    choices.append(fake_ans_fb)
                    
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": ans_str,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "percentile_basic_numeric",
            "generator_key": "b4.chap3.percentile_basic_numeric",
            "answer_type": "rational_fraction",
            "difficulty": difficulty,
            "diagnosis_tags": ["percentile"],
            "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "k": k, "answer": ans_str},
        }

    raise RuntimeError("Failed to generate unique parameters")

def quartile_basic_numeric(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    for _ in range(50):
        n = rng.choice([8, 10, 11, 12, 14, 15])
        scenario, data, prefix, context_desc, unit = _generate_dispersion_context(rng, n)
        q = rng.choice([1, 2, 3])
        k = q * 25
        
        param_tuple = (scenario, tuple(sorted(data)), q)
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        q_names = {1: "第一四分位數", 2: "第二四分位數（中位數）", 3: "第三四分位數"}
        question_text = f"{prefix}求{context_desc}的{q_names[q]} $Q_{q}$。"
        ans_str, ans_latex, step, ans_frac = _calculate_percentile(data, k)
        
        sorted_data_str = ", ".join(map(str, sorted(data)))
        explanation = (
            f"四分位數 $Q_{q}$ 相當於第 {k} 百分位數 $P_{{{k}}}$。\n"
            f"1. 先將數據由小到大排列：\n{sorted_data_str}\n\n"
            f"2. {step}"
        )
        
        choices = [ans_str]
        while len(choices) < 4:
            fake_k = rng.choice([25, 50, 75])
            fake_ans, _, _, _ = _calculate_percentile(data, fake_k)
            if fake_ans not in choices:
                choices.append(fake_ans)
            if len(choices) < 4:
                fake_val = float(ans_frac) + rng.randint(-5, 5)
                fake_ans_fb = str(int(fake_val)) if fake_val.is_integer() else str(fake_val)
                if fake_ans_fb not in choices and fake_val > 0:
                    choices.append(fake_ans_fb)
                    
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": ans_str,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "quartile_basic_numeric",
            "generator_key": "b4.chap3.quartile_basic_numeric",
            "answer_type": "rational_fraction",
            "difficulty": difficulty,
            "diagnosis_tags": ["quartile"],
            "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "q": q, "answer": ans_str},
        }

    raise RuntimeError("Failed to generate unique parameters")

def interquartile_range_basic(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    for _ in range(50):
        n = rng.choice([8, 10, 11, 12, 14, 15])
        scenario, data, prefix, context_desc, unit = _generate_dispersion_context(rng, n)
        
        param_tuple = (scenario, tuple(sorted(data)))
        if seen_parameter_tuples is not None:
            if param_tuple in seen_parameter_tuples:
                continue
            seen_parameter_tuples.add(param_tuple)
            
        question_text = f"{prefix}求{context_desc}的四分位距 (IQR)。"
        q1_str, q1_latex, q1_step, q1_val = _calculate_percentile(data, 25)
        q3_str, q3_latex, q3_step, q3_val = _calculate_percentile(data, 75)
        
        iqr_val = q3_val - q1_val
        if iqr_val.denominator == 1:
            ans_str = str(iqr_val.numerator)
            ans_latex = str(iqr_val.numerator)
        elif iqr_val.denominator == 2:
            ans_str = str(iqr_val.numerator / 2)
            ans_latex = str(iqr_val.numerator / 2)
        else:
            ans_str = f"{iqr_val.numerator}/{iqr_val.denominator}"
            ans_latex = f"\frac{{{iqr_val.numerator}}}{{{iqr_val.denominator}}}"
            
        sorted_data_str = ", ".join(map(str, sorted(data)))
        explanation = (
            f"四分位距 $IQR = Q_3 - Q_1 = P_{{75}} - P_{{25}}$。\n"
            f"1. 將數據由小到大排列：\n{sorted_data_str}\n\n"
            f"2. 計算 $Q_1$ (第 25 百分位數)：\n{q1_step}\n\n"
            f"3. 計算 $Q_3$ (第 75 百分位數)：\n{q3_step}\n\n"
            f"4. 四分位距 $IQR = {q3_latex} - {q1_latex} = {ans_latex}$。"
        )
        
        choices = [ans_str]
        while len(choices) < 4:
            fake_val = float(iqr_val) + rng.randint(-5, 5)
            fake_ans_fb = str(int(fake_val)) if fake_val.is_integer() else str(fake_val)
            if fake_ans_fb not in choices and fake_val > 0:
                choices.append(fake_ans_fb)
        rng.shuffle(choices)
        
        return {
            "question_text": question_text,
            "answer": ans_str,
            "choices": choices,
            "explanation": explanation,
            "skill_id": skill_id,
            "subskill_id": subskill_id,
            "problem_type_id": "interquartile_range_basic",
            "generator_key": "b4.chap3.interquartile_range_basic",
            "answer_type": "rational_fraction",
            "difficulty": difficulty,
            "diagnosis_tags": ["interquartile_range"],
            "remediation_candidates": ["vh_數學B4_DispersionMeasures"],
            "source_style_refs": ["B4_Ch3"],
            "parameters": {"scenario": scenario, "answer": ans_str},
        }

    raise RuntimeError("Failed to generate unique parameters")


def _hash_spec(spec: Dict[str, Any]) -> str:
    return hashlib.sha1(json.dumps(spec, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def cumulative_frequency_tables_graphs_review_shell_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    contexts = [
        ("score_band", "分數區間"),
        ("height_band", "身高區間（公分）"),
        ("time_band", "時間區間（分鐘）"),
        ("sales_band", "銷售量區間（件）"),
    ]
    context_id, context_label = rng.choice(contexts)
    n_bins = rng.choice([4, 5, 6])
    width = rng.choice([5, 10, 20])
    start = rng.choice([0, 10, 20, 40, 60])
    freqs = [rng.randint(2, 9) for _ in range(n_bins)]

    bins = [f"{start + i * width}-{start + (i + 1) * width - 1}" for i in range(n_bins)]
    cumulative_values: List[int] = []
    run = 0
    for f in freqs:
        run += f
        cumulative_values.append(run)

    rows = []
    for i, b in enumerate(bins):
        rows.append([b, freqs[i], "□" if i >= 1 else cumulative_values[i]])
    headers = ["組別", "次數", "累積次數"]
    table_title = "累積次數分配表"
    table_spec = {"headers": headers, "rows": rows, "bins": bins, "frequencies": freqs, "context": context_id}
    table_spec_hash = _hash_spec(table_spec)
    scenario_id = f"cumulative_frequency_table_completion_{context_id}_{n_bins}g_w{width}"
    parameter_signature = (
        f"cumulative_table:context={context_id},bins={','.join(bins)},"
        f"freq={','.join(str(v) for v in freqs)},cum={','.join(str(v) for v in cumulative_values)}"
    )
    param_tuple = ("cumulative_frequency_tables_graphs_review_shell_v2", scenario_id, parameter_signature)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)

    image_b64 = _build_table_png_base64(headers, rows, title=table_title)
    return {
        "question_text": f"下表為{context_label}的{table_title}，請補上空格中的累積次數，並簡述你的計算方式。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "cumulative_frequency_table_completion",
            "required_columns": headers,
            "cumulative_values": cumulative_values,
            "frequency_values": freqs,
        },
        "rubric": {
            "criteria": ["累積次數填寫正確", "計算步驟合理", "表格完成度"]
        },
        "choices": [],
        "explanation": "累積次數由上而下逐步累加：第 i 列累積次數 = 前一列累積次數 + 本列次數。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "cumulative_frequency_table_completion_review",
        "scenario_family": "cumulative_frequency_table_completion_review",
        "scenario_id": scenario_id,
        "parameter_signature": parameter_signature,
        "table_spec_hash": table_spec_hash,
        "generator_key": "b4.chap3.cumulative_frequency_tables_graphs_review_shell_v2",
        "answer_type": "handwriting",
        "answer_input_type": "free_response_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["cumulative_frequency", "table_completion"],
        "remediation_candidates": ["vh_數學B4_CumulativeFrequencyTablesAndGraphs"],
        "source_style_refs": ["B4_Ch3_cumulative_frequency"],
        "textbook_alignment_note": "補表題維持 review/手寫檢核，不硬轉 deterministic 多格表。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "cumulative_frequency_table_completion_review",
            "template_id": "cumulative_frequency_table_completion_review",
            "numeric_params": {"bin_count": n_bins, "width": width, "start": start},
            "context_params": {"context": context_id},
            "bins": bins,
            "frequencies": freqs,
            "cumulative_values": cumulative_values,
            "table_spec_hash": table_spec_hash,
        },
        "visual_backed": True,
        "visual_asset_type": "table",
        "table_title": table_title,
        "table": {"table_title": table_title, "headers": headers, "rows": rows},
        "image_base64": image_b64,
        "visual_aids": [{
            "type": "table",
            "title": table_title,
            "caption": table_title,
            "alt_text": table_title,
            "headers": headers,
            "rows": rows,
        }],
        "requires_handwriting": True,
        "requires_teacher_review": True,
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "review_mode",
        "grading_mode": "teacher_review",
    }


def frequency_distribution_table_construction_shell_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    contexts = [
        ("exam_scores", "某班數學小考分數"),
        ("heights", "某班學生身高（公分）"),
        ("running_time", "短跑完成時間（秒）"),
        ("sales_units", "商店每日銷售量（件）"),
    ]
    context_id, context_label = rng.choice(contexts)
    width = rng.choice([5, 10, 20])
    n_bins = rng.choice([4, 5, 6])
    start = rng.choice([0, 10, 20, 30, 40])
    bins: List[Tuple[int, int]] = []
    for i in range(n_bins):
        lo = start + i * width
        bins.append((lo, lo + width - 1))

    frequency_map: Dict[str, int] = {}
    raw_data: List[int] = []
    for lo, hi in bins:
        label = f"{lo}-{hi}"
        count = rng.randint(3, 8)
        frequency_map[label] = count
        raw_data.extend([rng.randint(lo, hi) for _ in range(count)])
    rng.shuffle(raw_data)

    headers = ["組別", "次數"]
    rows = [[k, "□"] for k in frequency_map.keys()]
    table_title = "次數分配表"
    raw_data_hash = hashlib.sha1(json.dumps(raw_data, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    table_spec_hash = _hash_spec({"headers": headers, "rows": rows, "context": context_id})
    scenario_id = f"frequency_table_construction_{context_id}_{n_bins}g_w{width}"
    parameter_signature = (
        f"frequency_table_construction:context={context_id},groups={n_bins},width={width},"
        f"start={start},raw_hash={raw_data_hash}"
    )
    param_tuple = ("frequency_distribution_table_construction_shell_v2", scenario_id, parameter_signature)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)

    return {
        "question_text": f"下列資料為{context_label}：{raw_data}。請整理成次數分配表並填入各組次數。",
        "answer": "",
        "correct_answer": "",
        "expected_answer_schema": {
            "type": "frequency_table_construction",
            "required_columns": headers,
            "frequency_map": frequency_map,
            "bin_edges": [list(b) for b in bins],
        },
        "rubric": {
            "criteria": ["分組區間正確", "次數統計正確", "表格完整"]
        },
        "choices": [],
        "explanation": "依各組區間統計原始資料筆數，可得到次數分配表。",
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "frequency_table_construction_review",
        "scenario_family": "frequency_distribution_table_construction",
        "scenario_id": scenario_id,
        "parameter_signature": parameter_signature,
        "table_spec_hash": table_spec_hash,
        "generator_key": "b4.chap3.frequency_distribution_table_construction_shell_v2",
        "answer_type": "handwriting",
        "answer_input_type": "free_response_or_handwriting",
        "difficulty": difficulty,
        "diagnosis_tags": ["frequency_distribution_table", "table_construction"],
        "remediation_candidates": ["vh_數學B4_FrequencyDistributionTableConstruction"],
        "source_style_refs": ["B4_Ch3_frequency_table_construction"],
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "frequency_distribution_table_construction",
            "template_id": "frequency_table_construction_review",
            "numeric_params": {"group_width": width, "group_count": n_bins, "start": start},
            "context_params": {"context": context_id},
            "raw_data": raw_data,
            "frequency_map": frequency_map,
            "raw_data_hash": raw_data_hash,
            "table_spec_hash": table_spec_hash,
        },
        "visual_backed": True,
        "visual_asset_type": "table",
        "raw_data": raw_data,
        "table_schema": {"headers": headers, "rows": rows},
        "table_title": table_title,
        "table": {"table_title": table_title, "headers": headers, "rows": rows},
        "visual_aids": [{
            "type": "table",
            "title": table_title,
            "caption": table_title,
            "alt_text": table_title,
            "headers": headers,
            "rows": rows,
        }],
        "requires_handwriting": True,
        "requires_teacher_review": True,
        "runtime_mode": "visual_or_handwriting_ai_checked",
        "check_mode": "handwriting_ai_checked",
        "grading_mode": "ai_assisted_review",
    }


def histogram_reading_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    contexts = [("score", "分數區間"), ("height", "身高區間（公分）"), ("time", "時間區間（分鐘）")]
    context_id, x_label = rng.choice(contexts)
    width = rng.choice([5, 10, 20])
    n_bins = rng.choice([4, 5, 6])
    start = rng.choice([0, 10, 20, 30, 40])
    bins = [f"{start + i * width}-{start + (i + 1) * width - 1}" for i in range(n_bins)]
    freqs = [rng.randint(2, 12) for _ in range(n_bins)]
    mode = rng.choice(["group_frequency", "total_frequency", "max_group"])

    if mode == "group_frequency":
        target_idx = rng.randrange(n_bins)
        question_text = f"附圖為直方圖，請問 {bins[target_idx]} 這一組的次數是多少？"
        answer = str(freqs[target_idx])
        explanation = f"{bins[target_idx]} 這一組柱高對應次數為 {answer}。"
    elif mode == "total_frequency":
        target_idx = None
        total = sum(freqs)
        question_text = "附圖為直方圖，請問全部資料的總次數是多少？"
        answer = str(total)
        explanation = f"總次數為各組次數相加：{' + '.join(str(v) for v in freqs)} = {total}。"
    else:
        target_idx = int(max(range(n_bins), key=lambda i: freqs[i]))
        question_text = "附圖為直方圖，請問哪一組的次數最多？"
        answer = bins[target_idx]
        explanation = f"柱高最高的組別為 {answer}。"

    chart_spec = {"type": "histogram", "title": "直方圖", "x_label": x_label, "y_label": "次數", "bins": bins, "frequencies": freqs}
    chart_spec_hash = _hash_spec(chart_spec)
    scenario_id = f"histogram_{context_id}_{mode}_{n_bins}g_w{width}"
    parameter_signature = f"histogram:context={context_id},mode={mode},bins={','.join(bins)},freq={','.join(str(v) for v in freqs)}"
    param_tuple = ("histogram_reading_v2", scenario_id, parameter_signature)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)

    image_b64 = _build_chart_png_base64(bins, freqs, chart_kind="bar", title="直方圖")
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": [answer],
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "histogram_reading",
        "scenario_family": "histogram_reading_short_answer",
        "scenario_id": scenario_id,
        "parameter_signature": parameter_signature,
        "chart_spec_hash": chart_spec_hash,
        "generator_key": "b4.chap3.histogram_reading_v2",
        "answer_type": "integer",
        "difficulty": difficulty,
        "diagnosis_tags": ["histogram_reading", "chart_reading"],
        "remediation_candidates": ["vh_數學B4_HistogramsAndFrequencyPolygons"],
        "source_style_refs": ["B4_Ch3_histogram"],
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "histogram_reading_short_answer",
            "template_id": "histogram_reading",
            "numeric_params": {"width": width, "n_bins": n_bins, "start": start},
            "context_params": {"context": context_id},
            "bins": bins,
            "frequencies": freqs,
            "question_target": mode,
            "chart_spec_hash": chart_spec_hash,
        },
        "chart_spec": chart_spec,
        "image_base64": image_b64,
        "visual_aids": [{
            "type": "histogram",
            "title": "直方圖",
            "caption": "直方圖",
            "alt_text": "直方圖",
            "x_label": x_label,
            "y_label": "次數",
            "bins": bins,
            "frequencies": freqs,
        }],
        "visual_backed": True,
        "visual_asset_type": "histogram",
        "runtime_mode": "visual_reading_with_short_answer",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def sampling_survey_foundation_choice_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_SAMPLING_SURVEY_SCENARIO_ID
    global _LAST_SAMPLING_SURVEY_PARAMETER_SIGNATURE
    rng = random.Random(seed)
    scenarios = [
        (
            "population_sample_size_identification_city_5000_250",
            "某城市共有 5000 位機車族，研究者抽出其中 250 位填寫問卷。下列何者是樣本？請輸入選項代號。",
            "3",
            [
                "1. 全城市 5000 位機車族",
                "2. 全城市所有交通工具使用者",
                "3. 被抽出的 250 位機車族",
                "4. 問卷題目本身",
            ],
            "樣本是實際被抽出並接受調查的對象，因此是被抽出的 250 位機車族。",
        ),
        (
            "population_identification_school_students",
            "某校想研究全校學生的早餐習慣，隨機抽出 120 人作答。下列何者是母群體？請輸入選項代號。",
            "1",
            [
                "1. 全校所有學生",
                "2. 抽出的 120 人",
                "3. 早餐種類清單",
                "4. 問卷題目",
            ],
            "母群體是研究想要推論的整體，這裡是全校所有學生。",
        ),
        (
            "sample_size_identification_factory_1200_80",
            "某工廠共有 1200 件產品，品管抽查其中 80 件。下列何者是樣本數？請輸入選項代號。",
            "2",
            [
                "1. 1200",
                "2. 80",
                "3. 1120",
                "4. 無法判斷",
            ],
            "樣本數是被抽查的件數，因此為 80。",
        ),
        (
            "population_size_identification_community_3000_150",
            "某社區共有 3000 位住戶，抽出 150 位進行訪問。下列何者是母群體數？請輸入選項代號。",
            "1",
            [
                "1. 3000",
                "2. 150",
                "3. 2850",
                "4. 3150",
            ],
            "母群體數是整體住戶人數，因此為 3000。",
        ),
        (
            "census_or_sample_city_commute",
            "調查某市通勤方式時，研究者只訪問其中 400 位市民。這屬於下列何者？請輸入選項代號。",
            "2",
            [
                "1. 普查",
                "2. 抽查",
                "3. 實驗研究",
                "4. 無法分類",
            ],
            "只調查部分對象屬於抽查。",
        ),
        (
            "census_or_sample_school_all_students",
            "學校調查午餐滿意度時，訪問全校每一位學生。這屬於下列何者？請輸入選項代號。",
            "1",
            [
                "1. 普查",
                "2. 抽查",
                "3. 分層抽樣",
                "4. 部落抽樣",
            ],
            "訪問全體成員屬於普查。",
        ),
        (
            "correct_statement_population_sample_traffic",
            "關於母群體與樣本，下列敘述何者正確？請輸入選項代號。",
            "4",
            [
                "1. 樣本一定比母群體大",
                "2. 母群體一定是 100 人",
                "3. 樣本數等於問卷題數",
                "4. 樣本是由母群體中抽出的部分對象",
            ],
            "樣本是由母群體中抽出的部分個體，這是基本定義。",
        ),
        (
            "population_sample_identification_food_test",
            "某食品公司從當日生產的 2000 包餅乾中抽出 100 包檢驗。下列何者是樣本？請輸入選項代號。",
            "2",
            [
                "1. 當日全部 2000 包餅乾",
                "2. 抽出的 100 包餅乾",
                "3. 生產機器台數",
                "4. 檢驗標準表",
            ],
            "樣本是實際拿來檢驗的 100 包餅乾。",
        ),
        (
            "bias_concert_choice_version",
            "某候選人為了了解支持度，只在自己的造勢晚會上發放問卷。這個調查最可能產生哪一種問題？請輸入選項代號。",
            "1",
            [
                "1. 樣本可能偏向支持該候選人的族群",
                "2. 樣本數一定太大",
                "3. 問卷題目一定太少",
                "4. 這是標準的普查",
            ],
            "只在造勢晚會取樣，樣本來源偏向支持者，代表性不足。",
        ),
        (
            "sample_size_identification_school_1800_90",
            "某校共有 1800 位學生，研究者抽出 90 位做問卷。下列何者是樣本數？請輸入選項代號。",
            "3",
            [
                "1. 1800",
                "2. 1710",
                "3. 90",
                "4. 1890",
            ],
            "樣本數是被抽出的對象數量，因此為 90。",
        ),
    ]
    picked = rng.choice(scenarios)
    if seed is None and _LAST_SAMPLING_SURVEY_SCENARIO_ID is not None and len(scenarios) > 1:
        if picked[0] == _LAST_SAMPLING_SURVEY_SCENARIO_ID:
            cur_idx = scenarios.index(picked)
            picked = scenarios[(cur_idx + 1) % len(scenarios)]

    scenario_id, question_text, answer, choices, explanation = picked
    parameter_signature = f"sampling_survey_choice:scenario={scenario_id},answer={answer}"
    param_tuple = ("sampling_survey_foundation_choice_v2", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    _LAST_SAMPLING_SURVEY_SCENARIO_ID = scenario_id
    _LAST_SAMPLING_SURVEY_PARAMETER_SIGNATURE = parameter_signature

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "sampling_survey_foundation_identification",
        "scenario_family": "sampling_survey_foundation_identification",
        "scenario_id": scenario_id,
        "parameter_signature": parameter_signature,
        "generator_key": "b4.chap3.sampling_survey_foundation_choice_v2",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["sampling_survey", "population_sample"],
        "remediation_candidates": ["vh_數學B4_SamplingSurvey"],
        "source_style_refs": ["B4_Ch3_sampling_survey"],
        "textbook_alignment_note": "聚焦母群體、樣本、母群體數、樣本數與普查/抽查基本概念。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "sampling_survey_foundation_identification",
            "parameter_signature": parameter_signature,
        },
        "visual_backed": False,
        "requires_teacher_review": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def data_organization_chart_type_selection_choice_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_DATA_ORG_SCENARIO_ID
    global _LAST_DATA_ORG_PARAMETER_SIGNATURE
    rng = random.Random(seed)
    scenarios = [
        (
            "trend_weekly_attendance_line_chart",
            "某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 折線圖", "2. 圓形圖", "3. 直方圖", "4. 樹狀圖"],
            "1",
            "觀察隨時間變化趨勢，最適合使用折線圖。",
        ),
        (
            "category_transport_bar_chart",
            "某班記錄學生通勤方式（步行、公車、機車、腳踏車），想比較各類別人數，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 長條圖", "2. 折線圖", "3. 散佈圖", "4. 樹狀圖"],
            "1",
            "比較不同類別的人數，長條圖最直觀。",
        ),
        (
            "proportion_snack_pie_chart",
            "班上調查最喜歡的點心種類，想呈現各類別所占比例，最適合使用哪一種圖表？請輸入選項代號。",
            ["1. 圓形圖", "2. 折線圖", "3. 直方圖", "4. 箱型圖"],
            "1",
            "呈現整體比例關係時，圓形圖最合適。",
        ),
    ]
    picked = rng.choice(scenarios)
    if seed is None and _LAST_DATA_ORG_SCENARIO_ID is not None and len(scenarios) > 1:
        if picked[0] == _LAST_DATA_ORG_SCENARIO_ID:
            idx = scenarios.index(picked)
            picked = scenarios[(idx + 1) % len(scenarios)]
    scenario_id, question_text, choices, answer, explanation = picked
    param_sig = f"chart_type_selection_by_purpose:{scenario_id}"
    param_tuple = ("data_org_chart_type_v2", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    _LAST_DATA_ORG_SCENARIO_ID = scenario_id
    _LAST_DATA_ORG_PARAMETER_SIGNATURE = param_sig

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_type_selection_by_purpose",
        "scenario_family": "chart_type_selection_by_purpose",
        "scenario_id": scenario_id,
        "parameter_signature": param_sig,
        "generator_key": "b4.chap3.data_organization_chart_type_selection_choice_v2",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "chart_selection"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "textbook_alignment_note": "依資料目的選擇圖表，符合課本資料整理與圖表應用主軸。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "chart_type_selection_by_purpose",
            "parameter_signature": param_sig,
        },
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def data_organization_first_step_choice_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_DATA_ORG_SCENARIO_ID
    global _LAST_DATA_ORG_PARAMETER_SIGNATURE
    rng = random.Random(seed)
    scenarios = [
        (
            "first_step_count_transport_categories",
            "某班記錄學生通勤方式，資料含步行、公車、機車、腳踏車。若要比較各類別人數，應先如何整理？請輸入選項代號。",
            ["1. 統計各類別出現次數", "2. 直接計算標準差", "3. 畫累積次數折線圖", "4. 假設資料服從常態分配"],
            "1",
            "先做分類計數，才能進一步繪製比較圖表。",
        ),
        (
            "first_step_count_reading_minutes",
            "某社團記錄社員每日閱讀分鐘數，想先整理成可比較的資料，第一步應為何？請輸入選項代號。",
            ["1. 分組並統計各組次數", "2. 直接求相關係數", "3. 先畫圓形圖", "4. 先假設資料無誤差"],
            "1",
            "先分組並統計次數，才能進行後續圖表呈現。",
        ),
        (
            "first_step_sort_sales_records",
            "商店記錄一週每日銷售件數，若要觀察資料趨勢，整理資料第一步通常是什麼？請輸入選項代號。",
            ["1. 依日期排序並整理成表格", "2. 先計算變異係數", "3. 先畫樹狀圖", "4. 先刪除極端值"],
            "1",
            "先依時間順序整理成表格，才適合後續趨勢分析。",
        ),
    ]
    picked = rng.choice(scenarios)
    if seed is None and _LAST_DATA_ORG_SCENARIO_ID is not None and len(scenarios) > 1:
        if picked[0] == _LAST_DATA_ORG_SCENARIO_ID:
            idx = scenarios.index(picked)
            picked = scenarios[(idx + 1) % len(scenarios)]
    scenario_id, question_text, choices, answer, explanation = picked
    param_sig = f"data_organization_first_step:{scenario_id}"
    param_tuple = ("data_org_first_step_v2", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    _LAST_DATA_ORG_SCENARIO_ID = scenario_id
    _LAST_DATA_ORG_PARAMETER_SIGNATURE = param_sig

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "data_organization_first_step",
        "scenario_family": "data_organization_first_step",
        "scenario_id": scenario_id,
        "parameter_signature": param_sig,
        "generator_key": "b4.chap3.data_organization_first_step_choice_v2",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "first_step"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "textbook_alignment_note": "資料整理第一步與圖表前處理，符合課本 3-1 概念題。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "data_organization_first_step",
            "parameter_signature": param_sig,
        },
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }


def data_organization_chart_usage_identification_choice_v2(
    skill_id: str,
    subskill_id: str,
    difficulty: int = 1,
    seed: Optional[int] = None,
    seen_parameter_tuples: Optional[Set[Tuple]] = None,
    multiple_choice: bool = True,
) -> Dict[str, Any]:
    global _LAST_DATA_ORG_SCENARIO_ID
    global _LAST_DATA_ORG_PARAMETER_SIGNATURE
    rng = random.Random(seed)
    scenarios = [
        (
            "chart_usage_trend_line",
            "若資料目的是呈現每日人數隨時間的變化，最常使用哪一種圖表？請輸入選項代號。",
            ["1. 折線圖", "2. 圓形圖", "3. 象形圖", "4. 樹狀圖"],
            "1",
            "時間序列變化通常用折線圖呈現。",
        ),
        (
            "chart_usage_category_bar",
            "若資料目的是比較不同類別的人數高低，最常使用哪一種圖表？請輸入選項代號。",
            ["1. 長條圖", "2. 折線圖", "3. 散佈圖", "4. 箱型圖"],
            "1",
            "比較類別高低時，長條圖最常見且易讀。",
        ),
        (
            "chart_usage_ratio_pie",
            "若資料目的是表達各類別在整體中的占比，最常使用哪一種圖表？請輸入選項代號。",
            ["1. 圓形圖", "2. 直方圖", "3. 折線圖", "4. 雷達圖"],
            "1",
            "呈現部分與整體關係時，圓形圖最常用。",
        ),
    ]
    picked = rng.choice(scenarios)
    if seed is None and _LAST_DATA_ORG_SCENARIO_ID is not None and len(scenarios) > 1:
        if picked[0] == _LAST_DATA_ORG_SCENARIO_ID:
            idx = scenarios.index(picked)
            picked = scenarios[(idx + 1) % len(scenarios)]
    scenario_id, question_text, choices, answer, explanation = picked
    param_sig = f"chart_usage_identification:{scenario_id}"
    param_tuple = ("data_org_chart_usage_v2", scenario_id)
    if seen_parameter_tuples is not None:
        validate_parameter_tuple_not_seen(param_tuple, seen_parameter_tuples)
        seen_parameter_tuples.add(param_tuple)
    _LAST_DATA_ORG_SCENARIO_ID = scenario_id
    _LAST_DATA_ORG_PARAMETER_SIGNATURE = param_sig

    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "choices": choices,
        "choices_display": choices,
        "explanation": explanation,
        "skill_id": skill_id,
        "subskill_id": subskill_id,
        "problem_type_id": "chart_usage_identification",
        "scenario_family": "chart_usage_identification",
        "scenario_id": scenario_id,
        "parameter_signature": param_sig,
        "generator_key": "b4.chap3.data_organization_chart_usage_identification_choice_v2",
        "answer_type": "integer",
        "answer_input_type": "choice",
        "difficulty": difficulty,
        "diagnosis_tags": ["data_organization", "chart_usage"],
        "remediation_candidates": ["vh_數學B4_DataOrganizationAndCharts"],
        "source_style_refs": ["B4_Ch3_data_organization"],
        "textbook_alignment_note": "圖表用途辨識題，對齊課本基礎應用情境。",
        "parameters": {
            "scenario_id": scenario_id,
            "scenario_family": "chart_usage_identification",
            "parameter_signature": param_sig,
        },
        "visual_backed": False,
        "runtime_mode": "deterministic_choice",
        "check_mode": "deterministic_auto_checked",
        "grading_mode": "deterministic",
    }

