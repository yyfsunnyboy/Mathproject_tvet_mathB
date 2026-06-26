# Gencode × AgentSkillV3 核心規範說明書

> **文件版本**：v1.10（Automated Domain Bootstrap & Domain Healer · 最終產品核心流程）  
> **Amendment Revision**：v1.10 · 2026-06-26  
> **Supersedes**：v1.9 中「缺 domain 僅 gap report／工程師人工建 domain／老師用 Codex」之隱含假設；v1.8 §1.7 僅涵蓋 skill package bootstrap，**不含**完整 domain 自動建立  
> **文件權威分工**：本文件為 Gencode × AgentSkillV3 **唯一規範權威**（原則、契約、狀態、錯誤碼、Gate 定義）；**題型介面／學生端作答契約／西堤作答套餐**之呈現與驗證規則亦以本文件為準。流程與時序見配套 [SOP_Gencode_AgentSkillV3_PipelineFlow.md](./SOP_Gencode_AgentSkillV3_PipelineFlow.md)（**唯一流程權威**；含 `answer_type` 判定、`generate()` 輸出契約、preview／smoke 流程）。兩份文件衝突時：規則以本文件為準；流程以 PipelineFlow 為準。  
> **適用範圍**：高職數學 B 版 Gencode Pipeline 全面升級至 V3「西堤套餐」微元件化架構；含全新 skill 第一次自動建立  
> **上位法規**：[Gencode與AgentSkillV2整合總體設計_v0.3.md](../Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md)（Layer 1–6 原則完整繼承，本文件僅增量定義 V3 微元件層）  
> **實體錨點目錄**：`docs/系統SOP/Gencode_AgentSkillV3整合/`  
> **實作狀態**：**SOP 已更新，程式尚待對齊**（v1.5–v1.6 多數條款 IMPLEMENTED；v1.8 Auto-Bootstrap、Domain Function Extension、狀態機擴充待程式對齊）

### v1.10 CHANGELOG（2026-06-26）

- 新增 **§1.10 Automated Domain Bootstrap & Domain Healer**（**最終產品必要能力**，非選配）
- 明確定義 domain 狀態 `draft`／`candidate`／`verified` 升格規則與驗證 Gate
- 規定 `generator algorithm ≠ answer oracle ≠ integrity validator` 三元分離
- 補充 `DOMAIN_CAPABILITY_UNRESOLVED`／`PARTIAL` 錯誤碼與教師端狀態對照
- §1.8 限縮為 **既有 verified domain 內** operation 擴充；全新 capability 走 §1.10
- 交叉引用總體設計 v0.3.3 §14、PipelineFlow §1.7

### v1.9 CHANGELOG（2026-06-26）

- 新增 **內容生成／資料呈現／學生作答** 三層分離原則（§2.0.1）
- 正式定義五種 **西堤作答套餐**：`short_answer`、`single_choice`、`multi_part`、`table_fill`、`drawing`（§2.0.2–§2.0.4）
- 新增 `answer_type` 選擇決策流程與禁止降級規則（§2.0.3、§2.0.5）
- 明確區分 **資料呈現模式**（`text`／`image`／`graph`／`readonly_table`／`canvas`）與 **學生作答模式**（五種套餐）
- `drawing` 強制 AI 檢查流程與 `ui_contract` 欄位定義（§2.0.4 套餐 E）；新 component 以 `drawing` 為準，§2.2.1 `handwriting` 僅作 legacy 映射
- 交叉引用 PipelineFlow：生成端如何產出契約（§2.0.6）

### v1.8 CHANGELOG

- 移除 production Generic Domain Fallback
- 固定 skill → fixed domain；缺 function 走 Domain Function Extension
- Auto-Bootstrap 不得由 AI 推論 Routing Domain
- 統一 `component_id = src_{textbook_example_id}`
- 修正 `required_core_components` 識別符
- 修正 Bootstrap Gate / Publish Gate
- 修正 Shadow Bridge 錯誤分類
- 修正 `practice.py` 相容性規範
- 區分 Skill Batch Build 與 Component Targeted Rebuild
- `unsupported_domain_operation` 映射為可恢復之 `DOMAIN_FUNCTION_MISSING`

---

## 0. 文件目的

本文件是 **AgentSkillV3 微元件生成與發布** 的工程 SOP，面向 Codex / Gemini Flash 閉環管線與人工審核。  
所有敘述均對接倉庫內**已存在**的模組路徑；不存在之編譯器名稱標註為 V3 目標模組，並指明現行等價實作。

### 0.0 核心架構權威鏈（v1.8 · 不可違反）

```text
textbook_example.skill_id
→ authoritative Skill Registry
→ fixed_domain_key
→ allowed_operations / domain functions
→ component generation
```

| # | 原則 |
|---|------|
| 1 | 教材例題已綁定的 `skill_id` 是權威事實 |
| 2 | 每個 `skill_id` 必須對應唯一固定 `fixed_domain_key` |
| 3 | AI 不得重新判斷、改寫或建議更換 skill |
| 4 | AI 不得重新決定或改派 Domain |
| 5 | 同一 skill 的所有 component 必須使用固定 Routing Domain |
| 6 | Domain 能力不足時，擴充原 Domain function（§1.8） |
| 7 | 不得借用其他 Domain |
| 8 | 不得用 generic Domain 取代正式 Routing Domain |
| 9 | 新 skill 缺少 package、component、wrapper 或 operation，**不代表** unsupported |
| 10 | 只有教材本質無法程式化時，才能標記 `UNSUPPORTED_TASK_TYPE` |

### 0.1 核心修訂原則

| 原則 | 剛性要求 |
|------|----------|
| **DB / 前台零侵入** | 嚴禁修改**學生學習數據表**；**不得破壞** `practice.py` 既有 public route、query contract、學生端 response contract 與 `skills.{skill_id}` import entry（允許相容 adapter、runtime loader、reload、結構化錯誤回應；見 §0.1.1）；教材例題權威庫之 Gencode 維運欄位增量見 §4.5 |
| **同構題自動變異** | 核心定位是 **Isomorphic Question Generator**：概念不動、難度不動、變數個數與計算公式與原題完全相同，**僅更換數值**；反向求解或題型變更由教材後續獨立 Source 承載，不在此管線融合 |
| **一題一對一隔離** | 教材每一道例題 / 隨堂 / 自我評量 → 一個獨立 `components/{component_id}/` 資料夾 + 單一 `generate.py`；**嚴禁**多題合一、嚴禁 AI 自由發揮融合 |
| **天然順序繼承難度** | 依 `SOURCE_KIND`（`example` / `quiz` / `test`，由 `source_description` 或 canonical problem_type 映射）注入 `ORDER_WEIGHT` 與 `DIFFICULTY_LEVEL`；**禁止**由 `component_id` 或 `src_*` 前綴推斷 |
| **AI 角色定位** | Gemini Flash 僅扮演 **單題同構模板填空搬運工**；在 Registry 固定 Domain 與 `allowed_operations` 白名單內選 operation / presentation；**不得**重判 skill、改派 Domain 或跨 Domain 選模板（見 §1.6） |
| **Skill-Fixed Domain Authority** | `textbook_example.skill_id` → Registry `fixed_domain_key` → `allowed_operations` → AI 選題型與呈現；此鏈為**不可違反** routing authority（見 §1.6） |

#### 0.1.1 `practice.py` 相容性規範（v1.8）

| 允許 | 禁止 |
|------|------|
| 修正 runtime loader、相容 adapter | 改變既有對外 URL |
| 結構化錯誤回應、改善 Unicode | 任意改變必要 request parameters |
| 修正 `importlib.reload` | 破壞既有 response contract |
| 支援 legacy / V2 / V3 `generate` signature | 讓舊 skill 無法出題 |
| — | 把未 verified component 暴露給學生端 |

### 0.2 v1.5 Component Domain Operation 與 Answer Schema Contract 摘要（IMPLEMENTED）

| # | 條款 | 模組 | 狀態 |
|---|------|------|------|
| 1 | `component_id = src_{textbook_example_id}`；`ex_*`/`quiz_*`/`test_*` 僅作 `SOURCE_KIND` | `component_tracker_service.derive_component_id` | IMPLEMENTED |
| 2 | Registry 分層：`skill_id → domain profile`；`induced spec → domain_operation` | `taxonomy_registry.SKILL_DOMAIN_PROFILE` | IMPLEMENTED |
| 3 | Full Matrix 兩層驗證：外殼六欄位 + `answer_schema_key` | `answer_schema_registry` / `domain_matrix_adapter` | IMPLEMENTED |
| 4 | 四層錯誤責任：component / domain / shared contract / packaging | `failure_responsibility` | IMPLEMENTED |
| 5 | 兩種重建入口：Skill Batch Build / Component Targeted Rebuild | `admin_gencode_action_service` | IMPLEMENTED |
| 6 | induced spec 必填：`domain_operation`、`answer_schema_key`、`checker_key` 等 | `induced_spec_contract` | IMPLEMENTED |

### 0.4 v1.6 Skill-Fixed Domain Authority 摘要（SOP 權威 · 2026-06-22）

| # | 條款 | 對應章節 | 狀態 |
|---|------|----------|------|
| 1 | 權威鏈：`skill_id` → `fixed_domain_key` → `allowed_operations` → AI selection | §1.6.1 | SOP |
| 2 | 西堤選餐模式：Skill=餐廳、Domain=菜單、Operation=菜色 | §1.6.2 | SOP |
| 3 | AI 權限邊界；`domain_key` / `recommended_skill` 等非 routing authority | §1.6.3 | SOP |
| 4 | Domain capability gap → `DOMAIN_FUNCTION_MISSING` → Domain Function Extension（§1.8） | §1.6.4 | SOP |
| 5 | 禁止跨 Domain fallback（nearest template / semantic similarity 等） | §1.6.5 | SOP |
| 6 | Routing Domain vs Shared Mathematical Primitive 分離 | §1.6.6 | SOP |
| 7 | 複合題仍由固定主 Domain orchestration | §1.6.7 | SOP |
| 8 | Domain function 可重複使用、禁一題一 function | §1.6.8 | SOP |
| 9 | Operation 選擇須對齊 source facts；`operation_contract_mismatch` | §1.6.9 | SOP |
| 10 | Registry / manifest 版本治理與 `needs_regeneration` | §1.6.10 | SOP |
| 11 | `verified` 八項語意門檻（非僅 compile / smoke） | §1.6.11 | SOP |
| 12 | 實例：`vh_數學B1_DistanceBetweenTwoParallelLines` | §1.6.12 | SOP |

### 0.3 v1.4 Domain 層架構摘要（保留 · 多數已落地）

| # | 條款 | 對應章節 |
|---|------|----------|
| 1 | 數學核心按**數學本質**收斂至 `core/domain/`，不按學制拆分 | §2.5 |
| 2 | `generate.py` 全面減肥為搬運工；禁止 Sympy / distractors / visual_spec 計算 | §2.6 |
| 3 | `skill_id` 硬編碼僅允許停在 Registry 中繼層 | §2.7 |
| 4 | Full Matrix Dictionary 六大欄位由 Domain 一次算完 | §2.3.2、§2.5.4 |
| 5 | 首波實作檢查點：直線方程式 `build_line_equation_matrix` | §2.5.5 |
| 6 | 教材例題影子對接表 `gencode_component_tracker`（§4.5） | §4.5 |
| 7 | 後台定點熱拔插與零重啟動態加載 | §4.6 |

### 0.3 v1.3 務實落地摘要（保留）

| # | 條款 | 對應章節 |
|---|------|----------|
| 1 | 廢除概念聚類與課綱家族 hard-code 特例（原 §1.4.2 / §1.4.3） | — |
| 2 | 一題一 `generate.py` + 題號前綴天然難度 | §1.5 |
| 3 | 極端數學邊界統一由 Domain Function 算子盾牌控制 | §2.3 |
| 4 | 修補半徑縮至單題檔案；核心例題 verified 即可 Partial Publish | §4.3 |
| 5 | 保留 v1.2：AST 精準掃描、Full Matrix Dict、P0 Checker、Taxonomy MVP 六單元 | §2.3、§2.4、§1.4.1 |

| 概念 | 現行實作（已落地） | V3 目標模組 |
|------|-------------------|-------------|
| 外層薄入口 | `skills/{skill_id}.py` | 不變 |
| 執行期調度 | `core/gencode/runtime_skill_wrapper.py` | 不變 |
| 插槽算子庫 | `core/gencode/slot_generators.py` → `SLOT_REGISTRY` | 微元件內部可委派 |
| Phase 3 編譯 | `core/gencode/phase3_skill_codegen.py` → `build_phase3_skill_module_code()` | `core/gencode/skill_wrapper_compiler.py`（抽離封裝） |
| Checker 登錄 | `core/gencode/checker_registry.py` → `CHECKER_CAPABILITIES` | 不變 |
| B4 Payload 驗證 | `core/vocational_math_b4/domain/b4_validators.py` | 不變 |
| Phase 2 閉環修補 | `gencode_closed_loop/controller.py` | 擴展至 component 粒度 |
| K7–K12 題型白名單 | — | `configs/gencode_taxonomy/k12_component_taxonomy.yaml` |
| **共用 Domain 邏輯層** | 分散於 `core/*_domain_functions.py`、`core/vocational_math_b4/domain/` | **`core/domain/{領域}/{主題}_domain.py`**（v1.4+ **IMPLEMENTED**） |
| **Domain 註冊中繼層** | — | **`core/registry/taxonomy_registry.py`**（v1.5：`SKILL_DOMAIN_PROFILE` + `SKILL_TO_DOMAIN` **IMPLEMENTED**） |
| **Answer Schema Registry** | — | **`core/gencode/answer_schema_registry.py`**（v1.5 **IMPLEMENTED**） |
| **教材例題權威庫（維運）** | 既有 `TextbookExample` / Word 匯入 → `textbook_examples` | **`gencode_component_tracker` 影子表**（§4.5） |
| **熱拔插編譯重載** | — | 後台 `admin_trigger_rebuild` → `skill_wrapper_compiler`（§4.6） |
| 圖形語意驗證 | — | `core/gencode/visual_schema_validators.py`（V3 目標） |
| 語意等價批改 | `core/checkers/expression_equivalence_checker.py` 等 | `rational_or_decimal_checker`（V3 擴充） |

---

## 1. 核心設計理念

### 1.1 為何引入「西堤套餐」微元件資料夾結構

舊架構將整個 skill 的 `generate()` / `check()` / 多模板分支壓在**單一巨型** `skills/{skill_id}.py`（或同等體積的 agent skill 腳本）中，造成：

1. **Codegen 失敗半徑過大**：一個 problem type 語法錯誤，整檔 skill 無法 import，前台全面 500。
2. **修補閉環無法精準鎖定**：`gencode_closed_loop/controller.py` 只能依 `GENERATOR_REPAIR_CATALOG` 粗粒度覆寫，難以對應單一題型原子。
3. **插槽庫持續膨脹**：`slot_generators.SLOT_REGISTRY` 已承載 30+ slot；若繼續單檔堆疊，違反 V2 §1.5.6 Anti-Bloat 原則。
4. **並行開發衝突**：多人同時改同一 skill 檔，Git merge 成本高。

**西堤套餐**（Set Meal）比喻：一個 skill 是一套餐；**每一道教材原題**對應一道可獨立烹調、獨立上菜、獨立下架的菜色（`src_4545`、`src_4610`…，一題一 `component_id`）。教材類型（例題／隨堂／自我評量）由 `SOURCE_KIND` 表達，**不得**併入目錄名。套餐對外仍叫同一個名字（`skill_id`），學生端與 DB Schema 無感。

**v1.3 定位一句話**：不做學院派概念聚類，只做**教材原題的同構數值變異生成器**。

### 1.2 標準目錄結構（V3 物理佈局）

本節為 **v1.4 實體檔案物理佈局與向後相容薄外殼** 的剛性防線。  
Codex / 管線產出之每一道教材原題 `py` 程式，**必須**依下列樹狀結構存放；違反即視為 Namespace 污染或向後相容破壞。

```text
skills/                               # 【老屋根目錄 — 行政入口層，路徑雷打不動】
  {skill_id}.py                         # 【自動生成 · 禁止手改】Thin Facade 薄外殼（見 §1.3）
  ...                                   # 其他既有 skill 薄外殼（vh_數學B1_*.py 等）同樣保留於此層

agent_skills_v3/                        # 【新屋軍火庫 — 微元件實體歸宿】
  {skill_id}/                           # 單一 skill 的物理邊界（一 skill 一子目錄）
    skill.json                          # 單元 meta + 動態發布門檻（見 §4.3）
    component_manifest.json             # Phase 3 自動生成：verified / failed 全記錄
    __init__.py                         # 【自動生成 · 禁止手改】新屋路由調度器（_COMPONENT_DISPATCH）
    components/                         # 微元件倉庫根；嚴禁在此層直接堆疊 .py
      src_{textbook_example_id}/        # 一題一資料夾；例：src_4545、src_4610（見 §1.2.2）
        metadata.py                     # 八維度 + ORDER_WEIGHT / DIFFICULTY_LEVEL（強制）
        generate.py                     # 單題同構生成器（Gemini Flash 產物 · 搬運工）
        get_hint.py                     # 三階段引導（強制）
        check.py                        # 薄委派或本地 check 包裝（可選）
        tests/                          # 專屬沙盒；與姊妹 component 物理隔離
          test_component_smoke.py       # 獨立 pytest，不 import 其他 component

configs/generated_registry/
  {scope}_verified_registry.v*.yaml   # Phase 3 尾端同步
```

#### 1.2.1 老屋保留，新屋新蓋（剛性三條）

| # | 層級 | 物理路徑 | 剛性要求 |
|---|------|----------|----------|
| 1 | **主技能薄外殼（老屋入口）** | `skills/{skill_id}.py` | **雷打不動**保留於 `skills/` **根目錄**下。它是行政入口、門面；前台消費者（如 `practice.py`）執行 `importlib.import_module("skills.{skill_id}")` 時**唯一認得**的向後相容防線。**嚴禁**移入 `agent_skills_v3/`、**嚴禁**更名、**嚴禁**移除或改寫 import 路徑。 |
| 2 | **微元件資料夾（新屋倉庫）** | `agent_skills_v3/{skill_id}/components/{component_id}/` | 每一道教材原題 Codegen 產出之 `py` 程式（`metadata.py`、`generate.py`、`get_hint.py` 及專屬測試），**必須嚴格**放在**同一** `skill_id` 子目錄下、**各自獨立**的 `{component_id}/` 資料夾內。 |
| 3 | **禁止大雜燴** | — | **嚴禁**將多道題的 `py` 程式大雜燴地擠在同一目錄（含 `components/` 根層、`agent_skills_v3/{skill_id}/` 根層、或跨 `skill_id` 共用目錄）。每個 `src_{textbook_example_id}/` 資料夾內部**必須**獨立包含 `metadata.py`、`generate.py`、`get_hint.py` 及專屬 `tests/`，以確保 Namespace 完全隔離；`failed` 題型與 `verified` 題型在物理上互不干涉，定點修補半徑不污染姊妹題。 |

