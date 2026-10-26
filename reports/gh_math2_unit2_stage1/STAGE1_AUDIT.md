# 普高數學2 單元2「級數」Stage 1 封板前稽核（唯讀）

判定：**NEEDS_REPAIR**（非 BLOCKED；無法重建的問題為零，4 項小修）。formal DB / uploads / Skill binding 皆未修改，未重新匯入。

## 來源
- curriculum general ／ 數學2 ／ 單元2 級數；DOCX `fe95de3920ab…09f5`（單元02-級數.docx，593,843 B）、PDF `9d32c092de77…c964`（單元02-級數.pdf，18 頁）；皆與 `textbook_import/uploaded_sources/general/數學2/` 檔案及匯入紀錄 JSON 的 SHA-256 一致。
- 新匯入列 12707–12743 = 37 題：例題 11、隨堂練習 11、觀念澄清 3、基礎題 8、進階題 4（與書上標號逐一相符）。

## 保真
- 中文題幹：以 PDF 文字逐 8 字塊比對，僅 7 列因數學式穿插而字塊不連續，人工核對無截斷／誤拆／誤合併；無說明文字被匯入成題。
- 數學：負號、上下標、(−3)+(−1)+1+…、(−2)×(−3)^9、S_n=−n²+6n、S_n=−2n²+n 與 PDF 渲染頁相符；Stage 1 gate 無 stem／math 問題。
- 小瑕疵：12710 `\sqrt[]{2}`（空根指數），應正規化為 `\sqrt{2}`。

## Needs review / 圖
Stage 1 gate 結果為 6 列 `required_figure_missing`（匯入頁面的 3 項 = 其中 pdf_visual_status 為 VISUAL_REQUIRED_MISSING 的 12719、12727、12743）。PDF 為向量圖（無點陣圖），故 PDF visual assets = 0 不代表不需要圖。
| id | 題 | 判定 |
|---|---|---|
| 12712 | 例題6 | 答題必需（∠A=45°、正方形 T1…）|
| 12719 | 隨堂練習6 | 答題必需（ABCD 內 5 個黑三角形）|
| 12727 | 習題基礎題6 | 答題必需（T1…T5 等腰直角三角形）|
| 12709 | 例題3 魚鱗陣 | 說明性；題幹已完整，但寫「依右圖」|
| 12734 | 例題11 香檳塔 | 示意照片（4 層示意圖）；題幹完整 |
| 12743 | 習題進階題12 | 第1–3圖；題幹以文字描述步驟 |
裝飾圖（老鼠、烏龜、樹懶、隨堂練習空白框）不建立題目圖片。

## Skill binding
`skill_curriculum` 351 gh_Series（甲.級數）、352 gh_CommonSeriesSummationFormulas（乙.常用級數的和公式）章節歸屬正確。題目對應：除 **12739（觀念澄清2，等比級數）與 12743（進階題12，等比級數／面積和）** 內容屬甲.級數，卻綁在 gh_CommonSeriesSummationFormulas 外，其餘合理。

## 需修復
1. 刪除舊版同單元 28 列（1334–1361；無來源紀錄、與新版內容不同，無 tracker／學習紀錄引用），否則 gh_Series 45、gh_CommonSeriesSummationFormulas 20 題被重複計入 pass target 與 Stage 2。
2. 為上表 6 題以手動 PDF 區域 sidecar 掛上圖（沿用 Unit 1 機制）。
3. 12739、12743 改綁 gh_Series（改後 gh_Series 26、gh_CommonSeriesSummationFormulas 11）。
4. 12710 `\sqrt[]` 正規化。
