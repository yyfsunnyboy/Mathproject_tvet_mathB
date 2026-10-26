# 數學2 Unit 1 正式發布 — 回滾紀錄（2026-10-25；未發生回滾）

- 授權：Yang-Fu Yeh，聊天內明確授權（見 deploy_unit1_approval_record.json）；範圍 gh_Sequence 17 + gh_RecursiveRelation 9 = 26 components。
- 備份目錄：`backups/math2_unit1_sequence_progression/20261025_204242/`（kumon_math.db 完整備份、gencode_promoted_capabilities.json、skill 綁定、tracker 原列（0 列））。
- 回滾步驟（均未執行）：
  1. `python reports/gh_math2_unit1_bundle/deploy_unit1.py rollback-publish --confirm`（移出 skills/gh_Sequence.py、gh_RecursiveRelation.py 與 agent_skills_v3/<skill>）。
  2. 以備份的 gencode_promoted_capabilities.json 還原 configs/，並移除 core/domain/promoted/sequence_progression/。
  3. 刪除 gencode_component_tracker 中 textbook_example_id 12667-12706 的 26 列（備份時為 0 列）。
  4. 若服務已載入新綁定，才需要重啟 Flask。
- Stage 1 教材（textbook_examples 等）本次發布未被改動。
