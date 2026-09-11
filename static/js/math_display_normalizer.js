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

  function normalizeMathText(value, options) {
    const source = String(value ?? "");
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
