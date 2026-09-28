# -*- coding: utf-8 -*-
"""Minimal TeX -> sympy reader used to re-derive B3 Chapter 4 answers.

Independent of the domain builders: it only reads the student-facing TeX.
Supports numbers, decimals, mixed numbers, letters, ``\\frac``/``\\dfrac``,
``\\sqrt[n]{}``, ``\\log_{b}`` (bare ``\\log`` is base 10), ``^``, ``\\times``,
parentheses/brackets/braces, unary minus, and implicit multiplication.
"""
from __future__ import annotations

import re

import sympy as sp

_MATH_RE = re.compile(r"\\\((.+?)\\\)", re.S)


def math_segments(text: str) -> list[str]:
    return [seg.strip() for seg in _MATH_RE.findall(text or "")]


def _tokenize(tex: str) -> list[str]:
    tex = tex.replace(r"\left", "").replace(r"\right", "").replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
    tex = tex.replace(r"\,", " ").replace(r"\;", " ").replace(r"\!", "")
    tokens: list[str] = []
    i = 0
    while i < len(tex):
        ch = tex[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "\\":
            j = i + 1
            while j < len(tex) and tex[j].isalpha():
                j += 1
            tokens.append(tex[i:j])
            i = j
            continue
        if ch.isdigit() or (ch == "." and i + 1 < len(tex) and tex[i + 1].isdigit()):
            j = i
            while j < len(tex) and (tex[j].isdigit() or tex[j] == "."):
                j += 1
            tokens.append(tex[i:j])
            i = j
            continue
        tokens.append(ch)
        i += 1
    return tokens


class _Parser:
    def __init__(self, tokens: list[str], symbols: dict[str, sp.Symbol]):
        self.t = tokens
        self.i = 0
        self.symbols = symbols

    def peek(self) -> str | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, expected: str | None = None) -> str:
        tok = self.peek()
        if tok is None or (expected is not None and tok != expected):
            raise ValueError(f"tex_parse:{expected}:{tok}:{self.i}")
        self.i += 1
        return tok

    def expr(self) -> sp.Expr:
        node = self.term()
        while self.peek() in {"+", "-"}:
            op = self.take()
            rhs = self.term()
            node = node + rhs if op == "+" else node - rhs
        return node

    def _starts_atom(self, tok: str | None) -> bool:
        if tok is None:
            return False
        return (
            tok[0].isdigit() or tok[0] == "." or tok.isalpha() or tok in {"(", "[", "{"}
            or tok in {r"\frac", r"\sqrt", r"\log", r"\pi"}
        )

    def term(self) -> sp.Expr:
        node = self.unary()
        while True:
            tok = self.peek()
            if tok in {r"\times", r"\cdot", "*"}:
                self.take()
                node = node * self.unary()
            elif tok in {"/", r"\div"}:
                self.take()
                node = node / self.unary()
            elif self._starts_atom(tok):
                node = node * self.unary()
            else:
                return node

    def unary(self) -> sp.Expr:
        if self.peek() == "-":
            self.take()
            return -self.unary()
        if self.peek() == "+":
            self.take()
            return self.unary()
        return self.power()

    def power(self) -> sp.Expr:
        base = self.atom()
        if self.peek() == "^":
            self.take()
            exponent = self.group() if self.peek() == "{" else self.atom()
            return sp.Pow(base, exponent, evaluate=True)
        return base

    def group(self) -> sp.Expr:
        self.take("{")
        node = self.expr()
        self.take("}")
        return node

    def atom(self) -> sp.Expr:
        tok = self.peek()
        if tok is None:
            raise ValueError("tex_parse:eof")
        if tok[0].isdigit() or tok[0] == ".":
            self.take()
            value = sp.Rational(tok)
            if self.peek() == r"\frac":
                return value + self.atom()
            return value
        if tok == r"\frac":
            self.take()
            num = self.group()
            den = self.group()
            return num / den
        if tok == r"\sqrt":
            self.take()
            index = sp.Integer(2)
            if self.peek() == "[":
                self.take("[")
                index = self.expr()
                self.take("]")
            radicand = self.group()
            return sp.root(radicand, index)
        if tok == r"\log":
            self.take()
            base = sp.Integer(10)
            if self.peek() == "_":
                self.take()
                base = self.group() if self.peek() == "{" else self.atom()
            arg = self.power()
            return sp.log(arg) / sp.log(base)
        if tok == r"\pi":
            self.take()
            return sp.pi
        if tok in {"(", "[", "{"}:
            close = {"(": ")", "[": "]", "{": "}"}[tok]
            self.take()
            node = self.expr()
            self.take(close)
            return node
        if tok.isalpha() and len(tok) == 1:
            self.take()
            return self.symbols.setdefault(tok, sp.Symbol(tok))
        raise ValueError(f"tex_parse:unexpected:{tok}")


def tex_to_sympy(tex: str, symbols: dict[str, sp.Symbol] | None = None) -> sp.Expr:
    parser = _Parser(_tokenize(tex), symbols if symbols is not None else {})
    node = parser.expr()
    if parser.peek() is not None:
        raise ValueError(f"tex_parse:trailing:{parser.t[parser.i:]}")
    return node


def split_equation(tex: str) -> tuple[str, str]:
    left, right = tex.split("=", 1)
    return left, right


def numeric(expr: sp.Expr, subs: dict | None = None) -> complex:
    value = sp.N(expr.subs(subs or {}), 40)
    return complex(value)


def log_arguments_positive(expr: sp.Expr, subs: dict) -> bool:
    for node in expr.atoms(sp.log):
        value = complex(sp.N(node.args[0].subs(subs), 40))
        if abs(value.imag) > 1e-12 or value.real <= 0:
            return False
    return True