#### 1.2.2 `component_id` 物理命名契約（第一階段 · 剛性）

為在第一階段**完全消除** AI 對題型前綴（`ex_*` / `quiz_*` / `test_*`）的分類與命名幻覺，物理微元件目錄命名**剛性規定如下**：

| 項目 | 規範 |
|------|------|
| **禁止** | 管線或 AI **不得**猜測、推斷或自行發明 `ex_*` / `quiz_*` / `test_*` 作為硬碟目錄名 |
| **`component_id` 公式** | `src_{textbook_example_id}` — 直接取自 `textbook_examples.id` 主鍵 |
| **命名範例** | `textbook_examples.id = 4545` → `component_id = "src_4545"` |
| **硬碟實體路徑** | `agent_skills_v3/{skill_id}/components/src_{textbook_example_id}/` |
| **影子表對齊** | `gencode_component_tracker.component_id` **必須**與上述目錄名完全一致 |

> **備註**：`source_description`（例題 / 隨堂 / 自我評量）與 `ORDER_WEIGHT` / `DIFFICULTY_LEVEL` 仍由 §1.5 依教材語意注入 `metadata.py`；**僅**硬碟目錄名與 `component_id` 錨定主表主鍵，不經 AI 命名。

**老屋不動、新屋新蓋** 的行政契約（與上表互補）：

- **老屋（不變）**：`skills/` 根目錄薄外殼路徑、`SkillInfo` DB 表、`GENERATOR_SPECS` 白名單矩陣、`practice.py` 的 `importlib.import_module("skills.{skill_id}")` 調度入口——**全部不變**。
- **新屋（增量）**：數學邏輯與多模板分支**僅**遷入 `agent_skills_v3/{skill_id}/components/{component_id}/`；Phase 3 編譯器掃描 `verified` 子目錄後，自動寫入 `component_manifest.json`、`agent_skills_v3/{skill_id}/__init__.py`（新屋路由），並同步覆寫原位 `skills/{skill_id}.py`（老屋門面）。

### 1.3 自動生成 `__init__.py` 路由調度器

`core/gencode/skill_wrapper_compiler.py`（現行邏輯位於 `phase3_skill_codegen.build_phase3_skill_module_code`）在 Phase 3 執行：

1. 掃描 `agent_skills_v3/{skill_id}/components/` 下各 `{component_id}/` 子目錄，讀取 `component_manifest.json` 中 `status == "verified"` 的列。
2. 為每個 `component_id` 生成 import 與 dispatch 表項。
3. **寫入新屋路由**：更新 `agent_skills_v3/{skill_id}/__init__.py` 之 `_COMPONENT_DISPATCH`（禁止手改）。
4. **覆寫老屋門面**：同步自動覆寫原位 `skills/{skill_id}.py` Thin Facade（與 V2 形狀一致；**嚴禁**移出 `skills/` 根目錄，見 §1.2.1）。

**生成的 `__init__.py` 職責邊界**（與 V2 Thin Facade 同構）：

```python
# ── 自動生成，禁止手改 ──
from __future__ import annotations
from typing import Any
import random

from core.gencode.runtime_skill_wrapper import check_answer as _global_check
from core.gencode.runtime_skill_wrapper import generate_for_skill as _global_generate

SKILL_ID = "<skill_id>"
GENERATOR_SPECS = [...]  # 由 manifest 編譯
GENERATOR_KEYS = [...]

# component 級動態 import（僅 verified 組件）
_COMPONENT_DISPATCH: dict[str, Any] = {
    "<component_id>": {
        "generate": <callable from components.{component_id}.generate>,
        "get_hint": <callable from components.{component_id}.get_hint>,
    },
    ...
}

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict[str, Any]:
  # 1) 依 GENERATOR_SPECS 抽 problem_type / component_id
  # 2) 若 component 已 verified → 呼叫 _COMPONENT_DISPATCH[component_id]["generate"]
  # 3) 否則 fallback → _global_generate(SKILL_ID, GENERATOR_SPECS, ...)
  ...

def check(user_answer, correct_answer, question_payload=None):
  return _global_check(user_answer, correct_answer, payload=question_payload)

def get_hint(step: int, question_payload: dict | None = None) -> str:
  component_id = str((question_payload or {}).get("component_id") or "")
  fn = _COMPONENT_DISPATCH.get(component_id, {}).get("get_hint")
  if fn:
      return fn(step, question_payload)
  return ""
```

**向後相容保證**：

| 消費端 | 契約欄位 | V3 行為 |
|--------|----------|---------|
| `practice.py` | `generate(level, seed)` | 不變；仍 import `skills.{skill_id}` |
| DB `SkillInfo` | `skill_id` 字串 | 不變 |
| `GENERATOR_SPECS` | `problem_type_id`, `checker_key` | 由 manifest 編譯，欄位集合不擴張 |
| `runtime_skill_wrapper` | `answer_contract` 驅動批改 | `check()` 仍委派全域 checker 鏈 |
| RAG / Chroma | `skill_id:family_id` | 不變（AGENTS.md §9） |

### 1.4 Taxonomy Gate（v1.7 修訂 · 非生成阻擋閘門）

**權威設定檔**：`configs/gencode_taxonomy/k12_component_taxonomy.yaml`

v1.3 **不再**以 Taxonomy 驅動概念聚類或題型拆分。  
**v1.7 修訂**：Taxonomy **不得**作為生成入口阻擋；未知 skill 須走 §1.7 Auto-Bootstrap。  
`component_id` 由教材實體題號決定（§1.5），**不由** Taxonomy 命名。

#### 1.4.1 MVP 範疇（v1.7 · 降級為審核提示，非生成阻擋）

> **DEPRECATED（v1.7 作為生成阻擋）**：「不在 MVP 六單元 → `human_approval_required` 且不予 Phase 2」已廢止。  
> MVP 清單僅供 **風險提示**、`review_required` 標記與灰度發布參考；**不得**阻止 Auto-Bootstrap 或 Shadow Bridge。

`configs/gencode_taxonomy/k12_component_taxonomy.yaml` 內 `mvp_scope: v1` 仍記錄首波六類核心單元（直線方程式、排列組合、機率、統計、國中一次方程、國中二次函數），用途如下：

| 用途 | 允許 | 禁止 |
|------|------|------|
| 標記 `review_required=true` | ✅ | — |
| 優先排程人工審核 | ✅ | — |
| 阻擋 Phase 2 / Shadow Bridge | — | ❌ |
| 映射為 `unsupported_task_type` | — | ❌ |

**v1.7 剛性規則**：

1. `skill_id` 不在 MVP → 仍須進入 Auto-Bootstrap；建立 **draft** taxonomy（`taxonomy_status=ai_inferred`）。
2. `skill_id` 在 MVP → 可標記較低審核優先級；**不**改變生成路徑。
3. 僅 **Publish Gate** 可因未通過驗證而阻擋學生端可見性。

### 1.5 元件物理排序與天然難度契約

本節為 v1.3 **一題一 code** 與**天然順序排序**的剛性法規，取代舊版概念聚類與人工難度演算法。

#### 1.5.1 一題一對一物理隔離

`pipeline_orchestrator` 在 Phase 1 讀取案源時：

1. **不進行**任何概念聚類、題型融合或「大膽拆分」。
2. 每一筆 usable Source（例題、隨堂練習、自我評量）**強制**對應一個獨立 component 資料夾與**單一** `generate.py`。
3. `component_id` 直接取自教材實體題號或 `source_id`：

| 教材類型 | `component_id` 命名 | 範例 |
|----------|---------------------|------|
#### 1.5.1 實體 component_id 與教材類型分離（v1.5 · 剛性）

| 概念 | 規範 | 範例 |
|------|------|------|
| **`component_id`** | `src_{textbook_example_id}` | `textbook_examples.id=4545` → `src_4545` |
| **`SOURCE_KIND`** | `example` \| `quiz` \| `test`（教材類型，**不得**併入 component_id） | 例題 → `example` |
| **`ORDER_WEIGHT`** | `example=10`, `quiz=20`, `test=30`；由 `source_description` / canonical `problem_type` 映射 | 隨堂 → `20` |
| **`DIFFICULTY_LEVEL`** | `example/quiz=easy`, `test=hard` | 自我評量 → `hard` |
| **`IS_REQUIRED_CORE`** | Taxonomy 靜態或架構師預置；AI / repair loop **不得**改寫 | `True` / `False` |

> **DEPRECATED（v1.5）**：以 `ex_{n}` / `quiz_{n}` / `test_{n}` 作為**實體** `component_id` 或硬碟目錄名。舊前綴僅允許出現在歷史報告；新管線一律 `src_*`。

#### 1.5.2 天然難度權重注入

管線在生成 `metadata.py` 骨架時，依 **`SOURCE_KIND`**（由 `core/gencode/source_kind_resolver.py` 自教材列推得）**自動**注入：

| `SOURCE_KIND` | `ORDER_WEIGHT` | `DIFFICULTY_LEVEL` | 語意 |
|---------------|----------------|-------------------|------|
| `example` | `10` | `"easy"` | 例題 / 示範 |
| `quiz` | `20` | `"easy"` | 隨堂練習 |
| `test` | `30` | `"hard"` | 自我評量 / 課後 |

```python
# metadata.py — 管線自動注入（禁止 AI 改寫）
COMPONENT_ID: Final[str] = "src_4545"
SOURCE_KIND: Final[str] = "example"
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "easy"
IS_REQUIRED_CORE: Final[bool] = False
```

**出題順序**：Phase 3 編譯 `GENERATOR_SPECS` 時依 `ORDER_WEIGHT` 升序排列；前台抽題可優先例題再隨堂再評量，**無需**額外難度推斷模組。

#### 1.5.3 同構變異契約（Isomorphic Contract）

每個 `generate.py` 僅服務**一道**原題，執行期行為：

- **固定**：題型結構、解題步驟數、變數個數、計算公式拓撲、`presentation_mode`、checker。
- **可變**：經 `seed` 驅動的數值參數（由 Domain Function `build_problem_matrix(seed=...)` 產生）。
- **禁止**：改變題型（如選擇題變填充題）、反向求解（除非該反向題在教材中有獨立 Source 與獨立 component）。

---

## 1.6 Skill-Fixed Domain Authority 與西堤選餐模式（v1.6 · 不可違反規則）

本節為 Gencode × AgentSkillV3 的 **routing authority 憲法**。凡與本節衝突之舊敘述（含暗示 AI 可選 Domain、nearest template fallback、跨 Domain 語意改派）均以本節為準。

### 1.6.1 核心法則：Skill-Fixed Domain Authority

教材例題的權威鏈**必須固定**為：

```text
textbook_example.skill_id
→ Skill Registry
→ fixed_domain_key
→ allowed_operations
→ AI 選擇題型與呈現
```

| # | 剛性規定 |
|---|----------|
| 1 | `textbook_example.skill_id` 是資料庫**權威事實**；管線自 `textbook_examples` 讀取，唯讀 |
| 2 | AI **不得**重新判斷、修改或建議更換 skill |
| 3 | 每個 skill 必須由 Registry 綁定**唯一**主 Routing Domain（`fixed_domain_key`） |
| 4 | AI **不得**選擇、覆寫或更換 Domain |
| 5 | Domain 能力不足時，**必須**擴充原 Domain 的通用 function；**禁止**改派其他 Domain |
| 6 | **禁止**將例題改派到其他 Domain 以「通過」生成 |

> **Deterministic Gate**：`Registry.fixed_domain_key` 為 Phase 1 之後所有管線步驟的**不可被 AI 覆寫**閘門；後端必須在 AI 回應進入 scaffold 前完成解析與白名單校驗。

### 1.6.2 西堤選餐模式

| 概念 | 西堤選餐比喻 | 管線語意 |
|------|-------------|----------|
| **Skill** | 已確定進入哪一家餐廳 | 行政歸屬；由 `textbook_example.skill_id` 鎖定 |
| **Domain** | 該餐廳固定菜系與菜單 | Registry `fixed_domain_key` + `allowed_operations` |
| **Operation** | 菜單中的數學題型 | `domain_operation` / `problem_type_id` |
| **Data presentation** | 盤飾與配菜呈現 | `text`／`image`／`graph`／`readonly_table`／`canvas`（§2.0.1；**非**作答模式） |
| **Answer interaction** | 學生怎麼吃（西堤作答套餐） | `answer_type`：`short_answer`／`single_choice`／`multi_part`／`table_fill`／`drawing`（§2.0.2） |
| **Input widget** | 餐具細節 | `presentation_mode` + `ui_contract.interaction_mode`（§2.2；套餐內輸入元件樣式） |
| **Question wording** | 題幹文字包裝 | Story Layer、`SCENARIO_POOL`、f-string 模板 |

因此：

```text
Skill 決定餐廳
Domain 決定菜單
AI 只能點菜與決定呈現
缺少菜色時擴充原菜單，不得換餐廳
```

本比喻與 §1.1「西堤套餐」微元件架構互補：套餐（skill）內每道菜（component）必須在**同一餐廳菜單**（固定 Domain）內點選，不得跨館借菜。

### 1.6.3 AI 權限邊界（v1.8）

**AI 可以分析**（不得改變 Routing Domain）：

```text
problem_type_id
domain_operation 候選
required_capabilities
parameterization strategy
answer_schema_key 候選
checker_key 候選
presentation_mode
answer_type
source facts
story template
required validation facts
question_intent
題幹文字、選項結構、語言表達
```

**AI 不可以決定**：

```text
skill_id
fixed_domain_key
curriculum / grade / volume / chapter / section
跨 Domain routing
是否改用 generic domain
是否跳過 Domain Function Extension
是否直接標 verified
重新分類到其他 skill
覆寫 Registry 的 fixed_domain_key
```

後端必須覆蓋或剝除 AI 回應中的：

```text
domain_key
recommended_domain
domain_family
recommended_skill
nearest_template
fallback_domain
```

若 AI response 仍包含上述欄位：**非 routing authority**；Phase 1 merge、induced spec 寫入前剝除或覆蓋；僅 `taxonomy_registry` 之 `fixed_domain_key` 有效。

### 1.6.4 Domain Capability Gap 與 Function Extension 入口

當固定 Domain **無法**處理教材例題所需數學能力時，系統**不得**改派其他 Domain；**必須**進入 **Domain Function Extension**（§1.8）。

**正確可恢復狀態**：`DOMAIN_FUNCTION_MISSING` 或 `DOMAIN_OPERATION_MISSING`（舊名 `unsupported_domain_operation` 僅作 backward compatibility，**不得**計入 `unsupported_count` 或映射為 `UNSUPPORTED_TASK_TYPE`）。

至少應記錄 capability gap：

```text
skill_id
fixed_domain_key
requested_capability
proposed_operation
proposed_function_name
available_operations
missing_domain_function
related_example_ids
failure_responsibility = domain_capability_gap
```

| 行為 | 規定 |
|------|------|
| 不得 `verified` | 在 function 測試通過前，沙盒與 manifest 皆排除 |
| 不得 `publish` | 不進入 `GENERATOR_SPECS` |
| 不阻斷姊妹題 | 同 skill 其他已有 function 的 components 仍可生成／發布（§4.3） |
| 必須啟動 | Domain Function Extension Phase（PipelineFlow §1.5） |

建議 tracker：`gencode_status = 'failed'` + `gencode_error_log` 結構化 `error_code=DOMAIN_FUNCTION_MISSING`；或 migration 後使用 `domain_function_missing`（§4.5.2）。

### 1.6.5 禁止跨 Domain Fallback

下列行為**明文禁止**（production 管線）：

```text
global template fallback
nearest-template fallback
cross-domain semantic similarity routing
AI-selected domain override
compatible domain fallback
generic domain fallback / generic.structured 作為 Routing Domain
generic line-equation fallback（當 fixed domain 非 line_equation 時）
在 operation 不支援時改派其他 Domain
registry missing → AI inferred domain 作為 routing authority
```

**唯一正確行為**：

```text
DOMAIN_FUNCTION_MISSING / DOMAIN_OPERATION_MISSING
→ Domain Function Extension（§1.8）
→ Domain Function Tests
→ 更新 allowed_operations
→ Resume Shadow Bridge
→ component generation
```

> **與執行期 slot fallback 之區分**：`runtime_skill_wrapper` 對**未 verified 之 legacy skill** 的 `slot_generators` 路徑屬執行期降級，**不構成** Gencode V3 管線之跨 Domain 授權。  
> **與分析工具之區分**：未發布 scaffold 草稿、測試用分析輔助工具**不得**作為 production routing、不得 `verified`、不得進 manifest／wrapper／學生端。

### 1.6.6 Routing Domain 與 Shared Mathematical Primitives

為避免 Domain 重複實作，SOP **區分**兩類能力：

| 類型 | 定義 | 路由影響 |
|------|------|----------|
| **Routing Domain** | Skill 唯一綁定之主 Domain（`fixed_domain_key`） | 決定 `allowed_operations` 與 orchestration 歸屬 |
| **Shared Mathematical Primitive** | 可跨 Domain 呼叫的底層數學原語 | **不**改變 skill / domain 歸屬 |

共用 primitive 範例（非窮舉）：

```text
直線係數正規化
分數化簡
方程式求解
距離公式
絕對值方程
座標幾何基礎運算
```

共用 primitive：

```text
不是可重新路由的 Domain
不得改變 skill/domain 歸屬
只提供底層數學能力
```

主 Routing Domain 的 entry function 可 `import` 或委派 primitive；但 **induced spec 的 `domain_operation` 仍須落在該主 Domain 白名單內**。

### 1.6.7 複合題處理原則

複合題**不得**因此跨 Domain 改派。

範例：

```text
先求兩平行線距離
再利用距離求面積
```

仍由**固定主 Domain**負責 orchestration，並呼叫共用 primitive 或 helper capability（如 `area_using_parallel_distance` 作為**同一主 Domain** 內之 operation，而非改派 `line_equation` Domain）。

僅在**人工治理**確認「教材 skill mapping 本身錯誤」時，方可由管理者修改資料庫或 Registry；**AI 不得自行改派**。

### 1.6.8 Domain Function 設計限制

新增 Domain function 時**禁止**：

```text
以 example_id 命名
一題一 function
skill_id 專屬 if
為通過單一題目寫硬編碼常數
```

