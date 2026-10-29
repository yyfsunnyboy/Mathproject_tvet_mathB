# 進階題12 圖像遺失：根本原因分析

證據性質：**new_isolated_readonly_trace**。原始任務證據仍為 **original_evidence_unavailable**。本分析以權威 PDF（SHA-256 `e24c72f8…ec166`）及上一輪隔離 dry-run 擷取的 37 列資料，直接呼叫現行偵測函式重跑；結果與已記錄的 `visual_bbox`、`visual_reason` 逐位一致（`reproduces_recorded_pipeline_result=true`）。全部數據見 [visual_pipeline_trace.json](visual_pipeline_trace.json)。

## 結論

**系統偵測失敗的起因不是「圖太淡」或「confidence 太低」，而是題目起點 y 對錯了。** 演算法把題目起點定在小題(2)那一行（y=678.2），題號「12」實際在 y=586.9。半圓圖位於 y 588–652，因此整張圖落在題目區域之外，從一開始就沒有成為候選。

區域內唯一能通過尺寸篩選的物件是頁尾橘色裝飾帶。它被裁成 609×9pt 的空白細條；Acceptance Gate 正確地拒絕了這條細條，因此分類變成 `skipped_low_confidence`。

此外還有兩個獨立的共用缺陷：即使把起點修正，仍會被這兩個缺陷擋下。

| 層級 | 缺陷 | 單獨修正此項的結果（記憶體內反事實） |
|---|---|---|
| R1 題目起點 y | 取「最長命中片語」的 y，而非題幹起點 | 題目區域涵蓋圖形，但頁尾帶仍是唯一候選，依舊產生 9pt 細條 |
| R2 頁面裝飾 | 只排除 blended 路徑；超出頁框的頁尾帶未被排除 | 頁尾帶不再成為候選，但結果變成完全沒有候選 |
| R3 圖形尺寸 | 只用「單一路徑」量尺寸；點和標籤字形不計入 | R1+R2 都修正後，半圓 79×39.7pt 仍未通過所有門檻 |
| R4 Acceptance | 「右側細片」規則不分完整或截斷，一律送審 | R1+R2+R3 修正後可抓到完整圖形，但現行 Gate 仍判為 `needs_review` |

## 逐步追蹤

1. **頁面索引**：使用 [`build_page_index`](../../core/textbook_pdf_visual.py)。半圓圖純由向量構成：圓弧加直徑是一條 79×39.7pt 的路徑（面積 3150pt²）；10 個點及 A₁–A₄、B₁–B₆ 標籤共 30 條小於 80pt² 的路徑，被分到 `small_drawings`。標籤是外框化字形，不在文字層中。頁面沒有嵌入點陣圖。
2. **Anchor 與頁面對位**：使用 `match_questions_to_pdf`。頁面判定為第 16 頁，**正確**（`unique_phrase+order`、0.99）。但 y 取自最長命中片語。文字層把第一句排成 `如圖AAAA1234…BBB126f…`：下標排在字母之後，省略號被映射成 `f`。DOCX 正規化後則是 `如圖A1A2A3A4…ldot`，因此第一句的 7 個片語全部比對失敗。最長命中是小題(2)的片語，位於 y=678.2。trace 的 `phrase_table` 列出 16 個片語各自是否命中及其 y 值。
3. **題目區域**：使用 `assign_question_regions`。區域為 `[36, 670.2, 573.4, 757.7]`。這是頁內最後一題，所以下界取頁高減 36（757.7），伸入從 736.6 開始的頁尾帶。圖形完全在區域上方。
4. **候選篩選**：使用 `classify_and_detect_visuals` L806–L895。半圓路徑與區域沒有交集。頁尾帶 `[-618, 736.6, 617.9, 802.2]` 不屬 blended，與區域相交，並通過 strong-cue 的 soft 門檻（area≥2500、w≥40、h≥40），成為唯一候選。soft 清單一旦非空，L913 的右側 fallback 就不會執行。
5. **挑選與組裝**：`_pick_compact_diagram_bbox` 因 primary 清單為空（頁尾寬 1235.9 > 0.85W），改用 fallback 清單 `[footer]`。ranking score 為 2.39；這是候選排序分數，不是 confidence。
6. **區域裁切**：L1077–L1113 把頁尾帶裁成 `[0, 736.58, 609.45, 745.70]`，即 609×9pt 的空白條。
7. **Acceptance**：`evaluate_visual_acceptance` 回傳 `needs_review`，原因為 `vh<40 → low_mapping_confidence`，以及 `寬高比 67 的全寬條 → overspan_multi_question`。**這一步 Gate 的判斷正確。**
8. **分類**：L1160–L1166 把 `needs_review` 改寫為 `skipped_low_confidence`、`should_mount=False`。
9. **裁切與資產**：`enrich_textbook_examples_with_pdf_visuals` L1590–L1594 在呼叫 `crop_pdf_bbox` 之前就 `continue`。**從未產生任何暫存或正式 PNG**，所以 `visual_assets=[]`。
10. **視覺狀態**：`classify_general_high_visual_status` 發現沒有 asset、題幹有「如圖」，判為 `VISUAL_REQUIRED_MISSING`。
11. **Stage 1 Gate**：`textbook_stage1_gate.py` L110–L115 據此回報 `required_figure_missing`。在上游漏抓的前提下，Gate 判斷正確。

