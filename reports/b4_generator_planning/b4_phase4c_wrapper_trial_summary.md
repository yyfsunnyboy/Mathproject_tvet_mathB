# B4 Phase 4C 單一 Skill Wrapper 試接成果凍結報告

## 1. 本階段目的
本階段目的為驗證單一 skill wrapper 與舊版 runtime 的相容性，確認能順利載入新版 B4 generator 所產生的 payload。為保持系統穩定，本階段**只驗證單一 wrapper**，不進行批次建立 wrapper，也完全不修改現有的 route 與 frontend 邏輯。

## 2. 試接範圍
- **wrapper 檔案**: `skills/vh_數學B4_CombinationDefinition.py`
- **skill_id**: `vh_數學B4_CombinationDefinition`
- **subskill_id**: `b4_ch1_comb_def_01`
- **problem_type_id**: `combination_definition_basic`
- **generator_key**: `b4.combination.combination_definition_basic`
- **實際呼叫的 core generator**: `core.vocational_math_b4.generators.combination.generate` 或其指定的子生成器 `combination_definition_basic`

## 3. 舊 runtime 載入方式
根據 runtime 證據報告，舊系統的載入與執行方式如下：
- **載入機制**: route 會將前端傳入的 `skill_id` 透過 `importlib.import_module(f"skills.{skill_id}")` 動態載入模組。
- **generate(level=...) 契約**: 後端會呼叫 `mod.generate(level=...)`，預期回傳包含 `question_text` 與 `correct_answer` 等必要欄位的 payload。
- **check(user_answer, correct_answer) 契約**: 後端呼叫 `check` 時，預期回傳包含 `{"correct": bool, "result": str}` 的字典以判定對錯並顯示回饋。
- **answer 與 correct_answer 共存原因**: 在現行 `/check_answer` 的實作中，route 會讀取 session 裡儲存的 `current['answer']`，並作為第二個參數傳遞給 `check()`，因此 wrapper 的 payload 必須同時提供 `answer` 以相容驗證流程，並與 `correct_answer` 保持一致。

## 4. Wrapper 契約
目前實作的 wrapper 提供了兩個主要介面：
- `generate(level=1, **kwargs)`
- `check(user_answer, correct_answer)`

在 `generate()` 回傳的 payload 中，確保至少包含以下欄位：
`question_text`, `answer`, `correct_answer`, `choices`, `explanation`, `skill_id`, `subskill_id`, `problem_type_id`, `generator_key`, `difficulty`, `diagnosis_tags`, `remediation_candidates`, `source_style_refs`, `parameters`。

## 5. 測試結果
- **測試檔案**: `tests/test_vocational_math_b4_skill_wrapper_phase4c.py`
- **通過數量**: 26 passed
- **是否修改 generator/domain/route/frontend**: 否
- **是否建立臨時檔**: 否

## 6. 已驗證的端到端流程
已確認可通行的資料傳遞架構如下：

前端 / route 傳入 skill_id
→ `skills/vh_數學B4_CombinationDefinition.py` (Wrapper)
→ `core/vocational_math_b4/generators/combination.py` (Generator)
→ `core/vocational_math_b4/domain/counting_domain_functions.py` (Domain Functions)
→ 回傳舊 runtime 可接受的 payload

## 7. 後續批次 wrapper 規則
未來批次擴充時應嚴格遵守以下保守原則：
- `skills/` 目錄下只存放主 skill wrapper。
- wrapper 內部**不寫**任何題型邏輯。
- wrapper **不重新計算**答案。
- wrapper **不重新產生**選項。
- wrapper 僅負責呼叫 router 或是指定的 generator。
- 未來應逐步改成呼叫 `question_router`，而不是讓每個 wrapper 直接呼叫 generator。
- 每新增一個 wrapper，必須有對應的 pytest 以確保契約完整。

## 8. 尚未處理事項
- 尚未建立統一的 `question_router` 機制。
- 尚未建立 `generator_registry` runtime loader。
- 尚未批次建立其他的 B4 skill wrapper。
- 尚未接 adaptive route。
- 尚未接前端正式操作流程。

## 9. 結論
1. Phase 4C 單一 wrapper 試接成功，已驗證舊有 runtime 完全可與新版 generator 相容。
2. 證實了維持現有 route 運作下，平滑導入 B4 deterministic 架構的可行性。
3. 下一步建議優先建立 `question_router` 以統一管理 `generator_key` 派發。
4. 待 router 完成後，即可依循本次建立的規則進行 wrapper 批次部署。
5. 後續需逐步處理尚未接入的 adaptive flow，並於前端進行最終 E2E 驗證。
