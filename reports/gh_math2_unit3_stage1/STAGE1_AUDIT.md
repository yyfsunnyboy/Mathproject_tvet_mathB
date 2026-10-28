# 普高數學2 Unit 3「計數原理」Stage 1 最終稽核（2026-10-26）

**最終判定：PASS／Stage 1 READY（2026-10-26）。** 依使用者本輪正式授權，已完成正式資料修復與封板驗證；未重新匯入、未進入 GenCode V3、未重啟 Flask。

## 正式封板結果

- 正式庫 Unit 3 僅保留新版 12744–12773 共 30 題，舊版 1362–1381 共 20 題已在限定章節範圍安全刪除；新版 21 列按隔離修復清單更新。Skill 分布 `gh_LogicAndSets` 9、`gh_CountingPrinciples` 21。
- 題幹與解答 `MATH_PARSE_FAILED` 0；Stage 1 Gate `READY`、blocked 0、needs_review 0；30 個 anchors 唯一，source order 完整為 1–30。必要圖僅掛載 12756、12773，檔案 SHA-256 與 notes 記錄一致。
- 正式 DB、備份 DB 的 `integrity_check` 均為 `ok`；與修復前正式備份相比，Unit 3 以外的教材及其餘 34 個資料表摘要全相同，含 `practice_attempts` 學生作答。舊題無有效教材 tracker 或其他宣告參照。正式後驗由 `verify_formal.py` 唯讀執行 PASS。
- 正式備份及列級／資產級回滾 manifest：`instance/backups/apply_manifest_unit3_20261026_224757_406749.json`；回滾命令為 `python -m reports.gh_math2_unit3_stage1.apply_unit3 --production --rollback instance/backups/apply_manifest_unit3_20261026_224757_406749.json`。相同套用程式已先於隔離庫完成 apply → Gate READY → rollback → preflight PASS。

以下保存**修復前稽核證據與問題判定**，供追溯本次寫入範圍。

## 來源與教材完整性

- 匯入來源紀錄：`textbook_import/uploaded_sources/general/數學2/80fe968ed2d3c218baf44e9d9782c1cb32cf4a708f543fbff754e970647819f6.json`，學制 `general`、冊別 `數學2`、Unit 3。
- Authoritative DOCX `cd38c1890caf_單元03-計數原理.docx`：431,823 B，SHA-256 `cd38c1890cafcd465f4c84e588fd23c593825f5c202bb27cdacfba11bef369f3`；配對 PDF `fe5ce0b620d3_單元03-計數原理.pdf`：2,030,303 B，SHA-256 `fe5ce0b620d368f2a87ca12494fbebb23722abaabd18eca8e5dba4d8a187a36c`。兩檔實際雜湊與來源紀錄、30 題 notes provenance 一致。
- 新版列 12744–12773 共 30 題：例題 7、隨堂練習 12、觀念澄清 3、基礎題 6、進階題 2。逐題題幹中文字符依記錄 PDF 頁做連續序列比對，30/30 覆蓋率 100%；PDF 頁 2、4、6、9、17、18 另經渲染檢視，檢查關鍵公式、負號、集合運算及圖。中文字符比對不代替數學符號檢查。
- 30 個 `question_anchor` 皆存在、唯一；`question_anchor.source_order` 為 1–30 且無缺號。DB `id` 順序按來源類型分組，不能當教材順序；教材管理列表程式依 anchor source order 排序。每題 source provenance 指向本次兩個雜湊。
- 原 DOCX 有 7 個 `eq \\o\\ac(■,解)` Word 欄位，均用於解答起始的「解」標記；無題幹作答資訊依賴這些 EQ 欄位。MathType/Equation 的 164/164 和 formula failures=0 不涵蓋下述 Symbol 字型 token 失敗。

## 真正阻斷項