## 回答八個問題

1. **是否偵測到半圓圖？** 否。半圓路徑從未進入候選清單。
2. **是否產生候選區域？** 有一個，但它是頁尾裝飾帶，不是半圓圖。
3. **confidence score？** 文字對頁分數為 0.99。視覺部分沒有數值型 confidence，只有 Acceptance 的分類結果 `needs_review`，原因為 `low_mapping_confidence`、`overspan_multi_question`。這兩個原因描述的是錯誤候選的形狀。
4. **為何標成 `skipped_low_confidence`？** 錯誤候選被 Gate 送審後，L1160 統一把它改寫成此分類。附帶問題：沒有任何候選的純文字題，也會因 `visual_bbox=None` 被標上 `rejected` 和 `low_mapping_confidence`（acceptance L254–L259）。所以 37 題全部顯示 `skipped_low_confidence`，這個標籤會誤導診斷。
5. **哪一層出錯？** 頁面對位正確。**題目起點 y 定錯**（主因 R1），其次是裝飾帶污染（R2）、單一路徑尺寸門檻（R3），最後 Acceptance 會阻擋完整的小圖（R4）。裁切、關聯和 Gate 本身沒有錯。
6. **是否產生暫存圖片？** 否。
7. **為何 `visual_assets=[]`？** 分類在裁切前就被跳過；裁切從未發生。
8. **是否有教材歧義需要教師判斷？** **沒有。** 圖形位於第 12 題題幹第 1–3 行右側，進階題11（y≈505）沒有圖，第 12 題後也沒有其他題目，歸屬沒有歧義。教師只需在系統產出裁切後檢查完整度，不需要判斷歸屬或提供座標。

## 是否為共用缺陷？是

- **R1**：這是演算法本身的取值方式，並非針對單一題目。凡第一句含下標、上標、省略號或分式，導致與 DOCX 正規化結果不一致，就會改由後面的句子定位。在 Unit 5 共 37 題中，題號標記規則只修正了進階題12，其他題目零副作用。另一個候選規則「最早命中」經人工檢查不安全：4 筆位移中有 2 筆跳進其他題塊（例1、基礎題5），因此已排除。
- **R2**：14 份普高 PDF 全部都有 2–6 頁，頁尾裝飾帶會伸入「頁內最後一題」的區域並通過 soft 門檻。只要該題的真實圖形沒有通過門檻，就會重現本案。
- **R3**：Unit 3、Unit 4 已有 6 個人工核准區域，全部是 57–115pt 的右側小型線條圖。其中 3 個的最大單一路徑不到 soft 門檻（30×24、20×20、85×36.5）。這 6 個人工座標本身就是同一類缺陷的累積成本。另外，`core/textbook_b2_11.py` 與 `core/textbook_b2_12.py` 也以 PDF hash 硬編碼座標修正職業類教材，屬於同樣的模式。
- **R4**：Acceptance L278–L280 規定，strong cue 且面積 < 9000、寬 < 140 時一律送審。上述 6 個人工圖與本題全部會觸發這條規則。
- **次要問題**：`assemble_visual_group_bbox` 的字形吸附只執行一輪，距離上限 6pt，B₆ 的下標距圓弧 6.7pt，因此會被截掉（CF_C2 有 4 條墨跡被裁到）。

## 反事實實驗（只在記憶體中執行，未寫入任何檔案、DB 或 notes）

| 實驗 | 進階題12 結果 | 37 題副作用 |
|---|---|---|
| CF_F 只排除頁面裝飾 | 無候選（`text_says_figure_but_no_clear…`） | — |
| CF_A 只修題號起點 | 起點 586.9；仍是頁尾 9pt 細條 | 0 列改變 |
| CF_B 修起點並排除裝飾 | 無候選（半圓卡在尺寸門檻） | 只有本題由 needs_review 變為 rejected |
| CF_C 在 B 之上加入原型墨跡聚類 | `[426.7, 588.0, 524.4, 652.1]`，31 個成員，包含全部墨跡，0 條被截斷，位於上一輪建議框內；現行 Gate 判 `needs_review`（R4） | — |
| Unit 3/4 共 6 個人工區域套用原型聚類 | 6 個候選全部落在人工框內；Unit 4 的 IoU 為 0.947–0.985，Unit 3 為 0.53–0.71（差異來自人工框的留白） | — |

`X_counterfactual_prototype_cluster_crop.png` 只是反事實結果，**不是 Pipeline 產物，也沒有核准**。