新增 function **必須**：

```text
代表可重複使用的數學能力
具有明確 input/output contract
可支援多筆同構教材例題
有獨立數學測試
不得依賴特定 example_id
```

### 1.6.9 Operation 選擇驗證

固定 Domain **不代表** AI 選擇 operation 一定正確。後端應依 **source facts** 驗證：

```text
是否含參數
題目要求的是距離、方程式、參數或關係
答案 cardinality
presentation_mode
single_choice / short_answer
題幹 intent
```

若 AI 選擇與教材結構不一致 → **`operation_contract_mismatch`**：

| 規定 | 說明 |
|------|------|
| 不得直接生成 | Phase 2 Codegen 前 fail-fast |
| 不得發布 | 不進 manifest / `GENERATOR_SPECS` |
| 修復路徑 | 修正 induced spec 或重跑 Phase 1 分類；**禁止**改派 Domain |

### 1.6.10 Registry 與版本治理

**Registry mapping** 至少保存：

```text
skill_id
fixed_domain_key
domain_version
registry_revision
mapping_reason
supported_capabilities
```

**Component / manifest** 至少保存：

```text
skill_id
component_id
domain_key
domain_version
domain_operation
operation_version
registry_revision
```

重新生成、重新包裝、發布時**必須**驗證：

```text
component.domain_key == current Registry fixed_domain_key
```

不一致 → **`needs_regeneration`**（§4.5.2）；**不得**沿用舊 component 靜默發布。

### 1.6.11 Verified 定義補強

`verified` **必須同時滿足**下列語意門檻（缺一不可）：

```text
skill identity verified
fixed domain identity verified
operation whitelist verified
source completeness passed
mathematical oracle passed
question-answer semantic consistency passed
presentation topology passed
runtime contract passed
```

**僅**下列條件**不得**視為 `verified`：

```text
Python 可編譯
runtime smoke 通過
schema 欄位存在
answer 與 payload 自洽
```

§4.1 沙盒清單為必要條件，但**不足**以單獨構成 verified；須疊加本節八項語意門檻。

### 1.6.12 實例：平行線距離 Skill

| 項目 | 值 |
|------|-----|
| `skill_id` | `vh_數學B1_DistanceBetweenTwoParallelLines` |
| Registry `fixed_domain_key` | `coordinate_geometry.parallel_lines_distance`（專案 Registry 實際 key 以 `taxonomy_registry` 為準） |

**AI 可從該 Domain 白名單選取**（示意；以 Registry `allowed_operations` 為準）：

```text
distance_between_parallel_lines
solve_parameter_from_parallel_distance
construct_parallel_line_at_distance
parallel_lines_distance_single_choice
area_using_parallel_distance
```

**AI 不得改派為**（屬其他 Domain / 非白名單 operation）：

```text
perpendicular_bisector
triangle_median_line
point_slope_line
line_from_two_points
slope_intercept_line
```

若原 Domain 尚未提供所需 operation → **`DOMAIN_FUNCTION_MISSING`**，啟動 §1.8 Domain Function Extension；**禁止**改用其他 Domain 之相似模板。

### 1.7 Auto-Bootstrap 與分層 Gate（v1.8）

#### 1.7.1 Auto-Bootstrap 定義

Auto-Bootstrap **自動建立**（skill／component 層 · 見 §1.10 補充 **domain 層**）：

- V3 skill package（`agent_skills_v3/{skill_id}/`）
- manifest skeleton、`skill.json` draft
- `components/src_{example_id}/` 目錄
- tracker rows、induced spec 草案
- wrapper skeleton
- capability gap 紀錄；**若缺 verified domain provider** → §1.10 Automated Domain Bootstrap（**不得**僅產 gap report 或要求老師寫程式）

Auto-Bootstrap **不得自動改變**：

- `skill_id`、skill 中文名稱
- curriculum、grade、volume、chapter、section
- `fixed_domain_key`（須 deterministic 解析，見下）
- 已確認 taxonomy、已確認 answer schema

#### 1.7.2 Registry 與 Skill-Domain Binding

| 情境 | 行為 |
|------|------|
| skill 已有 authoritative binding | 直接使用 `fixed_domain_key`（confirmed binding） |
| registry row 缺失，capability match 命中 verified provider | derived binding；重用 provider |
| registry row 缺失，capability **無** verified provider | `DOMAIN_CAPABILITY_UNRESOLVED`／`PARTIAL` → §1.10 Bootstrap |
| registry row 缺失，deterministic mapping 可解析且 domain 已 verified | 由 mapping 建立 registry row（`source=deterministic_mapping`） |
| 完全找不到 provider 且無法 Bootstrap | 安全停止該 component；**禁止**錯配相近 domain |
| — | **禁止** AI 自由猜 Routing Domain；**禁止**標 `UNSUPPORTED_TASK_TYPE`（教材可程式化時） |

AI 可推論 operation 與 capability；**不可**推論 Routing Domain。

#### 1.7.3 Bootstrap Gate vs Publish Gate

**Bootstrap Gate**（生成入口）只檢查：

- `skill_id`、`example_id` 存在
- 教材內容可讀
- skill-domain binding **可 deterministic 解析**（或明確 `DOMAIN_BINDING_MISSING`）
- AI runtime 可用
- 必要輸入資料存在

**不得**要求：V3 package、component、wrapper、operation、Domain function 已存在；skill 在 allowlist；taxonomy 已人工 verified。

若 operation／function 不存在 → 進入 **Domain Function Extension**（§1.8），**不是** unsupported。

**Publish Gate**（學生端發布）才檢查：component `verified`、Domain function tests passed、compile、smoke、answer schema、oracle、semantic、topology、integrity、variation audit、wrapper 可執行、無 blocker。

| 檢查項 | Bootstrap Gate | Publish Gate |
|--------|:--------------:|:------------:|
| skill-domain binding 可解析 | ✅ | ✅ |
| Shadow Bridge 已執行（function 就緒後） | 目標 ✅ | — |
| component `verified` | — | ✅ |
| Domain function tests passed | — | ✅ |
| MVP allowlist | ❌ 不得作為條件 | ❌ |

#### 1.7.4 其他 Bootstrap 規則

- 未知 skill（無 package／tracker）**不是** `UNSUPPORTED_TASK_TYPE`
- `SHADOW_BRIDGE_NOT_EXECUTED` 為 pipeline defect，**禁止**映射為 `UNSUPPORTED_TASK_TYPE`
- skill-specific allowlist **不得**作為生成入口；僅可用於灰度／風險提示
- 一題一 `src_{example_id}`；單題失敗不阻斷姊妹題；僅 verified 可發布

### 1.8 Domain Function Extension Contract（v1.8 · 限縮範圍 v1.10）

> **範圍**：本節僅適用於 **fixed domain 已存在且為 verified provider**、但缺少特定 operation／function 之情境。若 capability resolver 判定 **無可用 domain provider**（`DOMAIN_CAPABILITY_UNRESOLVED`／`PARTIAL`），**必須**改走 §1.10 Automated Domain Bootstrap，**不得**以相近 domain 硬套或僅產 gap report。

當 Domain Capability Check 確認固定 Domain 缺少 operation 或 function 時，**必須**執行本階段（詳細時序見 PipelineFlow §1.5）。

```text
Skill-Domain Binding Resolution
→ Domain Capability Check
→ Existing Function Search
→ Function Gap Detection
→ Domain Function Specification
→ Domain Function Generation / Extension
→ Domain Function Tests
→ Registry allowed_operations 更新
→ Resume Shadow Bridge
→ Component Generation
```

#### 1.8.1 Capability Check

逐教材例題分析（AI 僅描述，不改 Domain）：

- `required_capabilities`
- expected `domain_operation`
- `answer_schema_key`
- `validation_facts`
- visual requirements
- mathematical invariants

#### 1.8.2 Existing Function Search

只可搜尋：

1. 該 skill **固定 Domain** 的 `allowed_operations` 與 canonical functions
2. 該 Domain 明確允許的 **shared mathematical primitives**（§1.6.6）

須確認：是否已有相同／等價 function、是否可組合既有 function、是否僅 operation registry 尚未註冊。**禁止**在 component 內重寫數學核心。

#### 1.8.3 Function Gap Record

```text
skill_id
fixed_domain_key
requested_capability
proposed_operation
proposed_function_name
input_contract
output_contract
answer_schema_key
mathematical_invariants
edge_cases
related_example_ids
```

#### 1.8.4 Add Function to Fixed Domain

新 function **必須**：

- 位於固定 Domain 的 `core/domain/...` canonical 模組
- 不含 `skill_id`、`example_id`、教材硬編碼常數
- 可重用於多筆同構例題
- 回傳完整 Full Matrix Dictionary（§2.3.2）
- 保持 Fraction / Decimal / SymPy 精確性

#### 1.8.5 Domain Function Tests

通過前**不得**建立 verified component。須涵蓋：一般／邊界／非法輸入、數學不變量、多 seed、answer consistency、distractor uniqueness、visual consistency、與既有 Domain 回歸。

失敗 → `DOMAIN_FUNCTION_TEST_FAILED` 或 `DOMAIN_FUNCTION_EXTENSION_FAILED`。

#### 1.8.6 Resume Generation

function 測試通過後：更新 `allowed_operations` → 重建 induced spec → Shadow Bridge → `src_{example_id}` → compile / smoke / verification。

### 1.9 錯誤碼與狀態機（v1.8 規範權威）

#### 1.9.1 錯誤碼

| 錯誤碼 | 語意 |
|--------|------|
| `DOMAIN_BINDING_MISSING` | 無 deterministic skill-domain binding（**先** capability match；真缺 domain 走 §1.10） |
| `DOMAIN_CAPABILITY_UNRESOLVED` | 無 verified provider 可滿足 required capabilities（**可恢復** · §1.10 Bootstrap） |
| `DOMAIN_CAPABILITY_PARTIAL` | 部分 capability 有 provider；缺項走 §1.10 |
| `DOMAIN_BOOTSTRAP_PENDING` | Automated Bootstrap 進行中 |
| `DOMAIN_BOOTSTRAP_FAILED` | Bootstrap 失敗；保留 evidence |
| `DOMAIN_HEALER_EXHAUSTED` | Healer 達輪次上限；待管理員審查 |
| `DOMAIN_CANDIDATE_READY` | candidate 通過 Gate；待教師確認 |
| `DOMAIN_MODULE_MISSING` | 固定 Domain 模組不存在 |
| `DOMAIN_OPERATION_MISSING` | operation 未註冊 |
| `DOMAIN_FUNCTION_MISSING` | function 不存在（**可恢復**） |
| `DOMAIN_FUNCTION_EXTENSION_PENDING` | Extension 進行中 |
| `DOMAIN_FUNCTION_EXTENSION_FAILED` | Extension 失敗 |
| `DOMAIN_FUNCTION_TEST_FAILED` | Domain function 測試失敗 |
| `SHADOW_BRIDGE_NOT_EXECUTED` | 應執行卻未執行（**pipeline defect**） |
| `SHADOW_BRIDGE_FAILED` | Shadow Bridge 執行失敗 |
| `COMPONENT_GENERATION_FAILED` | codegen 失敗 |
| `COMPONENT_COMPILE_FAILED` | 編譯失敗 |
| `COMPONENT_SMOKE_FAILED` | smoke 失敗 |
| `COMPONENT_VERIFICATION_FAILED` | 驗證失敗 |
| `PACKAGING_FAILED` | wrapper／manifest 失敗 |
| `UNSUPPORTED_TASK_TYPE` | **僅**教材本質不可程式化 |

規則：`SHADOW_BRIDGE_NOT_EXECUTED` **禁止**映射為 `UNSUPPORTED_TASK_TYPE`。metadata／registry／package 缺失**不是** unsupported。

#### 1.9.2 狀態機（Target V3 Model）

**Pipeline / 內部階段**（未必全部持久化至 DB）：`discovered`、`classified`、`domain_binding_resolved`、`domain_capability_checking`、`domain_function_missing`、`domain_extension_pending`、`domain_extension_testing`、`domain_extension_verified`、`bootstrapped`、`draft_written`、`compile_passed`、`smoke_passed`、`packaged`、`published`、`domain_extension_failed`、`generation_failed`、`compile_failed`、`smoke_failed`、`verification_failed`、`unsupported`

**Tracker 持久化**：見 §4.5.2（Current Production vs Target；migration 前以 `failed` + 結構化 `error_code` 相容）。

### 1.10 Automated Domain Bootstrap & Domain Healer（v1.10 · **最終產品必要能力**）

> **產品定位（不可降級）**：本節為 **最終產品必要能力**，不是未來選配功能。正式產品使用者為一般數學老師；**不得**假設老師會使用 Codex、Python、Git、registry、domain、capability、scaffold、validator 等工程術語。教師端敘事見 [Gencode與AgentSkillV2整合總體設計_v0.3.md §14](../Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md)；端到端時序見 [SOP_Gencode_AgentSkillV3_PipelineFlow.md §1.7](./SOP_Gencode_AgentSkillV3_PipelineFlow.md)。

#### 1.10.1 觸發條件與分流

Phase 1 induced spec 完成後，resolver 採 **capability-first matching**（§1.6、ProblemType SOP §1.7）：

| 結果 | 行為 |
|------|------|
| 全部 `required_capabilities` 有 **verified** provider | 重用既有 domain → Shadow Bridge → component codegen |
| `matched_capabilities` 部分、`missing_capabilities` 非空 | `DOMAIN_CAPABILITY_PARTIAL` → Gap Report → §1.10.3 Bootstrap |
| 無任何可用 provider | `DOMAIN_CAPABILITY_UNRESOLVED` → Gap Report → §1.10.3 Bootstrap |
| 固定 domain 已存在但缺 operation（§1.8 範圍） | `DOMAIN_FUNCTION_MISSING` → §1.8 Extension（**不**新建 domain） |

**剛性規則**：

1. `SKILL_TO_DOMAIN` 僅為 **confirmed binding** 加速路徑，**不是** V3 使用資格門檻；未註冊 skill 可用 **derived binding** 正常進入 Bootstrap Gate。
2. 無完整 provider 時 **必須安全停止**，**禁止**錯配相近 domain 通過驗證。
3. 新 domain **建立一次**後，所有具相同 capability 的 skills **共用**；**禁止** skill-specific 或 example-specific domain。

#### 1.10.2 Domain 狀態模型（draft → candidate → verified）

| 狀態 | 定義 | 正式 resolver | 學生端 | 教師預覽 |
|------|------|:-------------:|:------:|:--------:|
| `draft` | AI 初步產物；僅存在隔離區 | ❌ | ❌ | ❌ |
| `candidate` | 通過 §1.10.5 基本品質閘門；可 dry-run | ❌ | ❌ | ✅ |
| `verified` | 完整驗證 + 教師／管理員核准；併入正式 provider 集合 | ✅ | ✅（經 Publish Gate） | ✅ |

**升格路徑**：

```text
draft（AI 產出）
→ 自動測試 + Healer（§1.10.6）
→ candidate（基本 Gate 通過）
→ 題目預覽 + 教師教學語意確認（§1.10.8）
→ verified（管理員／教師核准）
→ 更新正式 provider 索引（append · non-destructive）
→ 自動重跑原失敗 components
```

**禁止**：AI 產生的 domain **不得**直接修改正式 registry 或立即發布至學生端。

#### 1.10.3 Automated Domain Bootstrap — 輸入

Bootstrap 觸發前須完成成本控制鏈（§1.10.9）。輸入至少包括：

| 欄位 | 說明 |
|------|------|
| `problem_type_id` | induced spec 錨點 |
| `required_capabilities` | 題型語意所需能力集合 |
| `matched_capabilities` / `missing_capabilities` | resolver 輸出 |
| 教材例題集合 | 同 problem_type／同 capability 缺口之聚合例題 |
| `answer_contract` | equivalence、cardinality、格式 |
| `presentation_mode` / `answer_type` | 西堤套餐與 UI contract |
| `source_hashes` | Layer 1 標準化雜湊；未變則重用 artifact |
| 相近既有 domains | capability index 比對結果 |

#### 1.10.4 Automated Domain Bootstrap — 產物

產物至少包括（**全部**寫入 **candidate 隔離區**，不得 skill／example 專用）：

```text
domain manifest
純數學 core（domain operations 以外）
domain operations
capability declarations
matrix adapter
component scaffold contract
answer contract
validator（獨立於 generator）
unit tests
property tests
integration fixtures
題目預覽
成本與修補紀錄（bootstrap_run_id、token、輪次）
registry draft（candidate 區 · 非 production）
```

**禁止產物**：skill-specific domain、example-specific domain、以 `example_id` 命名之 function。

#### 1.10.5 Candidate 驗證與升格 Gate

`candidate` 升格前 **至少** 通過下列檢查（詳細時序見 PipelineFlow §1.7.3）：

| # | Gate | 說明 |
|---|------|------|
| 1 | module import | candidate 模組可 import |
| 2 | py_compile | 語法合法 |
| 3 | registry consistency | draft entry 與 manifest 一致 |
| 4 | operation callable | 各 operation 可呼叫且回傳契約矩陣 |
| 5 | 獨立數學 oracle | **與 generator 分離**之答案驗證 |
| 6 | answer contract | checker dispatch 正確 |
| 7 | 固定 seed 可重現 | 同 seed 同 payload |
| 8 | 不同 seed 合理變異 | 參數空間非退化 |
| 9 | 多 seed integrity | 批量 smoke |
| 10 | 教材同構檢查 | 與 source facts 結構一致 |
| 11 | UI contract | `answer_type`／呈現拓撲 |
| 12 | 禁止 skill/example 特例掃描 | 靜態掃描無 `skill_id`／`example_id` 硬編碼 |
| 13 | 既有 domain 回歸測試 | 不污染 verified provider |
| 14 | 安全與超時檢查 | 執行時間與資源上限 |

**三元分離（剛性）**：

```text
generator algorithm ≠ answer oracle ≠ integrity validator
```

**禁止**用同一段生成邏輯同時證明自己正確。validator 降標以通過測試 **一律視為 Healer 違規**（§1.10.6）。

#### 1.10.6 Domain Healer 規則

當 `candidate` 生成後結構化測試失敗，啟動 Healer **局部修補**：

```text
candidate 生成
→ 結構化測試失敗
→ healer 只修失敗 domain（candidate 隔離區）
→ 只重跑失敗測試與必要回歸
→ 最多 N 輪（預設 N 由管線設定；超限 → 待管理員審查）
→ 通過後繼續 candidate 預覽流程
→ 超過限制則保留 evidence → 管理員審查
```

**Healer 禁止項**：

