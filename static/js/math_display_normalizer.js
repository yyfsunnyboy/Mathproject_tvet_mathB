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

  // "/" division inside text that is already known to be math (an explicit
  // delimiter span or a choice classified as math).  Each operand follows
  // operator precedence: a number, a letter or \command with its ^/_ script,
  // a (...) / {...} group, or a known function call.  Anything else is left as is.
  const FUNCTION_NAME = /(?:\\?(?:sqrt|sin|cos|tan|cot|sec|csc|log|ln|exp))$/;
  const TEXT_COMMAND = /\\(?:text|mathrm|operatorname|textrm|mbox)\s*\{$/;
  const LETTER = /[A-Za-z\u03b1-\u03c9\u0391-\u03a9]/;

  function matchBack(text, close) {
    const closeChar = text[close];
    const openChar = closeChar === ')' ? '(' : '{';
    let depth = 0;
    for (let k = close; k >= 0; k -= 1) {
      if (text[k] === closeChar) depth += 1;
      else if (text[k] === openChar && --depth === 0) return k;
    }
    return -1;
  }

  function matchForward(text, open) {
    const openChar = text[open];
    const closeChar = openChar === '(' ? ')' : '}';
    let depth = 0;
    for (let k = open; k < text.length; k += 1) {
      if (text[k] === openChar) depth += 1;
      else if (text[k] === closeChar && --depth === 0) return k;
    }
    return -1;
  }

  function atomStart(text, end) {
    let j = end;
    const c = text[j];
    let start = -1;
    if (c === '²' || c === '³') return atomStart(text, j - 1);
    if (c === ')') {
      start = matchBack(text, j);
      if (start < 0) return -1;
      const before = text.slice(0, start);
      if (/\\(?:left|right)$/.test(before)) return -1;
      const name = before.match(FUNCTION_NAME) || (!/\\[A-Za-z]+$/.test(before) && before.match(/[A-Za-z]$/));
      if (name) start -= name[0].length;
    } else if (c === '}') {
      start = matchBack(text, j);
      while (start > 0 && text[start - 1] === '}') start = matchBack(text, start - 1);
      if (start < 0) return -1;
      if (TEXT_COMMAND.test(text.slice(0, start + 1))) return -1;
      const command = text.slice(0, start).match(/\\[A-Za-z]+$/);
      if (command) start -= command[0].length;
    } else if (/[0-9.]/.test(c || '')) {
      start = j;
      while (start > 0 && /[0-9.]/.test(text[start - 1])) start -= 1;
    } else if (LETTER.test(c || '')) {
      const command = text.slice(0, j + 1).match(/\\[A-Za-z]+$/);
      start = command ? j + 1 - command[0].length : j;
    } else {
      return -1;
    }
    if (start > 1 && (text[start - 1] === '^' || text[start - 1] === '_')) {
      const base = atomStart(text, start - 2);
      if (base >= 0) start = base;
    }
    return start;
  }

  function atomEnd(text, begin, allowScript) {
    const c = text[begin];
    let end = -1;
    const fn = text.slice(begin).match(/^\\?(?:sqrt|sin|cos|tan|cot|sec|csc|log|ln|exp)(?=\s*[({])/);
    if (fn) {
      const open = begin + fn[0].length + (text.slice(begin + fn[0].length).match(/^\s*/)[0].length);
      const close = matchForward(text, open);
      return close < 0 ? -1 : close + 1;
    }
    if (c === '(' || c === '{') {
      const close = matchForward(text, begin);
      if (close < 0) return -1;
      end = close + 1;
    } else if (c === '\\') {
      const command = text.slice(begin).match(/^\\[A-Za-z]+/);
      if (!command || command[0] === '\\left' || command[0] === '\\right') return -1;
      end = begin + command[0].length;
      while (text[end] === '{') {
        const close = matchForward(text, end);
        if (close < 0) return -1;
        end = close + 1;
      }
    } else if (/[0-9]/.test(c || '')) {
      end = begin;
      while (end < text.length && /[0-9.]/.test(text[end])) end += 1;
    } else if (LETTER.test(c || '')) {
      end = begin + 1;
    } else {
      return -1;
    }
    while (text[end] === '²' || text[end] === '³') end += 1;
    if (allowScript !== false && (text[end] === '^' || text[end] === '_')) {
      const scriptEnd = atomEnd(text, end + 1, false);
      if (scriptEnd > 0) end = scriptEnd;
    }
    return end;
  }

  function unwrapGroup(operand) {
    const first = operand[0];
    if ((first === '(' || first === '{') && matchForward(operand, 0) === operand.length - 1) {
      return operand.slice(1, -1).trim();
    }
    return operand.trim();
  }

  function slashFractionsToLatex(value) {
    let text = String(value ?? "");
    if (!text.includes('/')) return text;
    let from = 0;
    for (let guard = 0; guard < 64; guard += 1) {
      const slash = text.indexOf('/', from);
      if (slash < 0) break;
      from = slash + 1;
      if (text[slash - 1] === '/' || text[slash + 1] === '/') continue;
      const openText = text.slice(0, slash).match(/\\(?:text|mathrm|operatorname|textrm|mbox)\s*\{[^{}]*$/);
      if (openText) continue;
      let leftEnd = slash - 1;
      while (leftEnd >= 0 && text[leftEnd] === ' ') leftEnd -= 1;
      let rightBegin = slash + 1;
      while (rightBegin < text.length && text[rightBegin] === ' ') rightBegin += 1;
      const leftStart = leftEnd >= 0 ? atomStart(text, leftEnd) : -1;
      const rightEnd = rightBegin < text.length ? atomEnd(text, rightBegin) : -1;
      if (leftStart < 0 || rightEnd < 0) continue;
      const numerator = unwrapGroup(text.slice(leftStart, leftEnd + 1));
      const denominator = unwrapGroup(text.slice(rightBegin, rightEnd));
      if (!numerator || !denominator) continue;
      const latex = `\\frac{${numerator}}{${denominator}}`;
      text = text.slice(0, leftStart) + latex + text.slice(rightEnd);
      from = leftStart;
    }
    return text;
  }

  function normalizeMathText(value, options) {
    const source = String(value ?? "");
    // Only repair ASCII math in explicit delimiters; existing TeX passes through.
    const spans = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$|\$([^$]*?)\$/g;
    if (spans.test(source)) {
      spans.lastIndex = 0;
      return source.replace(spans, (whole, ...parts) => {
        const body = parts.slice(0, 4).find(x => x !== undefined);
        if (!body.includes('\\')) {
          const assignment = body.match(/^([A-Za-z]\s*=\s*)(.+)$/);
          const expression = assignment ? assignment[2] : body;
          const latex = numericLatex(expression.trim());
          if (latex !== null) return whole.replace(body, () => (assignment ? assignment[1] : '') + latex);
        }
        const converted = slashFractionsToLatex(body);
        return converted === body ? whole : whole.replace(body, () => converted);
      });
    }
    // "(1)" / "（2）" are subquestion markers; typesetting them drops the parentheses.
    if (/^[\(（]\s*\d{1,2}\s*[\)）]$/.test(source.trim())) return source;
    if (!/^[+-]?\d+(?:\.\d+)?$/.test(source.trim())) {
      const latex = numericLatex(source.trim());
      if (latex !== null) return `\\(${latex}\\)`;
    }
    if (!source) return source;
    const alreadyDelimited = /(?:\\\(|\\\[|\$\$|\$)/.test(source);
    const wrap = (latex) => alreadyDelimited ? latex : `\\(${latex}\\)`;
    // Bare TeX commands (vectors, fractions, roots) need delimiters for MathJax.
    if (!alreadyDelimited && /\\[a-zA-Z]+/.test(source) && (options?.mathContext === true || !isPlainTextException(source))) {
      return `\\(${options?.mathContext === true ? slashFractionsToLatex(source) : source}\\)`;
    }
    if (/\\(?:d?frac|tfrac)\s*\{/.test(source)) return source;
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

  return { normalizeMathText, normalizeElement, isPlainTextException, slashFractionsToLatex };
}));
