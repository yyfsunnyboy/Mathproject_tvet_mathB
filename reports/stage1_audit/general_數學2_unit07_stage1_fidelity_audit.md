# Stage 1 Fidelity Audit — 普高 數學2 單元7 數學期望值

- 稽核日期：2026-11-01（唯讀；未修改 DB、教材或 Skill）
- 初次結論：**BLOCKED**（2 題內容缺失，見 C）
- 修復後結論：**PASS**（2026-11-01 精確修復 12900、12909，見 E；21/21 通過）

## A. 教材摘要

| 項目 | 內容 |
|---|---|
| Curriculum / Volume / Chapter | `general`（普高，龍騰）/ `數學2` / `單元7 數學期望值`（section `7.數學期望值`） |
| Source DOCX | `textbook_import/uploaded_sources/general/數學2/360a978e359e_單元07-數學期望值.docx`，188328 bytes，SHA-256 `360a978e…02bcffc1`（實測一致） |
| Source PDF | `textbook_import/uploaded_sources/general/數學2/6ccf4aeb4b77_單元07-數學期望值.pdf`，1278733 bytes，SHA-256 `6ccf4aeb…5a2996d`（實測一致） |
| Skill | `gh_MathematicalExpectation`（數學期望值），`skill_curriculum` id 365 唯一綁定本章 |
| Questions | 21 筆，`textbook_examples` id 12891–12911；例題 5、隨堂練習 5、觀念澄清 2、基礎題 6、進階題 3 |
| Formula | DOCX 49 個 MathType OLE；DB 公式逐一對照 PDF 數值一致 |
| Visual assets | 0；PDF 10 頁無點陣題圖，僅裝飾插圖（商品卡、滷蛋、樹懶、福袋圖 1） |

教材身分以 DB `source_provenance`、上傳紀錄 JSON 與完整 SHA-256 確認，原始檔名 `單元07-數學期望值`。本來源為**普高數學2**，非技術型高中數學 B 系列。單一 DOCX 涵蓋本章章名至習題 9，21 題即完整範圍。DB 無其他單元7 舊題、無跨章重複文字、無作答紀錄、無 Gencode tracker。

## B. 21 題逐題驗收

| 題目 ID | 原始題號 | 文字 | 公式 | 圖形 | Skill | 結果 |
|---|---|---|---|---|---|---|
| 12891 | 例題1 (p127) | ✓ | ✓ 解 E=120/6=20 | 不需 | ✓ | PASS |
| 12892 | 例題2 (p128) | ✓ | ✓ C³₂/C⁵₂ 等，E=320 | 裝飾圖，不需 | ✓ | PASS |
| 12893 | 例題3 (p129) | ✓ | ✓ 56/120、8/120，E=3/5 | 裝飾圖，不需 | ✓ | PASS |
| 12894 | 例題4 (p130) | ✓ (1)(2) | ✓ −100、−60，E=−5、0 | 不需 | ✓ | PASS |
| 12895 | 例題5 (p131) | ✓ | ✓ −2000000+2400，E=2000 | 不需 | ✓ | PASS |
| 12896 | 隨堂練習1 (p128) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12897 | 隨堂練習2 (p128) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12898 | 隨堂練習3 (p129) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12899 | 隨堂練習4 (p131) | ✓ (a)(b)(1)(2) | ✓ | 不需 | ✓ | PASS |
| 12900 | 隨堂練習5 (p132) | ✗ 缺資料表 | ✗ 機率與利潤數值全缺 | 表格未匯入 | ✓ | **BLOCKER** |
| 12901 | 觀念澄清(1) (p133) | ✓ | ✓ 1/2 | 不需 | ✓ | PASS |
| 12902 | 觀念澄清(2) (p133) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12903 | 基礎題1 (p133) | ✓ | ✓ k=1,…,6、10k | 不需 | ✓ | PASS（註 1） |
| 12904 | 基礎題2 (p133) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12905 | 基礎題3 (p133) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12906 | 基礎題4 (p134) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12907 | 基礎題5 (p134) | ✓ (a)(b)(1)(2) | ✓ | 不需 | ✓ | PASS |
| 12908 | 基礎題6 (p134) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12909 | 進階題7 (p135) | ✗ 缺提問句 | — | 不需 | ✓ | **BLOCKER** |
| 12910 | 進階題8 (p135) | ✓ | ✓ | 不需 | ✓ | PASS |
| 12911 | 進階題9 (p135) | ✓ (1) 選項①–⑤、(2) | ✓ | 不需 | ✓ | PASS |

例題提供 `detailed_solution`，隨堂練習與習題原教材無解答；`correct_answer` 全空，與數學2 其他 11 個單元慣例一致。觀念澄清拆成每小題一筆，亦與單元1–6 慣例一致。

## C. 異常清單

1. **BLOCKER — 12900 隨堂練習5：題目依賴的資料表未匯入。**
   題幹寫「如下表」，但 `problem_text` 只有前後兩段文字。PDF p132 與 DOCX 表格 T15 內的巢狀子表格都有完整資料：

   | 經濟狀況 | 成長 | 持平 | 衰退 |
   |---|---|---|---|
   | 機率 | 0.4 | 0.5 | 0.1 |
   | 甲地利潤 | 40 | 15 | −10 |
   | 乙地利潤 | 55 | 10 | −30 |

   負號以 PDF 為準；DOCX 純文字抽取會遺失負號。缺表後本題無解。`pdf_visual_status=NO_VISUAL_REQUIRED` 與 `needs_review=false` 未攔下此問題。
