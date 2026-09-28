# B3 跨機器執行清單

1. `git pull`
2. 啟動專案 venv
3. 若 `requirements.txt` 有變，安裝相依套件
4. 還原或同步正式資料庫
5. 若資料庫早於圖片 linkage，執行 `python scripts/repair_b3_visual_asset_links.py --apply`（可重複執行，不會重複寫入）
6. 手動啟動 app
7. 例題管理中心篩選技高 / 11 / 數學B3，確認已完成題顯示「已上線」
8. 各抽一題確認：附圖題、多格作答、選擇題
