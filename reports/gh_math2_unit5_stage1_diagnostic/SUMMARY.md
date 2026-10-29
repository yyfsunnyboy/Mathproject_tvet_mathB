# 普高數學2 Unit 5「組合」Stage 1 診斷

## 證據性質

- 原始逐題 Gate／Auto-review：**original_evidence_unavailable**。原頁面僅留摘要，未保存 task URL；沒有找到原始 Gate JSON、audit 或 manifest。
- 以下逐題結果均為新隔離 dry-run，不能冒充原任務回傳。
- 唯一來源紀錄與永久 DOCX／PDF SHA-256 已核對一致。
- 原 Gemini JSON 未留存；本次依原題名盤點重建兩個概念群、禁用外部 AI。37 題 Skill assignment 不能證明原始綁定。

## 新 dry-run Gate

- status=BLOCKED；37 rows；blocked[]=1；needs_review[]=0。
- reasons：required_figure_missing=1；stem_not_verified_against_pdf=7。後者由 auto-review issues 加入。
- PDF visual：NO_VISUAL_REQUIRED=36；VISUAL_REQUIRED_MISSING=1。畫面 Needs review=1 為視覺待審計數，與 gate.needs_review[] 不同。

## 真正阻擋題目

- reason code：required_figure_missing；stage：PDF visual alignment → Stage 1 Gate。
- 5習題 進階題12（新 dry-run ID 12834）；anchor general_2_section_advanced_exercise_012_037；source_order=37；DOCX block_index=36。
- 來源 PDF 第 16 頁（印刷頁 99）確有 A₁–A₄、B₁–B₆ 半圓圖；重跑紀錄為 skipped_low_confidence、VISUAL_REQUIRED_MISSING、visual_assets=[]。
- 原因是 Pipeline 未把現有圖形配到該題，非教材缺圖。裁切檢視圖 pdf_page16_advanced12_figure_candidate.png 的 bbox [420,575,540,675] 尚未核准。

## 其他 auto-review issues

| 題目 | anchor | 重跑 source_page | PDF 中文候選頁 | 中文字數 |
| --- | --- | ---: | --- | ---: |
| 例題1 | general_2_section_example_001_001 | 3 | 3 | 5 |
| 隨堂練習1 | general_2_section_in_class_practice_001_002 | 3 | 3 | 5 |
| 5習題 觀念澄清3 | general_2_section_exercise_003_024 | 未配對 | 14 | 10 |
| 例題6 | general_2_section_example_006_012 | 未配對 | 10, 11 | 6 |
| 例題7 | general_2_section_example_007_014 | 未配對 | 10, 11 | 6 |
| 5習題 觀念澄清4 | general_2_section_exercise_004_025 | 16 | 14 | 27 |
| 隨堂練習10 | general_2_section_in_class_practice_010_019 | 13 | 12 | 7 |

- 例題1、隨堂練習1 各只有 5 個中文字，低於 pdf_fidelity 的 6 字門檻；PDF 第 3 頁有題幹。
- 其餘 5 筆是 source_page 未配對或與 PDF 候選頁不同。候選頁僅是中文序列檢索，仍需對照公式和版面。

## 最小修復建議（本輪未執行）

1. 教師核對進階題12圖形及歸屬，再以本 PDF hash + Unit 5 + anchor 記錄已驗證的視覺區域；不得沿用 Unit 4 的核准。
2. 對 7 筆 issue 逐題核對 DOCX／PDF；修正短數學題的中文長度判準及錯誤頁面對位，不得只清除旗標。
3. 修復後重跑同範圍隔離 Gate：37 題 anchor／課綱／Skill、131 個公式、PDF 圖片 hash／頁面／bbox、metadata alignment、auto_review_issues=[]、Gate READY、正式 DB 零寫入。

## 正式 DB

- 執行前後唯讀 SQLite 完整備份 SHA-256 相同：21dd90adca424349e430fa620ce70254cdb362b8031973e16c597461763c66ad。integrity_check=ok；Unit 5 原有 28 列前後不變。**正式 DB 零變更已確認**。
- 未修改程式碼、Unit 4 成果或服務。
