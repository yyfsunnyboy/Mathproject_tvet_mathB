# Phase 4B-3 Generator 樣題人工審查報告

## 總體檢查表

| Generator | 樣題數 | 唯一參數組 | 重複狀況 |
|---|---|---|---|
| b4.counting.divisor_count_prime_factorization | 5 | 5 | 無重複 |
| b4.combination.combination_polygon_count | 5 | 5 | 無重複 |
| b4.combination.combination_required_excluded_person | 5 | 5 | 無重複 |

---

## Generator: b4.counting.divisor_count_prime_factorization

### 參數組檢查

- Seed 1: `('divisor_count_prime_factorization', (2, 3), (2, 1))`
- Seed 2: `('divisor_count_prime_factorization', (2, 11), (1, 2))`
- Seed 3: `('divisor_count_prime_factorization', (3, 11), (2, 3))`
- Seed 4: `('divisor_count_prime_factorization', (3, 5), (1, 3))`
- Seed 5: `('divisor_count_prime_factorization', (5, 11), (3, 2))`

**是否有重複 parameter_tuple**: 否

### 樣題列表

**Seed 1 (Difficulty 1)**
- **Question:** 已知 N = 2^2 × 3^1，則 N 有多少個正因數？
- **Choices:** 6, 4, 3, 5
- **Answer:** 6
- **Explanation:** 若 N = p1^a1 × p2^a2 × ...，正因數個數為 (a1+1)(a2+1)...，本題為 (2+1)(1+1)=6。
- **Parameters:** `{"primes": [2, 3], "exponents": [2, 1], "parameter_tuple": ["divisor_count_prime_factorization", [2, 3], [2, 1]]}`

**Seed 2 (Difficulty 1)**
- **Question:** 已知 N = 2^1 × 11^2，則 N 有多少個正因數？
- **Choices:** 6, 5, 4, 3
- **Answer:** 6
- **Explanation:** 若 N = p1^a1 × p2^a2 × ...，正因數個數為 (a1+1)(a2+1)...，本題為 (1+1)(2+1)=6。
- **Parameters:** `{"primes": [2, 11], "exponents": [1, 2], "parameter_tuple": ["divisor_count_prime_factorization", [2, 11], [1, 2]]}`

**Seed 3 (Difficulty 1)**
- **Question:** 已知 N = 3^2 × 11^3，則 N 有多少個正因數？
- **Choices:** 6, 12, 10, 11
- **Answer:** 12
- **Explanation:** 若 N = p1^a1 × p2^a2 × ...，正因數個數為 (a1+1)(a2+1)...，本題為 (2+1)(3+1)=12。
- **Parameters:** `{"primes": [3, 11], "exponents": [2, 3], "parameter_tuple": ["divisor_count_prime_factorization", [3, 11], [2, 3]]}`

**Seed 4 (Difficulty 1)**
- **Question:** 已知 N = 3^1 × 5^3，則 N 有多少個正因數？
- **Choices:** 6, 8, 4, 7
- **Answer:** 8
- **Explanation:** 若 N = p1^a1 × p2^a2 × ...，正因數個數為 (a1+1)(a2+1)...，本題為 (1+1)(3+1)=8。
- **Parameters:** `{"primes": [3, 5], "exponents": [1, 3], "parameter_tuple": ["divisor_count_prime_factorization", [3, 5], [1, 3]]}`

**Seed 5 (Difficulty 1)**
- **Question:** 已知 N = 5^3 × 11^2，則 N 有多少個正因數？
- **Choices:** 10, 11, 6, 12
- **Answer:** 12
- **Explanation:** 若 N = p1^a1 × p2^a2 × ...，正因數個數為 (a1+1)(a2+1)...，本題為 (3+1)(2+1)=12。
- **Parameters:** `{"primes": [5, 11], "exponents": [3, 2], "parameter_tuple": ["divisor_count_prime_factorization", [5, 11], [3, 2]]}`

---

## Generator: b4.combination.combination_polygon_count

### 參數組檢查

- Seed 1: `('combination_polygon_count', 6, 'diagonal')`
- Seed 2: `('combination_polygon_count', 7, 'triangle')`
- Seed 3: `('combination_polygon_count', 8, 'triangle')`
- Seed 4: `('combination_polygon_count', 5, 'diagonal')`
- Seed 5: `('combination_polygon_count', 8, 'diagonal')`

**是否有重複 parameter_tuple**: 否

### 樣題列表

**Seed 1 (Difficulty 1)**
- **Question:** 一個正 6 邊形共有多少條對角線？
- **Choices:** 7, 4, 9, 8
- **Answer:** 9
- **Explanation:** 對角線數公式為 C(n,2)-n，所以 C(6,2)-6=9。
- **Parameters:** `{"n": 6, "question_variant": "diagonal", "parameter_tuple": ["combination_polygon_count", 6, "diagonal"]}`

**Seed 2 (Difficulty 1)**
- **Question:** 一個正 7 邊形任取 3 個頂點可形成多少個三角形？
- **Choices:** 36, 35, 34, 33
- **Answer:** 35
- **Explanation:** 三角形數為 C(n,3)，所以 C(7,3)=35。
- **Parameters:** `{"n": 7, "question_variant": "triangle", "parameter_tuple": ["combination_polygon_count", 7, "triangle"]}`

