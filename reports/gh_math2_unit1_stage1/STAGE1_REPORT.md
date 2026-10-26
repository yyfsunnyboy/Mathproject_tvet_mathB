# 普高數學2 單元1「數列與遞迴關係」Stage 1 隔離修復報告

- 範圍：`textbook_examples` id 12667–12706（`general` / `數學2` / `單元1 數列與遞迴關係`）
- 權威來源（完整 SHA-256 已核對）：DOCX `742ea24d…6b38`、PDF `f2bef2bd…1789`（`textbook_import/uploaded_sources/general/數學2/`）
- **所有修復只發生在隔離複本** `sandbox/kumon_math_copy.db`（以 `mode=ro` + sqlite backup 自正式庫複製）與 `sandbox/uploads/`；**正式庫與正式 uploads 零寫入**
- 結論（隔離複本）：**Stage 1 READY（25/25 PASS）**；修復前同一驗證器：BLOCKED（8/21 PASS，13 FAIL）。**尚未套用正式庫，需你明確授權。**

## 1. 逐題修復前後差異（完整表見 `row_diff.md`）

| id | 題目 | 修復前 | 修復後 | 驗證 |
|---|---|---|---|---|
| 12668 | 例題2 | 缺圖（數字螺旋＋①–④ 選項圖） | 2 張 PDF p.3 裁圖（主圖、選項圖） | 裁圖目視核對完整 |
| 12673 | 隨堂練習2 | 題幹只剩引導句；圖為半隻手＋吉祥物（誤裁） | 補回 `1,2,…,10`、`a_n` 定義、(1)(2)；重裁 PDF p.4 手指計數圖（含完整 1–10 路徑） | 題幹逐字比對 DOCX/PDF；圖目視核對 |
| 12686 | 例題6 | 缺圖 | PDF p.8 六邊形地磚圖 1–3 | 目視 |
| 12687 | 例題7 | 缺圖 | PDF p.9 三角形分割圖 1–4 | 目視 |
| 12688 | 例題8 | 缺圖 | PDF p.11 魚鱗陣圖 | 目視（首次裁切右緣被切，已加寬重裁） |
| 12690 | 隨堂練習7 | 缺圖；題幹缺 `a_n` 定義與 (1)(2) | 補圖（p.10）；補「第5圖、第6圖…線段個數（a₁=1、a₂=2）(1)遞迴關係式 (2)求 a₉」 | 依 PDF p.10 文字層（`求a9`）與 DOCX 比對 |
| 12694 | 習題 基礎題5 | 缺圖 | PDF p.21 地磚圖 1–3 | 目視 |
| 12695 | 習題 基礎題6 | 缺圖 | PDF p.22 九等分正方形圖 1–3 | 目視 |
| 12698 | 習題 進階題9 | 缺圖 | PDF p.23 飛魚圖案 1–3 | 目視（首次裁切底部標籤被切，已重裁） |
| 12699 | 習題 進階題12 | 缺圖 | PDF p.24 T₁–T₅ 套疊正方形 | 目視 |
| 12702 | 例題11 | 缺圖（蜥蜴圖＋①–③ 選項） | 2 張 PDF p.17 裁圖（主圖、選項圖） | 目視 |
| 12691 | 隨堂練習8 | **偽題**：「數學超展開」側欄句「隨堂練習中，一直重複…康托集…圖4」被判為題目 | 自複本刪除（確認 tracker／作答／錯題本均無參照；DOCX 只有 11 個「隨堂練習」標題） | 數量 39；隨堂練習編號 1–11 連續 |
| 12692／12703／12704／12705 | 隨堂練習9／10／11／12 | 編號因偽題多 1；12703、12704 的 linked_example 錯（例題10、例題11） | 改為 8／9／10／11；12703→例題9、12704→例題10（與 DOCX 相鄰例題一致）；anchor_id／anchor_key／question_label／圖檔路徑同步；`source_order`、`block_index` 保持原解析值 | 驗證器比對 DOCX 順序與 linked_example |
| 12701 | 例題10 | 缺「恆為6的倍數」，並多出 `a_n =` | `4ⁿ+2 恆為 6 的倍數。` | 對 PDF p.16 |
| 12704 | 隨堂練習11→10 | 缺「恆為12的倍數」 | `9ⁿ+3 恆為 12 的倍數。` | 對 PDF p.17 |
| 12671 | 例題5 | `a, 2, b 1`：DOCX `w:sym F02D`（減號）遺失；詳解同樣遺失 | `a, 2, b-1` | 詳解推導 a+b=5、ab=4 → a=1 或 4 與 `b-1` 一致（`b+1` 無實根） |
| 12676 | 隨堂練習5 | `r2`（上標遺失） | `r²` | 對 DOCX 段落 112（`vertAlign` run） |
| 12692、12705 | — | `needs_review=True`（信心 0.4，圖已掛） | 逐題核對題幹＋圖後清除，保存 `manual_stem_review` 證據 | 見 `verify_after.json` |

