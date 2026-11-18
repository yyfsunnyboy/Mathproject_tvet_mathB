# 第二冊 Unit 9 二維數據分析 — Stage 1 最小修復（2026-11-18）

狀態：隔離重播 READY（26 列／0 blocked／0 needs_review），**等待網頁前端正式重新匯入**；未寫入正式 DB、未 Promotion／Publish。

## 來源

| 檔案 | SHA-256 |
| --- | --- |
| DOCX `單元09-二維數據分析.docx` | `da56a174…`（完整值見匯入紀錄 `9c9b32ac….json`） |
| PDF `632399683e47_單元09-二維數據分析.pdf` | `632399683e47eb6954aa20d9c131deb0cdec4b63109d57239ed6d04d30d6dc4a` |

## 必要圖

| 題目 | 來源 | 說明 |
| --- | --- | --- |
| 例題6 | PDF p16 bbox [120,590,515,666] → `example6_pdf_p16.png` | 選項 ①–④ 四張散布圖（40 個資料點）。DOCX `9-例6-1~4.jpg` 無 ①–④ 編號且點為黑色，故採 PDF；資料表保留在題幹 |
| 9習題 基礎題2 | PDF p22 bbox [170,165,468,268] → `basic2_pdf_p22.png` | A（r=−0.7）、B（r=−0.9）、C 三張散布圖，15 個資料點；未含鄰題或頁尾 |

## 空白作答方格紙（answer_workspace）

四張圖經 PDF 與 DOCX 原圖核對：只有格線、刻度與 x/y 標記，0 個資料點，數據全在題幹表格中。依 DOCX 圖片 SHA-256 登錄於 `configs/stage1_verified_visual_regions.json` 的 `answer_workspaces`，runtime 為手寫畫布，不作題目必要圖。

| 題目 | PDF 頁／bbox | DOCX 圖 SHA-256 |
| --- | --- | --- |
| 隨堂練習2 | p8 [376,624,514,746] | `00fe827c…a203da` |
| 隨堂練習3 | p10 [395,122,514,292] | `df3b72c5…c69969` |
| 9習題 基礎題1 | p21 [256,534,381,656] | `3c280928…f63834` |
| 9習題 基礎題3 | p22 [256,476,381,598] | `3c280928…f63834`（與基礎題1 同圖） |

## Skill 對應（`general_數學2_單元9_二維數據分析_stage1_v1`）

簡稱：散布圖＝`gh_ScatterPlot`，相關係數＝`gh_CorrelationCoefficient`，迴歸＝`gh_LeastSquaresMethodAndRegressionLine`。錨點前綴 `general_2_section_`。

