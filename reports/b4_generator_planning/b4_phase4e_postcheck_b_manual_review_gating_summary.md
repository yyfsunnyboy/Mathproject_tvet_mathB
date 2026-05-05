# B4 Phase 4E Postcheck-B Manual Review Skill Gating Summary

## 1. 本階段目的

本階段修正 manual_review skill 進入 practice 頁時的錯誤體驗，避免使用者從 dashboard 或直接 URL 進入頁面時看到 500 或 `No module named`。

本階段不建立 deterministic wrapper、不接 question_router、不產題，只提供 friendly unavailable 狀態。

## 2. 處理 skills

| skill_id | status | behavior | future_path |
|---|---|---|---|
| `vh_數學B4_TreeDiagramCounting` | manual_review / future_ai_judged | practice page 回傳 200，顯示暫緩與 AI 手寫判分候選說明，下一題與提交 disabled | future_ai_judged / handwriting checked / visualization / structured-answer listing |
| `vh_數學B4_PascalTriangle` | manual_review / future_ai_judged | practice page 回傳 200，顯示暫緩與教師審閱候選說明，下一題與提交 disabled | future_ai_judged / teacher review / structured derivation |

## 3. 實作方式

- 在 `core/routes/practice.py` 加入 `MANUAL_REVIEW_SKILLS` gating。
- `/practice/<skill_id>` 對 manual_review skills 直接渲染 unavailable 狀態，不 import missing wrapper。
- `/get_next_question` 在 import `skills.<skill_id>` 前 early return friendly JSON，避免 `No module named`。
- 修改 `templates/index.html`，對 manual_review unavailable 狀態顯示友善說明，並 disabled 下一題、答案輸入、提交按鈕。
- dashboard label 未修改；本階段優先修正 practice page friendly gating。
- 未新增 unavailable template，沿用既有 practice template。

## 4. 測試結果

- Focused pytest：`4 passed`
- Core runtime pytest：`45 passed`
- 測試中未出現 `No module named`。

執行命令：

```text
python -m pytest tests/test_vocational_math_b4_manual_review_skill_gating_postcheck_b.py -q
python -m pytest tests/test_vocational_math_b4_question_router_registry_canonical.py tests/test_vocational_math_b4_question_router_phase4e14b.py tests/test_vocational_math_b4_skill_wrappers_phase4e14b.py tests/test_vocational_math_b4_question_router_phase4e13f.py tests/test_vocational_math_b4_skill_wrappers_phase4e13f.py -q
```

## 5. 不做的事

- 不新增 deterministic wrapper。
- 不接 question_router。
- 不產題。
- 不把 manual_review 題型標成 runtime_ready。
- 不修改 generator。
- 不修改 domain functions。
- 不修改 coverage matrix。

## 6. 結論

TreeDiagramCounting 與 PascalTriangle 已有 friendly unavailable gating。  
manual_review skill 進入 practice page 不再需要 missing wrapper。  
目前行為不會產題，也不會接入 deterministic runtime。  
dashboard label 本階段未修改。  
focused 與 core runtime pytest 均通過。  