```text
修改 production core
修改已 verified domain
新增 skill 白名單
新增教材 ID 特例
為通過測試而降低 validator 標準
```

#### 1.10.7 缺少 capability 時的完整閉環（教師視角）

```text
DOMAIN_CAPABILITY_UNRESOLVED / PARTIAL
→ 建立 Domain Gap Report
→ 聚合同類教材例題
→ Automated Domain Bootstrap
→ 建立 candidate domain
→ 產生 core / operations / registry draft / adapter / validator / tests
→ 自動測試
→ Domain Healer 局部修補
→ 產生題目預覽
→ 教師確認教學語意與題目品質
→ 升格 verified
→ 自動重跑原失敗 components
```

單一 component 失敗 **不得** 500 整 skill、**不得** 產錯題、**不得** 阻斷姊妹 components。

#### 1.10.8 教師端可回答的問題（教學語意）

系統以結構化問答呈現；**不**暴露 stack trace、registry key 或 Python 路徑：

- 角度採度數或弧度？
- 變異數採母體或樣本公式？
- 答案要求精確值或近似值？近似到小數第幾位？
- 多解是否全部列出？
- 題目難度與教材是否一致？

#### 1.10.9 成本控制（產品政策）

```text
先重用 existing artifact
→ no-LLM deterministic classification
→ existing-domain capability matching
→ 相近 domain extension analysis（§1.8 優先）
→ 確認真的缺 domain
→ 才呼叫 AI Bootstrap
```

AI 啟動前須顯示：預估呼叫次數、預估 token、預計建立或擴充的 domain、預計 operations、受影響 components。`source_hash` 未變時 **必須** 重用既有 classification、gap report 與 `candidate`，**不得** 重複呼叫 AI。

#### 1.10.10 教師端狀態文字（建議）

| 教師可見狀態 | 內部語意 |
|-------------|----------|
| 已找到既有出題能力 | verified provider matched |
| 正在生成題目 | Shadow Bridge / component codegen |
| 偵測到新的數學能力 | `DOMAIN_CAPABILITY_UNRESOLVED` |
| 正在建立可重用出題能力 | Bootstrap → `candidate` |
| 自動測試與修補中 | validator + Domain Healer |
| 等待教師確認 | `candidate` 預覽就緒 |
| 已核准並重新生成 | `verified` + 失敗 components 重跑 |
| 需要管理員審查 | healer 超限或 bootstrap 失敗 |

技術錯誤詳情僅保留於管理員診斷頁。

#### 1.10.11 成功與失敗標準

| 情境 | 預期 |
|------|------|
| 已有 domain | V3 重新生成 → 自動生成 → `verified` |
| 缺少 domain | 不 500、不產錯題、不阻斷其他 components、不要求老師寫程式、自動 `candidate` |
| Candidate 通過 | 教師確認 → `verified` → 原失敗 components 自動重跑 |
| Candidate 無法修復 | 保留 evidence → 待管理員審查 → **不**影響其他 skill |

#### 1.10.12 本節取代的舊規則

| 舊敘述（已廢止） | 新正式架構 |
|------------------|------------|
| 新 domain 必須由工程師人工建立 | Automated Domain Bootstrap |
| 未知 skill 必須先加入 `SKILL_TO_DOMAIN` | derived binding + Bootstrap Gate |
| Auto-Bootstrap 只產生 gap report | Gap Report + 完整 Bootstrap 產物 + Healer |
| 老師需使用 Codex 修復 | Healer 自動修 `candidate`；老師只確認教學語意 |
| `DOMAIN_BINDING_MISSING` 一律停止 | 先 capability match；真缺 domain 走 Bootstrap，非錯配 |

#### 1.10.13 與 §1.7 / §1.8 分工

| 章節 | 職責 |
|------|------|
| §1.7 | skill package／tracker／component 骨架之 Auto-Bootstrap；Bootstrap Gate vs Publish Gate |
| §1.8 | **既有 verified fixed domain** 內新增 operation／function |
| §1.10 | **全新 capability** 之 domain 自動建立、Healer、升格 |

---

## 2. 八維度原子組件身分證合約

每個 `components/{component_id}/metadata.py` **必須**宣告下列八個維度。  
管線在 Phase 2 沙盒編譯前做靜態校驗；缺任一維度 → `component_contract_incomplete` blocker。

| 維度 | 欄位名 | 說明 |
|------|--------|------|
| D1 | `COMPONENT_ID` | 全域唯一；**必須**為 `src_{textbook_example_id}`（§1.2.2、§1.5） |
| D2 | `SKILL_ID` | 行政歸屬；唯讀，與 Word 匯入鎖定一致 |
| D3 | `TARGET_TASK` | 數學任務 token；對接 `template_slot_resolver.TASK_FAMILY_TO_SLOT` |
| D4 | `TEMPLATE_SLOT` | 執行期插槽名；必須存在於 `SLOT_REGISTRY` 或為 V3 新註冊 slot |
| D5 | `PRESENTATION_MODE` | 前台外觀 Key（見 §2.2） |
| D6 | `DOMAIN_LIBRARY` | 允許 import 的 Helper / Ops 白名單（見 §2.3） |
| D7 | `ANSWER_VERIFICATION_TYPE` | `checker_key` + `equivalence_type`；對接 `checker_registry` |
| D8 | `GENERATOR_READINESS` | `draft` / `runtime_ready` / `failed` / `verified` |

> **v1.9 補充**：除八維度外，每個 component 的 `generate()` 輸出與 induced spec **必須**宣告正式 `answer_type`（§2.0.2）及完整 `ui_contract`／`answer_contract`；`metadata.py` 之 `ANSWER_VERIFICATION_TYPE["answer_type"]` 須與 `generate()` 一致。

### 2.0 內容生成、資料呈現與學生作答三層分離（v1.9 · 西堤作答套餐權威）

本節為 **題型介面／學生端作答契約** 之唯一規範來源。Gencode 管線如何判定並產出這些契約，見 [PipelineFlow §1.3 Step 3／§2.4 Step 2–3](./SOP_Gencode_AgentSkillV3_PipelineFlow.md)。

#### 2.0.1 三層決策原則

每筆教材例題（每個 `src_{textbook_example_id}` component）**必須分別決定**下列三層；三層**不得混為同一分類**。

**（1）數學內容層**（Domain／Generator 責任）

| 欄位 | 說明 |
|------|------|
| `skill_id` | 行政歸屬（DB 權威） |
| `fixed_domain_key` | Registry 固定 Domain |
| `domain_operation` | 白名單內數學操作 |
| induced constraints | 參數化限制 |
| generator | `generate.py` 搬運工 |
| checker | `checker_key` |
| validator | Domain／schema／topology gate |

**（2）資料呈現模式**（題幹附件；**非**作答方式）

| 模式 | 說明 | 典型 payload 欄位 |
|------|------|-------------------|
| `text` | 純文字題幹 | `question_text` |
| `image` | 靜態圖 | `image_base64` |
| `graph` | 可互動或程式繪製圖表 | `visual_spec`、`visual_aids` |
| `readonly_table` | 唯讀表格（資料來源） | `table_data` |
| `canvas` | 作圖畫布區（展示或作答載體） | `ui_contract` + `visual_spec` |

**（3）學生作答模式**（西堤作答套餐；§2.0.2）

五種正式 `answer_type`：`short_answer`、`single_choice`、`multi_part`、`table_fill`、`drawing`。

**組合範例**（資料呈現 + 作答模式）：

| 資料呈現 | 作答模式 | 說明 |
|----------|----------|------|
| `graph` | `multi_part` | 同一張圖回答多小題 |
| `graph` | `single_choice` | 圖表題配選項 |
| `readonly_table` | `short_answer` | 表格為資料，單一簡答 |
| `readonly_table` | `multi_part` | 表格為資料，多小題各自輸入 |
| `table_fill` | — | 答案須填入表格 cell 本身 |
| `graph` + `canvas` | `drawing` | 學生在 canvas 作圖 |

**剛性澄清**：

- 有表格 **不代表** 一定是 `table_fill`；只有答案須**直接填入表格特定 cell** 時才用 `table_fill`。
- 有多個答案 **不代表** 一定是 `multi_part`；若答案位置在表格 cell，應使用 `table_fill`。
- `readonly_table` 僅表示表格為**唯讀資料來源**；學生最後若只答一題，搭配 `short_answer` 或 `single_choice`。

#### 2.0.2 正式五種學生作答介面（西堤作答套餐）

下列五種為 **唯一正式** 學生作答介面選項；新 component **必須**擇一，並貫穿下列管線節點：

| 節點 | 要求 |
|------|------|
| component `metadata.py` | `ANSWER_VERIFICATION_TYPE["answer_type"]` |
| `generate()` 輸出 | `answer_type` + 套餐所需欄位（§2.0.4、PipelineFlow §2.4） |
| `ui_contract` | `interaction_mode` 與前台元件一致 |
| `answer_contract` | `checker_key`、`answer_order` 等 |
| checker registry | 對應 `checker_key` 已 `runtime_available` |
| validator gate | Phase 2.5 套餐專屬斷言 |
| preview | 實際驗證學生可操作方式 |
| production smoke | 依 `answer_type` 分項驗證（PipelineFlow §3.4 Step 5） |
| 本 SOP | 契約定義與禁止降級（§2.0.5） |

| `answer_type` | 中文名稱 | 核心操作 |
|---------------|----------|----------|
| `short_answer` | 單一簡答題 | 單一文字、數值或式子輸入 |
| `single_choice` | 單選題 | 從選項中選擇唯一答案 |
| `multi_part` | 多重填充題 | 多個獨立小題，各有獨立輸入欄 |
| `table_fill` | 表格填空題 | 直接在表格指定格子中填答 |
| `drawing` | 作圖題 | 在 canvas 作圖，**強制** AI 檢查 |

#### 2.0.3 作答套餐選擇決策流程

Phase 1 classifier／induced spec 與 component-local config **必須**依教材**原始作答拓撲**判定 `answer_type`（不得僅依數學 Domain 推斷）：

```text
1. 答案是否必須填在表格特定 cell？
   → 是：table_fill

2. 是否有兩個以上獨立小題（(1)(2)(3) 或語意可區分之多問）？
   → 是：multi_part

3. 是否要求學生畫圖（作圖為主要作答方式）？
   → 是：drawing
   ※ 即使同時有文字描述或 expected_answer 字串，也不得降級為 short_answer

4. 是否提供選項且只有一個正解？
   → 是：single_choice

5. 其餘
   → short_answer
```

#### 2.0.4 各套餐必要契約

##### 套餐 A：`short_answer`（單一簡答題）

**適用**：只有一個答案；學生輸入一個數值、代數式、分數、文字或簡短結果。

```json
{
  "answer_type": "short_answer",
  "answer": {"value": 16},
  "ui_contract": {
    "interaction_mode": "single_input"
  }
}
```

**UI 規則**：顯示單一輸入框；不得顯示內部 `field_key`；輸入框尺寸應符合答案型態；不得把多小題強制塞入同一輸入框。

##### 套餐 B：`single_choice`（單選題）

**適用**：有多個選項，只有一個正確答案。

```json
{
  "answer_type": "single_choice",
  "choices": [
    {"label": "A", "text": "15"},
    {"label": "B", "text": "18"}
  ],
  "answer": {
    "value": "B",
    "semantic_value": 18
  },
  "ui_contract": {
    "interaction_mode": "choice_list"
  }
}
```

**規則**：選項不可重複；必須有唯一正解；若依賴圖表，圖表與選項必須同時可見；checker **不得**只依選項位置而忽略 `semantic_value`。

##### 套餐 C：`multi_part`（多重填充題）

**定義**：一道題中有兩個以上彼此可區分的小題，每個小題需要獨立作答。

**典型情境**：同一張圖多問；分別求斜率、截距、方程式；同一組資料衍生多個問題；題目含 `(1)、(2)、(3)` 等小題。

```json
{
  "answer_type": "multi_part",
  "subquestions": [
    {
      "part": "(1)",
      "field_key": "part_1",
      "prompt": "第一小題",
      "expected_answer": 16,
      "input_type": "number"
    },
    {
      "part": "(2)",
      "field_key": "part_2",
      "prompt": "第二小題",
      "expected_answer": 21,
      "input_type": "number"
    }
  ],
  "answer": {
    "value": [16, 21]
  },
  "answer_contract": {
    "checker_key": "multi_part_answer_checker",
    "answer_order": ["part_1", "part_2"]
  },
  "ui_contract": {
    "interaction_mode": "multiple_inputs"
  }
}
```

**UI 標準**：每一小題顯示自己的題號、文字及輸入框；共用圖表只顯示一次；不得要求逗號分隔多答案；提交後須有 per-part 正確／錯誤／未作答；切題時清除所有小題狀態。

**Validator**：`subquestions` 不得為空；小題數與答案數一致；`field_key` 唯一；`answer_order` 完整；每個答案可由題面唯一求出；**不得**降級為 `short_answer`。

##### 套餐 D：`table_fill`（表格填空題）

**定義**：答案必須直接填入表格中的指定 cell；列、欄位置本身具有數學語意。

**適用**：次數分配表、累積次數分配表、函數值表、統計資料表、數列規律表、係數表等。

**不適用**（表格僅為資料來源，學生最後答一題）：`readonly_table` + `short_answer`／`single_choice`／`multi_part`。

```json
{
  "answer_type": "table_fill",
  "table_question": {
    "type": "table_fill",
    "interaction_mode": "inline_input",
    "headers": ["欄1", "欄2", "欄3"],
    "display_rows": [],
    "blank_cells": [
      {
        "row": 0,
        "col": 2,
        "field_key": "field_1",
        "label": "",
        "expected_answer": 5,
        "input_type": "number"
      }
    ],
    "answer_order": ["field_1"],
    "show_blank_labels": false
  },
  "answer_contract": {
    "checker_key": "table_fill_answer_checker"
  },
  "ui_contract": {
    "interaction_mode": "inline_table_input"
  }
}
```

**UI 標準**：使用真正的 HTML table；完整外框與欄線；標題列、資料列、總計列清楚；輸入框直接位於待填 cell；不得在表格下方產生一長串重複輸入欄；不得顯示 `lt_1`、`gt_1`、`field_3` 等工程名稱；窄螢幕支援水平捲動；每個 cell 可個別顯示正確、錯誤、未填。

**空格代號規則**：預設 `show_blank_labels: false`（直接顯示空白輸入框，不顯示 a、b、c）。僅在教材明確命名 a、b、c、d、題幹要求「求 a、b、c、d」或後續問題需引用代號時設為 `true`。若表格不顯示代號，題幹也不得要求 a、b、c、d，應改為「請完成下方表格。」或「請在空格中填入正確數值。」

**Validator**：`blank_cells` 不得為空；`row`／`col` 有效且不可重複；`field_key` 唯一；`answer_order` 涵蓋所有格；`expected_answer` 與題目資料一致；已知資料足以唯一求解；input 數量與 `blank_cells` 數量一致；**不得**退化為表格下方多重輸入框。

##### 套餐 E：`drawing`（作圖題）

**定義**：學生必須在 canvas 上作圖；文字答案及一般提交流程**不得**使用；**必須**強制透過 AI 作圖檢查。

```json
{
  "answer_type": "drawing",
  "ui_contract": {
    "interaction_mode": "canvas",
    "drawing_required": true,
    "ai_check_required": true,
    "text_answer_enabled": false,
    "submit_button_enabled": false,
    "auto_next_on_correct": true,
    "success_dialog_required": true
  }
}
```

**UI 強制規則**（`answer_type == "drawing"` 或 `drawing_required == true`）：

- 顯示 canvas 與作圖工具、AI 檢查按鈕
- 文字答案 textbox **hidden 或 disabled**；一般「提交」按鈕 **hidden 或 disabled**
- **不得**執行一般 short-answer checker；**不得**讓學生跳過 AI 檢查直接提交
- AI 檢查是**唯一**正式送出管道

**AI 檢查流程**：

```text
學生完成作圖
→ 點擊 AI 檢查
→ 鎖定按鈕，顯示檢查中
→ 擷取 canvas
→ 呼叫圖形檢查 endpoint
→ 處理正確、錯誤或 API 錯誤
```

| 階段 | 行為 |
|------|------|
| 檢查中 | AI 檢查按鈕 disabled；防止重複送出；可暫時鎖定 canvas |
| AI 判定錯誤 | 保留圖形；留在原題；顯示可操作提示；不跳下一題；不記錄答對；按鈕恢復可用 |
| API 錯誤 | 不得誤判答對；不得跳題；顯示稍後重試；恢復 canvas 與按鈕 |
| AI 判定正確 | 依序：寫入答對紀錄 → 更新連續答對與學習狀態 → 防止重複計分 → 鎖定 canvas 與按鈕 → 顯示成功 msgbox → 學生按「確定」→ 自動載入下一題 |

**正確流程必須為**：

```text
AI check passed → record success → show success msgbox → user confirms → next question
```

不得在資料寫入完成前跳題，也不得未顯示成功訊息就直接跳題。

**建議成功 response**：

```json
{
  "success": true,
  "is_correct": true,
  "message": "作圖正確",
  "attempt_recorded": true,
  "next_action": "show_success_then_next"
}
```

**Validator**：`drawing_required` 與 `ai_check_required` 為 true；textbox 與一般 submit 不可操作；AI 檢查按鈕可見；成功時寫入紀錄並顯示 msgbox；確認後跳下一題；失敗或 API 錯誤不跳題；重複點擊不重複計分；切題後 canvas 與狀態完整 reset。

> **Legacy 映射**：歷史 `answer_type: "handwriting"` 與 §2.2.1 欄位在新 component 中**統一**遷移至 `drawing` + 上列 `ui_contract`；舊 payload 由 adapter 向後映射，新產出不得再宣告 `handwriting` 為正式套餐。

#### 2.0.5 禁止降級與 Contract Violation

下列情形一律視為 **contract violation**；Quality Gate **必須**標記 blocker，**不得** `verified`／`published`：

| # | Violation |
|---|-----------|
| 1 | `multi_part` 被壓成單一輸入框 |
| 2 | `table_fill` 被改成表格下方長串輸入框 |
| 3 | `table_fill` 顯示內部 `field_key` |
| 4 | 題幹寫「完成下表」但沒有真正表格 |
| 5 | 題幹寫「如下圖」但圖未顯示 |
| 6 | `drawing` 題仍可操作文字 textbox |
| 7 | `drawing` 題一般提交按鈕仍可操作 |
| 8 | `drawing` 題未強制 AI 檢查 |
| 9 | AI 判定錯誤卻跳下一題 |
| 10 | AI API 錯誤卻記錄答對 |
| 11 | `drawing` 題成功後未顯示 msgbox |
| 12 | 選擇題沒有唯一正解 |
| 13 | `answer_type` 與 UI 實際操作不一致 |
| 14 | component contract 經 adapter／wrapper／API 後欄位遺失 |