1. **Symbol 字型未轉換。** 題幹 5 列：12744（∩、∪、補集撇號）、12745（>）、12748（∩、∪、補集撇號）、12763（>、<）、12764（=）；解答另有 12744、12750–12752。DB 存 `MATH_PARSE_FAILED:symbol:Symbol:*`，必須依原書還原；不能以「formula failures=0」略過。
2. **必要圖 2 張未掛載。** 12756 隨堂練習6：PDF 第 9 頁／書頁 56，四頂點 A-B-C-D 路徑圖，bbox `[420,650,520,730]`；12773 進階題8：PDF 第 18 頁／書頁 65，六格 L 形區域，bbox `[415,585,530,650]`。已逐圖看過裁區且用既有 `core.textbook_pdf_visual` 的人工 region override 在隔離目錄成功生成 2 張，與題一一對應。PDF 相關頁為向量圖，`get_images()=0` 不代表無必要圖。
3. **Skill 錯綁 4 題。** 12763–12764 為邏輯命題；12766–12767 為集合交聯與差集，應由 `gh_CountingPrinciples` 改綁 `gh_LogicAndSets`。兩個 reused Skills 的章節註冊本身正確；現況 5/25，修後 9/21。章末題的來源類型不是獨立 Skill。
4. **舊版殘留 20 題。** 同一 `general + 數學2 + 單元3 計數原理` 範圍內 id 1362–1381 無新版 provenance，與 12744–12773 同時存在。隔離前置檢查未發現指向舊題的資料表 FK 參照；正式寫入前仍須重新檢查作答、tracker、資產與外部參照，並備份。不得僅靠 id 區間清理。

## 4 個視覺 review 候選

| 題目 | PDF 頁 | 判定 | Stage 1 |
|---|---:|---|---|
| 12749 例題2 | 9 | 樹狀圖在解答區；題目本身要學生畫，桌球圖片為裝飾。 | 非阻斷，不掛圖 |
| 12756 隨堂練習6 | 9 | 題幹「如圖」直接依賴 A-B-C-D 路徑圖。 | 阻斷，需掛圖 |
| 12768 基礎題3 | 17 | 題目要求學生自行作樹狀圖；PDF 題區沒有提供樹狀圖。 | 非阻斷，不掛圖 |
| 12773 進階題8 | 18 | 題幹「如右圖」，六格 L 形的幾何配置不可由文字唯一確認。 | 阻斷，需掛圖 |

匯入 UI 的 `Needs review: 4` 對應這 4 個視覺候選；DB notes 另有 12 列 `needs_review=true`（含低信心文字題），其中 12748 有真正符號損壞；12746–12747、12758–12762 逐題對書後可解除低信心標記。現行純資料 Gate 對上述 4 項都報缺圖，需按 PDF 實際角色改判。

## 隔離演練與正式寫入範圍

- `rehearse_repair.py` 從正式庫以 read-only SQLite backup 建隔離副本；僅對本章 30 題修正，對舊 20 題做限定範圍刪除演練。未重新匯入。
- 隔離修復後 Stage 1 Gate：`READY`、30 題、blocked 0、needs_review 0；舊題剩餘 0；SQLite `quick_check=ok`。在同一隔離交易 rollback 後，本章逐列摘要與演練前一致。正式庫仍為 50 題、未修改。
- 正式候選 write scope：`textbook_examples` 中精確 `general + 數學2 + 單元3 計數原理` 的舊 1362–1381 共 20 列刪除；新版 21 列更新：12744–12752、12756、12758–12764、12766–12768、12773（只改題幹/解答 Symbol、Skill、review/visual notes 的適用欄位）；`uploads/question_assets` 僅新增上述 2 張 PDF 裁圖。`skill_curriculum` 兩列 353、354 保留，Unit 1/2 與其他單元不動。
- 正式回滾方案：先用 SQLite backup API 及檔案 SHA-256 備份正式 DB，預檢每列舊值、來源 hash、參照數與目標資產不存在；在單一交易按 curriculum+volume+chapter 及指定 id 更新/刪除，失敗即 rollback。資產先放暫存路徑，交易成功後原子移入；若後驗 Gate、資產雜湊或章外摘要失敗，依備份逐列恢復 20+21 列與兩個資產並重新驗證。正式操作前需獨立授權。

上述前置檢查、正式寫入、來源／資產／章外完整性驗證已通過，Stage 1 已封板。本輪依授權到此停止。
