# Phase 5H AI-Judged Free-Response Adaptive Candidates Summary

## 1) 本階段目的
- 將 `vh_數學B4_TreeDiagramCounting` 與 `vh_數學B4_PascalTriangle` 登錄為 B4 Chapter 1 的 AI-judged free-response adaptive candidates。
- 保持其練習入口為原 `/practice` 手寫作答流程，並與 `/analyze_handwriting` rubric 對接。

## 2) 為什麼不加入 deterministic allowlist
- 兩者皆非單一 `int-answer` 題型，需依手寫內容整體判斷。
- 依賴 `answer_type=handwriting` + `grading_mode=ai_judged_free_response` + `/analyze_handwriting`。
- `partial / needs_review` 不應直接納入 deterministic mastery/APR 計分路徑。

## 3) 新增 candidate list / metadata
- 新增 `B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILLS`：
  - `vh_數學B4_TreeDiagramCounting`
  - `vh_數學B4_PascalTriangle`
- 新增 `B4_CHAPTER_1_AI_JUDGED_FREE_RESPONSE_SKILL_METADATA`，包含：
  - `problem_type_id`
  - `answer_type`
  - `grading_mode`
  - `index_param`
  - `default_variant`
  - `adaptive_role`
  - `mastery_scoring=deferred_teacher_review`
- 新增 helper：
  - `is_b4_chapter1_ai_judged_free_response_skill()`
  - `get_b4_chapter1_ai_judged_free_response_metadata()`

## 4) Curriculum progression with checkpoints
- 新增 `B4_CHAPTER_1_CURRICULUM_PROGRESSION_WITH_FREE_RESPONSE`：
  - `TreeDiagramCounting` 放在 `MultiplicationPrinciple` 後。
  - `PascalTriangle` 放在 `BinomialCoefficientIdentities` 與 `BinomialTheorem` 之間。
- 新增 `get_b4_chapter1_curriculum_progression(include_free_response=False)`：
  - `False` 時維持原 deterministic progression（不變）。
  - `True` 時回傳含 checkpoint 之完整教學順序。

## 5) Runtime boundary
- 不改 `/check_answer`。
- 不改 adaptive submit scoring 行為（不讓 handwriting partial/needs_review 直接影響 mastery/APR）。
- 不改 B4 deterministic `question_router`。
- 不改 deterministic generators。
- 不改 coverage matrix。

## 6) Tests and results
- 新增 `tests/test_phase5h_ai_judged_free_response_adaptive_candidates.py`，覆蓋：
  - candidate list 與 deterministic allowlist 邊界
  - metadata 正確性
  - progression checkpoint 順序
  - default progression 不變
  - dashboard 仍走 `/practice` 手寫入口
  - tree/pascal `/get_next_question` handwriting smoke
- 其餘回歸測試一併執行（見本階段測試輸出）。

## 7) Known limitations
- 本階段為 registration-only + runtime audit 可見性，不將 checkpoint 直接插入 `/api/adaptive/submit_and_get_next` 的 deterministic 出題主流程。
- handwriting `partial / needs_review` 仍維持 deferred policy，待教師審閱策略完成後再納入 mastery 口徑。

## 8) Next step
- Phase 5H-B：Optional guided progression insertion for AI-judged checkpoints。
- Phase 5H-C：Teacher review / scoring policy。
- Phase 5H-D：Adaptive mastery integration after human-review policy。
