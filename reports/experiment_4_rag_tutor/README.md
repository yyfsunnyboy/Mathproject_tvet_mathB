# Experiment 4: Weak + RAG Tutor（研究等級分析）

本資料夾呈現 Weak 學生在相同 AB3 與 foundation support 條件下，
baseline 與 RAG tutor 的對照結果。所有數值均來自當次模擬輸出，未使用人工填值。

## 核心結論
- RAG 的主要價值在於提升學習效率（learning efficiency），不只是最終表現。
- 改善增益集中在較弱子技能，顯示介入具有目標導向特性。
- breakpoint 仍可用於辨識尚未突破的結構性瓶頸。

## 主要輸出
- `rag_vs_baseline_summary.csv`：baseline vs RAG 的主指標摘要。
- `rag_efficiency_summary.csv`：`learning_efficiency = mastery_gain / total_steps`。
- `rag_subskill_summary.csv`：各子技能起始/最終/增益摘要。
- `rag_breakpoint_shift.csv`：失敗案例 weakest subskill 分布。
- `fig_rag_efficiency.png`：效率主圖（標示最佳方法與相對 baseline 改善）。

## 研究解讀
- RAG improves efficiency, not just performance.
- Gains are concentrated on weak subskills.
- Results indicate intelligent targeting behavior under constrained interventions.
