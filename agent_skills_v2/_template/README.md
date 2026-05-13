# Agent Skill v2 Template

## 說明
此目錄為 Agent Skill v2 規格包的範本 (Template)。
當需要為新技能 (如 B1 第 1 章) 建立流水線時，請複製此目錄並根據具體技能內容填充相關 YAML 檔案。

## 重要警告
- **不可直接作為 Runtime Code**：此目錄下的檔案僅為規格定義與範例，系統運行時路由應讀取各冊具體的實例。
- **嚴禁手動修改 Production Registry**：所有對 `configs/b4_generator_registry.yaml` 等生產配置的更改，應通過自動化腳本或經過 Verifier 驗證後的 Promotion 流程完成。

## 檔案清單
- `skill.yaml`: 技能主體定義。
- `problem_types.yaml`: 子題型規格與 IO 契約。
- `examples_map.yaml`: 課本例題映射。
- `domain_functions.yaml`: 數學家族與領域函數限制。
- `prompt_gencode.md`: AI 生成提示詞模板。
- `evals.yaml`: 驗證器閘門設定。