#### 2.0.6 與 Gencode 管線銜接（交叉引用）

| 本文件（呈現與驗證） | PipelineFlow（產出與流程） |
|---------------------|---------------------------|
| §2.0.2 五種套餐定義 | §1.3 Step 3：`answer_type` 判定 |
| §2.0.4 各套餐 JSON 契約 | §2.4 Step 2：`generate()` 通用輸出契約 |
| §2.0.5 禁止降級 | §2.4 Step 3：validator／preview 斷言 |
| §2.0.4 套餐 E AI 流程 | §3.4 Step 5：production smoke 分項 |
| `ui_contract` 完整保留 | §2.4：adapter 不得剝除 UI 欄位 |

`candidate_verified` 與 `verified`：**不僅**看數學答案，**必須**確認 UI 可依 `answer_type` 實際作答；`ui_contract` 不完整 → **不得** verified／published。

### 2.1 標準 Metadata 宣告範例

```python
# agent_skills_v3/vh_數學B1_LinearFunction/components/src_4545/metadata.py
from __future__ import annotations
from typing import Final

# ── D1–D2：身份 ──────────────────────────────────────────
COMPONENT_ID: Final[str] = "src_4545"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "4545"              # textbook_examples.id（管線注入）

# ── 天然難度（管線依 SOURCE_KIND 自動注入，禁止 AI 改寫）──
SOURCE_KIND: Final[str] = "example"
ORDER_WEIGHT: Final[int] = 10                 # example=10, quiz=20, test=30
DIFFICULTY_LEVEL: Final[str] = "easy"         # test → "hard"

# ── D3–D4：數學任務與插槽 ────────────────────────────────
TARGET_TASK: Final[str] = "determine_linear_function_from_two_points"
TEMPLATE_SLOT: Final[str] = "linear_function_two_point_choice"

# ── D5：外觀 Key（穩定集合，禁止自創）────────────────────
PRESENTATION_MODE: Final[str] = "single_choice"
# 合法值全集：
#   integer | choice | single_choice | rational | interval_set
#   | equation | text_short | handwriting

# ── D6：Domain 白名單（僅允許 import 下列模組）────────────
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
    # 經 taxonomy_registry 解析；禁止在 generate.py 硬編碼 skill_id
)

# ── D7：批改合約（精確對接 checker_registry）──────────────
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",       # → core.checkers.choice_label_checker
    "equivalence_type": "choice_label",          # CHECKER_CAPABILITIES 內合法等價類型
    "answer_type": "single_choice",              # payload answer_type
    "module": "core.checkers.choice_label_checker",
}

# ── D8：就緒狀態 ─────────────────────────────────────────
GENERATOR_READINESS: Final[str] = "draft"  # 沙盒通過後由管線改為 verified

# ── 語意附帶（非八維度，但 Phase 1 必填）──────────────────
SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率",
    "兩點決定直線",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point",
    "linear_function",
    "horizontal_line",   # 水平線 — Phase 1 拆分依據
    "vertical_line",     # 鉛直線
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
```

### 2.2 PRESENTATION_MODE 穩定 Key 對照表

> **v1.9 分工**：`answer_type`（§2.0.2 西堤作答套餐）決定**學生怎麼答**；本節 `PRESENTATION_MODE` 決定**輸入元件外觀**（數字框、分數框、選項樣式等），透過 `ui_contract.interaction_mode` 與套餐對接。資料呈現（圖、唯讀表）見 §2.0.1，**不得**與 `answer_type` 混用。

以下為前台 Web 與 `answer_contract.presentation_mode` **已穩定支援**的外觀 Key。  
AI Codegen **不得**自創新 Key；若需擴充，須先修改 `core/gencode/answer_format_hint.py` 與前台 renderer。

| Key | 典型 `answer_type` | 前台輸入元件 | 對接 Checker |
|-----|-------------------|--------------|--------------|
| `integer` | `short_answer`（`integer`／`numeric` 語意） | 數字輸入框 | `integer_checker` / `numeric_checker` |
| `choice` | `single_choice`（泛用選項） | 選項群組 | `choice_label_checker` |
| `single_choice` | `single_choice` | A/B/C/D 單選 | `choice_label_checker` |
| `rational` | `short_answer`（分數語意） | 分數輸入 | `rational_checker` / `fraction_checker` |
| `interval_set` | `short_answer`（區間語意） | 區間輸入 | `interval_checker` |
| `equation` | `short_answer`（方程式語意） | 方程式輸入 | `equation_checker` / `linear_equation_equivalent_checker` |
| `text_short` | `short_answer` | 短文字 | `text_short_checker` |
| `inline_table_input` | `table_fill` | 表格內嵌輸入 | `table_fill_answer_checker` |
| `multiple_inputs` | `multi_part` | 多欄位輸入 | `multi_part_answer_checker` |
| `canvas` | `drawing` | canvas + AI 檢查 | `ai_judged_checker` |
| `handwriting` | **legacy** → 新題用 `drawing` | 手寫板（舊） | `ai_judged_checker` / `manual_review_checker` |

> **備註**：歷史資料中 `presentation_mode: "short_answer"` 與 `text_short` 外觀等價；V3 新組件之正式 `answer_type` 使用 §2.0.2 五選一，`skill_wrapper_compiler` 負責向後映射。

#### 2.2.1 作圖題前端硬體連動（`drawing` · 取代 legacy `handwriting`）

當 `answer_type == "drawing"`（或 legacy `PRESENTATION_MODE == "handwriting"`）時，`runtime_skill_wrapper` 在 `finalize_generator_payload()` 階段**必須**注入下列前台控制宣告（完整契約見 §2.0.4 套餐 E；**不得破壞** `practice.py` 學生端 response contract（§0.1.1））：

```python
payload.update({
    "answer_type": "drawing",              # 新 component 正式值；legacy 可映射 handwriting
    "answer_input_type": "drawing",
    "requires_handwriting": True,          # legacy 相容欄位
    "input_mode": "canvas",
    "text_input_disabled": True,
    "text_answer_enabled": False,
    "submit_button_enabled": False,
    "drawing_required": True,
    "ai_check_required": True,
    "allow_camera_upload": True,
    "allow_canvas_drawing": True,
    "runtime_mode": "visual_or_handwriting_ai_checked",
    "check_mode": "handwriting_ai_checked",
    "grading_mode": "ai_judged_free_response",
    "ui_contract": {
        "interaction_mode": "canvas",
        "drawing_required": True,
        "ai_check_required": True,
        "text_answer_enabled": False,
        "submit_button_enabled": False,
        "auto_next_on_correct": True,
        "success_dialog_required": True,
    },
})
```

**剛性防線**（詳見 §2.0.4 套餐 E）：

- 前台讀取 `text_answer_enabled: false`／`text_input_disabled: True` 後，**禁止**鍵盤文字作答
- **禁止**一般 submit；僅 AI 檢查為正式送出管道
- 批改由 Vision LLM 執行；component 內**不得**自寫 `check()` 覆寫
- AI 正確流程：`record success → msgbox → user confirms → next question`

### 2.3 DOMAIN_LIBRARY 精確對接表

`DOMAIN_LIBRARY` 宣告的是 **Python import 路徑字串**，不是自由描述。  
Codegen 產生的 `generate.py` 只能 `from ... import ...` 此清單內的符號。

> **算子盾牌原則（v1.3）**：所有極端特例（如鉛直線分母為零崩潰、水平線退化、分母為零等）與數學變異，**統一**由工程師預先寫好的共用 Domain Function 算子盾牌進行 **deterministic** 控制。  
> Gemini Flash **僅允許**扮演搬運工：將算子回傳的 **Full Matrix Dictionary** 填入該單一題目的 f-string 模板，**禁止**自行解算或依題型在規格書內開專章 hard-code。  
> 規格書不再為每一種數學邊界撰寫獨立條文；邊界行為以算子庫實作與沙盒驗證為準。

| 領域 token | Helper 類別（首選） | Ops 類別（細算子） | 模組路徑 |
|------------|----------------------|-------------------|----------|
| `coordinate_geometry` | `build_line_equation_matrix` | — | **`core/domain/coordinate_geometry/line_equation_domain.py`**（v1.4 目標） |
| `algebra` | `build_linear_equation_matrix` | — | **`core/domain/algebra/linear_equation_domain.py`**（v1.4 目標） |
| `counting` | `build_permutation_combination_matrix` | — | **`core/domain/counting/permutation_combination_domain.py`**（v1.4 目標） |
| `statistics` | `build_descriptive_statistics_matrix` | — | **`core/domain/statistics/descriptive_statistics_domain.py`**（v1.4 目標） |
| `integer` | `IntegerFunctionHelper` | `IntegerOps` | `core/integer_domain_functions.py` / `core/prompts/domain_function_library.py`（現行） |
| `fraction` / `rational` | `FractionFunctionHelper` | `FractionOps` | `core/fraction_domain_functions.py`（現行） |
| `polynomial` | `PolynomialFunctionHelper` | `PolynomialOps` | `core/polynomial_domain_functions.py`（現行） |
| `radical` | `DomainFunctionHelper` | `RadicalOps` | `core/domain_functions.py` / `core/scaffold/domain_libs.py`（現行） |
| `calculus` | — | `CalculusOps` | `core/prompts/domain_function_library.py`（現行） |
| `geometry_slot` | — | `SLOT_REGISTRY[slot]` | `core/gencode/slot_generators.py`（現行） |
| `b4_payload` | `validate_*` / `check_*` | — | `core/vocational_math_b4/domain/b4_validators.py`（現行） |

> **遷移原則**：v1.4 目標模組上線後，`DOMAIN_LIBRARY` 白名單以 `core/domain/` 為 canonical；現行 `core/*_domain_functions.py` 僅作過渡 re-export，新題型**不得**再擴充舊路徑。

#### 2.3.1 Codegen 剛性防線：Domain Function 驅動（禁止 AI 自算）

**鐵律**（寫入 Gemini Flash Codegen 系統提示詞，違反即沙盒 AST / 語意掃描 blocker）：

> `generate.py` 內**禁止**出現 AI 自行撰寫的數學四則運算、手動組裝干擾項、或以 `random` 直接捏造「看起來合理」的錯誤答案。  
> 所有**正確答案**與**干擾項（distractors）**必須透過呼叫 `DOMAIN_LIBRARY` 白名單內的 Domain Function / Helper 計算並回傳。  
> AI 僅負責題幹字串的包裝、`SCENARIO_POOL` 填空（見 §3.4）、以及將 Domain Function 回傳值嵌入 payload。

**合法 / 非法對照**：

```python
# ❌ 非法：AI 自算答案與干擾項
correct = a * b + c
wrong = [correct + 1, correct - 2, correct * 2]

# ✅ 合法：委派 Domain Function，解開 Full Matrix Dict（見 §2.3.2、§2.5）
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
matrix = build_line_equation_matrix(
    seed=seed,
    line_type="two_points",
    curriculum_profile="vocational_high_b",
    difficulty_profile="easy",
)
correct = matrix["answer"]["canonical_form"]
distractors = matrix["distractors"]
```

**沙盒 AST 掃描規則**（Phase 2.5；v1.2 精準化，避免誤殺控制流）：

##### 敏感區白名單（不得誤殺）

下列運算屬**控制流 / 基礎資料結構**，AST 掃描器**一律放行**，不觸發 `ai_math_operation_forbidden`：

| 敏感情境 | 合法範例 |
|----------|----------|
| 難度 / 層級遞增 | `level + 1`、`difficulty + 1` |
| 種子衍生 | `seed + 17`、`random.Random(seed + attempt)` |
| 迴圈邊界 | `range(n + 1)`、`for i in range(level + 2)` |
| 幾何顯示範圍 | `x_range = [-8, 8]`、`y_range = (-10, 10)` |
| 數值夾限 / 微調 | `min(1.0, base + 0.1)`、`max(-9, x - 1)` |
| 陣列索引 | `choices[i + 1]`、`SCENARIO_POOL[seed % len(SCENARIO_POOL)]` |
| 字串模板拼接 | `f"點 A({x}, {y})"`（非數學語意運算） |

##### 剛性阻擋條件（精準左值比對）

僅當**同時滿足**下列三條，才判定 `ai_math_operation_forbidden`：

1. **運算算子**：存在 `+`、`-`、`*`、`/`、`//`、`%`、`**` 之一的二元運算。
2. **賦值左值（Lvalue）敏感**：該運算結果直接或間接賦值至下列名稱之一，或其子欄位：
   - `answer`、`correct_answer`、`choices`、`distractors`、`options`
   - `visual_spec` 內的幾何數學坐標（如 `points[].x`、`points[].y`、`lines[].y`、`lines[].x`）
3. **無 Domain 算子特徵**：該 Code Block（同一 `def` 或同一 `while` 迴圈體）內，**完全沒有**對 `DOMAIN_LIBRARY` 白名單 Helper / Ops 的呼叫特徵（如 `_helper.`、`build_problem_matrix`、`CountingFunctionHelper` 等）。

> **設計意圖**：阻擋 AI 在答案路徑上「手算數學」；不阻擋 `level + 1` 這類與數學語意無關的控制流。

**其他沙盒規則**：

1. 選擇題：干擾項必須來自 Domain Function 回傳的 `distractors` 欄位，或 Helper 的 `build_*_distractors()`；禁止硬編碼四個字串選項。
2. 若 `visual_spec` 坐標由 Domain Function 的 `visual_spec` 鍵提供，component 內禁止對坐標重新四則運算。

#### 2.3.2 Domain Function 回傳契約：Full Matrix Dictionary

全面廢除單一 `compute_answer()` 回傳純量或單一字串的設計。  
`core/domain/` 下所有算子庫（v1.4 目標）及過渡期 `core/*_domain_functions.py`，**必須**回傳下列標準完整字典（Full Matrix Dictionary）：

```python
# Full Matrix Dictionary — 六大矩陣欄位（Domain 端一次算完，generate.py 禁止加工）
ProblemMatrix = {
    "givens": {                    # 已知條件（點、斜率、係數等原始數值）
        "point_a": (1, 3),
        "point_b": (3, 7),
        "slope": 2,
    },
    "answer": {                    # SymPy 算出的精確答案（結構化；非字串手拼）
        "canonical_form": "y=2x+1",
        "general_form": "2x-y+1=0",
        "line_type": "oblique_line",
    },
    "distractors": [               # 單選題誘答選項（已由算子生成，禁止 generate.py 改寫）
        "y=x+1",
        "y=2x-1",
        "y=-2x+1",
    ],
    "explanation_steps": [         # 步驟化解析提示（供 get_hint / 教師端）
        "代入點斜式",
        "化簡得斜截式",
    ],
    "validation_facts": {          # 驗證事實（供 Validator / Checker 交叉驗證）
        "slope": 2,
        "is_integer_slope": True,
        "line_passes_through": [(1, 3), (3, 7)],
    },
    "visual_spec": {               # 繪圖規格與坐標（僅數據，不在此時渲染）
        "kind": "coordinate_plane_spec",
        "points": [{"x": 1, "y": 3, "label": "A"}, {"x": 3, "y": 7, "label": "B"}],
        "lines": [{"type": "slope_intercept", "m": 2, "b": 1}],
        "x_range": [-8, 8],
        "y_range": [-8, 8],
    },
}
```

> **payload 封裝**：`generate.py` 可將 `matrix["answer"]["canonical_form"]` 填入 `payload["correct_answer"]` 等前台欄位，但**不得**對答案、誘答項或坐標做任何數學運算或重新推導。

#### 2.3.3 Answer Schema Registry 與兩層驗證（v1.5 · IMPLEMENTED）

**Canonical 模組**：`core/gencode/answer_schema_registry.py`

| 層級 | 函式 | 驗證範圍 |
|------|------|----------|
| 第一層 | `validate_full_matrix_shell(matrix)` | 六大外層欄位存在且型別正確 |
| 第二層 | `validate_answer_schema(answer, answer_schema_key=...)` | `matrix["answer"]` 內部欄位依 schema key |

**七種分流責任（不得互相代替）**：

```text
skill_id              → 行政歸屬與學生端入口
domain                → 共用數學領域（如 coordinate_geometry）
domain_operation      → 該題實際數學操作（induced spec 決定）
problem_type_id       → 題型身份與 runtime 分流鍵
answer_schema_key     → matrix["answer"] 結構契約
answer_type           → 學生作答套餐（§2.0.2 五選一）
data_presentation     → 題幹附件呈現（§2.0.1；text/image/graph/readonly_table/canvas）
presentation_mode     → 輸入元件外觀 Key（§2.2）
ui_contract           → 前台互動宣告（interaction_mode 等）
checker_key           → 批改與語意等價判定
```

**剛性禁止**：

1. 不得由整個 `coordinate_geometry` domain 或 `skill_id` 直接決定固定 answer fields。
2. schema 不存在 → **fail-fast** → `DOMAIN_FUNCTION_MISSING` / `needs_human_review`；**禁止** fallback 到其他 Domain 之相似 schema。
3. Full Matrix 共用 validator **不得**直接要求 `slope` / `intercept` / `distance` 等 operation-specific 欄位。

**Legacy migration**：舊 induced spec 缺 `answer_schema_key` 時，僅允許依 `problem_type_id` / `domain_operation` **deterministic mapping**；無法唯一判定 → `needs_human_review`（禁止假裝分類成功）。

**AI（Gemini Flash）搬運工角色**：

| 允許 | 禁止 |
|------|------|
| 呼叫 `build_problem_matrix()` 解開 Dict | 對 `givens` 內數值自行四則運算推導答案 |
| 將 `answer` / `distractors` 填入 payload 與 choices | 手動組裝或改寫 `distractors` 陣列 |
| 用 `givens` + `SCENARIO_POOL` 模板包裝 `question_text` | 對 `validation_facts` / `visual_spec` 坐標二次運算 |
| 將 `explanation_steps` 轉寫入 `metadata.derivation` | 覆寫 `answer` 字串內容 |

**沙盒斷言**（Phase 2.5）：`generate()` 內必須存在對 `core/domain/` 入口函式的呼叫（如 `matrix = build_line_equation_matrix(...)`），且 `payload["correct_answer"]` 可追溯至 `matrix["answer"]`（如 `matrix["answer"]["canonical_form"]`），**未經**手算改寫。

**幾何坐標算子**（水平線 / 鉛直線 / 兩點距離 / 分點 / 中點等）不在 component 內重寫 matplotlib；  
component 輸出結構化 `visual_spec`（見 §3.2），由底層 `slot_generators` 或 B4 visual runtime 統一渲染。

