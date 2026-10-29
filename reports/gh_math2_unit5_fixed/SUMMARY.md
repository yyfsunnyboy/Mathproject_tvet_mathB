# 普高數學2 Unit 5「組合」習題進階題12 — 停損處理（固定題庫 Fallback）

- 範圍：`general_2_section_advanced_exercise_012_037`（DOCX block 36、PDF 第 16 頁），`gh_Combination`
- 結論：**採用固定題庫方案**。P1–P4 共用演算法未實作，依停損指示不再開發；圖片改走既有「人工核准 verified region」流程，作答走既有 `fixed_textbook_practice` graded。
- 狀態：隔離驗證全部 PASS；**待教師確認預覽**後，才進行正式寫入（需另行授權）。

## 做法（全部沿用既有機制）

| 項目 | 機制 | 產物 |
|---|---|---|
| 半圓圖 | Stage 1 既有 `configs/stage1_verified_visual_regions.json` 人工核准區域（staged，未寫入 live） | `staged_visual_region.json`（bbox `[425.0,586.5,526.0,653.5]`，`pending_teacher_confirmation`） |
| 答案 oracle | 由權威 PDF 向量圖取 10 點座標，列舉 45 組點對／120 組三點 | `derive_fixed_oracles.py`、`fixed_oracles.json`（直線 40 →③，三角形 116） |
| 固定題 | `fixed_textbook_practice` graded、multi_part（(1) `choice_label_checker`、(2) `integer_checker`），以題幹 SHA-256 綁定 | `build_fixed_config.py`、`staged_fixed_entries.json` |
| 隔離 Stage 1 | 正式 DB 唯讀備份 → sandbox 重建 Unit 5 | `rehearse_unit5_fixed.py`、`rehearsal_result.json` |
| 學生端 | Flask test client（pytest 隔離 DB＋暫存設定合併） | `tests/test_gh_unit5_fixed_advanced12.py` |
| 教師預覽 | 原始 PDF 對照＋系統裁切圖＋題幹＋答案解析＋來源 | `teacher_preview.html`、`teacher_preview.png` |

parts 不含 `expected_answer`（answer_contract 會在作答前送到瀏覽器），答案只存在伺服器端 `answer` dict。

## 唯一程式修改（最小擴充）

`core/routes/practice.py` fixed graded 分支：`answer` 為 dict 時保留 dict（multi_part 依 part key 取值），其他維持 `str(...)`。
原本 `str(dict)` 會讓 multi_part checker 取不到各小題答案，正解也被判錯。現有 6 個 live 條目的 answer 都是字串，行為不變。

## 驗證結果

| 檢查 | 結果 |
|---|---|
| Stage 1 Gate（隔離，以 `evaluate_stage1_gate` 重新評估） | READY，37 題，blocked 0，needs_review 0 |
| 進階題12 圖片 | `VISUAL_ATTACHED`、accepted、`manual_page_region`、anchor／頁碼／bbox 正確，A1–A4、B1–B6 完整 |
| 其餘 36 題 | 內容／Skill／anchor／圖片狀態與上一輪 replay 零差異 |
| 題幹／Skill／解析 | 與上一輪 replay 一致；題幹含完整 (1)(2) 與 ①–⑤ |
| 學生端（Unit 5，13 項） | PASS：出題含半圓圖、送出前無答案洩漏；③／3／40＋116 判對；錯答與缺答判錯；錯答寫入作答與錯題紀錄；37 題中只有本題是固定題；非 Generator（`no_generator_serve_textbook_example`） |
| 回歸：Unit 4／Unit 2／Unit 3 固定題 | 9＋27 項 PASS |
| 正式 DB／live 設定 | 零變更（SHA 比對）；`configs/` 未修改 |

註：同一列教材題的 `question_uid` 固定，已答對後重送相同答案會被既有重複提交保護略過紀錄，這是現行規則。

## 尚需授權（依序）

1. 教師確認 `teacher_preview.html`：裁切圖、題幹、答案 ③／116 與解析。
2. 將 staged region 寫入 `configs/stage1_verified_visual_regions.json`，並填 `verified_by`／`verified_on`。
3. 正式 Unit 5 匯入／取代（備份＋transaction；Gate 應為 READY）。
4. 以正式 DB 執行 `build_fixed_config.merge_into_live(released_db)`：依 anchor 重新綁定正式 row id，再合併到 `configs/fixed_textbook_practice.json`。
5. Flask 需重啟一次才會載入 `practice.py` 的修改（本輪未重啟）。

未執行：正式 DB 寫入、verified region 寫入、Promotion／Publish、服務重啟、commit／push。
