# Phase 5A：Pilot Readiness / Teacher QA Checklist

## 目的與範圍

本文件用於 **B4 Chapter 1 deterministic adaptive runtime** 進入小規模教師 QA 與學生 pilot 前的操作準備。  
本階段重點為：營運可用性、課堂可操作性、觀測與安全檢查。  
本階段 **不** 擴張 generator coverage、**不** 新增 problem type、**不** 改 adaptive 核心策略。

---

## 1) 系統啟動檢查清單

- [ ] **Python 版本確認**：使用專案指定 Python（建議與 Phase 4F 回歸環境一致）。  
- [ ] **虛擬環境 / 依賴狀態**：確認 `venv` 或等價環境已啟用，必要套件可 import。  
- [ ] **App 啟動指令可執行**：例如 `python app.py`（或專案既定啟動方式）。  
- [ ] **本機網址可開啟**：確認預期 local URL（例如 `http://127.0.0.1:5000`）可存取。  
- [ ] **DB 連線檢查**：啟動後無 DB 連線錯誤、核心頁面可正常查詢。  
- [ ] **Schema / migration 檢查**（若適用）：資料表存在且欄位相容，無啟動期 schema 例外。

---

## 2) 教師 QA 流程檢查清單

- [ ] 以教師帳號登入成功。  
- [ ] 可進入班級 / 學生相關 dashboard。  
- [ ] 可進入 B4 Chapter 1 練習或 adaptive 入口。  
- [ ] 題目正常顯示（文字、必要欄位、版面未崩）。  
- [ ] 可提交答案。  
- [ ] 可看到作答結果 / 回饋。  
- [ ] 若介面可見，確認 audit / debug 欄位可檢視（或後端 log 可查）。

---

## 3) 學生 pilot 流程檢查清單

- [ ] 以學生帳號登入成功。  
- [ ] 可進入 B4 Chapter 1 adaptive 練習。  
- [ ] 可取得 generator-backed deterministic 題目。  
- [ ] 正確答案提交後流程正常。  
- [ ] 錯誤答案提交後流程正常。  
- [ ] 可順利進到下一題。  
- [ ] 全程未出現 manual_review / unavailable 題型內容。

---

## 4) B4 adaptive 安全檢查清單

- [ ] Allowlist 已生效（僅允許 B4 Chapter 1 deterministic adaptive skill 範圍）。  
- [ ] 下列排除題型未出現在 deterministic adaptive：
  - [ ] `binomial_expansion_basic`
  - [ ] `tree_diagram_listing`
  - [ ] `pascal_triangle_derivation`
- [ ] 可檢查 `adaptive_audit`（或等價欄位）。  
- [ ] 可檢查 `b4_deterministic_catalog_audit`（適用路徑時）。  
- [ ] 可觀測 `generator_first` / `generator_fallback` 行為（透過回應或 log）。

---

## 5) 資料蒐集檢查清單

- [ ] **記錄了哪些 logs**：啟動、路由、題目來源、錯誤事件、adaptive audit。  
- [ ] **儲存了哪些學生識別資訊**：如 user id / username（依實作）。  
- [ ] **儲存了哪些作答紀錄**：題目、答案、對錯、時間等欄位。  
- [ ] **是否儲存截圖 / 圖像**：若有 image 上傳、圖像題或視覺輔助，需確認儲存範圍。  
- [ ] **是否儲存 AI 聊天紀錄**：若啟用對話輔助，需確認存放位置與可追溯性。  
- [ ] **報告前匿名化要求**：輸出教師報告前移除可識別個資（帳號、姓名、班級代碼、裝置識別）。

---

## 6) 教師課堂觀察表（簡版）

> 建議每位學生或每組操作填 1 份。

- [ ] 學生可自行開始練習（不需大量口頭協助）。  
- [ ] 題目敘述可理解。  
- [ ] 作答格式說明清楚。  
- [ ] 系統回應速度可接受。  
- [ ] 回饋內容對學生有幫助。  
- [ ] 題目重複感：過於相似 / 可接受（請註記）。  
- [ ] 技能名稱或介面文字是否有令人困惑之處。  
- [ ] 是否出現 route failure / `404` / `500`。  
- [ ] 是否出現明顯誤判（正確答案被判錯）。  

**補充紀錄欄：**
- 班級 / 時段：
- 學生代號（匿名）：
- 問題截圖或時間點：
- 教師備註：

---

## 7) Pilot 範圍建議

- 建議首批規模：**3–5 位學生**。  
- 建議時長：先做 **一節短時段**。  
- 建議單元：**僅 B4 Chapter 1**。  
- 建議模式：**deterministic adaptive only**。  
- 不建議在本 pilot 啟用：experimental free-response / AI-judged 路徑。

---

## 8) 已知限制

- frontend smoke 目前為 lightweight，非完整 browser 自動化 QA。  
- 仍有 dependency / model 初始化 warnings，但 Phase 4F 回歸已確認非阻斷。  
- Advanced RAG / 模型載入可能拖慢部分測試時間。  
- pilot 仍需教師現場觀察，不可只依賴自動化結果。  
- 目前 adaptive 驗證範圍是 **B4 Chapter 1 deterministic pool**，非所有 B4 章節。

---

## 9) Go / No-Go 準則

### Go（可進 pilot）若全部成立

- [ ] App 可正常啟動。  
- [ ] 教師與學生登入正常。  
- [ ] B4 adaptive 題目可載入。  
- [ ] 作答提交流程正常。  
- [ ] 排除題型未出現。  
- [ ] 無阻斷性 `500` 錯誤。  
- [ ] logs / audit 可檢查、可追溯。

### No-Go（暫停 pilot）若任一成立

- [ ] App 無法啟動。  
- [ ] DB 錯誤阻斷練習流程。  
- [ ] adaptive 路徑反覆出現 `404` / `500`。  
- [ ] deterministic adaptive 出現 manual_review 題型。  
- [ ] 正確答案反覆被誤判。  
- [ ] 學生資料記錄範圍不清楚或無法稽核。

---

## 10) 下一階段建議

- 建議進入 **Phase 5B：Limited Pilot Smoke Run**。  
- 下一階段重點應是現場流程驗證與風險收斂。  
- **不是** generator expansion。  
- **不是** adaptive core redesign。

---

## B) 輕量 smoke 指令區（建議）

### Phase 4F 已通過參考指令

```powershell
python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py
python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py tests/test_phase4f_main_c_adaptive_v2_allowlist.py tests/test_phase4f_main_b_adaptive_e2e_smoke.py tests/test_phase4f_main_a_adaptive_generator_first.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py
```

### 建議 pre-pilot 最小檢查指令

```powershell
python -m pytest -q tests/test_phase4f_main_d_real_smoke_retry_alignment.py tests/test_phase4f_main_c_adaptive_v2_allowlist.py
python -m pytest -q tests/test_phase4f_main_b_adaptive_e2e_smoke.py tests/test_phase4f_main_a_adaptive_generator_first.py
```

> 若時間允許，建議再跑完整 Phase 4F 組合回歸。
