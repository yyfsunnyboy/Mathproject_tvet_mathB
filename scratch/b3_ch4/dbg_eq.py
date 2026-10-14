from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer as eq

pairs = [
    ("$c>a>b$", "$b>a>c$"),
    ("$c>a>b$", "$a>c>b$"),
    ("$c>a>b$", "$c>b>a$"),
    ("$c\\gt a\\gt b$", "$b\\gt a\\gt c$"),
    ("$c\\gt a\\gt b$", "$c\\gt b\\gt a$"),
    ("$c>a>b$", "$c>a>b$"),
    ("$c > a > b$", "$c>a>b$"),
]
for a, b in pairs:
    print(repr(a), repr(b), eq(a, b))
