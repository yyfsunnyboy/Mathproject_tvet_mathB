# B1 檔名解析與章節顯示規則修正報告

## 1. 問題描述
在 B1 教材匯入過程中，由於多個小節（如 1-1, 1-2）可能被標記為同一個大章節（如「第一章」），導致前台儀表板顯示了多個編號為「1」的卡片。此外，AI 解析有時無法準確提取檔名中的結構資訊。

## 2. 檔名規則來源
系統現在支援從符合以下模式的教材檔名中解析元數據：
- 一般小節：`第[一|1]章 [1-2] [標題]-課本.docx`
- 自我評量：`第[一|1]章 自我評量-課本.docx`

## 3. 新檔名解析規則
已建立 `core/textbook_filename_parser.py` 模組，提供 `parse_textbook_filename_metadata` 函式：
- **一般小節**：提取 `chapter_index`, `section_code`, `section_index`, `section_title`。
- **自我評量**：`section_code` 設為 `X-review`，`section_index` 設為 `99`，`source_scope` 設為 `chapter_review`。

## 4. 前台章節卡片顯示規則
修改 `app.py` 的 `dashboard` 路由邏輯：
- **動態編號**：針對技高數學 B 系列，優先從 `section` 欄位解析 `X-Y` 模式，取 `Y` 作為卡片編號。
- **複習標記**：若 `section` 包含 `review` 或 `自我評量`，卡片顯示為 `【複習】[標題]`。
- **排序**：依據 `SkillCurriculum.display_order` 排序，該欄位在匯入時已整合 `chapter_index` 與 `section_index`。

## 5. 修改檔案
- `core/textbook_filename_parser.py` [NEW]: 專用檔名解析模組。
- `core/textbook_processor.py` [MODIFY]: 整合解析模組至 `save_to_database` 流程。
- `app.py` [MODIFY]: 優化 `dashboard` 顯示與排序邏輯。

## 6. 修正前後對照
| 檔案範例 | 修正前顯示 | 修正後顯示 | 備註 |
|---|---|---|---|
| 1-1 數線與絕對值 | 1 數線與絕對值 | 1 數線與絕對值 | 維持原樣 |
| 1-2 平面坐標系與函數 | 1 坐標系與函數 | 2 平面坐標系與線型函數 | 成功提取小節索引 2 |

## 7. 自我評量處理方式
自我評量檔案會被解析為 `section_index = 99`，在 DB 中排序於章節末尾。前台卡片會顯示 `【複習】` 前綴或獨立顯示為 `自我評量`。

## 8. B4 影響檢查
B4 教材已匯入且 `section` 欄位符合 `X-Y` 模式（如 1-1, 2-1），新邏輯將自動提取 `Y`。由於 B4 原本的 `chapter` 欄位已包含正確數字（1, 2, 3...），顯示結果將保持一致。

## 9. 下一步建議
1. **重新匯入 B1 1-2**：建議刪除現有 B1 1-2 資料後，使用正確格式的檔名重新匯入，以觸發新的 `display_order` 與 `chapter_title` 生成。
2. **統一 Skill ID**：目前 B1 1-2 存在 `vh_mathB1_` 前綴，建議後續批次更新為 `vh_數學B1_`。

---
**核對人**: Antigravity AI
**日期**: 2026-05-13
