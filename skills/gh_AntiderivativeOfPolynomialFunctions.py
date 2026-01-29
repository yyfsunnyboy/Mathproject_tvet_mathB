# ==============================================================================
# ID: gh_AntiderivativeOfPolynomialFunctions
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 119.27s | RAG: 2 examples
# Created At: 2026-01-29 13:30:34
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# --- 2. Number Theory Helpers ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

def op_latex(num):
    return fmt_num(num, op=True)

def clean_latex_output(s):
    return str(s).strip()

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度，僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理：剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}


import re

from datetime import datetime

# --- Helper Functions (遵循視覺化與輔助函式通用規範) ---

def _generate_polynomial_term_params(min_coeff, max_coeff, min_exp, max_exp, allow_zero_coeff=False):
    """
    功能: 生成多項式項的隨機係數和指數。
    回傳: (coeff, exp)
    """
    coeff = 0
    while coeff == 0 and not allow_zero_coeff: # 確保係數不為零，除非明確允許
        coeff = random.randint(min_coeff, max_coeff)
    
    # 指數範圍 [min_exp, max_exp]
    exp = random.randint(min_exp, max_exp)
    return coeff, exp

def _format_polynomial_latex(terms, is_derivative=False):
    """
    功能: 將 (係數, 指數) 列表轉換為 LaTeX 格式的多項式字串。
    範例: [(3, 2), (-1, 1), (5, 0)] -> "3x^2 - x + 5"
    參數:
        terms (list): 包含 (係數, 指數) 元組的列表。
        is_derivative (bool): 若為 True，則在格式化時忽略常數項 (exp=0)。
    回傳: LaTeX 字串。
    """
    if not terms:
        return r"0"

    parts = []
    # 按照指數降序排序，並過濾掉係數為 0 的項
    terms_filtered = sorted([t for t in terms if t[0] != 0], key=lambda x: x[1], reverse=True)

    for i, (coeff, exp) in enumerate(terms_filtered):
        if is_derivative and exp == 0: # 導函數的常數項為 0，因此省略
            continue

        coeff_str = ""
        term_str = ""

        # 處理係數為 1 或 -1 的情況，以及常數項
        # 例如：x 而不是 1x, -x 而不是 -1x
        if abs(coeff) != 1 or exp == 0:
            coeff_str = str(abs(coeff))
        
        if exp == 0: # 常數項
            term_str = coeff_str
        elif exp == 1: # x 的一次方項
            term_str = coeff_str + r"x"
        else: # x 的 n 次方項 (n > 1)
            term_str = coeff_str + r"x^{" + str(exp) + r"}"

        # 處理正負號和連接符號
        if coeff < 0:
            parts.append(r"- " + term_str)
        else:
            if parts: # 如果不是第一個項，則添加 "+"
                parts.append(r"+ " + term_str)
            else: # 第一個項直接添加
                parts.append(term_str)

    if not parts:
        return r"0" # 如果所有項都為 0，則返回 "0"
    
    # 嚴格使用字串拼接方式建構 LaTeX 字串，禁止 f-string
    return r"".join(parts)

def _integrate_polynomial_terms(terms):
    """
    功能: 對 (係數, 指數) 列表進行反導函數運算。
    回傳: 新的 (新係數, 新指數) 列表，分數係數以字串 "numerator/denominator" 表示。
    """
    integrated_terms = []
    for coeff_val, exp in terms:
        # 如果係數已經是分數字串，先轉換為浮點數或分數元組
        if isinstance(coeff_val, str) and '/' in coeff_val:
            current_num, current_den = map(int, coeff_val.split('/'))
        elif isinstance(coeff_val, float):
            # 將浮點數轉換為分數 (例如 2.5 -> 5/2)
            s = str(coeff_val)
            if '.' in s:
                decimal_places = len(s.split('.')[1])
                current_den = 10 ** decimal_places
                current_num = int(coeff_val * current_den)
                common_divisor = math.gcd(current_num, current_den)
                current_num //= common_divisor
                current_den //= common_divisor
            else: # 浮點數形式的整數
                current_num = int(coeff_val)
                current_den = 1
        else: # 整數係數
            current_num = int(coeff_val)
            current_den = 1
        
        # K12 多項式反導函數通常不涉及 log 項 (即 exp != -1)
        # 根據 _generate_polynomial_term_params 的 exp_range 和常數項處理，exp 始終 >= 0
        new_exp = exp + 1
        
        # 新係數為 (current_num / current_den) / new_exp
        # 等價於 current_num / (current_den * new_exp)
        final_num = current_num
        final_den = current_den * new_exp
        
        # 簡化分數
        common_divisor = math.gcd(final_num, final_den)
        final_num //= common_divisor
        final_den //= common_divisor

        # 確保分母為正，符號放在分子
        if final_den < 0:
            final_num *= -1
            final_den *= -1

        if final_den == 1: # 如果分母為 1，則為整數係數
            integrated_terms.append((final_num, new_exp))
        else: # 否則為分數係數
            integrated_terms.append((f"{final_num}/{final_den}", new_exp))
    return integrated_terms