| 錨點 | 題目 | 主要 Skill | 其他概念 | 理由 | 複合 | 跨題依賴 |
| --- | --- | --- | --- | --- | --- | --- |
| example_001_001 | 例題1 | 散布圖 | — | 由對照表繪出散布圖 | 否 | 否 |
| in_class_practice_001_002 | 隨堂練習1 | 散布圖 | — | 由散布圖判斷相關 | 否 | 否 |
| example_002_003 | 例題2 | 相關係數 | 散布圖 | 求 r，先畫散布圖 | 是 | 否 |
| in_class_practice_002_004 | 隨堂練習2 | 相關係數 | 散布圖 | 同例題2 | 是 | 否 |
| example_003_005 | 例題3 | 相關係數 | 散布圖 | 求 r，先畫散布圖 | 是 | 否 |
| in_class_practice_003_006 | 隨堂練習3 | 相關係數 | 散布圖 | 同例題3 | 是 | 否 |
| in_class_practice_004_007 | 隨堂練習4 | 相關係數 | 散布圖 | 由散布圖排序相關係數大小 | 是 | 否 |
| example_004_008 | 例題4 | 迴歸 | — | 由統計量求迴歸直線，答 \(y=-\tfrac43x+17\) | 否 | 否 |
| in_class_practice_005_009 | 隨堂練習5 | 迴歸 | 相關係數 | 由迴歸斜率反求 \(r=\tfrac5{12}\) | 是 | 否 |
| example_005_010 | 例題5 | 迴歸 | — | 由數據求迴歸直線並預測 | 否 | 否 |
| in_class_practice_006_011 | 隨堂練習6 | 迴歸 | — | 同例題5 | 否 | 否 |
| example_006_012 | 例題6 | 迴歸 | 散布圖 | (1) 選散布圖 ①；(2) \(y=3.8x+66.4\)，\(x=26.8\) 得 168 | 是 | 否 |
| in_class_practice_007_013 | 隨堂練習7 | 相關係數 | — | 承例題6 加入 (26,174)，判斷 r 變化（0.9003→0.7522，變小） | 否 | **是：例題6 數據** |
| example_007_014 | 例題7 | 迴歸 | 相關係數 | 以軟體求兩年氣溫的 r 與迴歸直線 | 是 | 否 |
| exercise_001_015 | 9習題 觀念澄清1 | 相關係數 | 散布圖 | 判斷「散布圖點愈多，相關程度愈高」 | 是 | 否 |
| exercise_002_016 | 9習題 觀念澄清2 | 迴歸 | 相關係數 | r 與迴歸斜率同號 | 是 | 否 |
| exercise_003_017 | 9習題 觀念澄清3 | 迴歸 | 相關係數 | 標準差相等時 r 與斜率關係 | 是 | 否 |
| exercise_004_018 | 9習題 觀念澄清4 | 相關係數 | — | \(-1\le r\le1\) | 否 | 否 |
| exercise_005_019 | 9習題 觀念澄清5 | 相關係數 | — | 點全在 \(y=2x-1\) 上時 r 是否為 1 | 否 | 否 |
| exercise_001_020 | 9習題 基礎題1 | 相關係數 | 散布圖 | 繪散布圖，判斷去掉哪筆數據後 r 最大 | 是 | 否 |
| exercise_002_021 | 9習題 基礎題2 | 相關係數 | 散布圖 | 由 A、B 散布圖與 r 推估 C 的 r | 是 | 否 |
| exercise_003_022 | 9習題 基礎題3 | 相關係數 | 散布圖 | 畫散布圖並求 r | 是 | 否 |
| exercise_004_023 | 9習題 基礎題4 | 迴歸 | — | 求迴歸直線並預估需求量 | 否 | 否 |
| exercise_005_024 | 9習題 基礎題5 | 迴歸 | 相關係數 | 由統計量與 \(y=2x+k\) 求 k 及 r | 是 | 否 |
| advanced_exercise_006_025 | 9習題 進階題6 | 迴歸 | 相關係數 | 由平均數、r 與通過點判斷迴歸直線性質 | 是 | 否 |
| advanced_exercise_007_026 | 9習題 進階題7 | 相關係數 | — | 配分線性調整後的 r | 否 | 否 |

主要 Skill 數量：散布圖 2、相關係數 13、迴歸 11。分類依教材段落與題目實際要求，未採用 Gemini 分類，未新增 Skill。

## 隨堂練習與例題連結

依 `question_anchor.source_order` 與「承例題」文字判定，不以題號推算：

| 隨堂練習 | 連結例題 | 證據 |
| --- | --- | --- |
| 隨堂練習1–3 | 例題1–3 | 各緊接對應例題（order 2、4、6） |
| 隨堂練習4 | 例題3 | order 7，位於例題3／隨堂練習3 之後、「相關係數性質」說明後；為性質判讀練習，非例題3 的數值變式 |
| 隨堂練習5 | 例題4 | order 9，緊接例題4（8）；原推斷為例題5 |
| 隨堂練習6 | 例題5 | order 11，緊接例題5（10）；原推斷為例題6 |
| 隨堂練習7 | 例題6 | order 13，題幹「承例題6」；原推斷為例題7 |

隨堂練習7 的 notes 記錄 `source_dependency = {kind: continues_example, example_title: 例題6, requires_example_data: true}`；map 若與題幹「承例題N」衝突，該題改列 needs_review、不覆寫連結。

## MathType

OLE #57（`rId118`，段落 116）與 #63（`rId128`，段落 119）為「乙 相關係數」說明文字中帶 prime 的公式，DSMT6 解析 `list index out of range`。匯入只存題目列，隔離重播的 DB 與產物都不含這兩段文字，因此不影響正式題目頁；登錄於 `KnownIssues_TechnicalDebt.md`，converter 未修改。

## 重播與驗證

- `replay_isolated.py`：sqlite backup 複製正式 DB 到暫存目錄，stub Gemini，套用 Stage 1 Gate；結束時比對正式 DB SHA。
- 結果：`[STAGE1 GATE] status=READY rows=26 blocked=0 needs_review=0`；`[PDF VISUAL] VISUAL_ATTACHED 5, NO_VISUAL_REQUIRED 21`；`[SOURCE SKILL MAP] changed=8 unmapped=[] missing=[]`；MathType ole=205 converted=203 failed=2；`formal_db_unchanged=true`。
- `replay_rows.jsonl`：重播後 26 列的 Skill、連結、依賴、圖片狀態。