`needs_review` 的清除只發生在已逐項目視核對的 13 題，且每題在 `notes` 保存 `manual_visual_review`／`manual_stem_review`（含來源雜湊、頁碼、bbox、裁圖 SHA-256）；`stem_before_repair` 保留原題幹以便回溯。驗證器另有一項檢查「被標記過的 13 題皆有證據」。

## 2. 同類問題檢查

單元內（驗證器全題掃描）：除上列題目外沒有其他截斷、符號遺失、偽題或缺圖。DOCX 中文段落覆蓋率 68.8%，未覆蓋 49 段為教材敘述與部分例題詳解（本單元只有 10 題匯入詳解，屬 Warning，不影響題幹）。

全普高範圍（`scan_common_defects.py`，唯讀啟發式；**未修改任何其他單元**）：

| 位置 | 發現 | 判定 |
|---|---|---|
| 數學1 單元1 實數 | 9 題 needs_review、1 題 visual_required_missing | 需另行查證（可能為舊匯入世代），不在本輪範圍 |
| 數學1 單元11 id 12629 | 題幹「所以x  1, 3, 5」遺失 `=`（同一類符號遺失） | 建議下一輪以同範本局部修復 |
| 數學1 單元10／8 | 各 2 題 description 仍含 `needs_review=true` 字樣（旗標已清） | 低風險，僅標籤殘留 |
| 數學4A 單元6／7、數學2 單元12、選修甲(下) 單元4／7 | 空隙或 `L1`、`z1` 疑似下標遺失 | 舊格式匯入（非 gh_ 新路徑），啟發式命中，屬待查 Warning |

## 3. 共通匯入缺陷與最小修復方案（僅提案，**未改任何程式碼**；需在授權後以 dry-run 驗證）

| # | 缺陷與根因 | 最小修復 |
|---|---|---|
| 1 | **偽題**：`core/textbook_processor.py` 的 `_GH_PRACTICE_START_RE`（約 L321）沒有像 `_GH_EXAMPLE_START_RE` 那樣排除「例題8 的／中／之」的敘述句，所以「隨堂練習中，…」被當成新題 | 在隨堂練習的 regex 加上同樣的 `(?!\s*[的中之裡])` 保護（一行） |
| 2 | **符號／上標遺失**：`extract_converted_latex_docx`（約 L2419）用 `para.text`，python-docx 會丟棄 `w:sym`（如減號 F02D），且把 `vertAlign` 上下標 run 攤平（`r2`） | 沿用 `textbook_processor_v2._docx_paragraph_text_with_symbols`（v2 L2469，已有 Symbol 解碼）改為共用，並對 `vertAlign` run 輸出 `^{…}`／`_{…}`；未知 Symbol 保留明確 `MATH_PARSE_FAILED` 標記而非靜默刪除 |
| 3 | **題幹截斷**：`scan_general_high_layout` 的 `stem_open` 只接受以 `(n)`、`\(`、`\[`、`$` 開頭的行作為續行（`_GH_CONTINUATION_RE`），純文字續行（`1, 2, 3…`、`依此規律可畫第5圖…`、`恆為6的倍數。`）會結束題幹，練習／習題更會把後續行丟棄 | 對尚未遇到詳解標記、且不在 `body_set`、也不是結構標題的純文字行：當前一題幹行未以句末標點結尾、或以 `\)` 結尾、或整題尚無任何問句時視為續行；並加完整性 Gate（題幹須以句末標點或小題結尾、證明題須含結論），不通過即標 needs_review 而不是靜默匯入 |
| 4 | **缺圖**：DOCX 內多數圖不是可映射的 blip 資產，PDF 補圖因 `overspan_multi_question`／低信心被跳過（10 題），匯入仍顯示成功 | 不建議放寬對位演算法；改為匯入摘要明確列出「required visual unmatched」並判為 BLOCKED，延續 Unit 10 的 `regions.py` 手動對位範本；本單元的 `IMAGE_FIXES` 即可作為此範本 |

