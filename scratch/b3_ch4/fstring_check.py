import sys
import tokenize

for path in sys.argv[1:]:
    with open(path, "rb") as fh:
        tokens = list(tokenize.tokenize(fh.readline))
    stack = []  # per f-string: brace depth
    for tok in tokens:
        name = tokenize.tok_name[tok.type]
        if name == "FSTRING_START":
            stack.append(0)
            continue
        if name == "FSTRING_END":
            stack.pop()
            continue
        if not stack:
            continue
        if tok.type == tokenize.OP and tok.string == "{":
            stack[-1] += 1
            continue
        if tok.type == tokenize.OP and tok.string == "}":
            stack[-1] -= 1
            continue
        if any(depth > 0 for depth in stack[:-1]) or stack[-1] > 0:
            if "\\" in tok.string:
                print(f"{path}:{tok.start[0]}: {tok.string[:60]}")
