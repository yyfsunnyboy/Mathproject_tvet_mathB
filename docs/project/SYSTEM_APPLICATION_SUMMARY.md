# AI 自適應學習系統 (Mathproject TVET Math B)｜升學備審與作品集精簡摘要

---

## A. 系統現在是什麼 (系統定位與現況概述)

本系統是一套以 **Python (Flask)、混合式 RAG (向量檢索與知識圖譜)、強化學習 (PPO/AKT 認知狀態追蹤) 與符號數學自動批改引擎** 為核心構建的「AI 數學自適應學習平台」。系統以台灣 108 課綱（涵蓋技高數學 B 與國中核心代數幾何）為骨幹，具備 4,200+ 題結構化範例題庫與 700+ 個動態微生成器。系統打破傳統死板刷題模式，能在學生答錯時自動診斷認知斷點、降維檢索先備知識、提供蘇格拉底式階梯引導，並支援手寫數學式辨識與班級管理，目前已在單機與區域網路環境具備完整可操作的產品閉環。

---

## B. 已經完成的核心能力 (Core Accomplishments)

1. **章節級自適應動態學習閉環 (End-to-End Adaptive Loop)**：
   * 結合強化學習策略（PPO Policy）與精熟度評估（APR/Frustration Index），學生答錯時自動觸發「原題鞏固 (stay)」、「斷點先備補救 (remediate)」、「返回主線 (return)」三態動態派題機制。
2. **非字串比對的「符號數學即時自動批改引擎」**：
   * 深入解析代數、多項式長除法、分式約分、根式化簡、區間符號、坐標數對與向量運算，具備數學等價性判定（Symbolic Equivalence Check）與微小誤差容忍。
3. **混合式 RAG 蘇格拉底階梯提示與 AI 助教 (Hybrid RAG Socratic Tutor)**：
   * 整合向量檢索（`text2vec-base-chinese` + ChromaDB 281 個知識節點）與知識圖譜先備橋接，不直接公佈最終答案，而是依學生卡關步驟分層引導與生成追問建議。
4. **多模態觸控電子計算紙與 AI 手寫數學式辨識 (Multimodal Handwriting Recognition)**：
   * 前端實作抗誤觸 Canvas 計算紙（支援 Surface Pro 觸控筆），結合 Vision LLM 提取手寫數學算式並進行步驟與答案驗證。
5. **程式代碼閉環生成與 AST 自癒修復機制 (AST Code Self-Healing Engine)**：
   * 具備在後台針對生成之題型 Python 代碼進行抽象語法樹（AST）靜態分析、缺失引用修復、正則校正與死迴圈防護之自動化測試發布管線。
6. **大規模結構化題庫與參數化微生成器矩陣**：
   * 內建 4,228 筆經課綱校準之教材範例，並研發 733 個參數化題型生成腳本（`agent_skills_v3/`），可無限產出隨機變數但保證嚴謹有解之數學題目。
7. **完整的教師端班級管理與 Excel 名冊批次匯入**：
   * 提供教師建立班級、專屬邀請碼加入、名冊 Excel 快速批次建帳與 B4 第二章可見度稽核日誌。
8. **嚴謹的軟體工程架構與測試保護**：
   * 建立 448 個單元與整合測試檔，並於系統底層實作 Session Cookie 自動修剪防護與 SQLite WAL 並行寫入優化。

---

## C. 目前仍在完善與驗證的部分 (Current Limitations & Gaps)

1. **深度知識追蹤模型 (AKT) 的在線即時推論微服務化**：
   * 目前已完成 PyTorch 課綱感知 AKT 模型的離線訓練與權重導出，但線上運行主要由輕量級 PPO 與規則引擎承載，尚未將大型深度神經網絡以獨立推論服務（如 TorchServe/ONNX Runtime）上線。
2. **學習診斷報告的歷史版本持久化歸檔**：
   * 目前雷達圖與弱點分析是以即時運算渲染為主，尚未建立歷次段考與月度學習診斷的長期追蹤資料表。
