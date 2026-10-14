# Cursor 交接包：vh_數學B1_AbsoluteValueInequality

- generated_at: `20261005T145632`
- capability_status: `needs_capability`
- gap_fingerprint: `7676ba42818ab53dfa23ebe3c76e2bee673a778eef5b00779d32f65aeacb4f20`
- domain_key: `algebra.absolute_value`
- domain_module: `core.domain.absolute_value_domain`
- entrypoint: `build_absolute_value_matrix`

## 目標與硬限制

- 目標：補齊 Gencode V3 所需 domain capability／operation／registry／schema／checker 接線。
- **不得**自動呼叫 Qwen／Gemini 修改正式 core。
- **不得**覆寫既有 verified／published production components。
- **不得**寫入學生端 production 或變更正式 tracker verified／published。
- Gencode V3 只會使用既有 domain 能力重新建置，不會自行發明 API。

## Domain resolver 結果

```json
{
  "capability_status": "needs_capability",
  "registry_entry": {
    "fixed_domain_key": "algebra.absolute_value",
    "domain_module": "core.domain.absolute_value_domain",
    "entrypoint": "build_absolute_value_matrix",
    "registry_revision": "2026-09-10-v1.10",
    "allowed_operations": [
      "absolute_value_inequality_zero_center_basic",
      "absolute_value_inequality_linear_expression_basic",
      "absolute_value_inequality_shifted_basic",
      "absolute_value_inequality_integer_solution_count_choice"
    ]
  },
  "supported_operations": [
    "absolute_value_inequality_zero_center_basic",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_integer_solution_count_choice"
  ],
  "missing_layers": [
    "example_operation_resolution"
  ],
  "wiring_error": "",
  "resolvable_example_count": 0,
  "unresolved_example_count": 10
}
```

## 缺少層級

- `example_operation_resolution`

## 教材題目清單

- total: 10
- resolvable: 0
- unresolved: 10

- `src_4400` (UNRESOLVED) type=`textbook_exercise` Q=`試求下列不等式之解：(1)$\left| x \right|$≤ 8 (2)$\left| x \right|$> 10 (3)$\left| x \right|$< 7 (4)$\left| x \right|$≥ 12` A=``
- `src_4402` (UNRESOLVED) type=`textbook_exercise` Q=`解下列不等式：(1)$\left| x-2 \right|\le 4$ (2)$\left| x+5 \right|>1$` A=``
- `src_4403` (UNRESOLVED) type=`textbook_exercise` Q=`解下列不等式：(1)$\left| x-3 \right|<2$ (2)$\left| x+5 \right|\ge 4$` A=``
- `src_4404` (UNRESOLVED) type=`textbook_exercise` Q=`解不等式$\left| 4x+1 \right|\le 6$。` A=``
- `src_4405` (UNRESOLVED) type=`textbook_exercise` Q=`解不等式$\left| 2x-3 \right|>1$。` A=``
- `src_4406` (UNRESOLVED) type=`textbook_exercise` Q=`解不等式$\left| 3x-1 \right|\ge 7$。` A=``
- `src_4407` (UNRESOLVED) type=`textbook_exercise` Q=`解不等式$\left| 5x+3 \right|<7$。` A=``
- `src_4409` (UNRESOLVED) type=`textbook_example` Q=`試求下列不等式之解：(1)$\left| x \right|$ ≤ 3 (2) $\left| x \right|$ ≥ 4` A=``
- `src_4413` (UNRESOLVED) type=`in_class_practice` Q=`試求下列不等式之解：(1) $\left| x \right|$ ≤ 6 (2) $\left| x \right|$> 5` A=``
- `src_4499` (UNRESOLVED) type=`self_assessment` Q=`試求滿足不等式$\left| 3x-2 \right|\le 8$的整數x共有多少個？ (A) 4 (B) 5 (C) 6 (D) 7。` A=``

## 同構分群建議

- `in_class_practice`: [4413]
- `self_assessment`: [4499]
- `textbook_example`: [4409]
- `textbook_exercise`: [4400, 4402, 4403, 4404, 4405, 4406, 4407]

## 既有相近 API／可重用方向

- 先查 `core/registry/taxonomy_registry.py` 與同章已 ready 的 skill binding。
- 優先擴充既有 `domain_module` 的 allowed_operations，而不是新建獨立 skill runtime。
- checker／answer schema 必須落在既有 registry（`answer_schema_registry`、`_ALLOWED_CHECKERS`）。

## 必須執行的 focused tests

- domain resolver：`resolve_domain_for_skill(skill_id)` 成功且 wiring_ok
- capability preflight：`capability_status == ready`
- 單題 no-LLM phase1：unresolved_example_count == 0
- 既有 verified skill 回歸：不得被本改動破壞

## 不可修改的 verified 成果

- `agent_skills_v3/<other_ready_skills>/...` production components
- 既有 tracker `verified`／`published` 列
- 正式 publish manifest（除非另開受控 publish 任務）

## 完成條件

1. `evaluate_skill_v3_capability` 回傳 `ready`
2. `/skills` 顯示「重新建置與驗證」
3. `POST .../gencode_v3_dryrun` 不再因 capability 回 409
4. 不自動 publish；由教師另按「更新到學生端」

## 建議 Cursor 執行 prompt

```text
請為 skill `vh_數學B1_AbsoluteValueInequality` 補齊 Gencode V3 domain capability。
目前 capability_status=`needs_capability`，missing_layers=['example_operation_resolution']。
只允許最小接線修改（registry / domain operation / schema / checker）。
禁止呼叫模型自動改 core，禁止覆寫其他 skill 的 verified/production。
完成後執行 focused tests，並確認 evaluate_skill_v3_capability == ready。
```
