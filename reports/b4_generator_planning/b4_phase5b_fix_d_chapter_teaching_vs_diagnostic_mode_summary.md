# B4 Phase 5B Fix-D：Chapter Teaching 與 Diagnostic Stop 分離

## Root Cause
- B4 Chapter 1 `單元練習` 雖已在入口橋接為 chapter path，但 `session_engine` 在 `textbook_cfg` 缺省時仍套用 legacy completion 邏輯。
- 該 legacy completion 使用 `MIN_STEPS_BEFORE_EARLY_PASS = 5` + APR 門檻，造成 teaching/practice 路徑也可能在約 5 題提前結束。
- 前端完成文案仍含診斷語意（例如「你已完成本單元自適應診斷。」），放大了模式混淆。

## Before Behavior
- 路徑：`數學B4 -> 1 排列組合 -> 單元練習`
- 實際上約 5 題後可能結束，並顯示診斷完成語意。
- 教學/練習與評量停止條件未完全隔離（特別是 `textbook_cfg` 缺省情境）。

## After Behavior
- B4 Chapter 1 單元練習入口明確攜帶 teaching/practice 語意：
  - `learning_mode=teaching`
  - `practice_kind=unit_practice`
- 前端 bootstrap 與後端 API bridge 會保留 chapter teaching context（`entry_mode=chapter`、`mode=teaching`）。
- `session_engine` 在 **B4 chapter teaching** 且 `textbook_cfg` 缺省時，不再使用 legacy 5 題自動停止。
- assessment 模式既有 stop 行為保留。
- 完成顯示文案調整為練習語意，不再使用「你已完成本單元自適應診斷。」。

## Files Inspected
- `templates/dashboard.html`
- `templates/adaptive_practice_v2.html`
- `core/routes/practice.py`
- `core/routes/adaptive_api.py`
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`

## Files Changed
- `templates/dashboard.html`
- `core/routes/practice.py`
- `templates/adaptive_practice_v2.html`
- `core/routes/adaptive_api.py`
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`

## Stop-Condition Change
- 位置：`core/adaptive/session_engine.py::_evaluate_unit_completion`
- 新增參數：`disable_legacy_teaching_autostop`
- 行為：
  - `mode=assessment`：維持原先 legacy completion（含 5 題 early-pass）
  - `mode=teaching` 且 `disable_legacy_teaching_autostop=True`：`textbook_cfg` 缺省時不自動 `unit_completed`
  - 其他情境：維持既有 legacy 行為（避免非 B4 行為擴散）
- 啟用條件（最小隔離）：`submit_and_get_next` 僅在 `mode=teaching` 且 `_is_b4_chapter1_entry_payload(payload)` 時打開該旗標。

## QA Commands / Result
- Command:
  - `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- 目標驗證點：
  - B4 chapter 單元練習 URL/context 為 teaching/practice
  - B4 chapter teaching 在 `textbook_cfg` 缺省時不會 5 題提前完成
  - assessment 模式仍保留固定停止行為
  - teaching 回應仍含 remediation/backtracking 相關欄位
  - excluded problem type blocking 仍維持

> 本次為最小安全修補：未修改 B4 generators、未改 coverage matrix、未改 question_router、未擴大 adaptive policy、未連接 manual_review/future_ai_judged。

## Manual Browser Smoke
- 本回合尚未執行實機瀏覽器 smoke。
- 建議手動路徑重測：
  - `數學B4 -> 1 排列組合 -> 單元練習`
  - 確認不再於約 5 題後顯示「你已完成本單元自適應診斷。」且流程持續進入 teaching/remediation/return 主線。