**Seed 3 (Difficulty 1)**
- **Question:** 一個正 8 邊形任取 3 個頂點可形成多少個三角形？
- **Choices:** 54, 55, 56, 112
- **Answer:** 56
- **Explanation:** 三角形數為 C(n,3)，所以 C(8,3)=56。
- **Parameters:** `{"n": 8, "question_variant": "triangle", "parameter_tuple": ["combination_polygon_count", 8, "triangle"]}`

**Seed 4 (Difficulty 1)**
- **Question:** 一個正 5 邊形共有多少條對角線？
- **Choices:** 4, 5, 2, 3
- **Answer:** 5
- **Explanation:** 對角線數公式為 C(n,2)-n，所以 C(5,2)-5=5。
- **Parameters:** `{"n": 5, "question_variant": "diagonal", "parameter_tuple": ["combination_polygon_count", 5, "diagonal"]}`

**Seed 5 (Difficulty 1)**
- **Question:** 一個正 8 邊形共有多少條對角線？
- **Choices:** 40, 10, 18, 20
- **Answer:** 20
- **Explanation:** 對角線數公式為 C(n,2)-n，所以 C(8,2)-8=20。
- **Parameters:** `{"n": 8, "question_variant": "diagonal", "parameter_tuple": ["combination_polygon_count", 8, "diagonal"]}`

---

## Generator: b4.combination.combination_required_excluded_person

### 參數組檢查

- Seed 1: `('combination_required_excluded_person', 6, 3, 'required', 1)`
- Seed 2: `('combination_required_excluded_person', 6, 2, 'required', 1)`
- Seed 3: `('combination_required_excluded_person', 10, 2, 'excluded', 1)`
- Seed 4: `('combination_required_excluded_person', 6, 4, 'excluded', 1)`
- Seed 5: `('combination_required_excluded_person', 8, 4, 'required', 1)`

**是否有重複 parameter_tuple**: 否

### 樣題列表

**Seed 1 (Difficulty 1)**
- **Question:** 某班有 6 位同學，今選出 3 位參加活動，若甲必須入選，共有多少種選法？
- **Choices:** 10, 8, 5, 9
- **Answer:** 10
- **Explanation:** 必選情況先固定指定人物，再從剩下 5 人選 2 人，使用 C(n,r) 得 C(5,2)=10。
- **Parameters:** `{"n": 6, "r": 3, "constraint_type": "required", "k": 1, "parameter_tuple": ["combination_required_excluded_person", 6, 3, "required", 1]}`

**Seed 2 (Difficulty 1)**
- **Question:** 某班有 6 位同學，今選出 2 位參加活動，若甲必須入選，共有多少種選法？
- **Choices:** 4, 2, 5, 3
- **Answer:** 5
- **Explanation:** 必選情況先固定指定人物，再從剩下 5 人選 1 人，使用 C(n,r) 得 C(5,1)=5。
- **Parameters:** `{"n": 6, "r": 2, "constraint_type": "required", "k": 1, "parameter_tuple": ["combination_required_excluded_person", 6, 2, "required", 1]}`

**Seed 3 (Difficulty 1)**
- **Question:** 某班有 10 位同學，今選出 2 位參加活動，若甲不能入選，共有多少種選法？
- **Choices:** 34, 36, 35, 37
- **Answer:** 36
- **Explanation:** 不可選情況先排除指定人物，再從剩下 9 人選 2 人，使用 C(n,r) 得 C(9,2)=36。
- **Parameters:** `{"n": 10, "r": 2, "constraint_type": "excluded", "k": 1, "parameter_tuple": ["combination_required_excluded_person", 10, 2, "excluded", 1]}`

**Seed 4 (Difficulty 1)**
- **Question:** 某班有 6 位同學，今選出 4 位參加活動，若甲不能入選，共有多少種選法？
- **Choices:** 2, 3, 5, 4
- **Answer:** 5
- **Explanation:** 不可選情況先排除指定人物，再從剩下 5 人選 4 人，使用 C(n,r) 得 C(5,4)=5。
- **Parameters:** `{"n": 6, "r": 4, "constraint_type": "excluded", "k": 1, "parameter_tuple": ["combination_required_excluded_person", 6, 4, "excluded", 1]}`

**Seed 5 (Difficulty 1)**
- **Question:** 某班有 8 位同學，今選出 4 位參加活動，若甲必須入選，共有多少種選法？
- **Choices:** 33, 34, 35, 36
- **Answer:** 35
- **Explanation:** 必選情況先固定指定人物，再從剩下 7 人選 3 人，使用 C(n,r) 得 C(7,3)=35。
- **Parameters:** `{"n": 8, "r": 4, "constraint_type": "required", "k": 1, "parameter_tuple": ["combination_required_excluded_person", 8, 4, "required", 1]}`

---

## 結論

1. 三個 generator 皆成功產生各 5 題樣題。
2. 經過 seed 抽樣微調，前 5 個 seed 皆無發生 parameter_tuple 碰撞。
3. 題幹、選項與詳解格式皆符合規範。
4. Phase 4B-3 的三個 generator 已具備高可靠度的決定性與多樣性。
