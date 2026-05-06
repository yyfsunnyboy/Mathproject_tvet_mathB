# B4 架構漂移備忘錄：從 SECG 內容工廠到自適應學習執行層

## 1. 背景

說明最初的 SECG 架構定位：

- Smart-Edu Content Generator 原本是一套 AI 教材內容生成後台。
- 主要管線包含：
  - 教材匯入 textbook importer
  - 技能檔案同步與 generator 生成
  - 技能提示詞補強與 guided prompts
  - 自動建立前置技能與知識圖譜
- 原始角色是把教科書內容轉換成：
  - DB 技能資料
  - 課綱與章節資料
  - 例題資料
  - Python 出題程式
  - 教學提示詞
  - 前置技能關係

## 2. 目前演化

說明技術型高中 B4 版本已經超出原本「內容工廠」範圍，新增了自適應學習執行層。

目前已經出現的新架構能力包括：

- B4 deterministic generator runtime
- problem_type readiness governance
- runtime_ready / manual_review 分帳
- adaptive allowlist
- generator-first / generator-fallback 題源策略
- session_engine 整合
- synthetic catalog entries
- teaching mode 與 diagnostic mode 分離
- B4-to-B4 remediation bridge
- pilot readiness checklist
- browser smoke / manual smoke 流程

## 3. 架構漂移判斷

- 這不是架構失敗，也不是完全重寫。
- 原本 SECG 仍然是內容工廠底座。
- 目前 B4 工作是在 SECG 上方新增 deterministic adaptive runtime。
- 舊文件仍可描述 Layer 1，但已不足以描述完整系統。
- 因此未來需要一份新版總架構文件，但現在還不是撰寫完整文件的時機。

## 4. 目前浮現的三層架構

### Layer 1：SECG Content Factory／內容工廠層

負責：

- 教材匯入
- DB skill / curriculum / example 建立
- Python generator 生成與同步
- AI 教學提示詞補強
- 前置技能與知識圖譜建構

### Layer 2：Deterministic Adaptive Runtime／確定性自適應執行層

負責：

- deterministic generator 驗證
- coverage / readiness classification
- allowlist gating
- excluded problem_type blocking
- adaptive question selection
- session_engine integration
- generator-first / synthetic catalog fallback
- B4-to-B4 remediation bridge

### Layer 3：Pilot / Teacher QA Operation／試用與教師 QA 層

負責：

- 教師 QA checklist
- 學生端 browser smoke
- Go / No-Go criteria
- 手動觀察紀錄
- 小規模 classroom pilot readiness
- logs / data review

## 5. 為什麼現在先不寫完整新版架構文件

- Phase 5B 仍在進行瀏覽器實測。
- B4-to-B4 remediation bridge 剛接上，還需要手動 smoke。
- 補救後是否能穩定回主線尚未確認。
- B4 YAML subskill ontology 尚未建立，已延後到後續階段。
- 若現在寫完整架構，很快就會因實測修正而過時。
- 因此目前只先保留架構漂移備忘錄。

## 6. 建議

- 本文件只是暫時性的架構漂移備忘錄。
- 先完成 Phase 5B manual smoke。
- 等以下流程確認後，再撰寫正式新版架構文件：
  - 章節入口
  - 第一題載入
  - 連續教學練習
  - 答錯後補救
  - 補救後回主線
  - 教師 QA / pilot checklist
- 未來正式文件建議命名為：`MathProject TVET B4 System Architecture v2`
- 未來正式文件應明確呈現：`SECG Content Factory + Deterministic Adaptive Runtime + Pilot Operation Layer`
