# 普高數學1 Unit 2（單元2 絕對值）— Source Fidelity 與 Stage 1 封板報告

- 日期：2026-10-18
- 範圍：僅普高（general）數學1「單元2 絕對值」教材資料（textbook_examples）與 2 張題圖
- 結論：**Stage 1 PASS（封板）**；無剩餘 Stage 1 blocker，Gencode tracker 差異依指示留待 Stage 2

## 1. 權威來源

| 檔案 | 大小 | SHA-256 |
|---|---|---|
| `textbook_import/source/general/數學1/單元02-絕對值.docx`（文字權威） | 1000223 | `5fbf935703d6598068d1cc9dcbf4f46221e005b4cd9b42ce9833f5dc9710ce80` |
| `textbook_import/source/general/數學1/單元02-絕對值.pdf`（視覺權威） | 2317055 | `4b45a8c12ae688ba77036bed0e295c987c5fc4e4d841c307b517bd19e0f23184` |

28 筆正式資料的 `notes.source_provenance` 均記錄上述兩個 hash，與測試通過版本相同。

## 2. 正式 DB 實際修改（`instance/kumon_math.db`）

單一 `BEGIN IMMEDIATE` 交易（`foreign_keys=ON`），新增 0、更新 28、刪除 12。

- 更新（保留原 id）：1027–1049、12323、12327、12331、12332、12333
- 刪除（重複舊教材）：12322、12324、12325、12326、12328、12329、12330、12334、12335、12336、12337、12338
- 題圖：
  - 例題2（id 1029）新增 `textbook_example_例2_…_dedupea7a0d2cdf5d6ae03_general__fig1.png`（PDF p3）
  - 隨堂練習2（id 12323）原子覆蓋 `in_class_practice_隨堂練習2_…_dedupe213cf3afb7411897_general__fig1.png`（PDF p4，取代原本誤掛的例題2截圖）

## 3. 替換後驗證

| 項目 | 結果 |
|---|---|
| Unit 2 教材數 | 28（例題 8、隨堂練習 8、基礎題 6、進階題 3、觀念澄清 3），缺漏 0、重複 0 |
| Skill 歸屬 | PointDivision 8、LinearEquations 6、LinearInequalities 14；與老師確認對照表 0 差異 |
| 題幹 | 28/28 與 DOCX 一致；`raw_problem_backup` 逐字一致；無公式佔位符；聯立式均有換行 |
| 題圖 | VISUAL_ATTACHED 2、NO_VISUAL_REQUIRED 26；正式圖檔與目視覆核檔案 hash 相同 |
| needs_review | 0 |
| integrity_check / foreign_key_check | ok / 0 違規 |
| 其他資料 | 全庫逐列比對：只有 textbook_examples 的上述 40 個 id 變動；其他資料表 0 變動 |
| Unit 1 / 技高 | 49 → 49 / 1268 → 1268，內容 0 變動 |
| 學生歷史 | progress、quiz_attempts 等學生資料表 0 變動；待刪 id 在全庫無任何引用 |
| Gencode tracker | 22 筆未修改，指向不存在題目的連結 0 筆 |

## 4. 推定頁碼（保留推定標記）

以下 3 題的 `pdf_visual_enrichment.page_source = between_same_page_neighbors`，不是直接比對到的來源證據。已依原始 PDF 目視覆核位置一致：

| id | 題目 | 推定頁 | 目視覆核 |
|---|---|---|---|
| 1039 | 觀念澄清2 | PDF p15（課本 p46） | 一致 |
| 1040 | 觀念澄清3 | PDF p15（課本 p46） | 一致 |
| 1048 | 進階題8 | PDF p16（課本 p47） | 一致 |

## 5. 確定性 Skill 對照

- 設定檔：`configs/general_high_source_skill_map.json`，map id `general_數學1_單元2_絕對值_v1`
- 生效範圍：curriculum=general、volume=數學1、chapter=單元2 絕對值，三者必須完全相符；技高與其他章節不受影響
- 套用時機：`process_textbook_file` 寫入資料庫後、PDF 題圖補強前（`apply_general_high_source_skill_map`）
- 原 AI 判定保存在 `notes.skill_binding.ai_skill_id`
- 本次匯入 AI 判錯 2 題，已由對照表修正：觀念澄清3（AI 判為方程式）、進階題7（AI 判為不等式）

## 6. Gencode tracker 與新版 Skill 差異（未修改，留待 Stage 2）

6 筆 tracker 的 skill 與新版歸屬不同，皆為舊教材把全部習題歸到「不等式」所致：

| textbook_example_id | 題目 | tracker skill | 新版 skill |
|---|---|---|---|
| 1038 | 觀念澄清1 | LinearInequalities | PointDivision |
| 1039 | 觀念澄清2 | LinearInequalities | PointDivision |
| 1041 | 基礎題1 | LinearInequalities | PointDivision |
| 1042 | 基礎題2 | LinearInequalities | PointDivision |
| 1043 | 基礎題3 | LinearInequalities | LinearEquations |
| 1047 | 進階題7 | LinearInequalities | LinearEquations |

- 沒有 tracker 的題目：例題2、隨堂練習2、4、6、7、8
- 22 個 component 的 induced spec 仍以舊題文為來源，Stage 2 需依新版 28 題重建或修正
- 明細：`backups/gh_unit2_stage1_prod_20261018_175757/tracker_skill_diff.json`

## 7. 備份與回滾

- 正式替換前 online backup（integrity ok）：`backups/gh_unit2_stage1_prod_20261018_175757/kumon_math_pre_stage1_replace.db`
- 被覆蓋題圖備份（含 sha256 manifest）：`backups/gh_unit2_stage1_prod_20261018_175757/assets/…`、`asset_manifest.json`
- 執行紀錄：`prod_dryrun.json`、`prod_apply.json`、`post_verify.txt`（同目錄）
- 較早的備份：`backups/gh_unit2_stage1_20261018_175344/`、`backups/gh_unit2_v3_20261018/`
- 回滾方式：從備份 DB 以單一交易還原這 40 個 id，並以 `assets/` 中的檔案覆蓋回題圖，不需要重啟服務

## 8. 非阻擋事項

- 兩張題圖截取的是整個題目框（含題幹文字），數線內容正確。
- Importer 修正與 skill 對照尚未 commit；5000/5001 以 `--no-reload` 執行，仍是舊程式碼。重啟前請勿從網頁重新上傳 Unit 2。
- 本次未執行：Gencode V3 adapter promotion、22 個元件重生、V3 publish、學生 facade、服務重啟、git commit/push。
