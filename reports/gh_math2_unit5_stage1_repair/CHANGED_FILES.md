# Changed files and diff summary

- `core/textbook_stage1_auto_review.py`：新增短數學題的中文字加公式 token 比對；在有限鄰近頁或相鄰 anchor 頁碼範圍內尋找唯一內容匹配，記錄頁碼校正證據。正式 PDF fidelity Gate 保持啟用。
- `tests/test_textbook_stage1_pdf_fidelity.py`：新增 3 個聚焦案例，覆蓋短題公式誤配、缺頁歧義、錯頁的公式與符號驗證。
- `reports/gh_math2_unit5_stage1_repair/`：隔離 runner、dry-run 原始回傳與 log、Gate／問題明細／37 題綁定／回歸結果、PDF 原始頁與裁切預覽、教師圖像確認資料。報告產生程式只讀來源與隔離結果。

正式程式 diff：1 檔，新增 106 行、刪除 11 行。`git diff --check` 通過。既有 `reports/gh_math2_unit5_stage1_diagnostic/` 保留；正式 DB、正式圖像設定、Unit 4 已發布資料未修改。

工作樹原有的 `reports/import_debug/數學2_unknown_title_inventory_report.md` 與 `templates/admin_prerequisites.html` 變動不屬本輪修改。
