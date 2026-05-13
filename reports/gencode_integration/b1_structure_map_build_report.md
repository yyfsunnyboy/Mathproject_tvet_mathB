# B1 Phase 3A-1E：教材結構地圖對齊機制報告

## 1. 教材結構 YAML (B1 Structure Map)
已建立權威章節結構 YAML：`configs/textbook_structure/longteng_數學B1_structure.v0.1.yaml`。

### 解析結果 (TOC)
- **Chapter 1: 坐標系與函數圖形**
  - 1-1 數線與絕對值
  - 1-2 平面坐標系與線型函數
  - 1-3 二次函數
  - 1-4 一元二次不等式
  - 1-review 自我評量
- **Chapter 2: 直線方程式**
  - 2-1 斜率
  - 2-2 直線方程式
  - 2-3 直線的一般式與點到直線的距離
  - 2-review 自我評量
- **Chapter 3: 式的運算**
  - 3-1 多項式的基本概念與四則運算
  - 3-2 除法原理與餘式定理
  - 3-3 因式分解與分式
  - 3-review 自我評量

## 2. 結構解析模組 (textbook_structure_parser.py)
新增 `core/textbook_structure_parser.py`，負責：
- 載入 YAML 設定。
- 建立以 `section_code` (如 1-2) 為鍵的快速查詢表。
- 提供 `chapter_title`, `section_title`, `display_order_base`, `type` 等元數據。

## 3. 匯入對齊機制 (textbook_processor.py)
已修正 `core/textbook_processor.py` 的 `save_to_database` 邏輯：
- **優先權**: Structure YAML > 檔名解析 (Filename Meta) > AI 解析結果。
- **對齊對象**: 技高數學 B 系列所有冊別。
- **自動標記**: 
    - 「自我評量」檔案自動標記 `problem_type` 為 `chapter_review`。
    - 若檔名代碼 (如 1-5) 在 YAML 中找不到，自動標記所有例題為 `needs_review: True`。
- **ID 前綴修正**: 統一 B1-B4 使用 `vh_數學BN_` 前綴，廢止 `vh_mathBN_`。

## 4. 檔名 parser 的對齊規則
| 檔名特徵 | 對應 Action | 備註 |
|---|---|---|
| 第一章 1-1... | 查 YAML 1-1 | 獲取標準標題與排序 |
| 第一章 自我評量 | 查 YAML 1-review | 標記為 chapter_review |
| 無代碼檔名 | Fallback to Filename Meta | 維持原本檔名解析邏輯 |
| YAML 查無代碼 | needs_review = True | 觸發人工審核 |

## 5. B1 已匯入資料處理建議
### 重新對齊需求
- **B1 1-1**: 已匯入，標題與排序基本正確，但若要套用 `chapter_review` 標籤，建議刪除後重新匯入「自我評量」檔案。
- **B1 1-2**: 已匯入，建議刪除後重新匯入，以套用 YAML 定義的標準章節標題「1 坐標系與函數圖形」與「2 平面坐標系與線型函數」。

## 6. 下一步建議
1. **執行 B1 1-2 重新匯入**: 驗證 YAML 對齊機制。
2. **建立 B2-B4 的 Structure YAML**: 沿用此框架擴展其他冊別。
3. **前端 UI 同步**: 確保管理後台能識別 `chapter_review` 型別並進行特殊標示。

---
**核對人**: Antigravity AI
**日期**: 2026-05-13
