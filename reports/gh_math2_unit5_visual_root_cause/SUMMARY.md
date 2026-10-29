# 普高數學2 Unit 5 進階題12：PDF 圖像對位調查

證據性質：**new_isolated_readonly_trace**；原始任務證據：**original_evidence_unavailable**。所有結論都以權威 PDF（SHA-256 `e24c72f8…ec166`）直接呼叫現行偵測函式重跑；重跑結果與上一輪記錄的 `visual_bbox`、`visual_reason` 逐位一致。教師提供的截圖沒有被當作任何證據。

## 一句話結論

系統找不到這張圖，是因為**題目起點 y 被定位到小題(2)**（y=678.2，題號「12」實際在 y=586.9），整張半圓圖落在題目區域之外。區域內唯一的候選是頁尾裝飾帶，裁成 9pt 空白細條後，被 Gate 正確拒收。這是**共用演算法缺陷**，不是單題特例，也不是教材歧義。

## 要點

- **Root cause**：共有四層缺陷疊加，詳見 [root_cause_analysis.md](root_cause_analysis.md)。
  - R1 起點取「最長命中片語」：PDF 文字層把下標排成 `AAAA1234`、省略號變成 `f`，所以第一句比對不到。
  - R2 超出頁框的頁尾帶沒有被當成頁面裝飾排除。
  - R3 只用單一路徑量圖形尺寸：半圓高 39.7pt，差 0.3pt 未達門檻；點和標籤字形都不計入。
  - R4 Acceptance 的尺寸規則會把完整的小圖也送審。
- **頁面對位正確**（第 16 頁，0.99）。裁切、關聯和 Stage 1 Gate 都依設計運作；錯誤發生在題目區域的起點與候選篩選。
- **系統是否產生圖片資產**：否。分類在裁切前就被跳過，沒有暫存 PNG，也沒有正式 PNG。
- **共用問題的證據**：
  - 14 份普高 PDF 都有頁尾帶伸入頁內最後一題區域的頁面。
  - Unit 3/4 已累積 6 個人工座標，全部是同類小型線條圖。
  - 原型「墨跡連通塊」演算法在這 6 張圖與本題上，都產生落在人工框內的完整候選。
- **是否需要教師判斷**：圖形歸屬沒有歧義。修復後，教師只需確認系統產出的裁切是否完整，不需要提供座標。
- **最小修復**：見 [proposed_fix.md](proposed_fix.md)。P1 用題號標記定位起點；P2 排除頁面裝飾；P3 以連通塊量尺寸，門檻不降；P4 以完整度取代尺寸送審，其中方案 A／B 需要您決定。

## 產物分類

| 類別 | 檔案或狀態 |
|---|---|
| SOURCE_PDF_IMAGE | [A_source_pdf_page16.png](A_source_pdf_page16.png)（直接 render 權威 PDF） |
| PIPELINE_CANDIDATE | [疊圖](B_pipeline_candidate_overlay_page16.png)、[候選裁切](B_pipeline_candidate_crop_render.png)（本調查依 Pipeline bbox 渲染；Pipeline 本身未寫檔） |
| PIPELINE_GENERATED_ASSET | **NOT_GENERATED** |
| ISOLATED_RENDER_PREVIEW | **NOT_PERFORMED**（本輪未授權隔離關聯） |
| PRODUCTION_DB_ASSET | **NONE**：正式 DB 的 Unit 5 共 28 列，image_assets 合計 0；正式資產目錄 `ch_unknown_單元5_組合` 是空的 |
| COUNTERFACTUAL_ONLY | [X_counterfactual_prototype_cluster_crop.png](X_counterfactual_prototype_cluster_crop.png)（記憶體實驗，非 Pipeline 輸出，未核准） |

對照頁：[visual_comparison.html](visual_comparison.html)、[visual_comparison.png](visual_comparison.png)。逐步追蹤：[visual_pipeline_trace.json](visual_pipeline_trace.json)。候選與評分：[candidate_regions.json](candidate_regions.json)。

## 安全與界線

- **正式 DB 零變更**：以唯讀連線計算 `textbook_examples` 全表（5017 列）內容指紋，前後一致。
- 沒有修改核心程式、Production 設定、正式圖片資產或 `stage1_verified_visual_regions.json`；沒有寫入 verified region，沒有匯入、Promotion、Publish，沒有重啟 Flask 或 Cloudflare，沒有 commit 或 push。
- 新增檔案只在本目錄內：兩支唯讀腳本（`trace_visual_root_cause.py`、`build_comparison.py`）及其輸出。`core/textbook_stage1_auto_review.py` 的工作樹變動來自上一輪修復，本輪沒有編輯。
- Stage 1 維持 **BLOCKED**（`required_figure_missing`）。下一步需要您授權修復，並決定 P4 採方案 A 或 B。
