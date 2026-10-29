# Unit 5 圖片補齊 — 正式寫入變更清單、備份與回滾（待教師授權，尚未執行）

範圍：普高 `general` / `數學2` / `單元5 組合`。只有 `5習題 進階題12`（anchor `general_2_section_advanced_exercise_012_037`，PDF 第 16 頁）需要圖片。

## 0. 前置條件

- 教師確認裁切圖：`reports/gh_math2_unit5_fixed/teacher_preview.html`；本報告 `screenshots/01`、`screenshots/06`。
- 權威來源 SHA-256 不變：
  - PDF：`e24c72f89309…ec166`（`textbook_import/uploaded_sources/general/數學2/e24c72f89309_單元05-組合.pdf`）
  - DOCX：`ae362631e1be…328fad`（`textbook_import/uploaded_sources/general/數學2/ae362631e1be_單元05-組合.docx`）

## 1. 變更清單（依序）

| # | 對象 | 變更 | 依據 |
|---|---|---|---|
| 1 | `configs/stage1_verified_visual_regions.json` | 新增 1 筆 region：PDF SHA＋curriculum/volume/chapter＋anchor、page 16、bbox `[425.0,586.5,526.0,653.5]`，並填入 `verified_by`、`verified_on` | `reports/gh_math2_unit5_fixed/staged_visual_region.json` |
| 2 | 正式 DB `instance/kumon_math.db` | 以既有 `general_replacement` 匯入流程（備份＋transaction）取代 Unit 5：刪除舊列 1413–1440（28 列），寫入新 37 列；Stage 1 Gate 必須自然為 READY，不得強制 | 隔離演練 `reports/gh_math2_unit5_fixed/rehearsal_result.json` |
| 3 | 正式 DB `skill_curriculum` | 清除 Unit 5 舊匯入留下、且已無題目引用的無效綁定（例如 `gh_ComprehensiveExercises`）。以匯入後的實際引用為準，只限本 chapter | AGENTS.md §3 |
| 4 | 正式 `uploads/question_assets/.../單元5_組合/...進階題12...fig1.png` | 由匯入流程依 verified region 產生 1 張 PNG（隔離版 sha `a8390a7a…`，288×194） | 隔離演練 |
| 5 | `configs/fixed_textbook_practice.json` | `build_fixed_config.merge_into_live(released_db)`：依 anchor 重新綁定正式 row id，新增進階題12 graded multi_part 條目；既有條目不變 | `reports/gh_math2_unit5_fixed/staged_fixed_entries.json` |
| 6 | 服務 | Flask 重啟一次，才會載入 `core/routes/practice.py` 的 multi_part dict 修正（上一輪已改，尚未重啟） | — |

不在範圍內：Promotion、Publish、GenCode 產碼、其他單元。

## 2. 備份

- 執行前：
  - 以 SQLite backup API 完整備份正式 DB；記錄檔案 SHA-256。
  - 另存 `configs/stage1_verified_visual_regions.json` 與 `configs/fixed_textbook_practice.json` 的原檔與 SHA。
- 記錄 Unit 5 舊列指紋（`scope_fingerprint`），以及 `formal_snapshot.py before` 的三表摘要：
  - `textbook_examples`：5017 列
  - `skills_info`：605 列
  - `skill_curriculum`：611 列
- `general_replacement` 會把舊列 ID 與指紋寫入 import policy，由 `validate_replacement_scope` 驗證範圍。

## 3. 寫入後驗證

1. Gate 為 READY；Unit 5 共 37 列，anchor 唯一，舊列 0。
2. 只有進階題12有 `image_assets`（1 張，PNG 存在且 SHA 相符）；其餘 36 題無圖。
3. Unit 5 以外的列、以及 Unit 4 的 38 列，摘要與寫入前相同。
4. Flask 重啟後，以真實學生練習頁檢查進階題12：
   - 顯示半圓圖；
   - 送出 ③＋116 判對；
   - 送出 ④＋116 判 (1) 錯；
   - 送出前不洩漏答案。

## 4. 回滾

1. 停止寫入，用備份檔還原 `instance/kumon_math.db`（需在 Flask 停止或維護時段進行），並核對 SHA 與寫入前相同。
2. 用原檔還原兩個 config 檔。
3. 刪除步驟 4 新產生的進階題12 PNG（只刪本次新增的路徑）。
4. 重啟 Flask，確認 Unit 5 回到舊版 28 列，Unit 4 不受影響。
