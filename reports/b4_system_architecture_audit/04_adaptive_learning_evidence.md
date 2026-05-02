# Adaptive Learning Evidence Report

## 1. 已閱讀檔案
- `adaptive_review_api.py` (依據先前的檔案記憶與上下文)
- `adaptive_review_examples.py`
- `adaptive_review_integration.py`
- `adaptive_review_mode.py`
- `akt_inference.py`
- `akt_v2.py`
- `app.py`
- `models/` (資料夾)
- `自適應複習/` (資料夾)
- `知識圖譜/` (資料夾)
- `check_prereqs.py`
- `analyze_skills.py`

## 2. Adaptive Function Evidence Table

| function_name | file_path | directly_observed_purpose | input_keys_seen | output_keys_seen | related_database_table_or_model | evidence_note |
| --- | --- | --- | --- | --- | --- | --- |
| `AdaptiveReviewEngine.__init__` | `adaptive_review_mode.py` | 初始化複習引擎，載入 AKT 與 RL 模型 | `akt_model_path`, `rl_model_path`, `data_path` | N/A | `akt_curriculum.pth`, `ppo_akt_curriculum.zip` | 綁定推論工具與模型 |
| `AdaptiveReviewEngine.get_knowledge_state` | `adaptive_review_mode.py` | 獲取當前知識狀態向量 | `item_history`, `skill_history`, `resp_history` | `s_t` (np.ndarray) | AKT 模型 | 封裝 AKT 推論 |
| `AdaptiveReviewEngine.get_apr` | `adaptive_review_mode.py` | 計算各技能平均掌握度 (APR) | `s_t` | float | N/A | |
| `AdaptiveReviewEngine.recommend_next_items` | `adaptive_review_mode.py` | 推薦下一批題目 | `item_history`, `skill_history`, `resp_history`, `n_items`, `use_rl` | List[Dict] 推薦題目 | PPO 模型 | 若 RL 失敗則使用 `_select_max_fisher` 備援 |
| `AdaptiveReviewEngine._select_max_fisher` | `adaptive_review_mode.py` | Max-Fisher 備援選題策略 | `s_t`, `visited` | int (`item_id`) | N/A | 選擇不確定性最高的題目 |
| `AdaptiveReviewEngine.simulate_session` | `adaptive_review_mode.py` | 模擬一個複習會話 | `item_history`, `skill_history`, `resp_history`, `session_name` | Dict (統計資訊) | N/A | |
| `analyze_weak_skills` | `adaptive_review_mode.py` | 分析學生弱項技能 | `engine`, `item_history`, `skill_history`, `resp_history` | Dict (弱項分析結果) | N/A | 計算 mastery 並排序 |
| `generate_review_plan` | `adaptive_review_mode.py` | 生成多會話複習計畫 | `student_history`, `num_sessions`, `engine` | Dict (計畫) | N/A | |
| `AKTInference.get_item_apr` | `akt_inference.py` | 計算 Item-level APR (所有題目答對機率平均) | `item_history`, `skill_history`, `resp_history` | float | AKT 模型 | |
| `AKTInference.get_skill_apr` | `akt_inference.py`, `akt_v2.py` | 計算 Skill-level APR | `item_history`, `skill_history`, `resp_history` | Tuple[float, Dict] | AKT 模型 | |
| `AKTInference.get_skill_mastery` | `akt_inference.py` | 判斷技能是否掌握 | `item_history`, `skill_history`, `resp_history`, `threshold` | Dict[str, bool] | N/A | `threshold` 預設 0.7 |
| `AKTInference.get_assessment_report` | `akt_inference.py` | 生成完整評估報告 | `item_history`, `skill_history`, `resp_history` | Dict | N/A | |
| `train` | `akt_v2.py` | 訓練 AKT 模型 | `data_path` | `model`, `n_items`, `n_skills`... | `assistments_2017.csv` | |

## 3. State Field Evidence Table

