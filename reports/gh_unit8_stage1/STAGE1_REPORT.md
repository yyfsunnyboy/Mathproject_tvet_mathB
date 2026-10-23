# 普高數學1 Unit 8「多項式的除法原理」Stage 1 教材保真報告

- 範圍：`textbook_examples` id 12517–12559（43 題），source_volume=`數學1`、source_chapter=`單元8 多項式的除法原理`
- 權威來源（完整 SHA-256 已與匯入紀錄核對）：
  - DOCX `textbook_import/uploaded_sources/general/數學1/5cde5954994d_單元08-多項式的除法原理.docx`（`5cde5954994d…4bcd0`）
  - PDF `…/f48be281b155_單元08-多項式的除法原理.pdf`（`f48be281b155…a3c0`）
- 執行日期：2026-10-23；DB 備份 `instance/backups/kumon_math_before_gh_unit8_stage1_20261023_170024.db`、`…_clearflags_20261023_170139.db`
- 腳本與紀錄：`stage1_repair.py`／`stage1_repair_log.json`、`stage1_clear_flags.py`／`stage1_clear_flags_log.json`（只改下列 10 列，未重新匯入、未改 Importer、未碰其他單元）

**結論：Stage 1 PASS**（43 題題幹／公式逐題對 PDF 與 DOCX 核對；`needs_review` 全數為 False；必要圖形 2 張皆已掛載；無重複、無舊版殘留；`skill_curriculum` 僅 4 筆有效綁定）。

## 1. 修復項目

| id | 題目 | 問題 | 處置 |
| --- | --- | --- | --- |
| 12537 | 習題 進階題14 | 題幹被截斷：缺 (1) 結尾「求實數 a, b, c, d 的值」與整個 (2)（求 f(0.505) 近似值） | 依 DOCX／PDF p.20 補回 |
| 12552 | 例題11 | 必要圖缺失（黑板：因式分解 x³+3x²−4x，常數項被擦掉）；匯入器因框選跨多題放棄 | 自 PDF p.16 bbox [348,565,515,670] 補圖，目視確認 |
| 12518 | 習題 觀念澄清1 | 餘式判斷，誤綁 BasicConcepts | 改綁 `gh_RemainderTheorem` |
| 12519 | 習題 觀念澄清4 | x⁵+1 是否被 x+1 整除，誤綁 BasicConcepts | 改綁 `gh_FactorTheorem` |
| 12517、12531、12541、12542、12554、12555 | 隨堂練習 1、7、9、10、12、13 | 僅 PDF 配對信心 0.4 的 `needs_review` | 題幹已對 PDF（p.2、10、12、13、16、17）核對一致，清旗標並寫入 `manual_stem_review` |

12555（隨堂練習13）原已掛載圖形，裁切含題幹與綜合除法遮蓋圖，內容正確。

## 2. Skill 綁定（4 個既有 Skill）

| Skill | 題數 |
| --- | --- |
| gh_BasicConceptsOfPolynomials | 1 |
| gh_ArithmeticOperationsOfPolynomials | 18 |
| gh_RemainderTheorem | 13 |
| gh_FactorTheorem | 11 |

12544（觀念澄清3，商式比較）、12536（基礎題6，12 的多項式值）歸屬有爭議，現行綁定可接受，未改。

## 3. 已知事項（不阻擋 Stage 1）

- 43 題 `correct_answer` 皆空（與 Unit 6 一致），答案由 Gencode 階段的 Oracle 提供。
- 例題 2、4、7、11 詳解中的直式／綜合除法表格匯入時遺失，詳解結尾停在「：」；結論文字完整。
- 本次以 PDF 文字與頁面圖逐題對照，未逐字比對 DOCX 全文。
