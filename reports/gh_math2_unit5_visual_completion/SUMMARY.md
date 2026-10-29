# 普高數學2 Unit 5 全單元圖片缺失檢查與集中修復 — 結案（隔離驗證）

結論：37 題中只有 1 題真正需要圖片：`5習題 進階題12`（PDF 第 16 頁的半圓 10 點圖）。

- 正式 DB 目前沒有這張圖。
- 隔離環境已補齊，並用真實學生練習頁驗證通過。
- 正式寫入尚待教師授權；變更清單、備份與回滾見 `FORMAL_WRITE_PLAN.md`。

## 八題回答

1. **37 題中需要圖片的題數：1 題（進階題12）。**
   - 另有 6 題的頁面有裝飾插圖或「解」內示意圖，但題幹沒有引用，不需要附圖：例題1、例題2、隨堂練習3、例題5（解內袋中取球圖）、例題7、例題10。
   - DOCX 共有 12 張非公式圖片，其中只有第 265 段屬於題幹（進階題12）。另有 131 個 MathType OLE 物件，都是公式，不當作圖片匯入。
2. **正式 DB 已有圖片：0 題。**
   - 正式 DB 的 Unit 5 仍是舊版匯入：28 列（1413–1440），全部沒有 anchor，也沒有 `image_assets`。
   - 舊列 1440（進階題12）的題幹寫「如圖」，但沒有附圖。
3. **缺圖的真正原因：**
   - 學生目前看到的是舊版 28 列，舊版匯入本來就沒有 PDF 圖片資產。
   - 新版 37 題匯入在 Stage 1 被 `required_figure_missing` 擋下，從未正式寫入。被擋的原因是自動偵測漏抓這張小型半圓向量圖。
   - 這不是前端顯示問題。
4. **前端顯示問題 0 題；未匯入 1 題。**
   - 前端可以顯示這張圖：學生頁、管理列表與編輯頁在有資產時都能正確顯示。
5. **隔離修復：1 題。**
   - 修法是人工核准裁切區域（verified region，屬於固定圖片資產，不是固定題庫），由既有匯入流程產生圖片。
   - 作答改用既有 `fixed_textbook_practice` 的 graded multi_part：(1) ③、(2) 116。
   - 其餘 36 題維持動態或原流程，不轉成固定題庫。
6. **需要教師確認：只有進階題12的裁切圖**（`pending_teacher_confirmation`）。沒有其他待確認圖片。
7. **真實學生頁檢查：PASS。**
   - 測試環境：隔離 SQLite 複本＋獨立 Flask 實例（127.0.0.1:5057），已關閉；正式 5000／5001 未動。
   - 進階題12 顯示完整的 A1–A4、B1–B6 半圓圖；送出 40＋116 顯示「答對了」；送出 45＋116 顯示「(1) 錯誤、(2) 正確」。
   - 例題2 等無圖題正確地沒有圖片。
   - 管理列表 37 列中只有 1 個「有附圖」標記；編輯視窗的附圖可正常載入（288×194）。
   - 截圖存放在 `screenshots/`。
8. **可以進入 GenCode V3 嗎？還不行。**
   - 前提是 Unit 5 的 Stage 1 正式封板，也就是 `FORMAL_WRITE_PLAN.md` 的步驟 1–5。
   - 教師確認裁切並授權正式寫入、重啟 Flask 後，Gate 應為 READY（隔離演練為 READY、blocked 0），才符合進入 GenCode V3 的條件。

## 驗證證據

| 檢查 | 結果 | 檔案 |
|---|---|---|
| 逐題盤點（PDF 逐頁＋DOCX＋DB） | 37 題，需要圖片 1 題 | `unit5_visual_inventory.md` / `.json`、`scan_raw.json`、`pages/` |
| HTTP 全 37 題（學生登入→出題） | 題幹、答案與 Stage 1 一致；只有 12834 帶圖，圖片 HTTP 200、PNG、SHA 相符；問題 0 | `isolated_http_result.json` |
| 判分 | 4 組答案（③／3＋116 判對；④＋116、③＋120 判錯）全部符合預期 | 同上 |
| Unit 5 以外的列（4989 列）與 Unit 4（38 列） | 與正式 DB 摘要相同 | 同上 |
| 真實瀏覽器（學生頁、管理列表、編輯視窗） | PASS | `screenshots/01–06` |
| pytest `tests/test_gh_unit5_fixed_advanced12.py` | 15 PASS（新增「整單元只有進階題12帶圖」測試） | — |
| 正式 DB 前後快照 | 零變更（`zero_change: true`） | `formal_db_snapshot.json` |

## 觀察（非 Unit 5 專屬）

送出答案、出現回饋後，畫布背景圖會隨版面縮小，但圖仍完整。這是共用畫布的行為，本輪沒有修改。

## 本輪未執行

- 正式 DB 寫入、正式圖片設定修改、Promotion／Publish
- 重啟 Flask／Cloudflare、commit／push
- 修改 PDF Visual 辨識演算法、修改題目數學內容

## 本輪新增檔案

- `reports/gh_math2_unit5_visual_completion/`：
  - 腳本：`scan_unit5_visuals.py`、`inventory_formal_db.py`、`isolated_server.py`、`verify_isolated_http.py`、`formal_snapshot.py`、`build_inventory.py`
  - 產出：報告、`pages/`、`screenshots/`
  - 隔離資料：`isolated/`（DB 複本與合併設定）
- `tests/test_gh_unit5_fixed_advanced12.py`：新增 1 個測試
