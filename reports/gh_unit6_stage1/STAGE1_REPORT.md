# 普高數學1 Unit 6「圓方程式」Stage 1 教材保真報告

- 範圍：`textbook_examples` id 12449–12480（32 題），source_volume=`數學1`、source_chapter=`單元6 圓方程式`
- 權威來源（SHA-256 已與匯入紀錄核對）：
  - DOCX `textbook_import/uploaded_sources/general/數學1/4c2b09003f42_單元06-圓方程式.docx`（`4c2b09003f42…79e2a3`）
  - PDF `…/b52f3a355f19_單元06-圓方程式.pdf`（`b52f3a355f19…ddb13`）
- 執行日期：2026-10-23；DB 備份 `instance/backups/kumon_math_before_gh_unit6_stage1_20261023_130706.db`
- 修復腳本與逐項紀錄：`stage1_repair.py`、`stage1_repair_log.json`（只改上述 32 列，未重新匯入、未碰其他單元）

**結論：Stage 1 PASS**（修復後 32/32 題 `needs_review=False`、`visual_required_missing=False`；4 張必要圖形檔均存在；該章節僅 32 題，無舊版 42 題殘留；`skill_curriculum` 僅 3 筆（甲、乙、丙），無無效綁定）。

## 1. Needs review 與必要圖形（皆對照 PDF 頁面原圖逐題複核）

| id | 題目 | 原因 | PDF 頁／bbox(pt) | 處置 |
| --- | --- | --- | --- | --- |
| 12457 | 例題7 | `required_diagram` 缺圖（羅盤、A/B 垃圾場、焚化廠 P） | p.8 [372,544,516,638] | 補圖 |
| 12466 | 例題10 | 圖已掛載但裁切錯誤：600×1338 的長條，涵蓋題幹與選項而非莫爾圓圖 | p.12 [394,176,518,270] | 重新裁切（舊檔備份 `old_assets/12466_before.png`） |
| 12478 | 習題 進階題6 | 缺圖；該「圖」其實是《天天日報》新聞框，內含題目必要數據（460 公里、半徑 80 公里、25 公里／時） | p.15 [110,482,510,574] | 補圖＋將新聞文字寫回題幹（原題幹缺這三個數據，無法作答） |
| 12480 | 習題 進階題8 | 缺圖（圓拱門、Q A P、B、R） | p.16 [420,296,528,392] | 補圖 |
| 12467 | 隨堂練習7 | 匯入信心 0.4（`linked_example` 對應錯位） | p.10 | 題幹與條件（P(1,−2) 在內、Q(−3,3) 在外、x²+y²=k）與 PDF 一致；清除 review 旗標，並將 `linked_example` 更正（見下） |

隨堂練習 7／8／9 的 `linked_example` 原為例題 10／8／9，依 PDF 版面實為例題 8／9／10（p.10、p.11、p.13 的練習框）；僅更正 `source_description` 的標註並在 `notes.linked_example_audit` 留紀錄，題幹未變。

另 12466（例題10）已掛載的圖形在 Stage 1 先前被視為 PASS，本次複核判定為錯裁，已更正。

## 2. 題幹／符號／詳解保真（逐題與 DOCX、PDF 核對）

- **12474 習題 觀念澄清5**：DOCX 以 Symbol 字型字元（`w:sym Symbol F070`，即 π）寫「面積為 2π」，匯入器丟失該字元，DB 變成「面積為2」——**數學上由「○」變成「×」**。已修為「面積為 \(2\pi\)」。全章 DOCX 僅此一處 Symbol 字元（已掃描）。這是共用匯入器對 Symbol 字型字元的遺漏；本次只修該列，未改匯入器。
- **12466 例題10 詳解**：原只存 (1) 的第一句，已依 PDF p.12–13 補齊 (1)–(3)（答案 ③、(x−3)²+y²=8、12π，皆以手算複驗）。
- 其餘 28 題題幹與條件逐一與 PDF／DOCX 核對無誤（含 12449–12456、12458–12465、12468–12469、12470–12473、12475–12477、12479）。例題7（12457）(1)(2) 與詳解推導（x²+y²−50x+400=0）手算複驗無誤。

## 3. 3 個 Skill 綁定

例題／隨堂練習依 heading span 綁定正確。**習題原本全綁在最後一個 heading 的 `gh_PointAndCircleRelationship`**，含圓方程式、一般式判斷等，與數學內容不符；已逐題依內容重新歸屬並在 `notes.skill_binding` 留稽核紀錄（`manual_topic_audit_unit6`）：

| Skill | 題數 |
| --- | --- |
| gh_StandardFormOfACircle | 9 |
| gh_GeneralFormOfACircle | 14 |
| gh_PointAndCircleRelationship | 9 |

（12470、12474、12476、12479、12480→標準式；12471、12472、12475→一般式；12462、12463 原本即在一般式。）

## 4. 未處理／已知事項（不阻擋 Stage 1）

- Symbol 字型字元（如 π）被匯入器丟失屬共用匯入器問題，建議另案修（本次不重構匯入系統）。
- 例題10 圖形在此題為「示意圖」，Gencode 階段只呈現題目給定的 A、B 與線段 AB（不畫出答案圓），見 `../gh_unit6_deploy/GENCODE_REPORT.md`。
