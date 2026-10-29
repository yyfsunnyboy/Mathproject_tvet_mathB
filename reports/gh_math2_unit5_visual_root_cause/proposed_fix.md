# 最小修復提案（本輪未修改任何核心程式）

**使用者決定（2026-10-28）**：授權下一輪實作 P1–P4，P4 採**方案 A**（產生裁切與 bbox 提案，教師核可後才寫入；核可前 Gate 維持 BLOCKED）。P5 未納入。正式寫入、Promotion、Publish 仍需另行授權。

目標：讓「題幹有明確圖形依賴、PDF 中有完整向量圖」的題目，由系統自行定位並產出裁切，不再為每個單元人工輸入座標。**不降低任何 Gate**：`required_figure_missing` 判斷不變；不確定的圖仍維持 `needs_review` 或 `rejected`。

所有規則都依版面結構判斷，不含 anchor、單元或 PDF hash 硬編碼。預計只改 2 個核心檔案與 1 個測試檔，約 120 行。

## P1 題目起點改用題號標記（修 R1，主因）

- 位置：`core/textbook_pdf_visual.py::match_questions_to_pdf`。在決定 `best` 之後加入一個小函式。
- 規則：從題目標籤取出結尾數字，例如「進階題12」取 `12`。在同頁「前一題起點」與「命中片語 y」之間，尋找位於左側邊界、且在題幹文字欄左邊的同號字詞。找到時，起點改為該字詞的 y，並記錄 `question_start_source="label_marker"`；找不到就沿用原值。
- 證據：在 Unit 5 共 37 題中只修正了進階題12（678.2 → 586.9），另外 36 題零變化。
- 已排除的替代方案：「改用最早命中片語」。4 筆位移中有 2 筆跳進其他題（例1、基礎題5），不安全。

## P2 排除頁面裝飾（修 R2）

- 位置：`build_page_index`。比照目前對 blended 路徑的處理方式。
- 規則：路徑超出頁框 1pt 以上，或是落在上下 60pt 邊界內、寬度至少 90% 頁寬的帶狀路徑，標記為 `furniture`，且不進入 `drawings` 候選。
- 證據：14 份普高 PDF 都有 2–6 頁，頁尾帶會伸入頁內最後一題的區域並通過 soft 門檻。

## P3 以「圖形墨跡連通塊」量尺寸（修 R3）

- 位置：`classify_and_detect_visuals` 的 strong-cue 分支。只在現有路徑都找不到候選時才啟用，因此不影響已成功的題目。
- 規則：在題目區域內，把非裝飾、非外框（寬度未達半頁）的 `drawings` 與 `small_drawings` 以 6pt 間距**反覆**合併成連通塊，排除與正文字詞重疊的塊，再用**原本的門檻**（w≥40、h≥40、area≥2500）檢查。門檻不降，只把量測對象從單一路徑改為整張圖。
- 同時修正 `assemble_visual_group_bbox` 的字形吸附，改為反覆執行直到不再增長。目前只執行一輪，會截掉 B₆ 的下標。
- 證據：本題連通塊為 `[426.7, 588.0, 524.4, 652.1]`，包含全部 31 條墨跡，0 條被截斷。Unit 3/4 的 6 個人工區域，連通塊全部落在人工框內（Unit 4 的 IoU 為 0.947–0.985）。

## P4 Acceptance 依「完整度」而非「尺寸」判斷（修 R4）

- 位置：`core/textbook_pdf_visual_acceptance.py::evaluate_visual_acceptance` L278–L280。
- 現況：strong cue 且面積 < 9000、寬 < 140 時一律送審。6 個人工圖與本題全部會觸發。
- 規則：只有在裁切邊界切到墨跡（被截斷的路徑數大於 0）時，才保留 `low_mapping_confidence`。其餘 Gate 規則全部不變，包括截斷、跨題、污染、多圖、共用資產，以及 vh<40。

**這一項需要您決定安全等級：**

- **方案 A（建議首次上線採用）**：完整小圖改為 `needs_review`，原因為 `auto_compact_figure_pending_confirm`，並在 dry-run 中產生裁切 PNG 和 bbox 提案。教師只需「核可／退回」，不再輸入座標；核可後才寫入既有的 `stage1_verified_visual_regions.json`。Gate 在核可前維持 BLOCKED。
- **方案 B**：同時符合以下全部條件時自動 accepted：頁面為唯一命中且分數 ≥0.9、題幹有 strong cue、區域內只有單一連通塊、0 條墨跡被截斷、沒有正文、完全位於本題範圍內、未與他題共用。任何一項不符就回到 `needs_review`。
- 建議先採方案 A。等 Unit 1–5 與數學1 的回歸結果證實零誤收後，再評估是否改用方案 B。

## P5（選擇性）修正誤導性標籤

沒有任何候選的純文字題，目前會被標為 `rejected`、`low_mapping_confidence` 並顯示 `skipped_low_confidence`（acceptance L254–L259）。建議改標 `no_visual`。這不影響 Gate，但會改變報表計數，可另案處理。

## 修復輪的必要驗證

1. 在 `tests/test_textbook_pdf_visual.py` 新增合成頁面單元測試，涵蓋：下標錯序時的題號定位、頁尾帶不得成為候選、小路徑加點與字形能組成合格連通塊、完整小圖不因尺寸被送審、截斷的圖仍會送審、與正文重疊的塊被排除。
2. 重跑 Unit 5 隔離 dry-run（37 題）。只允許進階題12 發生變化；正式 DB 零變更。
3. 以 Unit 3/4 的 6 個人工區域作為 golden set：自動候選必須落在人工框內，且其他題不得新增掛載。Unit 4 只做唯讀比較，不重新 Promotion／Publish。
4. 數學1 已匯入單元只做唯讀分類差異比較：不得出現與現行 accepted 資產不同的新 accepted 圖。
5. 執行既有的 PDF visual 與 Stage 1 Gate 測試。

## 防止下一章再發生

- 每個單元的 Stage 1 dry-run 都對所有 strong-cue 題目輸出「候選裁切 PNG、起點來源、拒收原因」清單，讓問題在匯入當下就能看見，不必事後追查。
- 把 Unit 3/4/5 的人工核准區域固定為 golden set 回歸測試。之後任何偵測器修改都必須讓這些圖仍可自動找到。
- 在 P1–P4 生效前，**不再新增** `textbook_b2_11.py`、`textbook_b2_12.py` 這類以 PDF hash 硬編碼座標的修正。

## 修復後仍需另行授權的步驟

在 Unit 5 正式寫入圖像設定、重跑正式 Stage 1、Promotion、Publish 之前，都需要另行授權。本提案不包含這些步驟。
