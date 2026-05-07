# B4 章節開發與自適應題型生成 SOP v0.2

version = v0.2

## 1. SOP 目的

本 SOP 用於 B4 後續章節開發，例如 Chap2、Chap3。
目標是把 Chap1 的經驗沉澱為可重複流程：
inventory → 題型分流 → deterministic generator → handwriting AI-judged → adaptive candidate registration → audit exposure → closure。

## 2. Chap N 開發總流程

1. Chapter inventory / skill inventory
2. DB skill order 檢查
3. 題型分類
4. deterministic int-answer 題型處理
5. AI-judged handwriting 題型處理
6. adaptive candidate 註冊
7. audit visibility exposure
8. manual smoke
9. closure summary
10. 下一章開始前 freeze

## 3. Chapter inventory 標準檢查

每章開始前必須先盤點：

- DB `skill_curriculum`
- `display_order`
- skill_id
- skill name / display name
- section
- source_type
- textbook_examples / in_class_practice / self_assessment
- 是否已有 skill file
- 是否已有 generator
- 是否已有 route / wrapper
- 是否為 deterministic int-answer
- 是否需要 handwriting AI-judged
- 是否 future_ai_judged / manual review

規則：
- skill 順序優先以 DB `skill_curriculum.display_order` 為主。
- Python fallback order 只能作 DB 缺漏時備援。

## 4. 題型分流規則

### 4.1 deterministic int-answer

適用：
- 單一整數答案
- 單一分數 / 小數答案
- 可 deterministic check_answer 的題型

處理方式：
- problem_type generator
- validator
- choices / answer / explanation
- router registry
- tests
- manual smoke

### 4.2 deterministic choice-answer

適用：
- 選擇題
- 可唯一判斷選項正確性的題型

處理方式：
- choices unique
- answer in choices
- explanation
- validator

### 4.3 AI-judged handwriting / free-response

適用：
- 樹狀圖列舉
- 巴斯卡三角形列值 / 展開式
- 完整二項式展開
- 推導型作答
- 學生答案不是單一數字

處理方式：
- 原 `/practice` 頁
- `answer_type = handwriting`
- `grading_mode = ai_judged_free_response`
- `/analyze_handwriting`
- rubric
- `expected_paths` / `expected_row` / `expected_terms` / `expected_expansion` 作為後端 AI 判斷參考
- 不走 `/check_answer`
- 不加入 deterministic int-answer allowlist

### 4.4 future_ai_judged / manual review

適用：
- 證明題
- 推導題
- 圖形畫法複雜
- AI 判斷尚未穩定

處理方式：
- 標記 future_ai_judged
- 不接入正式學生自動批改
- 可另開 handwriting AI prototype

## 5. Generator 設計原則

- B4 不採「一個 skill 一支 generator」為主要策略。
- B4 採：
  skill → subskill → problem_type → generator → domain function
- generator 應以 problem_type 為最小單位。
- 同一個 skill 可有多個 problem_type。
- 同一個 generator 可支援多個相近 variant。
- generator 應輸出：
  - skill_id
  - subskill_id
  - problem_type_id
  - generator_key
  - question_text
  - choices
  - answer
  - explanation
  - difficulty
  - diagnosis_tags
  - remediation_candidates
  - source_style_refs
- 數學式必須使用 LaTeX。
- 不可把完整展開 / 列舉 / 推導題硬塞成 int-answer。

## 6. AI-judged handwriting 題型 SOP

以 Chap1 的兩個成功案例作為標準流程。

### 6.1 Tree Diagram 模式

記錄：
- skill_id = `vh_數學B4_TreeDiagramCounting`
- problem_type_id = `tree_diagram_listing`
- answer_type = `handwriting`
- grading_mode = `ai_judged_free_response`
- 使用原 `/practice`
- 使用 `/analyze_handwriting`
- 使用 `expected_paths` rubric
- 使用 `tree_diagram_index` 下一題輪替
- 不新增 `skills/vh_數學B4_TreeDiagramCounting.py`
- 不進 deterministic allowlist

### 6.2 Pascal Triangle 模式

記錄：
- skill_id = `vh_數學B4_PascalTriangle`
- problem_type_id = `pascal_triangle_handwriting`
- answer_type = `handwriting`
- grading_mode = `ai_judged_free_response`
- 使用原 `/practice`
- 使用 `/analyze_handwriting`
- 使用 `expected_row` / `expected_terms` / `expected_expansion` rubric
- 使用 `pascal_triangle_index` 下一題輪替
- 不新增一般 int-answer Pascal generator
- 不進 deterministic allowlist

### 6.3 新 handwriting 題型標準步驟

