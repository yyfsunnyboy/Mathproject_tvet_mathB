# B2 第二章 2-1 題目來源盤點（唯讀 dry-run）

- 原始來源：`textbook_import\source\vocational\math_B2\第二章 2-1 正弦定理與餘弦定理-課本.docx`
- 現有 parser：`phase1_extract_docx_lines`、`phase2_deterministic_block_slice`；題型沿用 `source_type` / `infer_source_type_from_label`。
- Phase 2 的 skill 查詢、解析及持久化呼叫只在本次程序記憶體內攔截；未開啟 DB。skill 因此標為 unresolved。
- paragraph index 為 Word 結構解析器的 0-based 編號；題塊 span 由現有 21 個 anchor 對照原檔逐一核定。

## 統計

- `textbook_example`：5
- `in_class_practice`：5
- `self_assessment`：0
- `exam_practice`：1
- `textbook_exercise`：8
- `advanced_exercise`：2
- target total：11；non-target total：10
- target formulas：67；MathType OLE：62；Word EQ：5；OMML：0；failed now：0
- non-target formulas（所有 target 題塊以外，含課文／推導及 non-target 題塊）：123；MathType OLE：123；Word EQ：0；OMML：0；failed now：0。當中 non-target 題塊 47 式、非題目區域 76 式。
- target independent images：5
- WOULD_WRITE：YES 11；BLOCKED_FORMULA 0；NO 10

## 全部已辨識題塊與 WOULD_WRITE

| # | source_type | label | 題目開頭 80 字 | paragraph 0-based | table | target | reason | formulas | failed | images | skill / section | WOULD_WRITE |
|---:|---|---|---|---|---|---|---|---:|---:|---:|---|---|
| 1 | textbook_example | 例1 | 在△ABC中，已知、且，試求△ABC的面積。 | 21-23 | table 2 row 0 col 0 | True | allowed source_type | 9 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 2 | in_class_practice | 隨堂練習1 | 在△ABC中，已知、且，試求△ABC的面積。 | 25-26 | table 3 row 0 col 0 | True | allowed source_type | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 3 | textbook_example | 例2 | 在△ABC中，若，，且，試求a及其外接圓半徑R。 | 59-64 | table 5 row 0 col 0 | True | allowed source_type | 7 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 4 | in_class_practice | 隨堂練習2 | 在△ABC中，若，，且，試求c及其外接圓半徑R。 | 69-70 | table 6 row 0 col 0 | True | allowed source_type | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 5 | textbook_example | 例3 | △ABC中，已知，，，試求。 | 73-79 | table 7 row 0 col 0 | True | allowed source_type | 13 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 6 | in_class_practice | 隨堂練習3 | △ABC中，已知，，，試求。 | 81-82 | table 8 row 0 col 0 | True | allowed source_type | 4 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 7 | textbook_example | 例4 | 在△ABC中，已知、且，試求a之長。 | 117-124 | table 10 row 0 col 0 | True | allowed source_type | 11 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 8 | in_class_practice | 隨堂練習4 | 在△ABC中，已知、且，試求a之長。 | 126-127 | table 10 row 1 col 0 | True | allowed source_type | 3 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 9 | textbook_example | 例5 | 設△ABC的三邊長、、，試求。 | 130-135 | table 11 row 0 col 0 | True | allowed source_type | 8 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 10 | in_class_practice | 隨堂練習5 | 設△ABC的三邊長、、，試求。 | 137-138 | table 11 row 1 col 0 | True | allowed source_type | 4 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 11 | exam_practice | 113統測B | 小仲規劃從A地直線出發到C地，但AC路段在重鋪馬路， 無法通行，只好先繞到B地再到C地。已知AC路段的直 線距離為300 公尺，AB路段的直線距離為800 公尺 | 142-151 | body paragraph | True | allowed source_type | 2 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | YES |
| 12 | textbook_exercise | 2-1習題 基礎題 1 | 設表示△ABC的面積，a、b和c分別表示、和之對邊長，且R為其外接圓半徑，則 (1) 。 (2) 。 (3) 。 (4) ， ，。 (5) ， ，。 | 159-164 | body paragraph | False | source_type outside four allowed types | 16 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 13 | textbook_exercise | 2-1習題 基礎題 2 | 在△ABC中，已知、且，試求△ABC的面積。 | 166-166 | body paragraph | False | source_type outside four allowed types | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 14 | textbook_exercise | 2-1習題 基礎題 3 | 在△ABC中，已知、，且，試求a及其外接圓半徑R。 | 168-168 | body paragraph | False | source_type outside four allowed types | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 15 | textbook_exercise | 2-1習題 基礎題 4 | 在△ABC中，已知、，且，試求。 | 170-170 | body paragraph | False | source_type outside four allowed types | 4 | 0 | 1 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 16 | textbook_exercise | 2-1習題 基礎題 5 | 在△ABC中，若、，且，試求。 | 172-172 | body paragraph | False | source_type outside four allowed types | 4 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 17 | textbook_exercise | 2-1習題 基礎題 6 | 設△ABC的三邊長、、，試求。 | 174-174 | body paragraph | False | source_type outside four allowed types | 4 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 18 | textbook_exercise | 2-1習題 基礎題 7 | 設△ABC的三邊長、、，試求。 | 176-176 | body paragraph | False | source_type outside four allowed types | 4 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 19 | textbook_exercise | 2-1習題 基礎題 8 | 設△ABC中，a、b、c為三邊長，若，試求。 （提示：將式子左式化成） | 178-178 | body paragraph | False | source_type outside four allowed types | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 20 | advanced_exercise | 2-1習題 進階題 9 | 如圖，國外某一湖泊，建商想在湖泊旁蓋A、B兩棟度假飯店，今在湖之遠處C點，測得公里、公里，且，試求A、B兩棟飯店的直線距離。 | 182-182 | body paragraph | False | source_type outside four allowed types | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |
| 21 | advanced_exercise | 2-1習題 進階題 10 | 歐洲某大城市為提升旅遊品質吸引遊客到訪，決定在A、B、C三大觀光景點等距離的地方，設置免費的Wi−Fi基地臺，已知三景點間的距離為公尺、公尺、公尺，則基地臺與三 | 184-184 | body paragraph | False | source_type outside four allowed types | 3 | 0 | 0 | unresolved (DB bypassed) / 2-1 正弦定理與餘弦定理 | NO |

