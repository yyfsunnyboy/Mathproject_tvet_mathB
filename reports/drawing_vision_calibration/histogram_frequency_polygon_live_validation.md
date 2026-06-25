# Histogram/Frequency Polygon Live Vision Validation

- seed: `7`
- fixture_dir: `D:\Python\Mathproject_tvet_mathB\tests\fixtures\drawing_answers\histogram_frequency_polygon`
- report_generated_at_epoch: `1782353159`

## Fixture Spec

```json
{
  "drawing_type": "histogram_and_frequency_polygon",
  "x_categories": [
    "A組",
    "B組",
    "C組",
    "D組"
  ],
  "expected_values": [
    5,
    4,
    6,
    8
  ],
  "required_elements": [
    "x_axis",
    "y_axis",
    "histogram_bars",
    "frequency_polygon"
  ],
  "grading_rules": {
    "bar_count_matches_categories": true,
    "histogram_bars_touch": true,
    "polygon_connects_category_midpoints_in_order": true
  },
  "bar_rules": {
    "count": 4,
    "expected_heights": [
      5,
      4,
      6,
      8
    ],
    "touching": true,
    "baseline": 0
  },
  "polygon_rules": {
    "expected_points": [
      [
        "A組",
        5
      ],
      [
        "B組",
        4
      ],
      [
        "C組",
        6
      ],
      [
        "D組",
        8
      ]
    ],
    "connect_in_order": true
  },
  "tolerance": {
    "value": 0.8,
    "position_ratio": 0.12
  }
}
```

## Live Validation

Local role resolution, without sending images:

```json
{"available": false, "analyzer": "vision_analyzer:google:gemini-3.5-flash", "reason": "missing_api_key"}
```

Live validation attempted through:

```text
python scripts\run_drawing_vision_calibration.py --generate-fixtures --run-live --repeat-target 07_complete_correct_neat.png --repeat-count 3
```

The approval reviewer blocked the external Vision provider call because it would send repository-derived question/spec content and generated answer images to an unverified external destination. No workaround was attempted.

Result: live provider validation is blocked, not passed.

## Generated Fixtures

| fixture | purpose |
|---|---|
| `01_blank_canvas.png` | blank canvas |
| `02_random_line.png` | arbitrary single line |
| `03_histogram_only_correct.png` | histogram only, correct bars |
| `04_polygon_only_correct.png` | frequency polygon only, correct points |
| `05_both_one_bar_wrong.png` | both drawn, one bar height wrong |
| `06_both_polygon_wrong_order.png` | both drawn, polygon order wrong |
| `07_complete_correct_neat.png` | complete correct neat |
| `08_complete_correct_wobbly.png` | complete correct wobbly |
| `09_complete_correct_thick.png` | complete correct thick |
| `10_complete_correct_shifted.png` | complete correct shifted |
| `11_all_bar_heights_wrong.png` | all bar heights wrong |
| `12_polygon_along_bar_edges.png` | polygon follows bar edges |
| `blank_01_white_png.png` | full white PNG |
| `blank_02_axes_only.png` | preloaded axes only |
| `blank_03_tiny_touch.png` | tiny accidental stroke |
| `blank_04_normal_stroke.png` | normal student stroke |

## Local Blank Detection Check

| fixture | `_is_blank_png` |
|---|---:|
| `blank_01_white_png.png` | `True` |
| `blank_02_axes_only.png` | `True` |
| `blank_03_tiny_touch.png` | `True` |
| `blank_04_normal_stroke.png` | `False` |
| `01_blank_canvas.png` | `True` |
| `02_random_line.png` | `False` |

## Runtime Blank Flow Check

Full Flask test client path was exercised for blank-like fixtures:

```text
/get_next_question -> /check_answer -> free_response_drawing_checker -> drawing_answer_analysis_service
```

| fixture | component_id | checker | status | correct | is_correct | system_error |
|---|---|---|---|---:|---:|---:|
| `01_blank_canvas.png` | `src_3827` | `free_response_drawing_checker` | `blank_drawing` | `False` | `False` | `False` |
| `blank_02_axes_only.png` | `src_3827` | `free_response_drawing_checker` | `blank_drawing` | `False` | `False` | `False` |
| `blank_03_tiny_touch.png` | `src_3827` | `free_response_drawing_checker` | `blank_drawing` | `False` | `False` | `False` |

`vision_calls`: `0`

## Local Test Result

```text
python -m pytest tests\test_drawing_vision_analyzer.py tests\test_free_response_drawing_checker.py tests\test_drawing_pipeline_e2e.py
23 passed
```