3. **高耗時任務的非同步任務佇列 (Async Worker Queue)**：
   * 教材 Word (DOCX) MathType 批量解析與多題 AI 題目生成目前仍處於 HTTP 同步執行緒中，缺乏 Redis + Celery 等非同步佇列隔離，大量併發時容易造成連線阻塞。
4. **前端代碼模組化與組件化重構**：
   * 目前練習介面核心邏輯集中於 7,000+ 行之 HTML/Jinja2 模板中，需遷移為現代化前端框架（Vue 3 / React + TypeScript）以提升渲染效能與可維護性。

---

## D. 下一階段演進目標 (Path to Production Scale)

* **目標**：將目前的「單機/班級級高功能科研原型」升級為「可承載萬人併發的雲端分散式教育平台」。
* **關鍵里程碑**：
  1. **資料庫遷移**：從 SQLite 遷移至雲端託管 PostgreSQL / MySQL，配置連線池（PgBouncer）與讀寫分離。
  2. **非同步架構解耦**：導入 Redis 記憶體快取與 Celery 分散式背景任務，專責處理 AI 題型生成、Word 轉檔與報表聚合。
  3. **微服務化與 API 成本閘道**：為 LLM 呼叫建構 Semantic Cache（語意快取）與 Token 配額控管機制，降低 API 營運成本並提升響應速度。
  4. **前後端分離 (SPA / SSR)**：採用 Vue 3 / React + TailwindCSS 重構學生練習端與教師分析大屏。

---

## E. 銜接大學資工／軟體工程讀書計畫之知識缺口

本專案實作讓我深刻體會到「做出可用功能」與「構建大規模穩定系統」之間的巨大差距，我將依據本系統的真實演進需求，在大學階段深入修習以下領域：

### 1. 資料結構與演算法 (Data Structures & Algorithms)
* **實務連結**：系統中的知識圖譜遍歷、先備技能拓撲排序（Topological Sort）、AST 語法樹修復與 PPO 狀態空間搜索，需要更深入掌握圖論演算法（最短路徑、DAG、最大流）與複雜度分析，以優化大規模知識網絡的推薦延遲。

### 2. 資料庫系統 (Database Systems)
* **實務連結**：在面對數百名學生同時提交作答時，SQLite 的檔案鎖定與 Join 效能成為瓶頸。大學期間將深入學習關聯式資料庫交易隔離等級（ACID/MVCC）、索引底層結構（B+ Tree）、資料庫正規化，以及 NoSQL / 向量資料庫（Postgres pgvector、Milvus）的分區與快取策略。

### 3. 網路與分散式系統 (Networking & Distributed Systems)
* **實務連結**：為解決 AI 推論與大檔案轉檔阻塞問題，需深入學習 HTTP/2、WebSocket 即時通訊協定、分散式訊息佇列（Kafka、RabbitMQ）、負載平衡（Nginx、Envoy）與一致性雜湊，打造高可用（High Availability）後端架構。

### 4. 軟體工程與系統測試 (Software Engineering & DevOps)
* **實務連結**：專案累積了 448 個測試檔案與複雜的生成管線，使我深刻體認到 CI/CD、模組化設計模式（Clean Architecture）、Docker 容器化封裝與 Kubernetes 叢集編排在軟體全生命週期中的不可替代性。

### 5. 機器學習與強化學習 (Machine Learning & Reinforcement Learning)
* **實務連結**：目前系統已觸及 PPO 策略梯度演算法與 AKT 知識追蹤，未來需在大學 Mathematical Foundations of ML、深度強化學習（Deep RL）、圖神經網絡（GNN）等課程中深化理論，進一步提升自適應路徑規劃的數理嚴謹度。

### 6. 資訊安全 (Information Security)
* **實務連結**：教育平台涉及學生個資與成績隱私。需要深入學習 OAuth 2.0 / OIDC 認證授權體系、JWT 安全性、資料庫欄位級對稱加密、以及防禦 SQL Injection、XSS、CSRF 與 Session Hijacking 的全套安全防護機制。