### 2.4 ANSWER_VERIFICATION_TYPE 與 checker_registry 對接

`core/gencode/checker_registry.py` 中 `runtime_available == True` 的 Key 為 V3 合法批改器：

| checker_key | module 路徑 | 典型 equivalence_type |
|-------------|-------------|----------------------|
| `choice_label_checker` | `core.checkers.choice_label_checker` | `choice_label`, `choice_label_exact` |
| `integer_checker` | pipeline（`runtime_skill_wrapper` 內建） | `numeric_exact`, `numeric_equivalence` |
| `numeric_checker` | pipeline | `numeric_exact`, `numeric_tolerance` |
| `rational_checker` | pipeline | `rational_equivalent`, `fraction_equal` |
| `fraction_checker` | pipeline | `fraction_equal` |
| `decimal_tolerance_checker` | pipeline | `decimal_tolerance` |
| `percentage_checker` | pipeline | `percentage_equivalent` |
| `expression_equivalence_checker` | `core.checkers.expression_equivalence_checker` | `algebraic_equivalent`, `expression_equivalence` |
| `expression_checker` | pipeline | 同上 |
| `equation_checker` | pipeline / `core.checkers`（語意擴充版） | `equation_equivalent`, `linear_equation_equivalent` |
| `linear_equation_equivalent_checker` | `core.checkers.linear_equation_equivalent_checker` | `linear_equation_equivalent` |
| `rational_or_decimal_checker` | `core.checkers.rational_or_decimal_checker`（V3 語意擴充） | `rational_decimal_equivalent` |
| `solution_set_checker` | `core.checkers.solution_set_checker` | `unordered_solution_set`, `set_equal` |
| `set_checker` | `core.checkers.solution_set_checker` | 同上 |
| `interval_checker` | `core.checkers.interval_checker` | `interval_equivalence`, `interval_set` |
| `quadrant_checker` | `core.checkers.quadrant_checker` | `normalized_label` |
| `coordinate_pair_checker` | `core.checkers.coordinate_pair_checker` | `coordinate_pair_equivalence`, `ordered_pair` |
| `tuple_checker` | `core.checkers.coordinate_pair_checker` | 同上 |
| `text_checker` | pipeline | `exact_text`, `normalized_text_equivalence` |
| `text_short_checker` | pipeline | `exact_string`, `case_insensitive_string` |
| `matrix_checker` | pipeline | `matrix_exact` |
| `manual_review_checker` | pipeline | `manual_review_or_ai_judged` |
| `ai_judged_checker` | pipeline | `manual_review_or_ai_judged` |

#### 2.4.1 高階語意等價檢查器（Semantic Checker）

以下兩項為 V3 **數學語意閉環**核心；component 的 `check.py` **不得**自行比對字串，必須在 `metadata.py` 宣告對應 `checker_key` 並委派 `runtime_skill_wrapper.check_answer()`。

##### 垂直切片優先級（v1.2 MVP 基礎設施）

首波垂直切片以 `vh_數學B1_PointSlopeForm`（直線方程式）為上線標竿。下列兩個 Checker 為**最優先穩定**的底層基礎設施，須在 Phase 2 沙盒與 Phase 3 smoke 全數通過後，方可標記 component `verified`：

| 優先級 | checker_key | 首波適用單元 | 穩定性要求 |
|--------|-------------|-------------|-----------|
| **P0** | `linear_equation_equivalent_checker` | B1 直線方程式、`vh_數學B1_PointSlopeForm` | 斜截式與一般式等價判定 100% 通過回歸測試 |
| **P0** | `rational_or_decimal_checker` | B1/B4 含分數或小數答案之題型 | `1/2` ≡ `0.5` 等價判定 100% 通過回歸測試 |

**代數比對剛性要求**（不允許因前台輸入格式多變而誤判）：

1. **直線方程式**：底層透過 SymPy 移項化簡與係數比例判定法，確保下列寫法語意等價、皆判正確：
   - 斜截式 `y = 2x + 1`
   - 一般式 `2x - y + 1 = 0` 或 `x - y + 1 = 0`（同一直線之等價變形）
   - 頂點式 / 點斜式經化簡後與上列同族者
2. **分數小數**：底層透過 SymPy 有理數化簡，確保 `1/2`、`0.5`、`0.50` 在題目語意允許小數時皆判正確；**禁止**僅做字串相等比對。

**1. `rational_or_decimal_checker`（P0）**

| 項目 | 說明 |
|------|------|
| 用途 | 分數 / 小數 / 整數混合答案的語意等價判定 |
| 底層機制 | 自動調用 SymPy 代數化簡，將學生輸入與標準答案歸一化至同一有理數語意 |
| 等價範例 | `1/2` ≡ `0.5` ≡ `0.50`（在題目允許小數語意時）→ 皆判正確 |
| `equivalence_type` | `rational_decimal_equivalent` |
| module | `core.checkers.rational_or_decimal_checker`（V3 目標；現行可過渡至 `expression_equivalence_checker` + SymPy） |

**2. `linear_equation_equivalent_checker`（P0 — 直線方程式首波主 Checker）**

| 項目 | 說明 |
|------|------|
| 用途 | 直線方程式專用語意等價；`vh_數學B1_PointSlopeForm` 等 B1 直線族**預設**使用此 Checker |
| 底層機制 | SymPy 移項化簡 + 係數比例判定；將斜截式、一般式、點斜式歸一化至同一直線語意 |
| 等價範例 | `y = 2x + 1` ≡ `2x - y + 1 = 0` ≡ `y - 2x = 1` → 皆判正確 |
| `equivalence_type` | `linear_equation_equivalent` |
| module | `core.checkers.linear_equation_equivalent_checker` |

**3. `equation_checker`（泛用方程式 — 非首波 P0，多項式擴充用）**

| 項目 | 說明 |
|------|------|
| 用途 | 方程式型答案的語意等價；專用於直線方程式、多項式恒等式 |
| 底層機制 | 移項化簡 + 係數比例判定法；將不同表示法歸一化至同一幾何物件 |
| 等價範例 | 斜截式 `y = x + 1` ≡ 一般式 `x - y + 1 = 0` ≡ `y - x = 1` → 皆判為同一條直線，算答對 |
| `equivalence_type` | `equation_equivalent` 或 `linear_equation_equivalent` |
| module | 優先 `core.checkers.linear_equation_equivalent_checker`；多項式恒等式擴充走 `equation_checker` |

> **首波切片選用規則**：直線方程式類 component（`TARGET_TASK` 含 `line_equation` / 兩點式 / 點斜式）**必須**綁定 `linear_equation_equivalent_checker`，不得降級為純字串比對。  
> **與 `equation_checker` 的分工**：`equation_checker` 為泛用入口；直線子類以 `linear_equation_equivalent_checker` 為 P0 快速路徑。

靜態校驗規則（Phase 2.5）：

```python
from core.gencode.checker_registry import validate_answer_contract_capability

result = validate_answer_contract_capability({
    "checker_key": metadata.ANSWER_VERIFICATION_TYPE["checker_key"],
    "answer_type": metadata.ANSWER_VERIFICATION_TYPE["answer_type"],
    "equivalence_type": metadata.ANSWER_VERIFICATION_TYPE["equivalence_type"],
})
assert result["checker_capability_status"] != "blocked"
```

B4 機率統計題額外通過 `b4_validators.validate_problem_payload_contract()` 與 `validate_answer_in_choices()` 等生成期守衛。

### 2.5 共用 Domain 邏輯層架構（v1.4 規劃 · 待實作）

本節定義 **數學核心邏輯的唯一歸宿**。不再依學制（國中 / 普高 / 技高）分開撰寫邏輯；所有 SymPy 計算、誘答選項（distractors）生成、`visual_spec` 坐標推導，**一律**收斂於 `core/domain/`。

#### 2.5.1 設計原則

| 原則 | 剛性要求 |
|------|----------|
| **按數學本質分層** | 目錄以數學領域組織（`coordinate_geometry`、`algebra`、`counting`、`statistics`），不以 `vh_` / `jh_` 學制前綴組織 |
| **嚴禁 skill_id 滲透** | `core/domain/` 內**不得**出現任何行政 `skill_id`；課綱差異以 `curriculum_profile` 參數控制 |
| **一次算完** | 單一入口函式回傳完整 **Full Matrix Dictionary**（§2.3.2 六大欄位） |
| **generate.py 零數學** | component 層禁止 SymPy、禁止手寫 distractors、禁止重算 visual 坐標 |

#### 2.5.2 目標模組清單（第一階段）

| 模組路徑 | 入口函式 | 涵蓋數學本質 | MVP 優先 |
|----------|----------|-------------|----------|
| `core/domain/coordinate_geometry/line_equation_domain.py` | `build_line_equation_matrix(...)` | 兩點式、點斜式、水平線、鉛直線、斜直線 | **P0** |
| `core/domain/counting/permutation_combination_domain.py` | `build_permutation_combination_matrix(...)` | 排列、組合、計數原理 | P1 |
| `core/domain/algebra/linear_equation_domain.py` | `build_linear_equation_matrix(...)` | 一元一次、聯立方程 | P1 |
| `core/domain/statistics/descriptive_statistics_domain.py` | `build_descriptive_statistics_matrix(...)` | 平均、加權、標準差、全距 | P1 |

#### 2.5.3 控制參數契約（課綱差異的唯一入口）

Domain 函式**統一**接受下列參數；課綱 / 難度差異由內部解讀，**不得**在 component 內 if-else `skill_id`：

```python
def build_line_equation_matrix(
    *,
    seed: int | None,
    line_type: str,                    # two_points | point_slope | horizontal_line | vertical_line | oblique_line
    curriculum_profile: str,           # 例：vocational_high_b | junior_high | general_high
    difficulty_profile: str,           # 例：easy | medium | hard（可與 metadata DIFFICULTY_LEVEL 對接）
    constraints: dict[str, object] | None = None,  # 例：禁止複雜斜率證明、整數係數限定
) -> dict[str, object]:
    ...
```

**`curriculum_profile` 範例語意**（以技高數 B 直線方程式為例）：

- 允許：基礎斜率、點斜式、兩點式、水平 / 鉛直退化
- 禁止：過於複雜的斜率幾何證明、非課綱範圍之解析幾何推論
- 數值範圍、係數型態（整數 / 有理數）由 `constraints` 與 `difficulty_profile` 聯合決定

#### 2.5.4 `line_equation_domain` 內部職責（P0 標竿）

`build_line_equation_matrix` 須在**單一函式族**內處理：

| `line_type` | 內部行為 |
|-------------|----------|
| `two_points` | 兩點求直線；自動偵測退化為水平 / 鉛直 |
| `point_slope` | 已知一點與斜率 |
| `horizontal_line` | $y = k$；分母為零等邊界在此處理 |
| `vertical_line` | $x = k$；禁止誤用一般斜率公式 |
| `oblique_line` | 一般斜直線；SymPy 化簡斜截式 / 一般式 |

回傳之 `answer` 為**結構化 dict**（含 `canonical_form`、`general_form`、`line_type`）；`distractors` 與 `visual_spec` 必須與 `validation_facts` 數學一致。

#### 2.5.5 第一階段實作檢查點（直線方程式）

調整 `components/{component_id}/generate.py` 與 `line_equation_domain.py` 時，驗收**必須**確認：

- [ ] Domain 回傳六大欄位齊全：`givens`、`answer`、`distractors`、`explanation_steps`、`validation_facts`、`visual_spec`
- [ ] `generate.py` 內**無** `import sympy`、**無** distractors 組裝演算法、**無** visual 坐標四則運算
- [ ] `payload["correct_answer"]` 可追溯至 `matrix["answer"]`（未經手算改寫）
- [ ] 鉛直線 / 水平線退化案例由 Domain 內部 deterministic 處理（不在 SOP 開專章 hard-code）
- [ ] `curriculum_profile="vocational_high_b"` 時數值範圍符合技高 B 課綱

### 2.6 `generate.py` 搬運工契約（生成調度層）

`components/{component_id}/generate.py` 在 v1.4 架構下**全面減肥**，職責僅剩：

1. 從 `metadata.py` 讀取 `DOMAIN_LIBRARY` 與 profile 參數（`curriculum_profile`、`difficulty_profile`）。
2. 呼叫對應 Domain 入口函式（經 Registry 解析，見 §2.7）。
3. 將 Full Matrix Dictionary **原樣搬運**至 payload（允許 f-string 題幹模板填空，禁止數學加工）。
4. **必須**輸出完整 generator contract（§2.0.4、PipelineFlow §2.4 Step 2）；`answer_type` 與 induced spec 一致。

**`generate()` 通用輸出契約**（不相關欄位可為空陣列／空物件，但依 `answer_type` 所需欄位**不可缺失**）：

```json
{
  "question_text": "",
  "answer_type": "short_answer | single_choice | multi_part | table_fill | drawing",
  "answer": {},
  "choices": [],
  "subquestions": [],
  "table_question": {},
  "table_data": {},
  "image_base64": "",
  "visual_spec": {},
  "visual_aids": [],
  "ui_contract": {},
  "answer_contract": {}
}
```

```python
# ✅ v1.4 合法 generate.py 骨架（搬運工）
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="two_points",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"integer_coefficients": True},
    )
    givens = matrix["givens"]
    answer = matrix["answer"]["canonical_form"]
    choices = [answer] + list(matrix["distractors"])
    # ... 僅模板填空與 payload 封裝，無 SymPy、無坐標重算
    return {
        "question_text": f"過點 A{givens['point_a']} 與 B{givens['point_b']} 的直線方程式為何？",
        "correct_answer": answer,
        "choices": choices,
        "visual_spec": matrix["visual_spec"],
        "math_core": {"givens": givens, "derivation": matrix["explanation_steps"]},
    }
```

```python
# ❌ v1.4 禁止：generate.py 內自行計算
import sympy as sp
slope = (y2 - y1) / (x2 - x1)          # ai_math_operation_forbidden
distractors = [f"y={slope}x+{b+1}", ...]  # 禁止
visual_spec["points"][0]["x"] = x1 + 1    # 禁止
```

### 2.7 Domain 註冊與對應層（Registry 中繼 · v1.5 / v1.6）

**模組**：`core/registry/taxonomy_registry.py`（**IMPLEMENTED**）

Registry 為 **Skill-Fixed Domain Authority** 之唯一 routing 權威（§1.6.1）。AI 或 induced spec **不得**覆寫 `fixed_domain_key`。

Registry **分兩層責任**：

| 層 | 資料結構 | 職責 |
|----|----------|------|
| 行政 + 主 Domain 綁定 | `SKILL_DOMAIN_PROFILE` | `skill_id → fixed_domain_key`（或 `domain` token）+ `curriculum_profile` |
| 模組路由 + operation 白名單 | `SKILL_TO_DOMAIN` | `domain_module` + `entrypoint` + `allowed_operations` / `allowed_types` |

```python
SKILL_DOMAIN_PROFILE = {
    "vh_數學B1_DistanceBetweenPointAndLine": {
        "domain": "coordinate_geometry",           # 或等價 fixed_domain_key 前綴
        "fixed_domain_key": "coordinate_geometry.point_line_distance",  # v1.6 目標欄位
        "curriculum_profile": "vocational_high_b",
        "registry_revision": "2026-06-22",
    },
}
```

**Component induced spec** 在固定 Domain 內決定數學操作（**不得**改派 Domain）：

```json
{
  "component_id": "src_4575",
  "domain_operation": "point_to_line_distance",
  "problem_type_id": "distance_from_point_to_line",
  "answer_schema_key": "distance_scalar",
  "presentation_mode": "short_answer",
  "checker_key": "rational_checker"
}
```

**剛性原則**：

1. `skill_id` 硬編碼**只能**停留在 Registry / Taxonomy 設定層；**絕對禁止**傳入 `core/domain/` 內部。
2. 每 skill **唯一** `fixed_domain_key`；AI **不得**建議或寫入其他 `domain_key` 作為 routing。
3. **禁止**因同屬一 skill 而共用 answer schema；每 component 自 induced spec 帶入 `answer_schema_key`。
4. Domain 入口可選 `build_coordinate_geometry_matrix(domain_operation=...)`；`domain_operation` **必須**落在 `allowed_operations`，否則 `DOMAIN_OPERATION_MISSING` → Domain Function Extension（§1.8）。
5. 重新生成 / 發布時須驗證 `component.domain_key == Registry.fixed_domain_key`；不一致 → `needs_regeneration`（§1.6.10）。

#### Amendment 2026-06-22: coordinate geometry distance contracts

For point-to-line distance components, `answer_schema_key` MUST be resolved from
`problem_type_id` or an explicit `domain_operation` contract. It MUST NOT be
inherited from the whole coordinate-geometry domain.

Required contract examples:

| problem_type_id | answer_schema_key | required semantic fields |
|---|---|---|
| `distance_from_point_to_line` | `distance_scalar` | `distance` |
| `distance_from_point_to_line_parameter` | `parameter_scalar` | `parameter`, `distance`, `parameter_name` |
| `distance_from_point_to_line_parameter_single_choice_scalar` | `parameter_scalar` | `parameter`, `solution_cardinality=single`, `choice_value_shape=scalar` |
| `compare_point_to_line_distances` | `comparison_label` | `target_direction`, `closer_line`, `farther_line`, `comparison_relation`, `comparison_result`, `distances` |

Canonical line-equation serialization is owned by the domain model:

- `_format_general_expression(A, B, C)` returns only the left-hand expression.
- `_format_general_form(A, B, C)` appends exactly one `= 0`.
- Components and adapters must not repair duplicated equation text with runtime
  string replacement.

Source completeness is part of verification. A distance-parameter source missing
the point coordinates is `needs_human_review`, not `verified`. Auto-promotion and
partial publish must not re-promote such stale components. A component is
`verified` only after source completeness, answer schema validation, component
compile/smoke, multi-seed integrity, and semantic topology checks pass.

### 2.8 四層錯誤責任（v1.5 · IMPLEMENTED）

**模組**：`core/gencode/failure_responsibility.py`

| 層級 | 典型錯誤 | 處置 |
|------|----------|------|
| `component_local_failure` | 題幹模板缺欄、choices 重複、LaTeX 錯 | 只修該 component；最多 3 次 repair |
| `domain_operation_failure` | 距離公式錯、無法產生合法參數 | 標記 domain failure；禁止 AI 改寫 component 內數學 |
| `domain_capability_gap` | 白名單無所需 operation、缺通用 function | `DOMAIN_FUNCTION_MISSING` → §1.8 Extension |
| `operation_contract_mismatch` | AI 選 operation 與 source facts 不符 | fail-fast；不得生成 / 發布（§1.6.9） |
| `shared_contract_failure` | 多題相同 schema mismatch、registry 缺失 | **停止** component-level AI repair；修正共用架構後批次重跑 |
| `packaging_failure` | manifest / dispatch / wrapper 不一致 | 只重跑 compiler + integrity gate；不重新生成 component |