上述 1–3 項的回歸測試建議：以 `verify_stage1.py` 的對照邏輯做 dry-run（零寫入）重跑本單元與 Unit 5／10／11 的來源，期望本單元缺陷消失、已封板單元無新差異。

## 4. 剩餘 Blocker／Warning

**Blocker：隔離複本內無。** 若要讓正式庫也達 Stage 1 PASS，仍需套用本報告的變更集（見 §5）。

**Warning（不阻擋 Stage 1）**
- `correct_answer` 全空，詳解只有 10 題（例題1–5、6–8、9、11）；12701（例題10）原教材有證明但未匯入詳解。屬 Oracle 層，Stage 2 以 domain oracle／DEFERRED 處理。
- 12692 的圖是整個題框（含題幹文字），可讀但與文字重複；可日後改裁只含數字三角形。
- 證明題（12700、12701、12703、12704、12706、12696）與選擇圖像題（12668、12702）的作答拓撲，Stage 2 可能 DEFERRED。
- 11 題需圖的題目圖檔為 PDF 裁圖（200 dpi），非 DOCX 原檔。
- 其他單元的同類疑似缺陷（§2）待另案。

## 5. 未來正式套用的最小變更清單（`production_change_set.json`）

1. 備份正式 DB（backup API，`integrity_check=ok`），以單一 transaction 寫入，範圍僅 `textbook_examples` id 12667–12706。
2. DB：**1 筆 DELETE（id 12691）**＋**18 筆 UPDATE**（id：12668、12671、12673、12676、12686、12687、12688、12690、12692、12694、12695、12698、12699、12701、12702、12703、12704、12705；各列新值即 `production_change_set.json` 的 `new` 欄位）。
3. 檔案：複製 `sandbox/uploads/question_assets/…` 的 15 張 PNG 到正式 `uploads/question_assets/…`（含 SHA-256 清單）；舊 3 張（誤裁的 12673 圖、隨堂練習9／12 兩張舊名）在確認無參照後再處理。
4. 套用後：以 `verify_stage1.py --db instance/kumon_math.db --label prod_after` 重驗；`skill_curriculum`／`skills_info` 不需變更；不需重啟 Flask（教材列表為 DB 讀取），但圖檔需存在於 `uploads/`。
5. 不涉及：Skill 建立、其他單元、Stage 2、tracker。

## 6. 正式庫零寫入、零變更證據

`prod_guard.py` 在修復前後各取一次指紋（`prod_fingerprint_before.json` / `prod_fingerprint_after.json`），結果完全相同：

- 檔案 SHA-256：`kumon_math.db`、`-wal`、`-shm` 三者皆相同（mtime 同為 13:38／13:45）
- 全部資料表 row count 相同；`textbook_examples`、`skill_curriculum`、`skills_info`、`gencode_component_tracker` 內容摘要相同
- 驗證器另逐列比對複本與正式庫：範圍外 `textbook_examples`、`skill_curriculum`、`skills_info`、`gencode_component_tracker` 全相同
- 正式 `uploads/question_assets/…/數學2/` 仍為原 3 個檔案；`git status` 只新增 `reports/gh_math2_unit1_stage1/`（未追蹤），無任何已追蹤檔案被修改；未 commit、未 push
- 正式庫僅被 `mode=ro` 讀取與 sqlite backup API 讀取

## 7. 檔案

`stage1_repair.py`（修復，僅作用於複本，內含 assert 防止指向正式庫）、`verify_stage1.py`（Stage 1 驗證）、`scan_common_defects.py`、`build_change_set.py`、`prod_guard.py`、`repair_log.json`、`before_rows.json`、`verify_before.json`／`verify_after.json`、`row_diff.md`、`production_change_set.json`、`sandbox/`（複本 DB 與圖檔，約 17 MB，不建議提交）。
