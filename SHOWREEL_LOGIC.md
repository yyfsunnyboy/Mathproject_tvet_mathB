# SHOWREEL_LOGIC

更新日期: 2026-03-24
工作目錄: `D:\Python\Mathproject`

## 1. 這份文件的用途

這份文件用來承接今天對 `Mathproject` 的整合、修正、測試與 showreel/demo 相關決策。
之後若要讓 AI 接手，請先讀這份文件，再讀相關檔案。

本日工作主軸:

1. 將 `D:\Python\MathProject_AST_Research` 的 agent-skill / live_show 能力整合回 `D:\Python\Mathproject`
2. 將 `practice` AI 助教改成以 `qwen3-vl-8b` 為主，並強化國中生教學提示風格
3. 修正 `live_show` 下一題卡死問題
4. 重建缺失的 MCRI evaluator，讓 live_show 的 MCRI 分數不再是假 fallback
5. 整理 demo/showreel 可持續推進的待辦事項

---

## 2. 專案整合總原則

### 2.1 專案角色分工

- `D:\Python\Mathproject`
  - 主平台
  - 主資料庫
  - 既有操作流程與網站宿主

- `D:\Python\MathProject_AST_Research`
  - agent skill 子系統真源
  - live_show / healer / prompt architect / skill policies / research toolkit 真源

### 2.2 最終採用原則

- 平台主體保留 `Mathproject`
- agent skill / live_show / qwen3-vl-8b 推理鏈，採用 `AST_Research` 路線
- `config.py` 不整份覆蓋，採增量整合
- 主資料庫固定使用 `D:\Python\Mathproject\instance\kumon_math.db`
- research 額外 schema 採增量遷移，不用 research DB 蓋主庫

---

## 3. 已完成的整合與修改

### 3.1 Agent Skill / Live Show 主體已搬回主專案

已整合的核心範圍:

- `agent_skills/`
- `templates/live_show.html`
- `core/routes/live_show.py`
- `core/routes/live_show_pipeline.py`
- `core/prompt_architect.py`
- `core/code_generator.py`
- `core/code_utils/live_show_math_utils.py`
- `core/healers/live_show_healer.py`
- `core/skill_policies/`
- `agent_tools/`
- 多組 `live_show` regression tests

已刪除主專案中分裂的舊 radical skills:

- `agent_skills/jh_數學2上_RadicalSimplify`
- `agent_skills/jh_數學2上_RadicalMultiply`
- `agent_skills/jh_數學2上_RadicalAddSub`

保留由 research 版主導的:

- `agent_skills/jh_數學2上_FourOperationsOfRadicals`

### 3.2 資料庫策略

主資料庫:

- `D:\Python\Mathproject\instance\kumon_math.db`

已採用策略:

- 保留主庫
- 補 research 真正需要、且會寫入主庫的欄位
- 不把 research-only 即時實驗表整套塞回主庫

已確認不進主庫的 research-only 表:

- `ablation_summary`
- `execution_samples`
- `experiment_runs`
- `evaluation_items`
- `healer_events`

原因:

- 這些會寫到另外即時建立的 DB
- 不應污染主平台正式資料庫

### 3.3 config 與模型整合

原則:

- 保留 `Mathproject` 原本所有模型設定
- 不刪舊 model
- 新增 `qwen3-vl-8b`
- 之後可手動註解或切換，不強迫單一路線

目前關鍵設定位置:

- `config.py`
  - `DEFAULT_CODER_PRESET`
  - `MODEL_ROLES['coder']`
  - `MODEL_ROLES['vision_analyzer']`
  - `MODEL_ROLES['tutor']`

目前已採設定:

- `coder`: `qwen3-vl-8b`
- `vision_analyzer`: `qwen3-vl-8b`
- `tutor`: `qwen3-vl-8b`

舊 tutor 路線仍保留註解，方便改回。

### 3.4 practice AI 助教已改為 qwen3-vl-8b 主路徑

修改方向:

- `practice` AI 助教原本偏 Gemini 路線
- 目前已改成優先走 `get_ai_client(role='tutor')`
- `tutor` 角色綁 `qwen3-vl-8b`
- 舊 Gemini 流程保留作 fallback

主要修改檔案:

- `core/ai_analyzer.py`
- `config.py`

### 3.5 practice 頁面標題會顯示目前 tutor model 名稱

效果:

- `practice` 左上 AI 助教標題會顯示目前 model 名稱

主要修改檔案:

- `core/routes/practice.py`
- `templates/index.html`

### 3.6 practice 助教提示辭已改成國中生教學模式

目標:

- 一律繁體中文
- 國中生可懂
- 短、清楚
- 只能提示，不可直接講答案
- 對象是「會考 C 程度，目標升到 B」的學生

已實作兩層限制:

1. Prompt 層
   - 在 `core/ai_analyzer.py` 的 `build_chat_prompt()` 中重寫 system override
   - 明確禁止完整解法與直接答案

2. 後端防呆層
   - 新增 `sanitize_tutor_reply()`
   - 若偵測到像「答案是...」「=5」這類直接答案型回覆，會自動改寫成引導句

本次新增/調整的重要函式:

- `sanitize_tutor_reply`
- `_looks_like_direct_answer`
- `_build_guiding_reply`

### 3.7 live_show 不再硬編碼模型名稱

修正前問題:

- `live_show.py` 有直接寫死 model 名稱
- 不符合全域 config 控制原則

修正後:

- 改為統一由 `Config.MODEL_ROLES[...]` 與 `Config.DEFAULT_CODER_PRESET` 決定
- route 層不再硬綁 model string

### 3.8 live_show 下一題卡死問題已修正

使用者實際回報:

- 題型不是 100% 正確
- 程式只能呼叫 `generate()` 一次
- 點下一題一次後就卡死

根因:

1. 前端「下一題」只是重打 `/api/run_generated_code`
2. 後端缺少「這次是 next question」的明確旗標
3. 我們先前為 radicals regression 加的 sticky rerun，誤把「下一題」也當 rerun

已修正:

- `templates/live_show.html`
  - `runNextQuestion()` 會送 `next_question: true`
  - 同送回 `skill_id`、`ocr_text`、`json_spec`
  - 補記錄 `latestSkillId`、`latestJsonSpec`、`latestOcrText`

- `core/routes/live_show.py`
  - 新增 `next_question = bool(data.get("next_question", False))`
  - sticky rerun 只在 `not next_question` 時生效
  - response 會補 `file_path`

結果:

- Ab2 / Ab3 的「下一題」可連續使用
- 不再卡在同一題

### 3.9 MCRI evaluator 已重建

發現問題:

- 畫面上的 MCRI 分數很低
- 追查後發現不是模型品質本身，而是 `scripts/evaluate_mcri.py` 缺失
- `live_show.py` 與 `scaler.py` 仍在 import 它

缺檔造成的後果:

- `Ab3` 可能直接吃 `50` 的保底 fallback
- `Ab2` 可能走 `0.4*hygiene + 0.4*50 + 0.2*60` 的 fallback，常見為 `32%`

已重建檔案:

- `scripts/evaluate_mcri.py`
- `scripts/__init__.py`
- `tests/test_evaluate_mcri.py`

目前 evaluator 提供的 API:

- `analyze_code_robustness(code)`
- `evaluate_math_hygiene(question_text)`
- `evaluate_live_code(code, exec_result, healer_trace=None, ablation_mode=False)`

目前評估面向:

- syntax
- logic
- render
- stability
- hygiene breakdown

這版是可用 heuristic 版，不是 research 原版 100% 還原版，但已足夠讓 live_show 不再用假分數。

---

## 4. 本日主要修改檔案清單

以下為今天最重要的變動檔案:

- `config.py`
- `core/ai_analyzer.py`
- `core/routes/practice.py`
- `core/routes/analysis.py`
- `core/routes/live_show.py`
- `core/routes/live_show_pipeline.py`
- `templates/index.html`
- `templates/live_show.html`
- `scripts/evaluate_mcri.py`
- `scripts/__init__.py`
- `tests/test_evaluate_mcri.py`

另外還有先前整合進來的重要模組:

- `core/fraction_domain_functions.py`
- `core/integer_domain_functions.py`
- `core/polynomial_domain_functions.py`
- `core/architect_v01.py`
- `core/v01_pipeline.py`

---

## 5. 本日測試與驗證結果

### 5.1 全專案整合期曾通過的測試狀態

在前一輪整合完成時，整體測試結果曾為:

- `127 passed, 2 skipped`

### 5.2 practice 助教 smoke test

驗證方式:

- 透過 Flask test client 呼叫 `/chat_ai`

驗證結果:

- 助教已能回短句提示
- 範例輸出:
  - `8-3 是減法，你有看清楚符號嗎？`

這代表:

- qwen3-vl-8b tutor 路徑可通
- prompt 已往國中生提示風格收斂
- 後端 response sanitization 可生效

### 5.3 live_show 下一題修正驗證

已驗證:

- `tests/test_run_generated_code_regression.py`
  - 通過

- 手動連續觸發 `next_question: true`
  - 已可連續產題
  - 不再卡在同一題

### 5.4 live_show 相關測試

已通過或曾通過的重要測試:

- `tests/test_classify_image_text_consistency.py`
- `tests/test_run_generated_code_regression.py`
- `tests/test_live_show_fraction_helper.py`
- 多組 `test_live_show_*`

### 5.5 MCRI evaluator 驗證

已通過:

- `pytest -q tests/test_evaluate_mcri.py tests/test_classify_image_text_consistency.py`
- 結果:
  - `5 passed`

目的:

- 確保 `scripts.evaluate_mcri` 可被 import
- 確保三個公開函式可用
- 避免系統再退回假 fallback 分數

---

## 6. Showreel / Demo 目前的重要判斷

### 6.1 單模型策略

目前傾向:

- 全專案主模型先定為 `Qwen3-VL-8B`

原因:

- 已接進整個系統
- 能看圖
- 能 OCR
- 能做數學題理解
- 能做 tutor 提示
- 不想反覆換模型重調 prompt 與流程

### 6.2 硬體限制判斷

使用者補充情境:

- 開發機 GPU 只有 6GB
- 展演機是 4060 8GB notebook

目前判斷:

- 6GB 開發機:
  - 不適合把 `Qwen3-VL-8B` 當長時間主力
  - 適合做流程整合、prompt 調整、小量測試

- 8GB 展演機:
  - 可作為 showreel/demo 主模型
  - 但仍需保守配置:
    - 圖片不要太大
    - prompt 不要太長
    - output tokens 要控制
    - 避免多請求並發

### 6.3 模型建議

若堅持「一個模型打到底」:

- 目前建議: `Qwen3-VL-8B`

理由:

- 工程切換成本最低
- 已經是目前 project 中最完整接好的路線
- 比起繼續換模型，現在更值得把流程磨穩

若未來允許做 challenger 對照:

- 可評估 `MiniCPM-o 2.6`
- 優先拿來比較手寫數學辨識 / OCR / edge 效率

但目前不建議立刻改主模型路線。

---

## 7. 目前已知問題與風險

### 7.1 MCRI 是重建版，不是 research 原始完整版

目前 `scripts/evaluate_mcri.py` 是可用版。
它已能防止 fallback 假分數，但未必完全等同 research 版本的評分哲學。

後續若要更精準:

- 需再把 MCRI 與 isomorphic/structure drift/fingerprint 做更細對齊
- 可能還要把 evaluator 分數與 UI 語意重新校準

### 7.2 Structure Drift 與 MCRI 是兩套邏輯

目前畫面上:

- `Structure Drift Detected`
- `MCRI score`

這兩者不是同一件事。
後續要避免 demo 時誤導，需要再釐清或調整文案。

### 7.3 某些檔案仍有舊編碼/亂碼痕跡

例如部分歷史中文註解與舊字串出現編碼異常。
雖不一定影響執行，但會影響後續維護與 prompt 可讀性。

---

## 8. 建議的下一步工作

### A. 高優先

1. 實機在 `4060 8GB notebook` 上做完整 showreel smoke test
   - 測 `live_show`
   - 測 `practice`
   - 測手寫上傳與 OCR

2. 實際確認 `Qwen3-VL-8B` 在 demo 機上的穩定參數
   - 圖片大小
   - timeout
   - output token 長度
   - 單輪延遲

3. 驗證 MCRI 分數是否已從 fallback 變成真分數
   - 對同一題測 Ab1 / Ab2 / Ab3
   - 比對 `breakdown`
   - 必要時把 `breakdown` 暫時顯示到 debug panel

### B. 中優先

4. 微調 `practice` tutor 的追問模板
   - 再縮短回話
   - 更像「會考 C 拉到 B」的補救教學風格

5. 檢查 `agent_tools` 是否有舊路徑寫死到 research 目錄
   - 若有，改成主專案相對路徑

6. 清理亂碼與舊註解
   - 尤其是 `core/ai_analyzer.py`
   - 以免後續 prompt 修改被舊內容干擾

### C. 低優先

7. 將 MCRI evaluator 再精修成 research 對齊版
8. 規劃 `Qwen3-VL-8B` vs `MiniCPM-o 2.6` 的手寫數學 A/B 測試表

---

## 9. 接手 AI 建議先讀的檔案順序

若下一個 AI 要續做，建議先依序閱讀:

1. `SHOWREEL_LOGIC.md`
2. `config.py`
3. `core/ai_analyzer.py`
4. `core/routes/analysis.py`
5. `core/routes/practice.py`
6. `core/routes/live_show.py`
7. `core/routes/live_show_pipeline.py`
8. `templates/live_show.html`
9. `scripts/evaluate_mcri.py`
10. `tests/test_evaluate_mcri.py`

---

## 10. 一句話狀態摘要

主專案已成功承接 `AST_Research` 的 agent-skill / live_show 能力，
`practice` 助教已切到 `qwen3-vl-8b` 並收斂成國中生提示模式，
`live_show` 下一題卡死已修掉，
缺失的 MCRI evaluator 也已重建回來，
目前最值得做的是在 4060 8GB 展演機上完成一輪真機 smoke test 與分數校準。
