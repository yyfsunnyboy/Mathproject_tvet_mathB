(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MathDisplayNormalizer = api;
}(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "TEXTAREA", "INPUT", "PRE", "CODE", "MJX-CONTAINER"]);

  function fraction(sign, numerator, denominator, trailingPi) {
    const top = trailingPi ? (String(numerator) === "1" ? "\\pi" : `${numerator}\\pi`) : numerator;
    return `${sign || ""}\\frac{${top}}{${denominator}}`;
  }

  function isPlainTextException(text) {
    return /(?:https?:\/\/|file:\/\/|[A-Za-z]:\\|(?:日期|年月日|路徑|網址|URL|date|path)\s*[:：]?)/i.test(text);
  }

  // Defensive numeric-only parser shared by choices and explicit math spans.
  // It formats syntax, never executes expressions or interprets prose.
  function numericLatex(source) {
    if (source.length > 512 || !/^[0-9.sqrt()+*/\s-]+$/.test(source)) return null;
    const tokens = source.match(/sqrt|\d+(?:\.\d+)?|[()+*/-]/g) || [];
    if (tokens.length > 128 || tokens.join('') !== source.replace(/\s/g, '')) return null;
    let i = 0;
    const group = (v, p) => v.p < p ? `\\left(${v.text}\\right)` : v.text;
    function atom() {
      const token = tokens[i++];
      if (token === '+' || token === '-') {
        return { text: token + group(atom(), 3), p: 3 };
      }
      if (token === '(' || token === 'sqrt') {
        if (token === 'sqrt' && tokens[i++] !== '(') throw Error('sqrt argument');
        const value = expr(0);
        if (tokens[i++] !== ')') throw Error('parenthesis');
        return token === 'sqrt' ? { text: `\\sqrt{${value.text}}`, p: 4 } : value;
      }
      if (!token || !/^\d+(?:\.\d+)?$/.test(token)) throw Error('number');
      return { text: token, p: 4 };
    }
    function expr(min) {
      let left = atom();
      while (i < tokens.length) {
        const op = tokens[i];
        const p = op === '+' || op === '-' ? 1 : op === '*' || op === '/' ? 2 : 0;
        if (!p || p <= min) break;
        i++;
        const right = expr(p);
        if (op === '/') left = { text: `\\frac{${left.text}}{${right.text}}`, p: 4 };
        else {
          const rhs = group(right, p + 1);
          const sign = op === '*' ? (/^\\(?:sqrt|left\()/.test(rhs) ? '' : ' \\times ') : ` ${op} `;
          left = { text: group(left, p) + sign + rhs, p };
        }
      }
      return left;
    }
    try {
      const result = expr(0);
      return i === tokens.length ? result.text : null;
    } catch (_) { return null; }
  }

  function normalizeMathText(value, options) {
    const source = String(value ?? "");
    // Only repair ASCII math in explicit delimiters; existing TeX passes through.
    const spans = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$|\$([^$]*?)\$/g;
    if (spans.test(source)) {
      spans.lastIndex = 0;
      return source.replace(spans, (whole, ...parts) => {
        const body = parts.slice(0, 4).find(x => x !== undefined);
        if (body.includes('\\')) return whole;
        const assignment = body.match(/^([A-Za-z]\s*=\s*)(.+)$/);
        const expression = assignment ? assignment[2] : body;
        const latex = numericLatex(expression.trim());
        return latex === null ? whole : whole.replace(body, (assignment ? assignment[1] : '') + latex);
      });
    }
    if (!/^[+-]?\d+(?:\.\d+)?$/.test(source.trim())) {
      const latex = numericLatex(source.trim());
      if (latex !== null) return `\\(${latex}\\)`;
    }
    if (!source || /\\(?:d?frac|tfrac)\s*\{/.test(source)) return source;
    const alreadyDelimited = /(?:\\\(|\\\[|\$\$|\$)/.test(source);
    const wrap = (latex) => alreadyDelimited ? latex : `\\(${latex}\\)`;
    let text = source;

    text = text.replace(/\b(sin|cos|tan)\s*\(\s*(-?)(\d*)\s*\*?\s*(?:π|\\pi|pi)\s*\/\s*(\d+)\s*\)/gi,
      (_, fn, sign, coefficient, denominator) => wrap(`\\${fn.toLowerCase()}\\left(${fraction(sign, coefficient || "1", denominator, true)}\\right)`));
    text = text.replace(/(-?)\s*\(\s*(\d+)\s*\/\s*(\d+)\s*\)\s*(π|\\pi)/g,
      (_, sign, numerator, denominator) => wrap(`${sign || ""}\\frac{${numerator}}{${denominator}}\\pi`));
    text = text.replace(/(-?)(\d*)\s*\*?\s*(?:π|\\pi|pi)\s*\/\s*(\d+)/gi,
      (_, sign, coefficient, denominator) => wrap(fraction(sign, coefficient || "1", denominator, true)));
    text = text.replace(/-\s*\(\s*(\d+)\s*\/\s*(\d+)\s*\)/g,
      (_, numerator, denominator) => wrap(fraction("-", numerator, denominator, false)));

    if (!isPlainTextException(source) || options?.mathContext === true) {
      text = text.replace(/(^|[^\w\\/])(-?)(\d+)\s*\/\s*(\d+)(?![\w/])/g,
        (_, prefix, sign, numerator, denominator) => `${prefix}${wrap(fraction(sign, numerator, denominator, false))}`);
    }
    return text;
  }

  function normalizeElement(rootElement, options) {
    if (!rootElement || typeof document === "undefined" || !document.createTreeWalker) return rootElement;
    const walker = document.createTreeWalker(rootElement, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const parent = node.parentElement;
      if (!parent || SKIP_TAGS.has(parent.tagName) || parent.closest("mjx-container")) return;
      const normalized = normalizeMathText(node.nodeValue, options);
      if (normalized !== node.nodeValue) node.nodeValue = normalized;
    });
    return rootElement;
  }

  return { normalizeMathText, normalizeElement, isPlainTextException };
}));
