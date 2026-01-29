# ==============================================================================
# ID: gh_DefiniteIntegral
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 84.15s | RAG: 2 examples
# Created At: 2026-01-29 13:11:52
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

from datetime import datetime

from fractions import Fraction
import re

# Helper function for integral calculation (Type 1 and Type 2)
def _calculate_integral_value(func_coeffs, exponents, const_term, a, b):
    """
    Calculates the definite integral F(b) - F(a) for a polynomial-like function.
    func_coeffs: list of coefficients [A, B]
    exponents: list of exponents [n, m] (can be negative for Type 2)
    const_term: C for Type 1, 0 for Type 2
    a, b: lower and upper limits
    """
    
    # Define antiderivative function F(x)
    def F(x_val):
        result = Fraction(0)
        # Handle terms like Ax^n
        for i in range(len(func_coeffs)):
            coeff = func_coeffs[i]
            exp = exponents[i]
            # Type 2 explicitly states n != 1, so exp is never -1 for the A/x^n term.
            # For Type 1, exponents are positive integers, so exp+1 is never 0.
            # Thus, division by zero (exp+1=0) is avoided.
            result += Fraction(coeff, exp + 1) * (Fraction(x_val)**(exp + 1))
        
        # Add constant term integral (Cx)
        result += Fraction(const_term) * Fraction(x_val)
        return result

    return F(b) - F(a)

