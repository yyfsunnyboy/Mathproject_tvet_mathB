# 普高數學2 Unit 5 Stage 1 最小修復

**證據類型：`new_isolated_dry_run`。原始任務的完整 Gate 回傳仍是 `original_evidence_unavailable`。** 本報告不代表原始 Gate 結果，也沒有更動先前診斷資料。

## 結果

- 授權來源：[來源紀錄](../../textbook_import/uploaded_sources/general/數學2/12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json)。DOCX SHA-256：`ae362631e1be7030b8ac800c2553f9c067e8081c44e886e76cd0cbf0d4328fad`；PDF SHA-256：`e24c72f893099354886c288daef25eab59cd315facc778f7ffa96d4e242ec166`。執行前重新核對永久檔案雜湊。
- 7 筆 `stem_not_verified_against_pdf` 在新隔離重跑中全部消失；未新增 PDF fidelity issue。逐題的 DOCX 題幹、PDF 候選區、anchor、公式及頁碼見 [明細](pdf_fidelity_7_details.json)與各題裁切 PNG。
- 37 題、37 個唯一 anchor、來源順序 1–37 完整；Skill ID 與先前診斷一致，無新增綁定差異。131/131 MathType OLE 與 10/10 equation 欄位轉換成功，0 failure。驗證細節見 [anchor／Skill 表](anchor_skill_binding_37_verified.json)與 [dry-run log](dry_run_log.txt)。
- 最新 Stage 1 Gate：**BLOCKED**；`blocked=1`、`needs_review=0`、`auto_review_issues=0`。唯一原因 `required_figure_missing`，題目為 5習題進階題12，anchor `general_2_section_advanced_exercise_012_037`。見 [Gate JSON](stage1_gate_latest.json)、[圖片映射](pdf_visual_mapping_latest.json)。
- 圖像候選已整理於 [教師確認頁](TEACHER_ADVANCED12.md)與 [建議區域 JSON](teacher_advanced12_region_proposal.json)。狀態仍為 `pending_teacher_confirmation`，沒有設為 verified，也沒有寫入正式圖像設定。
- 正式 DB 的執行前後 SQLite 備份 SHA-256 都是 `21dd90adca424349e430fa620ce70254cdb362b8031973e16c597461763c66ad`；[零變更證據](formal_db_unchanged.json)。

## 七筆修復對照

| 題目 | Anchor | 原因 | 新 PDF 頁 | 新驗證 |
|---|---|---|---:|---|
| 例題1 | `general_2_section_example_001_001` | 中文 5 字的短題舊判準直接失敗，忽略組合數公式 | 3 | 局部中文字與數學 token |
| 隨堂練習1 | `general_2_section_in_class_practice_001_002` | 同上，公式與例題1不同 | 3 | 局部中文字與數學 token |
| 觀念澄清3 | `general_2_section_exercise_003_024` | 缺少映射頁碼 | 14 | 鄰近頁中文字與公式唯一匹配 |
| 例題6 | `general_2_section_example_006_012` | 缺少映射頁碼 | 10 | 局部中文字與 `(x+y)^5` |
| 例題7 | `general_2_section_example_007_014` | 缺少映射頁碼 | 11 | 局部中文字與 `(2x-y)^4` |
| 觀念澄清4 | `general_2_section_exercise_004_025` | 原映射誤指第 16 頁 | 14 | 鄰近頁中文字與二項式係數公式唯一匹配 |
| 隨堂練習10 | `general_2_section_in_class_practice_010_019` | 原映射誤指第 13 頁 | 12 | 局部中文字與交錯組合數公式 |

修復保留 PDF fidelity Gate。短題必須同時具備中文字順序及附近文字區塊內的數學 token；錯頁僅在有限鄰近頁找到實際內容且唯一匹配時校正。未找到證據仍回報 issue。

## 回歸與限制

- 聚焦 PDF fidelity 測試：3 passed。既有 Stage 1 auto-review 測試：12 passed。第一次既有測試因系統暫存目錄無法建立而在 setup 失敗；改用隔離暫存目錄後通過。
- Unit 4 已有 38 題的 PDF fidelity 唯讀比較：原判準 38/38 通過，新判準 38/38 通過，結果差異 0。沒有重跑 Unit 4 Promotion／Publish，也沒有改動其資料。見 [回歸結果](regression_results.json)。
- 此次隔離重跑使用前次診斷重建的 Gemini metadata；**原始 Gemini 回傳仍不可得**，因此此結果只能證明新重跑的範圍與一致性，不能取代原始人工核准。

## 修改與執行界線

- 程式：[PDF fidelity 邏輯](../../core/textbook_stage1_auto_review.py)：加入短數學題公式比對、有限鄰近頁搜尋及有證據的頁碼回填。
- 測試：[聚焦測試](../../tests/test_textbook_stage1_pdf_fidelity.py)：涵蓋短題公式正反例、缺頁唯一性及錯頁內容驗證。
- 本目錄新增隔離 runner、產生報告程式、JSON、頁面／候選裁切及教師預覽；沒有修改正式 DB、正式教材、Skill、圖片設定或 Unit 4 已發布資料；沒有 Promotion、Publish、服務重啟、commit 或 push。
- `reports/import_debug/數學2_unknown_title_inventory_report.md` 及 `templates/admin_prerequisites.html` 在本輪前已有工作樹變動，本輪未編輯。

教師確認圖像前，應維持 `required_figure_missing` 與 BLOCKED。確認後才在另一次授權工作中寫入圖像設定並重跑 Stage 1 Gate、PDF visual mapping、37 題完整性與正式資料保護核對。
