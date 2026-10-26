# 普高數學2 單元2「級數」Stage 1 修復與封板（2026-10-26）

**判定：PASS（Stage 1 READY，可進入整個 Unit 的 GenCode V3）。** 授權：使用者對話明確要求修復並套用正式（Yang-Fu Yeh，2026-10-26）。

| 項目 | 結果 |
|---|---|
| 來源 | DOCX fe95de39…09f5、PDF 9d32c092…c964，與匯入紀錄及永久檔一致 |
| 教材列 | 37 題（12707–12743）：gh_Series 26、gh_CommonSeriesSummationFormulas 11 |
| Stage 1 gate | READY（blocked 0、needs_review 0） |
| 圖 | 6 張向量圖由人工驗證 PDF 區域裁出（例題3、例題6、隨堂練習6、例題11、基礎題6、進階題12）；裝飾圖不建立 |
| 變更 | 刪舊版 28 列（1334–1361）；11 個例題列補 question_anchor；12739、12743 改綁 gh_Series；12710 `\sqrt[]`→`\sqrt` |
| 隔離流程 | DB 複本修復 → gate READY → 再對第二份正式複本 apply／rollback 演練（rollback 後與正式庫逐列摘要相同）|
| 正式套用 | preflight OK（43 操作、6 檔）→ sqlite 備份（integrity ok）→ 單一交易 → 事後驗證；manifest `instance/backups/apply_manifest_20261026_104622.json`，備份 `instance/backups/kumon_math_before_math2_unit2_stage1_*.db` |
| 範圍外 | 單元1 39 列、其他列、skill_curriculum、tracker、skills_info 摘要與套用前完全相同；uploads 554 → 560（僅 +6 個本次裁圖）|
| 回滾 | `apply_unit2.py --rollback <manifest>`（列級＋檔案級，已演練）|

## 供 Stage 2 注意
- 匯入器未替 11 個「例題」列產生 question_anchor（其餘列都有）——本次補在資料上；匯入器根因尚未修。
- 例題8、隨堂練習8（12731、12735）為數學歸納法證明，Stage 2 應列 DEFERRED（無證明判分契約）。
