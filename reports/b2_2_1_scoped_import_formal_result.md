# B2 2-1 scoped formal import result

正式 scoped 匯入已完成。`dry_run=false`、`allow_phase4=true`、`target_source_types` 四類 opt-in。

詳細 JSON：`reports/b2_2_1_scoped_import_formal_result.json`

## Backup

- path: `instance/backups/kumon_math_before_b2_2_1_scoped_20260922_165122.db`
- success: true（SHA 與匯入前 production 一致）
- pipeline 另建：`instance/backups/kumon_math_before_v3_phase4_20260922_165131.db`

## Preconfirm（寫入前）

- target questions: 11
- textbook_example 5 / in_class_practice 5 / self_assessment 0 / exam_practice 1
- required formulas: 73 / success 73 / failed 0
- unresolved: 0
- WOULD_WRITE YES: 11

Gate 通過後才進入 DB_WRITE。

## Import

- success: true
- inserted: 11
- updated: 0
- skipped: 0
- failed: 0
- phase3: deterministic_docx_structure（gemini_requests=0）
- MATH_PARSE_FAILED in new rows: 0

## Source Types（新增）

| type | count |
|---|---:|
| textbook_example | 5 |
| in_class_practice | 5 |
| self_assessment | 0 |
| exam_practice | 1 |
| non-target inserted | 0 |

## Formula

| item | value |
|---|---:|
| required | 73 |
| success | 73 |
| failed | 0 |
| unresolved | 0 |
| whole-doc MathType OLE | 185/185 |

## Images

- candidate: 5
- linked: 0（scoped formal path 保留 needs_review，未強制掛圖）
- needs_review: 5

| DB id | label | filename | paragraph | rel | needs_review |
|---:|---|---|---:|---|---|
| 11676 | 例1 | image25.jpeg | 23 | rId57 | true |
| 11678 | 例2 | image59.jpeg | 62 | rId126 | true |
| 11680 | 例3 | image78.jpeg | 78 | rId163 | true |
| 11682 | 例4 | image117.jpeg | 122 | rId240 | true |
| 11686 | 113統測B | image138.jpeg | 142 | rId281 | true |

隨堂練習 1–5 無圖片候選。

## Verified rows

| id | source_type | label | skill | formulas | images |
|---:|---|---|---|---:|---:|
| 11676 | textbook_example | 例1 | vh_數學B2_SubSection_2_1_1 | 9 | 1 candidate |
| 11677 | in_class_practice | 隨堂練習1 | vh_數學B2_SubSection_2_1_1 | 3 | 0 |
| 11678 | textbook_example | 例2 | vh_數學B2_SubSection_2_1_1 | 13 | 1 candidate |
| 11679 | in_class_practice | 隨堂練習2 | vh_數學B2_SubSection_2_1_1 | 3 | 0 |
| 11680 | textbook_example | 例3 | vh_數學B2_SubSection_2_1_1 | 13 | 1 candidate |
| 11681 | in_class_practice | 隨堂練習3 | vh_數學B2_SubSection_2_1_1 | 4 | 0 |
| 11682 | textbook_example | 例4 | vh_數學B2_SubSection_2_1_2 | 11 | 1 candidate |
| 11683 | in_class_practice | 隨堂練習4 | vh_數學B2_SubSection_2_1_2 | 3 | 0 |
| 11684 | textbook_example | 例5 | vh_數學B2_SubSection_2_1_2 | 8 | 0 |
| 11685 | in_class_practice | 隨堂練習5 | vh_數學B2_SubSection_2_1_2 | 4 | 0 |
| 11686 | exam_practice | 113統測B | vh_數學B2_SubSection_2_1_2 | 2 | 1 candidate |

section: `2-1 正弦定理與餘弦定理`  
chapter: `第2章 三角函數的應用`

## DB Changes

| table | before | after | delta |
|---|---:|---:|---:|
| textbook_examples | 4329 | 4340 | +11 |
| skills_info | 539 | 541 | +2 |
| skill_curriculum | 548 | 550 | +2 |

新增 skill（預期，對應課文兩個概念標題）：

- `vh_數學B2_SubSection_2_1_1` 正弦定理
- `vh_數學B2_SubSection_2_1_2` 餘弦定理

outline 已存在：`outline_vocational_數學B2_21`

student side:

- adaptive_learning_logs 344 → 344
- practice_attempts 317 → 317
- class_students 50 → 50

SHA-256:

- before: `a5ff6f24c0fe0f1e1ef6137dc40139d8c5a3190e85bd1eb654852750a8c5da5c`
- after: `20f6dd10bac831bcb0fc41a6febdd0b0e7e7837aea7dc9719ded31efd8b7ccd1`

unexpected DB changes: **NO**（僅預期的 +11 題與 +2 concept skills/curriculum；未動 B2 1-3）

## Tests

重跑：

- `tests/test_textbook_scoped_import.py`
- formula gate / allow_phase4=False related pipeline tests

**20 passed / 0 failed**

## Git

commit: NO  
push: NO
