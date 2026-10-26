# 數學2 單元1 Stage 1 — 正式套用準備（尚未執行；需使用者明確授權）

## 範圍（`production_change_set.json`，已與最新修復一致）
- `textbook_examples` id 12667–12706 only：**1 DELETE（12691 偽題）+ 19 UPDATE = 20 筆**；套用後 39 題、3 個 Skill（不改 `skill_curriculum`／`skills_info`／tracker）。
- 圖檔：15 張 PNG（13 張補圖／重裁 + 隨堂練習8、11 兩張改名複本），逐一附 SHA-256；複製到正式 `uploads/question_assets/.../數學2/.../sec_unknown_1數列與遞迴關係/`，目的地若已存在且內容不同即中止。
- 最新內容：12674 `3, −6, 12,…, −384`（含 (3) 小題）、12701 `a_n =4ⁿ+2 恆為 6 的倍數`、12671 題幹與詳解 `b-1`、12676 `r²`。

## 套用步驟（`apply_unit1.py`；預設 dry-run，正式庫需 `--production --user-authorized "<誰/何時>"`）
1. Preflight：每筆操作的現值指紋須等於建立變更集時的正式庫值（有漂移即中止）；來源 PNG 雜湊須吻合。
2. 備份：sqlite backup API → `instance/backups/…`，`integrity_check=ok`，記錄備份 SHA-256。
3. 單一 `begin immediate` 交易：UPDATE／DELETE → 交易內逐筆驗證新值、單元題數 = 39；失敗即 rollback 並刪除本次建立的檔案。
4. 複製圖檔、寫入 `apply_manifest_*.json`（含每列原值、建立的檔案與雜湊）。
5. 套用後：`verify_stage1.py --db instance/kumon_math.db --label prod_after`（預期 25/25）；不需重啟 Flask。

## 回滾
- 列級：`apply_unit1.py --rollback <manifest>`（還原每列原值、重新插回 12691、只刪本次建立且雜湊相符的檔案；不影響之後的其他變更）。
- 最後手段：以備份檔還原（會丟掉備份之後的所有變更）。
- 舊的 3 個圖檔（誤裁的 12673、舊名的隨堂練習9／12）保留為孤兒檔，不刪除。

## 隔離演練（已完成，於 DB 複本）
preflight OK → 套用 → 驗證 READY 25/25 → 重複套用被 drift 檢查拒絕 → 回滾後資料摘要與原複本完全相同、檔案全部移除；對正式庫的 `--apply` 無授權參數時被拒絕。