## 圖片（僅 target 題塊）

| question # | source_type | label | paragraph 0-based | table position | image | rel id | MathType preview | 可能必要 |
|---:|---|---|---:|---|---|---|---|---|
| 1 | textbook_example | 例1 | 22 | table 2 row 0 col 0 | image21.jpeg | rId50 | NO | YES |
| 3 | textbook_example | 例2 | 62 | table 5 row 1 col 0 | image53.jpeg | rId112 | NO | 需人工核對 |
| 8 | in_class_practice | 隨堂練習4 | 127 | table 10 row 1 col 0 | image102.jpeg | rId209 | NO | YES |
| 10 | in_class_practice | 隨堂練習5 | 137 | table 11 row 1 col 0 | image109.jpeg | rId225 | NO | 需人工核對 |
| 11 | exam_practice | 113統測B | 146 | body paragraph | image117.jpeg | rId240 | NO | YES |

## 公式失敗

目前命令列環境唯讀解碼的 target failure：0。

## 重要異常與限制

- 原始 DOCX 直接跑 Phase 1 時，MathType 公式在題目文字中消失（例如「已知、且」）；本報告只用結構位置盤點，不代表題幹可直接寫入。
- 現存 `_Latex.docx` 有 185 個 `[MATH_PARSE_FAILED_n]`；本次目前 Python 環境可唯讀解析全部 185 個 OLE。WOULD_WRITE 依本次唯讀診斷推算，不代表現有 importer 可通過 gate。
- 例題解答與題幹共用表格；span 含解答。image53.jpeg 位於例2解答段落，image109.jpeg 位於隨堂練習5標題段落，是否為題目必要圖片需人工核圖；其餘三張位於題幹段落。
- 自我評量通常是獨立來源文件；這份 2-1 課本 DOCX 沒有辨識到自我評量。
- 既有 Phase 2 會呼叫 skill 解析與持久化；本次已在記憶體攔截，所以 skill 欄無法確認正式綁定。
- 沒有修改 production code、教材 importer、DB、skill 或圖片資產；沒有 commit/push。
