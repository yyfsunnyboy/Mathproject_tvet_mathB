# B1 GenCode V3 異常追查與 Registry 精準修復報告

- 範圍：僅技高數學 B1
- 性質：Registry／facade／package 契約修復；**未** REBUILD Generator；**未**改 B2～B4
- 備份：`reports/gencode_rebuild_backup/b1_registry_repair_20261121_233725/`
- 延續盤點：`b1_b4_generator_problem_type_inventory.json`（未重跑全系統掃描）
- 修復前後差：`b1_registry_repair_delta.json`

## 一、B1 異常清單（修復前）

可執行 Skill 35；outline 10；合計 45。

### 1) 可執行且可用題型數＝0

| Skill ID | 原因 | 相關檔案 | 建議處置 |
|---|---|---|---|
| `vh_數學B1_QuadraticFunctionGraph` | facade 指向 `draft_v1` 假 key；磁碟有 `src_*` 但 package stub | `skills/...Graph.py`、`agent_skills_v3/.../components/src_*` | **已修**：依 metadata 重寫 facade/package |
| `vh_數學B1_QuadraticInequalityAndFactoring` | 同上 | 同上 | **已修** |
| `vh_數學B1_FunctionConcept` | 無 facade；僅有 package components | `agent_skills_v3/...FunctionConcept/` | **已修**：新建 thin facade + package router |
| `vh_數學B1_QuadraticInequalitySolution` | draft_v1 keys／package stub | 同上模式 | **已修**（Checker 部分題型另列） |
| `vh_數學B1_VertexFormOfQuadraticFunction` | draft_v1／`spec_v1` keys | 同上 | **已修** |
| `vh_數學B1_CompletingTheSquare` | draft_v1 keys | 同上 | **已修** |
| `vh_數學B1_QuadraticFunctionExtremum` | draft_v1 keys | 同上 | **已修** |
| `vh_數學B1_NumberLine` | bootstrap JH adapter；無 V3 package／無 SPECS | `skills/vh_數學B1_NumberLine.py` | **已補 SPECS**（仍為 bootstrap） |
| `vh_數學B1_SubSection332` | 無任何 Generator 產物 | — | **待人工**：是否為 outline／空殼 |

### 2) 有實作但 Runtime 先前無法選用（V3 component 路徑）

上表前 7 項：`src_*` generate.py 存在且 tracker=`verified`，但 facade 未以 `src_*` 註冊；正式 publish eligible=0（`DOMAIN_EVIDENCE_INCOMPLETE`）。本輪以磁碟 metadata 做契約修復，**未**走正式 publish gate。

### 3) facade／package KEYS 不一致

| Skill | 情況 |
|---|---|
| 二次函數／不等式族（7） | facade=`*:draft_v1`；package `__init__.py` 幾乎空 |
| FunctionConcept | 無 facade |
| Cartesian | KEYS 一致；facade SPECS 曾為 ListComp（靜態不可讀）→ **已改字面量** |

### 4) SPECS／problem_type_id 異常

- draft_v1 SPECS **無 `component_id`**（舊 `generate_for_skill` 路徑）
- 盤點初版只認 V3 component → 誤報 0 種（即使舊路徑可出題）
- 計數已補 legacy SPECS 規則

### 5) 「已上線」與 Runtime 能力不一致

多支 Skill 管理中心顯示「全部上線／已上線」，但可用題型曾為 0（Registry 斷線）。根因：status 以 tracker／manifest／coverage 為準，**不保證** facade KEYS 指向可載入 component。

> 多 component 同 `problem_type_id` 去重 **不是 Bug**。

## 二、P0 修復內容

腳本：`scripts/repair_b1_v3_registry_from_disk_metadata.py`

對 7 支 Skill：由 `components/*/metadata.py` 產生真實 `GENERATOR_KEYS`／`GENERATOR_SPECS`，重寫：

- `skills/<skill>.py`（thin facade → `dispatch_generate`）
- `agent_skills_v3/<skill>/__init__.py`
- `component_manifest.json`

另：