Batch dry-run 若偵測 ≥2 題完全相同之 `answer_schema_mismatch` → `should_skip_component_repair=true`。

### 2.9 兩種合法重建入口（v1.8）

| 入口 | 用途 | 行為 |
|------|------|------|
| **Skill Batch Build** | 新 skill 首次建立；整 skill 重建；Domain function／schema 重大變更後批次重建 | 逐 `textbook_example` 獨立 component；單題失敗不污染姊妹題；**允許**整 skill 重跑 |
| **Component Targeted Rebuild** | 單題修復；induced spec 調整；單題 generator 修復 | 只重建 `src_{id}`；通過後重跑該 skill wrapper compiler |

後台「⚡產生/重構出題程式」預設為 **Component Targeted Rebuild**；Skill Batch Build 由 CLI／管理員批次觸發。兩者共用 `run_gencode_phase2_v3_shadow_bridge` / `run_admin_v3_dryrun_for_example`，禁止第二套生成邏輯。

---

## 3. 應用問題與圖片題特殊處理防線

### 3.1 Phase 1：單題故事層與數學核心層解構（同構用）

**目標**：為**每一道**教材原題建立同構變異模板；數學核心由 Domain Function 算子盾牌產生，AI 僅負責題幹填空。

**強制三步解構**（每題獨立，在 `problem_type_induction` / Phase 1 merge 階段執行）：

```
┌─────────────────────────────────────────────────────────────┐
│ 原始 Source Example（課本文本 + 圖 + 答案）                    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer A：Story Layer         │
              │ - 人名、單位、情境動詞          │
              │ - 非數學修飾語                │
              │ → scenario_pool / literacy_stem │
              └─────────────┬───────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer B：Math Core Layer     │
              │ - target_task                │
              │ - givens / unknowns / constraints│
              │ → Domain Function 算子盾牌     │
              └─────────────┬───────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer C：Presentation Layer  │
              │ - data_presentation 模式     │
              │   (text/image/graph/         │
              │    readonly_table/canvas)    │
              │ - answer_type（西堤套餐）    │
              │ - presentation_mode Key      │
              │ - ui_contract / answer_contract│
              │ → SOURCE_KIND → ORDER_WEIGHT │
              └─────────────────────────────┘
```

**操作規則**（v1.3 同構優先）：

1. **一題一 component**：每道教材原題對應獨立 `component_id`（§1.5）；Story / Math Core / Presentation 三層僅用於**單題**模板填空，不驅動跨題聚類。
2. **Story 不得綁定 Checker**：`answer_contract` 只能來自 Math Core + Presentation；應用題故事層固定於該題 `SCENARIO_POOL`（§3.4）。
3. **禁止跨題拆分或合併**：同一 `textbook_examples.id` 即一個 `src_{id}` component；兩道獨立教材題 → 兩個獨立 component，**不得** AI 融合或拆分。
4. **去糖衣驗證**：Math Core 必須能在純數學模式下由 Domain Function 產生合法 payload；數值與答案僅來自算子盾牌。

### 3.2 圖片掛載機制：禁止 AI 手寫繪圖

| 角色 | 允許 | 禁止 |
|------|------|------|
| Gemini Flash（component `generate.py`） | 輸出 `visual_spec` JSON（坐標、線段、標籤、統計表） | `import matplotlib`、`plt.`、`PIL.`、任何 `image_base64 =` 賦值 |
| 底層管線 | 將 `visual_spec` 轉為 `image_base64`，附掛至 payload | — |
| Visual Validator | 對 `visual_spec` 執行幾何重算與範圍檢查（見 §3.2.2） | — |
| 前台 | 讀取 `image_base64` 或 `visual_asset_type` 渲染 | 執行 component 內嵌繪圖代碼 |

#### 3.2.1 `visual_spec.kind` 全中學數學範疇

V3 將 `kind` 擴展為下列 **canonical spec 類型**（`visual_spec.kind` 欄位值）：

| kind | 語意 | 典型數學場景 |
|------|------|-------------|
| `coordinate_plane_spec` | 坐標平面上的點、線、函數圖形 | 直線方程式、兩點距離、象限 |
| `geometry_diagram_spec` | 純幾何構圖（不一定有坐標軸） | 三角形、中線、角平分線 |
| `statistics_chart_spec` | 統計圖表 | 長條圖、折線圖、累積頻率 |
| `tree_diagram_spec` | 樹狀圖 / 列表樹 | 排列組合、機率樣本空間 |
| `table_spec` | 數據表格 | 分組頻率、二維列聯表 |
| `number_line_spec` | 數線 | 不等式解區間、絕對值 |

**`coordinate_plane_spec` 標準形狀**（component 輸出，管線消費）：

```python
visual_spec = {
    "kind": "coordinate_plane_spec",
    "points": [{"x": 1, "y": 2, "label": "A"}],
    "lines": [
        {"type": "horizontal", "y": 3, "label": "L1"},
        {"type": "vertical", "x": -2, "label": "L2"},
        {"through_points": ["A", "B"], "label": "L3"},  # 過兩點的直線
    ],
    "x_range": [-8, 8],
    "y_range": [-8, 8],
}
# generate() 回傳前禁止自行渲染；由 slot_generators 或 visual runtime 統一轉換：
# payload["image_base64"] = render_visual_spec(visual_spec)
# payload["visual_asset_type"] = "coordinate_plane_spec"
```

#### 3.2.2 圖形語意驗證器（Visual Validator）

**模組**：`core/gencode/visual_schema_validators.py`（V3 目標）

##### 三層權責剛性劃分（產生 / 搬運 / 審核）

| 層級 | 職責 | 剛性邊界 |
|------|------|----------|
| **Domain 邏輯層**（`core/domain/`） | **產生** | 利用 SymPy 等算子** deterministic** 產出答案、干擾項與 `visual_spec` 繪圖數據；寫入 Full Matrix Dictionary |
| **Component 層**（`generate.py`） | **搬運** | 僅將 Domain 回傳的 `visual_spec` 填入 payload，並以 f-string 包裝題幹；**嚴禁** SymPy、數學四則運算、坐標重算 |
| **Validator 層**（`visual_schema_validators`） | **審核** | **完整保留**代數幾何重算與斷言權力；沙盒驗證鏈中須放行 Validator 重新計算直線方程式、點線關係等，對搬運結果做剛性交叉驗證 |

> **與 §2.3.1 AST 掃描的關係**：`ai_math_operation_forbidden` **僅約束** `generate.py`（Component 層）不得在答案路徑手算數學；Validator 層的幾何重算屬**審核權**，不列入 AI 自算限制，亦不得被 AST 規則誤殺。

當 component payload 含 `visual_spec` 時，Phase 2.5 沙盒 **Fail-Fast** 驗證鏈必須調用此模組，進行**數學幾何剛性重算**，確保圖文 100% 一致：

| 驗證函式 | 觸發條件 | 檢查內容 |
|----------|----------|----------|
| `validate_coordinate_points_in_range` | `kind` 含 `coordinate` / `geometry` | 所有點 `(x,y)` 落在 `x_range` × `y_range` 內 |
| `validate_line_passes_through_points` | `lines[].through_points` 存在 | 重算直線方程，驗證必過宣告的兩點 |
| `validate_horizontal_line_y` | `lines[].type == "horizontal"` | 水平線 `y` 值與題幹 givens 一致 |
| `validate_vertical_line_x` | `lines[].type == "vertical"` | 鉛直線 `x` 值與題幹 givens 一致 |
| `validate_tree_diagram_branch_counts` | `kind == "tree_diagram_spec"` | 樹分支數與 `expected_paths` / `expected_count` 一致 |
| `validate_statistics_chart_data` | `kind == "statistics_chart_spec"` | 圖表數據列與 `math_core.givens` 數值一致 |

驗證失敗 → `visual_semantic_mismatch` blocker；觸發 component 級修補閉環（優先檢查 Domain 產出與 `generate.py` 搬運是否一致，**不**改繪圖引擎；Validator 重算邏輯本身不得削弱）。

**附掛規則**：

- `presentation_mode` 為 `single_choice` / `choice` / `integer` 時，均可帶 `image_base64`；圖為題幹附件，不改變 `checker_key`。
- `handwriting` + 樹狀圖/列表題：走 B4 `visual_or_handwriting_ai_checked` 契約（`core/routes/practice.py` 既有路徑），component 只輸出 `expected_paths` / `tree_depth` 等數據。

### 3.3 `get_hint(step)` 三階段引導式提示（強制 Skeleton）

每個 component **必須**實作 `get_hint.py`，且通過沙盒測試 `step in {1,2,3}` 均回傳非空字串。

```python
# agent_skills_v3/{skill_id}/components/{component_id}/get_hint.py
from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示 — 強制語意骨架。
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    payload = question_payload or {}
    story_ctx = str(payload.get("story_context") or "")
    math_core = payload.get("math_core") or {}
    givens = math_core.get("givens") or payload.get("metadata", {}).get("givens") or []

    if step == 1:
        # ── 閱讀轉譯：從故事層提取已知與所求，不給公式 ──
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return (
            f"請先閱讀題目，找出已知條件與要求的量。"
            f"{'情境：' + story_ctx if story_ctx else ''}"
            f"目前已知：{given_text}。請用一句話說明「要求什麼」。"
        )

    if step == 2:
        # ── 數學建模：建立變數、選擇數學物件，不展開完整計算 ──
        target = str(math_core.get("target") or payload.get("metadata", {}).get("target") or "未知量")
        objects = math_core.get("math_objects") or []
        obj_text = "、".join(objects) if objects else "適當的數學關係"
        return (
            f"將文字條件轉成數學語言：設定變數，並指出此題屬於「{obj_text}」類型。"
            f"目標是求：{target}。"
        )

    if step == 3:
        # ── 算式推導：給出關鍵一式或下一步，不直接給最終答案 ──
        derivation = math_core.get("derivation") or payload.get("metadata", {}).get("derivation") or []
        if derivation:
            return f"依序思考：{' → '.join(str(d) for d in derivation)}。寫出關鍵算式後再化簡。"
        return "寫出本題適用的核心公式，代入已知數值，逐步化簡得到答案。"

    return ""  # step 非法時回空；沙盒測試僅驗證 1–3
```

**強制要求**：

- `generate()` 回傳的 payload **應**包含 `math_core` 子物件（含 `givens`, `target`, `math_objects`, `derivation`），供 `get_hint` 數據驅動。
- 禁止在 hint 中輸出與 `correct_answer` 等價的最終數值（防洩答）。
- RAG 三層檢索（圖譜 / 課本 / SKILL.md）仍為 Review 模式補充；`get_hint` 為確定性鷹架，不依賴 LLM 即時生成。

### 3.4 應用問題「挖洞模板化」：`SCENARIO_POOL` 規範

應用題 / 情境字題的 Story Layer **禁止**在學生練習時由 LLM 即時自由發揮。Codegen 提示範本**強制**要求 AI 將應用題編寫為預定義字典陣列：

```python
# generate.py — 應用題強制結構（AI 模板工程師產出）
SCENARIO_POOL = [
    {
        "id": "prize_draw",
        "subject": "小朋友",       # 故事主體 A
        "object": "獎品",          # 故事客體 B
        "verb": "抽取",
        "template": "{subject}從箱中{verb}{object}，已知...求...",
    },
    {
        "id": "ice_cream_shop",
        "subject": "學生",
        "object": "冰淇淋",
        "verb": "購買",
        "template": "某{object}店，{subject}{verb}後...求...",
    },
    # ... 至少 3 筆，由 Phase 1 scenario_pool 驅動
]

def _pick_scenario(seed: int | None) -> dict:
    rng = random.Random(seed)
    return rng.choice(SCENARIO_POOL)

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict:
    scenario = _pick_scenario(seed)
    # Math Core 由 Domain Function 計算（見 §2.3.1）
    math_result = _DOMAIN_HELPER.compute(...)  # 正確答案來自算子，非 AI
    question_text = scenario["template"].format(
        subject=scenario["subject"],
        object=scenario["object"],
        verb=scenario["verb"],
        # ... 僅允許 f-string / format 剛性填空
    )
    ...
```

**剛性規則**：

1. Runtime 出題時**僅**透過 `seed` 從 `SCENARIO_POOL` 抽選故事層；禁止呼叫 LLM 改寫題幹。
2. 允許變異的僅為 `SCENARIO_POOL` 內預審詞彙；數值、答案、圖形坐標仍由 Domain Function 決定。
3. `question_text` 內的數學條件必須與 `math_core` 一致；沙盒以 `visual_schema_validators` 與 payload validator 交叉驗證。
4. 違反（執行期呼叫 `call_ai_*` 生成題幹）→ `runtime_llm_story_forbidden` blocker。

---

## 4. 優雅降級與放手哲學

### 4.1 子組件沙盒隔離測試

每個 `component_id` 在併入 manifest 前，**獨立**執行沙盒測試（不 import 姊妹 component）：

```bash
python -m pytest agent_skills_v3/{skill_id}/components/{component_id}/tests/ -q
```

**最低通過清單**：

1. `metadata.py` 八維度靜態校驗通過。
2. `generate(level=1, seed=0)` 連續 5 次無例外；payload 通過 `validate_generator_payload()` + `validate_generated_question_format()`。
3. `check(correct, correct)` 為 True；`check(wrong, correct)` 為 False。
4. B4 題型額外通過 `b4_validators.validate_problem_payload_contract()`。
5. `get_hint(1..3)` 皆非空。
6. 若含 `visual_spec`：斷言 component 內**無** `matplotlib` / `PIL` import；且通過 `visual_schema_validators` 全項檢查。
7. 斷言 `generate.py` 無違反 §2.3.1 的 AI 自算數學運算。
8. 應用題斷言存在 `SCENARIO_POOL` 且執行期不呼叫 LLM 改寫題幹。

沙盒失敗**只標記該 component**，不影響其他 component 的測試進程。

### 4.2 單一組件修補閉環（v1.3：修補半徑 = 單一題目檔案）

因採行「一題一 `generate.py`」架構，`gencode_closed_loop/controller.py` 的修補半徑**縮小至單一題目檔案**：

1. 讀取 `GENERATOR_REPAIR_CATALOG` 或 component 路徑映射，**僅**鎖定 `components/src_{textbook_example_id}/generate.py`。
2. 將 `blockers` + `generation_errors` 作為 Negative Feedback 餵給 Gemini Flash。
3. 覆寫**該單檔**後重跑沙盒；**不得**連帶修改姊妹題檔案。

```text
MAX_RETRY_PER_COMPONENT = 3   # 每道原題獨立計次
```

### 4.3 放手降級與動態發布門檻（v1.3 Partial Publish）

> **v1.3 修訂**：核心例題（`required_core_components`，以 `src_{textbook_example_id}` 標識）`verified` 即可 **Partial Publish**；單一隨堂或自我評量失敗不阻斷發布、不觸發 skill 級 `SYSTEM_INTERRUPT`。

#### 4.3.1 `skill.json` 發布門檻宣告

```json
{
  "skill_id": "vh_數學B4_SimplePermutation",
  "display_name": "簡單排列",
  "expected_component_count": 5,
  "required_core_components": [
    "src_4545",
    "src_4546"
  ]
}
```

| 欄位 | 說明 |
|------|------|
| `expected_component_count` | 此 skill 預期應有的 component 總數（例題 + 隨堂 + 自我評量）；用於覆蓋率審計 |
| `required_core_components` | **必須 verified 才能發布**的核心例題 `component_id` 清單（**必須**為 `src_{textbook_example_id}`） |

##### 4.3.1.1 `required_core_components` 權限剛性鎖定（禁止 AI 自動判定）

`agent_skills_v3/{skill_id}/skill.json` 中的 `required_core_components` 為**發布門檻憲法級欄位**，寫入權限嚴格限定：

| 合法寫入來源 | 說明 |
|-------------|------|
| `k12_component_taxonomy.yaml` 內該 `skill_id` 的靜態 `required_core_components` 條目 | **首選唯一自動來源** |
| 架構師人工預置 / PR 審核合併 | 僅限擴充 MVP 範疇時 |

**嚴禁行為**（Phase 1 案源誘導、Phase 2 Codegen、修補閉環、AI 提示詞）：

1. 管線程式**不得**依誘導結果動態新增、刪除或改寫 `required_core_components`。
2. Gemini Flash **不得**在 `generate.py` / `metadata.py` 或任何產物中輸出「建議 core 清單」並由腳本寫回 `skill.json`。
3. 禁止 AI 投機性地將高難度核心題型從 `required_core_components` 移除，以規避發布門檻。

**防禦意圖**：確保發布門檻反映課綱真實核心，而非 AI 討好式降標。

> `expected_component_count` 亦僅能由 Taxonomy 靜態條目或架構師預置；AI 與 Phase 1/2 管線同樣**不得**自動修改。

#### 4.3.2 動態發布判定邏輯

| 條件 | 管線行為 |
|------|----------|
| 單一非核心 component（`SOURCE_KIND=quiz` / `test`）重試 3 次仍失敗 | 標記 `GENERATOR_READINESS = "failed"`；寫入 manifest `status: failed`；**停止該題修補**；從發布清單剔除 |
| `required_core_components`（`src_*` 核心例題）**全部** `verified` | **Partial Publish**：將其餘 `verified` 題目編譯發布；`failed` 題**直接剔除** |
| `required_core_components` 僅 1 個且該項 `verified` | **允許 Partial Publish**（小技能豁免） |
| 任一 `required_core_components` 未達 `verified` | `publish_status: blocked`；**仍不觸發** `SYSTEM_INTERRUPT` |
| 無 `required_core_components` 宣告時（舊 skill 過渡） | fallback：`verified_count >= max(2, ceil(expected_component_count * 0.5))` |
| controller 無法定位任何可修補檔案，或 skill 級基礎設施損壞 | **唯一**觸發 `SYSTEM_INTERRUPT` 的情境 |

**關鍵原則（v1.3）**：

- `SYSTEM_INTERRUPT` **禁止**因單一非核心題失敗而觸發。
- 只要 `skill.json` 預置的核心例題組件處於 `verified`，系統便將通過題目編譯發布（Partial Publish），失敗題目靜默剔除。
- `publish_status` 可為 `partial_published`（含剔除的 failed 題）或 `full_published`（全部 verified）。

