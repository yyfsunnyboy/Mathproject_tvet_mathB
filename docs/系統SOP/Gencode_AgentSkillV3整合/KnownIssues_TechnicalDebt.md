# Known Issues / Technical Debt

## CartesianCoordinateSystem skill-local `check()` 字串比對

- 位置：`skills/vh_數學B1_CartesianCoordinateSystemEstablishment.py` 的 skill-local `check()`
- 現象：仍存在 skill-local 字串比對，未走共用數學等價 checker
- 範圍：不屬於共用 checker 層；與 B1 Chapter 3 無關
- 本輪：不處理、不順手修
- 狀態：deferred

runtime wrapper `check_answer` 在 contract 指向象限 checker 時仍走共用路徑。未對齊的是 skill 本體 `check()`。