| field_name | file_path | function_name_or_template | observed_usage | evidence_note |
| --- | --- | --- | --- | --- |
| `mastery` | `adaptive_review_mode.py` | `analyze_weak_skills` | `skill_stats.append({'mastery': float(np.mean(mastery_scores)), ...})` | 計算弱項技能時使用 |
| `mastery` | `akt_inference.py` | `get_assessment_report` | `unmastered = [s for s, m in skill_mastery.items() if not m]` | 產生掌握狀態字典 |
| `fail_streak` | N/A | N/A | 目前未找到 | 僅在 `adaptive_review_mode.py` 的配置字典中找到 `max_consecutive_failures` |
| `frustration` | N/A | N/A | 目前未找到 | |
| `current_skill` | N/A | N/A | 目前未找到 | |
| `current_mode` | N/A | N/A | 目前未找到 | |
| `post_mode` | N/A | N/A | 目前未找到 | |
| `learning_mode` | N/A | N/A | 目前未找到 | |
| `in_remediation` | N/A | N/A | 目前未找到 | |
| `remediation_triggered` | N/A | N/A | 目前未找到 | |
| `return_to_mainline` | N/A | N/A | 目前未找到 | |
| `has_returned_to_main` | N/A | N/A | 目前未找到 | |
| `skill_family_bridge` | N/A | N/A | 目前未找到 | |
| `prerequisite` | `check_prereqs.py` | 全域腳本 | `p.prerequisite_skill.skill_ch_name` | 存取前置技能實體 |
| `prerequisites` | `check_prereqs.py` | 全域腳本 | `db.session.query(SkillPrerequisites)` | 關聯資料表名稱 |

## 4. Data Source Evidence Table

| table_or_file_name | file_path | usage_context | evidence_note |
| --- | --- | --- | --- |
| `models/akt_curriculum.pth` | `akt_inference.py`, `adaptive_review_mode.py` | `torch.load(checkpoint_path)` | AKT 知識追蹤權重模型 |
| `models/rl_akt_curriculum/ppo_akt_curriculum.zip` | `adaptive_review_mode.py` | `PPO.load(rl_model_path, device=device)` | PPO 路由決策模型 |
| `synthesized_training_data.csv` | `adaptive_review_mode.py`, `akt_inference.py` | 讀取以建立 `problemId`, `skill`, `correct` 映射與計算預設難度 | 作為中介對應表 |
| `assistments_2017.csv` | `akt_v2.py` | AKT 訓練資料 | |
| `課本題庫.xlsx` | `analyze_skills.py` | 篩選大於 10 題的技能 | |
| `SkillInfo` | `check_prereqs.py` | `db.session.query(SkillInfo)` | SQL 表，用來查詢技能中文名稱 |
| `SkillPrerequisites` | `check_prereqs.py` | `db.session.query(SkillPrerequisites)` | SQL 表，用來查詢前置知識對應關係 |
| `StudentHistory`, `ReviewSession`, `Student` | `adaptive_review_integration.py` | 文件註解範例 | 說明建議的資料庫實作方式 |

## 5. Current Flow Evidence
1. **初始化與模型載入**：`AdaptiveReviewEngine` 會載入 `AKTInference` (依賴 `.pth`) 與 `PPO` (依賴 `.zip`)，並讀取 `.csv` 建立題目與技能的屬性映射 (`_load_item_properties`)。
2. **狀態推論**：進行推薦或分析時，會先呼叫 `AKTInference.get_knowledge_state`，傳入 `item_history`, `skill_history`, `resp_history` 取得當前向量 `s_t`。
3. **計算 APR**：呼叫 `get_apr(s_t)` 計算當前整體掌握度。
4. **題目推薦 (RL + 備援)**：在 `recommend_next_items` 中，若設定使用 RL 且模型存在，則以 `s_t` 為觀察值呼叫 `rl_model.predict(obs)`；如果該題目已做過或模型不可用，則切換呼叫 `_select_max_fisher(s_t)` 選出不確定性最高的題目。
5. **前置知識查詢**：看到 `check_prereqs.py` 呼叫 `db.session.query(SkillPrerequisites)` 尋找指定技能的基礎單元。
目前未找到上述流程如何與 `in_remediation` 或 `fail_streak` 的切換模式相連。

## 6. Unknowns
- 在指定的閱讀範圍內，完全沒有看見處理 `in_remediation` (補救模式)、`fail_streak` (連續錯誤中斷)、`return_to_mainline` (返回主線) 的狀態轉換程式碼。推測這些流程寫在本次未允許閱讀的路由層 (`session_engine.py` 或其他模組) 中。
- `frustration` 等變數在這些模型推論與複習引擎檔案中並未出現。
- `models/rl_akt_curriculum` 目錄雖然存在，但指定只允許閱讀根目錄 `models/` 的淺層資訊，因此未能直接觀察該目錄內的其他 PPO 參數檔。