2. **BLOCKER — 12909 進階題7：題尾提問句被截斷。**
   DB 只到計分規則「…該題以零分計算。」，缺少原文（DOCX 段落 89 換行後、PDF p135）：「今有一題某考生已經確定選項(1)與(2)是正確的，其餘3個選項則隨意猜測，求此考生在該題得分的期望值。」缺少必要條件與所求，本題無法作答。

非阻斷註記：
- 註 1：12903 的 `raw_problem_backup` 仍含 `[MATH_PARSE_FAILED:symbol:Symbol:F03D]`（Symbol 字型的「=」），`problem_text` 已正確為 `k = 1, 2, 3, 4, 5, 6`；數學2 其他單元另有 9 筆同型備份標記，屬既有模式。
- 12891 等題的數字包覆不一致（如 `1,2或 \(3\)`），不影響題意。

## D. Gate 與證據來源

| Gate | 自動 Gate | 本次人工／程式實證 | 判定 |
|---|---|---|---|
| Source fidelity（身分、SHA-256） | READY | 永久檔雜湊實測一致 | PASS |
| Formula integrity | 49/49、0 failures | 全 21 題公式與 PDF 數值逐一對照 | PASS |
| Question completeness | 21/21 titles | 2 題內容缺失（12900、12909） | **FAIL** |
| Curriculum binding | reused 1 | 單一 Skill、單一 `skill_curriculum` 綁定、本章語意相符 | PASS |
| PDF visual completeness | 0 assets | 無必要題圖；必要資料表缺失已計入完整性 | PASS（圖）／表格見上 |
| Duplicate / collision | — | 21 個 anchor 唯一；跨章無重複文字；無舊版殘留 | PASS |
| Needs review | 0 | 自動旗標漏判 2 題 | 不可採信 |
| Stage 1 readiness | READY | — | **BLOCKED** |

處置建議（已於 E 執行）：依 Lean SOP §2.3 第 8 點，只修 12900、12909 的 `problem_text`，依本報告列出的原文與表格逐字還原。修復前備份 DB，並保留 `raw_problem_backup`、`question_anchor` 與 Skill 綁定，在 `notes` 記錄修復來源。修復後重驗這 2 題即可封板，不需要重新匯入教材。

## E. 精確修復與重驗（2026-11-01）

- 授權範圍：僅 `textbook_examples` 12900、12909 的 `problem_text` 與新增 `notes.stage1_text_repair`；腳本 `reports/stage1_audit/repair_general_math2_unit07_stems.py`（單一 `BEGIN IMMEDIATE` 交易，先比對備份，任何超出範圍的變化即 rollback）。
- 備份：`C:\Users\yehiv\MathProject_DB_Archives\unit7_repair\kumon_math_pre_unit07_repair_20261101_173221.db`，SHA-256 `32720789699263768b3a06372024d0097e62420b453207233de6d3dfa23c90bb`；integrity ok、FK 0、36 表。
- 12900：在「如下表：」與「若以一年利潤…」之間補入 PDF p.132 資料表。學生頁以 textContent + MathJax（僅行內 `\( \)`）顯示題幹，Markdown 表格不會渲染，故採 MathJax `array`（含 `\hline` 框線，負號以 PDF 為準）。
- 12909：題尾補回 PDF p.135 問句。練習頁會把裸 `(1)`、`(2)` 誤判為小題編號，`\((1)\)` 又會失去括號；故依本題既有寫法將數字包成行內公式，選項標號為 `\(\left( 1 \right)\)`，顯示為「選項 (1) 與 (2) 是正確的，其餘 3 個選項…」，用字與順序不變；原文純文字存於 `notes.stage1_text_repair.source_text`。
- 實際異動：`textbook_examples` 2 列 × 2 欄（`problem_text`、`notes`）；其餘 5037 列、35 張表內容雜湊不變（bridge 67、telemetry 0、practice_attempts 2764、skill_curriculum 610、skills_info 605、`sqlite_sequence` 均相同）；integrity ok、FK 0。驗證期間無學生寫入。
- 顯示路徑：5001 練習頁經 `/get_next_question?textbook_example_id=` 由 DB 讀出並以頁面 `renderQuestion` 渲染；12900 表格 1 個 `mtable`、0 個 MathJax 錯誤；12909 問句 1 次、無小題誤判、0 錯誤。
- 重驗：12900、12909 文字、數值、公式與 PDF 一致，anchor、`raw_problem_backup`、Skill 不變；其餘 19 題與備份逐欄相同；Unit 7 仍 21 題、單一 Skill `gh_MathematicalExpectation`。

| Gate | 修復後判定 |
|---|---|
| Source fidelity / Formula integrity / Curriculum binding / Duplicate | PASS（不變） |
| Question completeness | PASS（21/21） |
| PDF visual completeness | PASS（無必要題圖；資料表已補入題幹） |
| Stage 1 readiness | **PASS** |