```python
# 動態發布決策虛擬碼（skill_wrapper_compiler 內）
skill_meta = load_skill_json(skill_id)
required = skill_meta.get("required_core_components") or []
verified_ids = {c["component_id"] for c in manifest["components"] if c["status"] == "verified"}

if required:
    core_ok = all(cid in verified_ids for cid in required)
    if core_ok:
        compile_partial_router(skill_id, [c for c in manifest["components"] if c["status"] == "verified"])
        sync_verified_registry(skill_id, verified_ids)
        publish_status = "partial_published" if any_failed else "full_published"
    else:
        publish_status = "blocked_core_components_missing"
else:
    # 舊 skill 過渡 fallback
    verified = [c for c in manifest["components"] if c["status"] == "verified"]
    threshold = max(2, math.ceil(skill_meta.get("expected_component_count", 2) * 0.5))
    publish_status = "partial_published" if len(verified) >= threshold else "blocked_insufficient_components"
```

### 4.4 manifest 記錄格式

`component_id` **必須**為 `src_{textbook_example_id}`（§1.2.2），不得使用 `target_task` 或任務聚類命名。

```json
{
  "skill_id": "vh_數學B1_LinearFunction",
  "compiled_at": "2026-06-15T14:30:00+08:00",
  "publish_status": "partial_published",
  "components": [
    {
      "component_id": "src_4545",
      "status": "verified",
      "presentation_mode": "single_choice",
      "checker_key": "choice_label_checker",
      "retry_count": 1
    },
    {
      "component_id": "src_4610",
      "status": "failed",
      "last_error": "generator_semantically_unsafe: choices mismatch",
      "retry_count": 3
    }
  ]
}
```

---

### 4.5 教材例題權威庫資料庫（DB Schema）增量設計

本節為 v1.4 **線上滾動式維運**所需之**唯一允許** DB 增量設計。  
**不修改** `textbook_examples` 既有欄位結構；Gencode 管線狀態、Low-Code 誘導規格與沙盒錯誤日誌**全部**收斂至獨立影子對接表 `gencode_component_tracker`。  
**嚴禁**修改學生練習紀錄、答題軌跡、成績彙總等學習數據表。

#### 4.5.1 Current Production DDL（SQLite 3 · 現行 CHECK）

> **v1.8**：下列 CHECK 為**現行 production** 已對齊值。Target V3 擴充狀態見 §4.5.2；**須 migration 後**方可寫入 DB。

```sql
CREATE TABLE IF NOT EXISTS gencode_component_tracker (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    textbook_example_id     INTEGER NOT NULL,
    skill_id                TEXT    NOT NULL,
    component_id            TEXT    NOT NULL,
    gencode_status          TEXT    NOT NULL DEFAULT 'pending',
    induced_spec_payload    TEXT,
    gencode_error_log       TEXT,
    created_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    CONSTRAINT fk_gencode_component_tracker_example
        FOREIGN KEY (textbook_example_id) REFERENCES textbook_examples (id) ON DELETE CASCADE,
    CONSTRAINT fk_gencode_component_tracker_skill
        FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
    CONSTRAINT uq_gencode_tracker_example_id
        UNIQUE (textbook_example_id),
    CONSTRAINT uq_gencode_tracker_namespace_pool
        UNIQUE (skill_id, component_id),
    CONSTRAINT ck_gencode_status_values
        CHECK (gencode_status IN (
            'pending', 'usable', 'generating', 'verified', 'failed',
            'enrichment', 'needs_human_review', 'needs_regeneration',
            'unsupported_domain_operation'
        ))
);
```

**Migration 前程式相容**：新錯誤碼應寫入 `gencode_error_log` 結構化 JSON；`gencode_status` 暫用 `failed` 或 `needs_human_review`，**不得**誤算為 `unsupported`。

```sql
CREATE INDEX IF NOT EXISTS idx_gencode_tracker_query_gate
    ON gencode_component_tracker (skill_id, gencode_status);
CREATE INDEX IF NOT EXISTS idx_gencode_tracker_reverse_lookup
    ON gencode_component_tracker (textbook_example_id);
```

**雙重 UNIQUE**：`uq_gencode_tracker_example_id`（一題一列）；`uq_gencode_tracker_namespace_pool`（skill 內 `component_id` 唯一）。

#### 4.5.2 狀態模型（Production · Target · Compatibility）

##### A. Current Production Status Values（上表 CHECK）

| 值 | 語意 |
|----|------|
| `pending` | 尚未進入 Phase 2 |
| `usable` | induced spec 就緒 |
| `generating` | Codegen 進行中 |
| `verified` | 通過 §1.6.11 與沙盒，可進 manifest |
| `failed` | 單題失敗（含 Extension／verification 失敗） |
| `enrichment` | 非核心題標記 |
| `needs_human_review` | 需人工審核 |
| `needs_regeneration` | Registry／spec 漂移待重跑 |
| `unsupported_domain_operation` | **Legacy**；v1.8 映射為 `DOMAIN_FUNCTION_MISSING` 流程入口，**非**終止 unsupported |

##### B. Target V3 Status Model（SOP 定義 · migration 後啟用）

`discovered`、`classified`、`domain_binding_resolved`、`domain_capability_checking`、`domain_function_missing`、`domain_extension_pending`、`domain_extension_testing`、`domain_extension_verified`、`bootstrapped`、`draft_written`、`compile_passed`、`smoke_passed`、`packaged`、`published`、`domain_extension_failed`、`generation_failed`、`compile_failed`、`smoke_failed`、`verification_failed`、`unsupported`

##### C. Migration Required

- 擴充 `ck_gencode_status_values` 以納入 Target 狀態
- 或新增 `pipeline_stage` / `error_code` 欄位承載內部階段
- **本輪僅修文件，不執行 migration**

##### D. Compatibility Mapping

| Legacy / 內部 | v1.8 規範 |
|---------------|-----------|
| `unsupported_domain_operation` | `DOMAIN_FUNCTION_MISSING` → Extension |
| `v3_shadow_bridge_not_executed` | `SHADOW_BRIDGE_NOT_EXECUTED` |
| tracker `failed` + `error_code` | 承載 Extension 進行中／失敗 |

#### 4.5.3 影子表 Service 層契約（行政歸屬斷言）

後端 Service 層在**新增或更新** `gencode_component_tracker` 紀錄前，**必須**強制檢查並斷言：

```text
gencode_component_tracker.skill_id == textbook_examples.skill_id
```

（其中 `textbook_examples` 為 `textbook_example_id` 所指向之列。）

| 項目 | 剛性要求 |
|------|----------|
| 寫入前校驗 | `INSERT` / `UPSERT` / `UPDATE` tracker 前，以 `textbook_example_id` 讀取 `textbook_examples.skill_id`，與待寫入之 `skill_id` 比對 |
| 不一致處置 | 斷言失敗 → 拒絕寫入，回傳 `skill_id_mismatch`（或等價 blocker）；**禁止**靜默覆寫或跨 skill 掛載 |
| `component_id` 連帶 | 寫入時 `component_id` **必須**為 `src_{textbook_example_id}`（見 §1.2.2），與硬碟目錄名一致 |

**防線意圖**：影子表為 `textbook_examples` 與微元件物理路徑的橋樑；跨表 `skill_id` 不一致將導致 Partial Publish、編譯器白名單與 `practice.py` 路由全面錯位。

#### 4.5.4 `induced_spec_payload` 內容契約

存放 Phase 1 **剛性去糖衣**後、由 AI 提取之純數學結構，**不含**自由發揮之故事層噪點。SQLite 3 以 `TEXT` 儲存 JSON 字串。建議 JSON 骨架：

```json
{
  "component_id": "src_4545",
  "skill_id": "vh_數學B1_PointSlopeForm",
  "domain_key": "coordinate_geometry.line_equation",
  "domain_version": "1.0",
  "domain_operation": "two_points",
  "operation_version": "1.0",
  "registry_revision": "2026-06-22",
  "target_task": "determine_linear_function_from_two_points",
  "presentation_mode": "single_choice",
  "math_core": {
    "givens": {},
    "constraints": {}
  },
  "story_template": "過點 {point_a} 與 {point_b} 的直線方程式為何？",
  "domain_params": {
    "line_type": "two_points",
    "curriculum_profile": "vocational_high_b",
    "difficulty_profile": "easy"
  }
}
```

管理員於後台修正文本噪點或 `domain_params` 後，透過 §4.6 觸發定點重構；**不得**在此欄位寫入可執行 Python 或 SymPy 程式碼。

#### 4.5.5 `gencode_error_log` 寫入規則

- 僅在狀態轉為 `failed`（或 `needs_regeneration` 保留前次摘要）時追加或覆寫（保留最近一次失敗摘要即可）。
- 範例：`Missing validation_facts matrix`、`ai_math_operation_forbidden: distractors assigned without Domain call`、`visual_semantic_mismatch: line does not pass through point B`。
- `verified` 時應清空或標記為 `NULL`，避免管理後台誤判。

---

### 4.6 後台「⚡重構出題程式」按鈕與動態熱拔插（Hot Swap）機制

本節將批次管線 CLI 行為，標準化為後台 **Low-Code 維運**操作，支援**單題定點**修復與**零重啟**上線。

#### 4.6.1 觸發源（管理後台）

| 項目 | 規範 |
|------|------|
| 按鈕文案 | **⚡產生/重構出題程式**（`admin.gencode.rebuild_component`） |
| 預設作用範圍 | **Component Targeted Rebuild**：單一 `src_{textbook_example_id}` |
| 批次入口 | **Skill Batch Build** 由 CLI／管理員另行觸發整 skill 重建（§2.9） |
| 前置條件 | 管理員已修正 `gencode_component_tracker.induced_spec_payload`（題幹模板、Domain 參數等） |
| 執行方式 | 非同步背景工作（Celery / RQ / 內建 job queue）；HTTP 立即回傳 `job_id`，避免阻塞後台 UI |

#### 4.6.2 定點 Codegen 與驗證（Phase 2 子集）

管線被喚醒後，**僅鎖定**該題：

1. 讀取 `gencode_component_tracker.induced_spec_payload` → 生成或覆寫 `agent_skills_v3/{skill_id}/components/{component_id}/generate.py`（及必要之 `metadata.py` / `get_hint.py`）。
2. 對該 `component_id` **獨立**執行 Phase 2.5 沙盒（AST、Full Matrix Dict、Validator、P0 Checker）；修補半徑仍為單檔，最多 3 次（§4.2）。
3. 通過 → `gencode_component_tracker.gencode_status = 'verified'`，清空 `gencode_error_log`，並由 Python 主動更新 `updated_at = datetime('now', 'localtime')`。
4. 失敗 → `gencode_status = 'failed'`，寫入 `gencode_error_log`，同步更新 `updated_at`；**不**觸發 skill 級 `SYSTEM_INTERRUPT`（§4.3）。

#### 4.6.3 編譯器一鍵重載（Reload Compiler）

單題 `verified` 後，自動調用 `skill_wrapper_compiler.py`（現行等價：`phase3_skill_codegen`）：

1. 重新掃描該 `skill_id` 下**所有** `gencode_component_tracker.gencode_status = 'verified'` 的列（見 Pipeline §3.4 Step 4 場景 2 SQL；**必須** `ORDER BY textbook_example_id ASC, component_id ASC`）。
2. 重寫 `component_manifest.json` 與 `agent_skills_v3/{skill_id}/__init__.py` 的 `_COMPONENT_DISPATCH` 路由器。
3. 重新生成 `skills/{skill_id}.py` Thin Facade 之 `GENERATOR_SPECS` / `GENERATOR_KEYS`。
4. 執行 Phase 3 smoke（可抽樣新修復之 `component_id` + `required_core_components` 回歸）。

#### 4.6.4 零重啟動態加載契約

| 層級 | 剛性要求 |
|------|----------|
| `__init__.py` 路由器 | 抽題命中 `component_id` 時，須透過 `importlib.import_module` 載入 `components.{component_id}.generate`；若模組已載入，須對該模組執行 `importlib.reload` 以取得最新 `generate.py` |
| `runtime_skill_wrapper` | 在 `generate_for_skill()` 路徑中，優先走 component dispatch；動態載入失敗時 fallback 既有 slot 路徑，**不得**使學生請求 500 |
| `practice.py` | **不得破壞** public route 與 response contract；仍 `importlib.import_module("skills.{skill_id}")` 後呼叫 `generate()`（§0.1.1） |
| 運維禁令 | Manifest 白名單更新後，**不允許**重啟整個 Web 伺服器作為發布手段；熱拔插必須在進行中請求下安全生效 |

```python
# __init__.py 動態載入契約（概念虛擬碼）
import importlib

def _load_component_generate(component_id: str):
    module_path = f"agent_skills_v3.{SKILL_ID}.components.{component_id}.generate"
    mod = importlib.import_module(module_path)
    return importlib.reload(mod) if module_path in sys.modules else mod
```

**熱拔插閉環**：後台按鈕 → 單題 Codegen + 驗證 → `gencode_component_tracker` 標記 `verified` → Reload Compiler → `importlib.reload` → 下一筆學生 `practice` 請求即命中新程式。

#### 4.6.5 影子表維運契約（剛性）

**時間戳更新契約（`updated_at`）**：

- 本表時間戳更新採用**做法 A**：由 Python 程式在執行 `UPDATE` SQL 時**主動填入** `datetime('now', 'localtime')`。
- **明確不啟用**資料庫隱式 Trigger 自動維護 `updated_at`，以保持管線維護與除錯的完全透明度。

**物理路徑推導契約**：

- 本表**不存儲** `component_path` 字串欄位。
- 執行期微元件路徑統一由 `skill_id` 與 `component_id` 依規則公式**動態拼接**：

```text
agent_skills_v3/{skill_id}/components/{component_id}/
```

- 避免硬碟目錄搬移或路徑重構時，DB 內過期絕對路徑造成數據漂移。

---

## 5. 與 V2 法規的銜接

| V2 條款 | V3 延伸 |
|---------|---------|
| 薄入口外殼原則（§13） | `skills/{skill_id}.py` 仍為唯一前台 import 路徑 |
| 插槽去耦合（§14） | component 委派 `SLOT_REGISTRY`，禁止複製 slot 邏輯 |
| Phase 錯誤對照地圖（§16） | V3 新增本目錄為 AgentSkillV3 專屬權威；Phase 1–2 仍對照 V2 總體設計 |
| `skill_id:family_id` RAG 身份 | component 內 `diagnosis_tags` 不改變 family 鍵 |

---

## 6. Codex 任務執行檢查清單

- [ ] **三層分離（§2.0.1）**：數學內容層、`data_presentation`、`answer_type` 分別決定，不得混用
- [ ] **西堤作答套餐（§2.0.2）**：`answer_type` 為五選一；貫穿 metadata、generate、UI、checker、validator、preview、smoke
- [ ] **作答決策（§2.0.3）**：依教材原始作答拓撲判定；作圖題不得降級 `short_answer`
- [ ] **禁止降級（§2.0.5）**：multi_part／table_fill／drawing 契約 violation 不得 verified
- [ ] **Skill-Fixed Domain Authority（§1.6）**：`skill_id` 自 DB 唯讀；Registry `fixed_domain_key` 不可被 AI 覆寫；無跨 Domain fallback
- [ ] **Verified 八項門檻（§1.6.11）**：除沙盒外須通過 skill/domain/operation/source/oracle/semantic/topology/runtime 驗證
- [ ] **物理佈局防線（§1.2）**：`skills/{skill_id}.py` 保留於 `skills/` 根目錄；每題 `py` 獨立於 `agent_skills_v3/{skill_id}/components/{component_id}/`；無大雜燴目錄
- [ ] **雙重寫入（§1.3、Pipeline §3.4 Step 4）**：Phase 3 已同步更新 `__init__.py` 之 `_COMPONENT_DISPATCH` 與原位 `skills/{skill_id}.py` Thin Facade
- [ ] **Domain Function Extension（§1.8）**：缺 function 走 Extension，禁止 generic／跨 Domain fallback
- [ ] **Auto-Bootstrap（§1.7）**：Bootstrap／Publish Gate 分離；`DOMAIN_BINDING_MISSING` 時停止生成、不猜 Domain
- [ ] 新數學邏輯寫入 **`core/domain/`**；`generate.py` 僅搬運；**不破壞** `practice.py` public contract（§0.1.1）
- [ ] **一題一 `generate.py`**：`component_id = src_{textbook_example_id}`；無多題合一
- [ ] `ORDER_WEIGHT` / `DIFFICULTY_LEVEL` 依 `SOURCE_KIND` 注入；MVP 不阻擋生成
- [ ] 核心 `required_core_components`（`src_*`）`verified` 即可 Partial Publish（§4.3）
- [ ] `skill_id` 硬編碼僅出現在 `taxonomy_registry`；`core/domain/` 內無 skill_id（§2.7）
- [ ] `generate.py` 為搬運工：無 SymPy、無 distractors 演算法、無 visual 坐標重算（§2.6）
- [ ] Full Matrix Dictionary 六大欄位由 Domain 一次算完（§2.3.2、§2.5.4）
- [ ] 直線方程式 P0：`build_line_equation_matrix` 檢查點通過（§2.5.5）
- [ ] `PRESENTATION_MODE` 使用穩定 Key；`handwriting` 已注入 `text_input_disabled` 等 payload 宣告
- [ ] `generate.py` 通過 AST 精準掃描（§2.3.1）；敏感區白名單運算未被誤殺
- [ ] 應用題已實作該題專屬 `SCENARIO_POOL`；執行期無 LLM 即時改寫題幹
- [ ] 直線 / 分數題已綁定 P0 Checker：`linear_equation_equivalent_checker` / `rational_or_decimal_checker`（§2.4.1）
- [ ] 無 matplotlib / PIL；`visual_spec` 由 Domain **產生**、`generate.py` **搬運**、Validator **審核**（§3.2.2 三層權責）；Validator 幾何重算不受 AST 自算限制
- [ ] `get_hint.py` 三階段 skeleton 已實作
- [ ] 沙盒測試獨立通過後才寫入 `component_manifest.json`
- [ ] `required_core_components` **僅**來自 Taxonomy / 架構師預置，未被 AI 或管線改寫（§4.3.1.1）
- [ ] 核心例題 `verified` 即可 Partial Publish；非核心題失敗剔除、不觸發 `SYSTEM_INTERRUPT`（§4.3）

---

*本文件為 AgentSkillV3 架構規範書 v1.8（Skill-Fixed Auto-Bootstrap · Domain Function Extension）。修訂須同步更新 [SOP_Gencode_AgentSkillV3_PipelineFlow.md](./SOP_Gencode_AgentSkillV3_PipelineFlow.md)。**實作狀態：SOP 已更新，程式尚待對齊。***