def generate(level=1):
    problem_type = random.choice([1, 2, 3]) # Use 3 to represent Type 3a/3b
    
    question_text = ""
    correct_answer = ""
    
    if problem_type == 1:
        # Type 1 (Maps to RAG Example: 基本多項式定積分計算)
        A = random.randint(-4, 4)
        while A == 0:
            A = random.randint(-4, 4)
        B = random.randint(-4, 4)
        while B == 0:
            B = random.randint(-4, 4)
        
        n, m = random.sample(range(1, 5), 2)
        C = random.randint(-5, 5)
        
        a = random.randint(-2, 1)
        b = random.randint(a + 1, 4)
        
        # Format the integrand expression strictly without f-strings for LaTeX parts
        integrand_parts = []
        
        # Term Ax^n
        if A != 0:
            term_str = ""
            if A == 1:
                term_str += ""
            elif A == -1:
                term_str += "-"
            else:
                term_str += str(A)
            
            if n == 1:
                term_str += "x"
            else:
                term_str += r"x^{" + str(n) + r"}"
            integrand_parts.append(term_str)

        # Term Bx^m
        if B != 0:
            term_str = ""
            if B > 0:
                if integrand_parts: term_str += "+"
                if B == 1: term_str += ""
                else: term_str += str(B)
            else: # B < 0
                if B == -1: term_str += "-"
                else: term_str += str(B)
            
            if m == 1:
                term_str += "x"
            else:
                term_str += r"x^{" + str(m) + r"}"
            integrand_parts.append(term_str)

        # Constant term C
        if C != 0:
            term_str = ""
            if C > 0:
                if integrand_parts: term_str += "+"
                term_str += str(C)
            else: # C < 0
                term_str += str(C)
            integrand_parts.append(term_str)

        if not integrand_parts:
            integrand_expr = "0"
        else:
            integrand_expr = "".join(integrand_parts)
        
        # Calculate correct answer
        func_coeffs = [A, B]
        exponents = [n, m]
        const_term = C
        
        result_fraction = _calculate_integral_value(func_coeffs, exponents, const_term, a, b)
        correct_answer = str(result_fraction)
        
        # Construct question text using .replace()
        question_template = r"計算 $\int_{a}^{b} ({integrand}) dx$。"
        question_text = question_template.replace("{a}", str(a)).replace("{b}", str(b))
        question_text = question_text.replace("{integrand}", integrand_expr)

    elif problem_type == 2:
        # Type 2 (Maps to RAG Example: 含負指數或分母形式的定積分)
        A = random.randint(-3, 3)
        while A == 0:
            A = random.randint(-3, 3)
        B = random.randint(-3, 3)
        while B == 0:
            B = random.randint(-3, 3)
        
        n = random.randint(2, 4) # Denominator exponent, n != 1 (avoids ln|x|)
        m = random.randint(1, 3) # Positive exponent
        
        a = random.randint(1, 2) # Ensures interval doesn't include 0
        b = random.randint(a + 1, 4)
        
        # Format the integrand expression strictly without f-strings for LaTeX parts
        integrand_parts = []
        
        # Term A/x^n (Ax^-n)
        if A != 0:
            term_str = r"\frac{" + str(A) + r"}{x^{" + str(n) + r"}}"
            integrand_parts.append(term_str)
        
        # Term Bx^m
        if B != 0:
            term_str = ""
            if B > 0:
                if integrand_parts: term_str += "+"
                if B == 1: term_str += ""
                else: term_str += str(B)
            else: # B < 0
                if B == -1: term_str += "-"
                else: term_str += str(B)
            
            if m == 1:
                term_str += "x"
            else:
                term_str += r"x^{" + str(m) + r"}"
            integrand_parts.append(term_str)
        
        if not integrand_parts:
            integrand_expr = "0"
        else:
            integrand_expr = "".join(integrand_parts)
            
        # Calculate correct answer
        # Convert A/x^n to Ax^(-n) for calculation
        func_coeffs = [A, B]
        exponents = [-n, m] # Note the negative exponent for the first term
        const_term = 0 # No constant term for Type 2
        
        result_fraction = _calculate_integral_value(func_coeffs, exponents, const_term, a, b)
        correct_answer = str(result_fraction)
        
        # Construct question text using .replace()
        question_template = r"計算 $\int_{a}^{b} ({integrand}) dx$。"
        question_text = question_template.replace("{a}", str(a)).replace("{b}", str(b))
        question_text = question_text.replace("{integrand}", integrand_expr)

    else: # problem_type == 3 (Type 3a or 3b)
        # Type 3 (Maps to RAG Example: 定積分性質應用)
        sub_type = random.choice(['3a', '3b'])
        
        if sub_type == '3a':
            # Type 3a (線性性質)
            P = random.randint(-15, 15)
            Q = random.randint(-15, 15)
            k1 = random.randint(-4, 4)
            while k1 == 0:
                k1 = random.randint(-4, 4)
            k2 = random.randint(-4, 4)
            while k2 == 0:
                k2 = random.randint(-4, 4)
            
            a = random.randint(-3, 0)
            b = random.randint(a + 1, 3)
            
            correct_answer = str(Fraction(k1 * P + k2 * Q))
            
            # Format k1*f(x) + k2*g(x) strictly without f-strings for LaTeX parts
            integrand_parts = []
            
            # k1 f(x) term
            k1_str = ""
            if k1 == 1:
                k1_str = "f(x)"
            elif k1 == -1:
                k1_str = "-f(x)"
            else:
                k1_str = str(k1) + "f(x)"
            integrand_parts.append(k1_str)
            
            # k2 g(x) term
            k2_str = ""
            if k2 > 0:
                k2_str += "+" # Always add + if positive and not the first term
                if k2 == 1:
                    k2_str += "g(x)"
                else:
                    k2_str += str(k2) + "g(x)"
            else: # k2 < 0
                if k2 == -1:
                    k2_str += "-g(x)"
                else:
                    k2_str += str(k2) + "g(x)" # str(k2) will include the negative sign
            
            integrand_parts.append(k2_str)
            integrand_expr = "".join(integrand_parts)

            question_template = r"已知 $\int_{a}^{b} f(x) dx = {P}$ 且 $\int_{a}^{b} g(x) dx = {Q}$，試求 $\int_{a}^{b} ({integrand}) dx$。"
            question_text = question_template.replace("{a}", str(a)).replace("{b}", str(b))
            question_text = question_text.replace("{P}", str(P)).replace("{Q}", str(Q))
            question_text = question_text.replace("{integrand}", integrand_expr)

        else: # sub_type == '3b'
            # Type 3b (區間加成性質)
            P = random.randint(-15, 15)
            Q = random.randint(-15, 15)
            
            limits_raw = random.sample(range(-5, 5), 3)
            limits_raw.sort()
            a, b, c = limits_raw[0], limits_raw[1], limits_raw[2]
            
            correct_answer = str(Fraction(P + Q))
            
            question_template = r"已知 $\int_{a}^{b} f(x) dx = {P}$ 且 $\int_{b}^{c} f(x) dx = {Q}$，試求 $\int_{a}^{c} f(x) dx$。"
            question_text = question_template.replace("{a}", str(a)).replace("{b}", str(b))
            question_text = question_text.replace("{c}", str(c)).replace("{P}", str(P)).replace("{Q}", str(Q))
            
    return {
        "question_text": question_text,
        "correct_answer": correct_answer,
        "image_base64": None,
        "created_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Robust Check Logic (from Architect's Specification, section 6)

    cleaned_user_answer = re.sub(r'[\$\\]|x=|y=|k=|Ans:|[{} ]', '', user_answer)
    cleaned_correct_answer = re.sub(r'[\$\\]|x=|y=|k=|Ans:|[{} ]', '', correct_answer)

    try:
        user_fraction = Fraction(cleaned_user_answer)
        correct_fraction = Fraction(cleaned_correct_answer)
        return user_fraction == correct_fraction
    except ValueError:
        try:
            user_float = float(cleaned_user_answer)
            correct_float = float(cleaned_correct_answer)
            return abs(user_float - correct_float) < 1e-9 # Using a small tolerance
        except ValueError:
            return False


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
