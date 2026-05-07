# Phase 5H-C AI-Judged Free-Response Adaptive Audit Summary

## 1. 本階段目的

- 將 `TreeDiagramCounting` / `PascalTriangle` 暴露在 B4 Chapter 1 adaptive chapter flow 的 `adaptive_audit` 中。
- 僅提供 checkpoint 可見性（audit exposure），不納入 deterministic scoring。

## 2. 已暴露 checkpoints

- 樹狀圖（`vh_數學B4_TreeDiagramCounting`）
- 巴斯卡三角形（`vh_數學B4_PascalTriangle`）

## 3. Audit Schema

- `enabled`
- `scope`
- `scoring_policy`
- `adaptive_insertion_policy`
- `checkpoints`

附加 metadata（僅在 B4 Ch1 chapter teaching/unit_practice flow）：

- `free_response_candidate_count`
- `free_response_scoring_policy`

## 4. Runtime Boundary

本階段維持以下不變：

- 不改 `check_answer`
- 不改 adaptive submit scoring semantics
- 不改 mastery / APR
- 不改 remediation trigger / return-to-mainline
- 不改 deterministic allowlist
- 不改 question_router / generators / coverage matrix

## 5. Privacy / Answer Exposure Guard

`adaptive_audit.ai_judged_free_response_checkpoints` 不暴露以下 answer keys：

- `expected_paths`
- `expected_row`
- `expected_terms`
- `expected_expansion`

## 6. Tests and Results

新增測試：

- `tests/test_phase5h_c_ai_judged_free_response_adaptive_audit.py`

覆蓋重點：

- audit helper schema 與 policy 值
- checkpoint 名單與 metadata 正確性
- 不暴露 expected_* answer keys
- B4 Ch1 chapter flow response 包含 `adaptive_audit.ai_judged_free_response_checkpoints`
- non-B4 response 不包含該 B4 checkpoints audit
- Tree/Pascal 仍不在 deterministic allowlist

## 7. Known Limitations

- 目前僅提供 audit visibility。
- 尚未自動插入 adaptive next-question。
- 尚未串接 teacher review DB。
- 尚未建立正式 scoring policy。

## 8. Next Steps

- Phase 5H-D：Optional dashboard / adaptive UI badge for handwriting checkpoints
- Phase 5H-E：Teacher review / scoring policy
- Phase 5H-F：Adaptive insertion after review policy
