# 普高數學1 Unit 9「一次與二次函數」Stage 1 教材保真報告

- 範圍：`textbook_examples` id 12560–12597（匯入 38 題）＋12598–12602（補入 5 題），source_volume=`數學1`、source_chapter=`單元9 一次與二次函數`
- 權威來源（SHA-256 已與匯入紀錄核對）：
  - DOCX `textbook_import/uploaded_sources/general/數學1/e61b79199c18_單元09-一次與二次函數.docx`（`e61b7919…3381`）
  - PDF `…/94c28e39fe3c_單元09-一次與二次函數.pdf`（`94c28e39…6ff3`）
- 執行日期：2026-10-23；DB 備份 `instance/backups/kumon_math_before_gh_unit9_stage1_20261023_213603.db`（integrity ok）
- 腳本與紀錄：`stage1_repair.py`、`stage1_repair_log.json`（先在 DB 複本預演，再於單一 transaction 寫入；只改下列 8 列、新增 5 列，未重新匯入、未碰其他單元）

**結論：Stage 1 PASS**（43 題、`needs_review`／缺圖旗標為 0、必要圖形 8 張皆存在、Unit 9 內無 `MATH_PARSE_FAILED`）。

## 1. 修復 8 題

| id | 題目 | 問題 | 處置 |
| --- | --- | --- | --- |
| 12571 | 例題7 | 詳解的 MathType 公式 #220 轉換失敗（`mtef_unsupported_record:32`），DB 留 `[MATH_PARSE_FAILED_220]` | 依 PDF p.13 補回配方法 4 步推導（y=−x²+3x+1 … =−(x−3/2)²+13/4），並留 `manual_formula_repair` 紀錄 |
| 12574 | 例題10 | 題幹的資料表遺失（訂單數量 5、10 千個；收入 45、80 萬元） | 依 PDF p.16 補回表格 |
| 12592 | 基礎題9 | 題幹被截斷，缺 y=−5x²+20x 與 (1)(2)(3) | 依 DOCX 補全；原有圖片保留 |
| 12593 | 進階題10 | 題幹缺「求 f(x) 及其頂點坐標。」 | 依 DOCX 補全 |
| 12573 | 例題9 | 題幹「在圖(a)中…」的圖 (a)(b) 未掛載，也未被標記 | 由 PDF p.15 裁圖（bbox [230,230,398,327]），目視確認 A–F 標示與 (a)(b) 完整 |
| 12591 | 基礎題8 | 必要拋物線圖缺失（`visual_required_missing`） | 由 PDF p.22 裁圖（bbox [388,139,538,264]），含 (−2,0)、(1/2,0)、O、x、y 標示；清旗標 |
| 12585、12586 | 隨堂練習12、13 | 僅 PDF 配對信心 0.4 的 `needs_review` | 題幹已與 DOCX／PDF（p.17、p.19）逐字核對一致，清旗標並寫入 `manual_stem_review` |

其餘 6 張既有圖片（12566、12584、12592、12595、12596、12597）已逐張目視確認裁切正確。12584 的裁切較寬、連題幹文字一起裁入，但圖形完整。

## 2. 新增 5 題觀念題

來源：DOCX 段落 296–301「9習題 觀念題」，為五個獨立的 ○× 敘述，原先未被匯入器辨識。DB 事前無同源題。沿用 `chapter_exercise` 與既有來源識別（`source_description`＝`9習題 觀念題N [source_type=chapter_exercise | dedupe=…]`，dedupe 以匯入器同一演算法計算；`question_anchor` 另用 `c1…c5` 編號以免與基礎題的錨點衝突，並在 `notes.stage1_added` 記錄原因與來源）。

| id | 敘述 | Skill |
| --- | --- | --- |
| 12598 | (1) 一次函數 y=2x+3 的圖形是一條斜率為3的直線 | gh_LinearFunctions |
| 12599 | (2) 拋物線 y=2x² 往左平移1單位得 y=2(x+1)² | gh_QuadraticFunctions |
| 12600 | (3) y=(2x+1)²+3 的對稱軸為直線 2x+1=0 | gh_QuadraticFunctions |
| 12601 | (4) 2≤x≤4 內 f(x)=−(x−1)²+5 的最大值為 f(2) | gh_QuadraticFunctions |
| 12602 | (5) 二次函數的圖形與 y 軸一定有一交點，但與 x 軸不一定有交點 | gh_QuadraticFunctions |

教材未附答案，`correct_answer` 保持空白，未自行猜測（與其他習題一致，答案由 Gencode 階段的 Oracle 提供）。

## 3. 最終結果與 Skill 題數

- Unit 9 共 43 題：`gh_LinearFunctions` 8、`gh_QuadraticFunctions` 35；`skill_curriculum` 僅 2 筆（乙、丙），無失效綁定。
- 章節切換處已核對：標題「丙 二次函數」之後的例題3 歸二次函數，之前的隨堂練習2 歸一次函數，沒有重演 Unit 8 的錯綁。
- DB 實際異動：`textbook_examples` 8 列修改、5 列新增；其他 30 列與其他資料表筆數完全未變；學生作答資料未動。

## 4. 已知事項（不阻擋 Stage 1）

- 12568 例題4 詳解中的示意圖、12560／12561 詳解的「如右圖」示意圖未掛載，不影響出題。
- 12576 隨堂練習3 為在空白坐標平面上描繪，視為繪圖題，不需要原圖。
- 12585、12586 的 `linked_example` 標註未處理（本輪範圍外）。
