# 普高數學2 Unit 5「組合」— 正式 Stage 1 匯入與驗收（2026-10-29）

結論：正式 Stage 1 已完成並封板。

- Gate 結果：READY（blocked 0、needs_review 0）。
- 舊版 28 題已由新版 37 題取代。
- 只有進階題12帶圖。
- 固定題庫已綁定正式 ID。

## 授權與核准
- 教師核准裁切圖：進階題12、anchor `general_2_section_advanced_exercise_012_037`、PDF 第 16 頁、bbox `[425.0,586.5,526.0,653.5]`，A1–A4、B1–B6 完整。
- 已寫入 `configs/stage1_verified_visual_regions.json`：`verified_by=teacher`、`verified_on=2026-10-29`。
- 教師授權正式寫入。

## 執行步驟（沿用 Unit 4 正式程序）
| 步驟 | 結果 | 檔案 |
|---|---|---|
| 唯讀 preflight | 來源 SHA 與匯入紀錄一致（PDF `e24c72f8…ec166`、DOCX `ae362631…328fad`）；舊列 28 筆（1413–1440）；沒有任何作答或其他資料表引用舊 ID；`gh_Combination`／`gh_BinomialTheorem` 未被其他單元使用 | `preflight_formal.py` |
| 寫 region 前備份設定 | 4 個 live config 已備份 | `instance/backups/math2_unit5_stage1_pre_region_20261029_220150/` |
| 以 live region 重放匯入（正式 DB 複本） | Gate READY；37 列；只有 12834 帶圖，圖片 SHA `a8390a7a…`；與先前 Stage 1 演練零內容差異 | `replay_formal.py`、`replay_formal_result.json` |
| 變更集 | 舊 28 列換成新 37 列（12812–12848）；`skill_curriculum` 358／359 的 `display_order` 改成 50001／50002；刪除 360（共用 Skill `gh_ComprehensiveExercises` 在 Unit 5 的失效綁定，該 Skill 其他 11 筆綁定保留）；新增 1 張圖；其餘 34 張表完全相同 | `build_change_set.py`、`production_change_set.json` |
| 演練（DB 複本） | 套用→驗證→回滾（逐表完全還原、圖檔移除）→再套用，全部 PASS | `rehearse_apply.py`、`rehearse_apply_result.json` |
| 正式寫入 | `APPLY PASS`（單一交易、交易內做範圍外比對、提交後驗證） | `apply_unit5.py`、`instance/backups/math2_unit5_stage1_20261029_220334/` |
| 固定題庫 | 依 anchor 對正式 DB 重新查出 row 並綁定 ID 12834，題幹 SHA 也對正式 row 計算；live 條目從 6 筆變成 7 筆，既有條目不變 | `reports/gh_math2_unit5_fixed/build_fixed_config.py` |

正式 ID 12834 與隔離 ID 相同，原因是新列從 `max(id)+1 = 12812` 開始依序配號。綁定 ID 是重新查出來的，不是沿用隔離 ID。

## 正式驗收（`post_verify_prod.py`、`post_verify_prod.json`）
- `pragma integrity_check` 為 ok，備份 SHA 相符。
- Unit 5 共 37 列：`gh_Combination` 23 列、`gh_BinomialTheorem` 14 列；舊 ID 剩 0。
- 正式 Gate 重算：READY。
- 只有 12834 有 `image_assets`，圖檔存在且 SHA 相符；沒有殘留的 `.pending` 暫存檔。
- 34 張表在本次範圍以外與備份完全相同：users 547、practice_attempts 2752、progress 398、錯題本 126，筆數不變。
- Unit 4 的 38 列與備份完全相同。
- 固定題庫條目 12834 的 anchor、題幹 SHA、Skill 都與正式資料一致。
- 真實學生頁（5001，Cursor 瀏覽器，admin 帳號）：
  - 進階題12 以「課本原題・可自動判分」出題，半圓圖完整（圖片 HTTP 200），送出前不洩漏答案。
  - 送出 45＋116 顯示「部分小題答錯。(1)：錯誤 (2)：正確」，並寫入作答紀錄（2963、2964）與錯題本（128）。
  - 例題1（12812）正確地沒有圖。
- 正解路徑（③／40＋116 判對）：依據隔離環境的瀏覽器實測與 `tests/test_gh_unit5_fixed_advanced12.py`（15 PASS）。教師表示不需要在正式環境再測。

## Flask
- 5001 沒有重啟：`core/routes/practice.py` 的修正（10/28 23:17）已在 10/28 23:25 的啟動中載入。
- 固定題庫設定每次讀取都會比對檔案修改時間，自動載入新條目。
- Cloudflare 與 5000 都沒有動。

## 回滾
```
python reports/gh_math2_unit5_stage1_formal/apply_unit5.py --rollback instance/backups/math2_unit5_stage1_20261029_220334/apply_manifest.json --production
```
另外需要用 `instance/backups/math2_unit5_stage1_pre_region_20261029_220150/` 還原兩個 config 檔。也可以直接用整份備份 DB 還原。