- NumberLine：宣告 2 種 bootstrap `GENERATOR_SPECS`
- Cartesian：SPECS 改字面量
- 盤點函式：支援 legacy problem-type registry

**未做**：批次 REBUILD generate.py；未改 B2～B4；未寫入學生作答表。

## 三、修復前後可用題型數

| Skill ID | 修復前 | 修復後 |
|---|---:|---:|
| QuadraticFunctionGraph | 0 | **2** |
| QuadraticInequalityAndFactoring | 0 | **1** |
| FunctionConcept | 0 | **2** |
| QuadraticInequalitySolution | 0 | **5** |
| VertexFormOfQuadraticFunction | 0 | **5** |
| CompletingTheSquare | 0 | **2** |
| QuadraticFunctionExtremum | 0 | **3** |
| NumberLine | 0 | **2** |
| CartesianCoordinateSystemEstablishment | 3 | **3**（WARN→PASS） |
| SubSection332 | 0 | **0**（仍無產物） |

## 四、Runtime 測試（正式 skills.*.generate 路徑）

| Skill | 可選用 | 題幹/答案 | problem_type_id | Checker |
|---|---|---|---|---|
| 上述 7 支修復 Skill | PASS | PASS | PASS | 6/7 全樣本 PASS；QIS 有 4/29 component 既有契約問題 |
| PointAndLine / ParallelLines / SlopeOfALine | PASS | PASS | PASS | 回歸 PASS |
| Cartesian / NumberLine | PASS | PASS | PASS | PASS |
| src_4584 ∈ PointAndLine、∉ Parallel | PASS | — | — | 靜態+測試 PASS |

### 未修復（待人工）

1. **`vh_數學B1_QuadraticInequalitySolution` / `integer_reverse_quadratic_inequality_coefficients`**（src_4474/4482/4493/4507）：答案為整數，payload checker 卻是 `linear_equation_equivalent_checker` → 正解 check=False。屬 Answer Contract／Checker 語意，需人工確認後改契約（非 Registry）。
2. **正式 publish eligible 仍為 0**（domain evidence 缺 `resolution_source`／`fixed_domain_key`；FunctionConcept 另有 `CHOICE_CONTRACT_INCOMPLETE`）。本輪契約修復不代表通過正式 Promotion Gate。
3. **`vh_數學B1_SubSection332`**：無 Generator。
4. **`vh_數學B1_NumberLine`**：仍為 JH bootstrap；教材來源不足狀態未變。

## 五、B1 健康狀態（修復後，可執行 35）

- **PASS：34**
- **WARN：1**（NumberLine bootstrap／無 V3 package）
- **FAIL：0**
- **UNKNOWN：0**
- 題型數為 0 的可執行 Skill：僅 **`vh_數學B1_SubSection332`**

## 六、管理中心驗收與狀態語意（建議，先不改語意）

現況欄位「Generator 題型數」已接共用盤點函式；修復後上述 Skill 應顯示 `N 種`（Flask 需 reload 後生效；本輪未重啟）。

| 狀態詞 | 現行大致意義 | 與題型數關係 |
|---|---|---|
| 已上線／全部上線 | tracker／coverage／published 計數面向 | **不保證** facade 可選用 |
| READY／可解析 eligible | 來源題可進入 V3 管線 | **不是** Runtime 題型數 |
| Generator 題型數 | facade∩package 可選用 `problem_type_id` 去重 | 本欄權威 |

### 最小修改方案（建議下一輪，本輪不改狀態語意）

1. 保留既有「已上線／READY」定義不動。
2. 當 `published_count>0` 且 `usable_problem_type_count==0` 時，在 Gencode V3 欄旁加 **非破壞性警告徽章**（例如「Registry 斷線」），或在題型數顯示 `0 種⚠`。
3. Tooltip 說明三角色分離：上線套件 ≠ eligible 來源 ≠ Runtime 題型數。

## 七、測試

- `tests/gencode/test_generator_problem_type_inventory.py` PASS
- `tests/test_src_4584_point_line_distance_mapping.py` PASS

**停止於 B1，等待人工驗收。**
