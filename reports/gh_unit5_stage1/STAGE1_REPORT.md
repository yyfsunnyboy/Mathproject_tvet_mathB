# 普高數學1 Unit 5「直線方程式」Stage 1 教材保真報告

- 範圍：`textbook_examples` id 12403–12448（46 題），source_volume=`數學1`、source_chapter=`單元5 直線方程式`
- 權威來源（SHA-256 已與匯入紀錄核對）：
  - DOCX `textbook_import/uploaded_sources/general/數學1/1f2615727f0a_單元05-直線方程式.docx`（`1f2615727f0a…93d0`）
  - PDF `…/c1b9452d216e_單元05-直線方程式.pdf`（`c1b9452d216e…a3bd`）
- 執行日期：2026-10-23；DB 備份 `instance/backups/kumon_math_before_gh_unit5_stage1_20261023_110001.db`
- 修復腳本與逐項紀錄：`stage1_repair.py`、`stage1_repair_log.json`（只改上述 46 列，未重新匯入、未碰其他單元）

**結論：Stage 1 PASS**（修復後 46/46 題 `needs_review=False`、`needs_table_review=False`、`visual_required_missing=False`；所有圖檔存在；無舊版 38 題殘留）。

## 1. 六個 Needs review 逐題結果（皆對照 PDF 頁面原圖，非批次通過）

| id | 題目 | 原因 | PDF 頁／bbox(pt) | 處置 |
| --- | --- | --- | --- | --- |
| 12410 | 隨堂練習4 表格填空 | 表格內容整個遺失（stem 只剩「在下列的表格中填入適當的答案：」） | p.8 表格 | 依 PDF 還原 3×4 表格（方程式／斜率／x截距／y截距，3 列已給資料）寫入 `problem_text` |
| 12416 | 隨堂練習6 | 缺圖；題幹被截斷，漏「點 B(5,3) 為 L 外一點，使得 AB⊥L，求 a,c 的值」 | p.13 [420,528,520,625] | 補圖；題幹依 DOCX 段落 205–206 補齊 |
| 12417 | 隨堂練習7 | 缺圖（S、A、B 三點與直線 SA） | p.15 [392,565,518,652] | 補圖 |
| 12430 | 隨堂練習 鋪色區域 | 缺圖（鋪色區域與兩直線） | p.27 [398,292,520,414] | 補圖 |
| 12443 | 習題 基礎題8 | 缺圖；題幹被截斷，漏「的解區域，求 a,b,c」 | p.29 [392,468,534,592] | 補圖；題幹依 DOCX 段落 472／PDF 補齊 |
| 12448 | 習題 進階題13 | 缺圖（平行線族、A、B、P） | p.30 [370,518,532,678] | 補圖 |

## 2. 已掛載的 6 個 PDF 圖形資產複核

| id | 結果 |
| --- | --- |
| 12403 例題1（5 條直線） | 完整、可辨識，保留 |
| 12404 隨堂練習1（A,B,C 三線） | 完整，保留 |
| 12427 例題14（三角形區域） | 完整，保留 |
| 12444 習題 進階題9（矩形 ABCD/CDEF） | 完整，保留 |
| 12421 例題11（窗戶） | **裁切不完整**（右側標籤 `(34,5)`、尺寸標註與軸標籤被切掉）→ 重新裁切 p.20 [368,274,520,440]；舊檔備份於 `old_assets/12421_before.png` |
| 12436 習題 基礎題1（四直線） | **裁切不完整**（`L1` 標籤被切掉）→ 重新裁切 p.28 [392,372,538,508]；舊檔備份於 `old_assets/12436_before.png` |

其他「如圖／右圖」檢查：12425、12426、12428、12429、12442、12447 的「圖示」是作答動詞而非附圖；12446 的堡壘示意圖（p.30）未被題幹引用且座標已給，不阻擋；其餘 36 題無需圖。

## 3. 46 題題幹、條件、來源與 Skill 綁定

- 題幹／條件：逐題與 DOCX 文字及 PDF 版面核對。修正項：12410 表格、12416／12443 被截斷的題幹、12421 小題標號 (1)(2) 遺失。重要符號（⊥、平行、不等號 ≥ ≤ < >、座標）核對無誤；僅 12413 **詳解**中的平行符號被轉成 `\ /`，已改回 `\parallel`（僅該列詳解）。
- 6 個 Skill 綁定：例題／隨堂練習 28 題依 heading span 綁定正確；**習題 18 題原本全綁在最後一個 heading 的 `gh_LinearInequalityInTwoVariables`**（含斜率比較、平移、距離等），與數學內容不符，已逐題依內容重新歸屬並在 `notes.skill_binding` 留稽核紀錄（`manual_topic_audit_unit5`，含原 skill 與理由）。修復後分佈：

  | Skill | 題數 |
  | --- | --- |
  | gh_LineSlope | 3 |
  | gh_EquationOfALine | 9 |
  | gh_TranslationOfALine | 3 |
  | gh_ParallelAndPerpendicularLines | 12 |
  | gh_DistanceFromPointToLine | 8 |
  | gh_LinearInequalityInTwoVariables | 11 |

- 新版取代舊版：該章節僅 46 題；`skill_curriculum` 僅 6 筆（甲～己），無舊版殘留題或無效綁定。

## 4. 未處理／已知事項（不阻擋 Stage 1）

- 平行符號 `∥` 在 MathType 轉換成 `\ /` 屬共用匯入器問題，本次只修該列詳解，未改匯入器。
- 12428（三個圖示）與 12447（圖示＋格子點個數）教材保真無誤，但作答拓撲超出 Spec §5 的五種契約，Gencode 階段列 DEFERRED（見 `../gh_unit5_deploy/GENCODE_REPORT.md`）。