def _evaluate_integrated_polynomial(integrated_terms, x_val, C_val):
    """
    功能: 評估給定 x_val 和積分常數 C_val 的反導函數值。
    參數:
        integrated_terms (list): 包含 (係數_字串或浮點數或整數, 指數) 元組的列表。
        x_val (float/int): x 的值。
        C_val (float/int): 積分常數 C 的值。
    回傳: 浮點數值。
    """
    result = 0.0
    for coeff_str_or_num, exp in integrated_terms:
        coeff = 0.0
        if isinstance(coeff_str_or_num, str) and '/' in coeff_str_or_num:
            num, den = map(int, coeff_str_or_num.split('/'))
            coeff = num / den
        else: # 它是整數或浮點數
            coeff = float(coeff_str_or_num)
        
        result += coeff * (x_val ** exp)
    
    result += C_val
    return result

# --- Main Functions ---

def generate(level=1):
    problem_type = random.choice([1, 2, 3, 4]) # 隨機選擇題型
    
    question_text = ""
    correct_answer = ""
    image_base64 = None # 本技能不涉及圖片

    # 係數和指數的通用範圍
    coeff_range = (-5, 5) # f(x) 的係數範圍
    exp_range = (1, 4) # f(x) 項的指數範圍，確保是正整數指數

    if problem_type == 1:
        # Type 1 (Maps to Example 1: 基本反導函數與定點求值)
        # 給定一個單項多項式函數 f(x)，要求找出其滿足特定初始條件 F(x0)=y0 的反導函數 F(x)，
        # 並計算在另一個點 k 的函數值 F(k)。
        
        coeff, exp = _generate_polynomial_term_params(*coeff_range, *exp_range, allow_zero_coeff=False) # 係數不能為零
        f_terms = [(coeff, exp)]
        f_x_latex = _format_polynomial_latex(f_terms)

        integrated_terms_no_C = _integrate_polynomial_terms(f_terms)

        # 初始條件 (x0, y0)
        x0 = random.randint(-3, 3)
        y0 = random.randint(-10, 10)
        
        # 計算積分常數 C
        C_val = y0 - _evaluate_integrated_polynomial(integrated_terms_no_C, x0, 0)

        # 評估點 k
        k_val = random.randint(-3, 3)
        while k_val == x0: # 確保 k_val 與 x0 不同
            k_val = random.randint(-3, 3)
        
        final_answer = _evaluate_integrated_polynomial(integrated_terms_no_C, k_val, C_val)
        
        # 遵循排版與 LaTeX 安全規範
        question_text_template = r"已知函數 $f(x) = {f_x}$，且 $F(x)$ 是 $f(x)$ 的一個反導函數。若 $F({x0}) = {y0}$，則 $F({k_val})$ 的值為何？"
        question_text = question_text_template.replace("{f_x}", f_x_latex).replace("{x0}", str(x0)).replace("{y0}", str(y0)).replace("{k_val}", str(k_val))
        correct_answer = str(round(final_answer, 4)) # 遵循答案數據純淨化規範

    elif problem_type == 2:
        # Type 2 (Maps to Example 2: 多項式反導函數與定點求值)
        # 給定一個多項式函數 f(x) 包含多個項，要求找出其滿足特定初始條件 F(x0)=y0 的反導函數 F(x)，
        # 並計算在另一個點 k 的函數值 F(k)。

        num_terms = random.randint(2, 3) # 隨機生成 2 或 3 項
        f_terms = []
        for _ in range(num_terms):
            coeff, exp = _generate_polynomial_term_params(*coeff_range, *exp_range, allow_zero_coeff=False)
            f_terms.append((coeff, exp))
        
        # 添加一個常數項 (exp=0)
        constant_coeff = random.randint(coeff_range[0], coeff_range[1])
        if constant_coeff != 0:
            f_terms.append((constant_coeff, 0))

        f_x_latex = _format_polynomial_latex(f_terms)
        integrated_terms_no_C = _integrate_polynomial_terms(f_terms)

        # 初始條件 (x0, y0)
        x0 = random.randint(-3, 3)
        y0 = random.randint(-10, 10)
        
        # 計算積分常數 C
        C_val = y0 - _evaluate_integrated_polynomial(integrated_terms_no_C, x0, 0)

        # 評估點 k
        k_val = random.randint(-3, 3)
        while k_val == x0:
            k_val = random.randint(-3, 3)
        
        final_answer = _evaluate_integrated_polynomial(integrated_terms_no_C, k_val, C_val)
        
        question_text_template = r"已知函數 $f(x) = {f_x}$，且 $F(x)$ 是 $f(x)$ 的一個反導函數。若 $F({x0}) = {y0}$，則 $F({k_val})$ 的值為何？"
        question_text = question_text_template.replace("{f_x}", f_x_latex).replace("{x0}", str(x0)).replace("{y0}", str(y0)).replace("{k_val}", str(k_val))
        correct_answer = str(round(final_answer, 4))

    elif problem_type == 3:
        # Type 3 (Maps to Example 3: 反導函數與積分常數求解)
        # 給定一個多項式函數 f(x)，要求找出其滿足特定初始條件 F(x0)=y0 的反導函數 F(x)，
        # 並明確計算積分常數 C 的值。

        num_terms = random.randint(1, 2) # 隨機生成 1 或 2 項
        f_terms = []
        for _ in range(num_terms):
            coeff, exp = _generate_polynomial_term_params(*coeff_range, *exp_range, allow_zero_coeff=False)
            f_terms.append((coeff, exp))
        
        # 添加一個常數項
        constant_coeff = random.randint(coeff_range[0], coeff_range[1])
        if constant_coeff != 0:
            f_terms.append((constant_coeff, 0))

        f_x_latex = _format_polynomial_latex(f_terms)
        integrated_terms_no_C = _integrate_polynomial_terms(f_terms)

        # 初始條件 (x0, y0)
        x0 = random.randint(-3, 3)
        y0 = random.randint(-10, 10)
        
        # 計算積分常數 C 的值
        C_val = y0 - _evaluate_integrated_polynomial(integrated_terms_no_C, x0, 0)
        
        question_text_template = r"已知函數 $f(x) = {f_x}$，且 $F(x)$ 是 $f(x)$ 的一個反導函數。若 $F({x0}) = {y0}$，則 $F(x)$ 中的積分常數 $C$ 為何？"
        question_text = question_text_template.replace("{f_x}", f_x_latex).replace("{x0}", str(x0)).replace("{y0}", str(y0))
        correct_answer = str(round(C_val, 4))

    elif problem_type == 4:
        # Type 4 (Maps to Example 4: 二階反導函數與定點求值)
        # 給定二階導函數 f""(x)，以及一階導函數 f'(x) 和原函數 f(x) 各自的初始條件，
        # 要求找出原函數 f(x)，並計算在特定點 k 的函數值 f(k)。

        # 生成 f""(x) = ax + b (指數為 1 和 0 的項)
        coeff_f_double_prime_x, _ = _generate_polynomial_term_params(*coeff_range, 1, 1, allow_zero_coeff=False) # x 項
        coeff_f_double_prime_const, _ = _generate_polynomial_term_params(*coeff_range, 0, 0, allow_zero_coeff=True) # 常數項
        
        f_double_prime_terms = [(coeff_f_double_prime_x, 1)]
        if coeff_f_double_prime_const != 0:
            f_double_prime_terms.append((coeff_f_double_prime_const, 0))
        
        f_double_prime_latex = _format_polynomial_latex(f_double_prime_terms)
        
        # 第一次積分得到 f'(x) = A x^2 + B x + C1
        f_prime_terms_no_c1 = _integrate_polynomial_terms(f_double_prime_terms)

        # f'(x) 的初始條件
        x0_prime = random.randint(-2, 2)
        y0_prime = random.randint(-5, 5)
        
        # 計算 C1
        C1_val = y0_prime - _evaluate_integrated_polynomial(f_prime_terms_no_c1, x0_prime, 0)
        
        # 將 C1 作為常數項添加到 f'(x) 的項中，準備第二次積分
        f_prime_terms_with_c1 = f_prime_terms_no_c1 + [(C1_val, 0)]
        
        # 第二次積分得到 f(x) = D x^3 + E x^2 + F x + G + C2
        f_terms_no_c2 = _integrate_polynomial_terms(f_prime_terms_with_c1)

        # f(x) 的初始條件
        x0_func = random.randint(-2, 2)
        y0_func = random.randint(-5, 5)
        
        # 計算 C2
        C2_val = y0_func - _evaluate_integrated_polynomial(f_terms_no_c2, x0_func, 0)

        # 評估點 k
        k_val = random.randint(-2, 2)
        # 確保 k_val 與初始條件的 x 值不同
        invalid_k_values = {x0_prime, x0_func}
        while k_val in invalid_k_values:
            k_val = random.randint(-2, 2)
        
        final_answer = _evaluate_integrated_polynomial(f_terms_no_c2, k_val, C2_val)

        question_text_template = (
            r"已知函數 $f""(x) = {f_double_prime_x}$，且 $f'({x0_prime}) = {y0_prime}$ 及 $f({x0_func}) = {y0_func}$。"
            r"則 $f({k_val})$ 的值為何？"
        )
        question_text = question_text_template.replace("{f_double_prime_x}", f_double_prime_latex) \
                                             .replace("{x0_prime}", str(x0_prime)) \
                                             .replace("{y0_prime}", str(y0_prime)) \
                                             .replace("{x0_func}", str(x0_func)) \
                                             .replace("{y0_func}", str(y0_func)) \
                                             .replace("{k_val}", str(k_val))
        correct_answer = str(round(final_answer, 4))
        
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "answer": correct_answer, # [Fix] 由 "" 改為 correct_answer，確保前端能顯示答案
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1" # 初始版本
    }

# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