每新增一個 AI-judged handwriting 題型，依序做：

1. 建立 free_response helper
2. 建立 payload builder
3. 定義 problem_type_id
4. 定義 answer_type / grading_mode
5. practice.py 攔截 skill / problem_type
6. dashboard link 導向原 `/practice`
7. index 參數支援下一題
8. index 參數支援參數化出題
9. `/analyze_handwriting` 加 rubric 分支
10. 不走 `/check_answer`
11. 不加入 deterministic allowlist
12. 測試 helper / practice / handwriting / dashboard / allowlist boundary
13. manual smoke
14. closure summary

## 7. Adaptive candidate 註冊 SOP

- deterministic int-answer skill 使用 deterministic allowlist。
- handwriting AI-judged skill 使用獨立 candidate list。
- 例如：
  - `B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS`
  - metadata map
  - grading_mode
  - answer_type
  - practice_url
  - scoring_policy
- 不可把 handwriting 題型塞進 deterministic allowlist。
- adaptive audit 可以顯示 checkpoint。
- 但在 scoring policy 未定義前：
  - 不更新 mastery
  - 不更新 APR
  - 不影響 fail_streak
  - 不觸發 remediation
  - `partial` / `needs_review` 不直接視為錯

## 8. Chapter order / skill order SOP

- 主順序來源：DB `skill_curriculum.display_order`
- dashboard 使用 DB order
- guided progression helper 應優先讀 DB
- fallback order 只作 DB 缺漏時備援
- 每章開始前要確認：
  - display_order 是否合理
  - section 是否正確
  - handwriting checkpoint 是否在 DB 中有正確順序
- 不可讓 Python hard-coded order 成為唯一順序來源。

## 9. 測試標準

每個 chapter phase 應至少包含：

- helper tests
- generator tests
- router tests
- allowlist tests
- practice route tests
- handwriting analyze tests
- adaptive audit tests
- dashboard link tests
- manual smoke checklist

每次測試回報格式：

- 修改檔案
- 測試指令
- 測試結果
- manual smoke 結果
- known limitations
- 是否可 closure

## 10. Closure summary 標準格式

每個 phase 收尾必須新增 report：

`reports/b4_generator_planning/<phase_name>_summary.md`

Closure 應包含：

1. Phase 目的
2. 完成範圍
3. 支援題型 / variants
4. 修改檔案
5. 測試結果
6. manual smoke 結果
7. runtime boundary
8. known limitations
9. Go / No-Go
10. next phase 建議
11. Final closure statement

## 11. Chap2 開發前 Checklist

- [ ] 確認 Chap2 章名與章節 id
- [ ] 匯出 Chap2 skill list
- [ ] 檢查 skill_curriculum.display_order
- [ ] 檢查 textbook_examples / in_class_practice / self_assessment 數量
- [ ] 分類 deterministic / handwriting / future_ai_judged
- [ ] 先做 inventory report，不改 code
- [ ] 先建立 problem_type closure table
- [ ] 再決定 generator / handwriting flow / adaptive candidate
- [ ] 每次只處理一小批題型
- [ ] 每批完成後 closure

## 12. 明確禁止事項

- 不要一次處理整章所有題型。
- 不要把 free-response 題型硬塞成 int-answer。
- 不要沒有測試就改 adaptive scoring。
- 不要讓 AI 自動大範圍重構。
- 不要直接改 coverage matrix 除非 phase 明確要求。
- 不要新增 skill generator 檔來掩蓋 missing module 問題，除非該題型確實是 deterministic generator。
- 不要只備份 DB 而不備份 YAML / Python / reports。
- 不要讓 `expected_paths` / `expected_row` / `expected_expansion` 顯示在正式學生端。

## 13. 備份與資料來源

資料分工：

- DB：
  - `skill_curriculum`
  - `display_order`
  - `skills_info`
  - `textbook_examples`
  - `skill_prerequisites` 若有資料
- YAML：
  - `configs/adaptive/subskill_remediation.yaml`
  - 子技能與補救 ontology
- Python：
  - generator
  - routing helper
  - adaptive candidate metadata
  - handwriting payload builders
- Markdown reports：
  - phase summary
  - closure summary
  - audit report

提醒：
- Excel DB 備份不包含 YAML / Python / reports。
- Chap2 開發前應做完整專案資料夾或 Git 備份。

## 14. 本次更新摘要

changelog

v0.2 更新：
- 納入 Chap1 deterministic + handwriting AI-judged 經驗
- 新增題型分流
- 新增 handwriting SOP
- 新增 adaptive candidate SOP
- 新增 DB-first order SOP
- 新增 closure summary 標準
- 新增 Chap2 前檢查表
