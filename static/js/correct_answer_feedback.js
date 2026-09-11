(function (global) {
  "use strict";

  function appendText(parent, tag, text, className) {
    if (text === undefined || text === null || text === "") return null;
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = String(text);
    parent.appendChild(node);
    return node;
  }

  async function typeset(node) {
    if (!global.MathJax) return;
    if (typeof global.MathJax.typesetPromise === "function") {
      await global.MathJax.typesetPromise([node]);
    } else if (typeof global.MathJax.typeset === "function") {
      global.MathJax.typeset([node]);
    }
  }

  function mathText(value) {
    const text = String(value ?? "");
    if (global.MathDisplayNormalizer) {
      return global.MathDisplayNormalizer.normalizeMathText(text, { mathContext: true });
    }
    const alreadyDelimited = /(?:\\\(|\\\[|\$\$|\$)/.test(text);
    return !alreadyDelimited && /\\(?:frac|dfrac|tfrac|sqrt|pi|theta|sin|cos|tan|overline|vec)\b/.test(text)
      ? `\\(${text}\\)`
      : text;
  }

  function appendDisplay(root, display) {
    if (!display || typeof display !== "object") return false;
    appendText(root, "div", "正確答案：", "correct-answer-title");
    if (display.answer_type === "single_choice") {
      appendText(root, "div", `${display.label || "正確選項"}：${mathText(display.option_text || "")}`, "correct-answer-value");
    } else if (Array.isArray(display.items)) {
      const list = document.createElement("dl");
      list.className = "correct-answer-items";
      display.items.forEach((item) => {
        appendText(list, "dt", item.label || item.key || "", "correct-answer-item-label");
        appendText(list, "dd", mathText(item.value), "correct-answer-item-value");
      });
      root.appendChild(list);
    } else if (display.answer_type === "drawing") {
      [["參考", display.reference], ["評分準則", display.rubric]].forEach(([label, value]) => {
        if (!value) return;
        if (typeof value !== "object") {
          appendText(root, "div", `${label}：${value}`, "correct-answer-reference");
          return;
        }
        const list = document.createElement("dl");
        Object.entries(value).forEach(([key, item]) => {
          appendText(list, "dt", key, "correct-answer-item-label");
          appendText(list, "dd", Array.isArray(item) ? item.join("、") : item, "correct-answer-item-value");
        });
        root.appendChild(list);
      });
    } else {
      appendText(root, "div", mathText(display.value), "correct-answer-value");
    }
    return true;
  }

  async function render(target, data, message) {
    if (!target) return;
    target.textContent = "";
    appendText(target, "div", message || data?.message || data?.result || (data?.correct ? "正確！" : "錯誤"), "grading-message");
    if (data?.required_form_feedback) {
      appendText(target, "div", data.required_form_feedback, "required-form-feedback");
      if (data.required_form_hint) appendText(target, "div", `格式要求：${data.required_form_hint}`, "required-form-hint");
      if (data.correct_answer_display) appendText(target, "div", "正確答案格式：", "correct-answer-format-title");
    }
    appendDisplay(target, data?.correct_answer_display);
    await typeset(target);
  }

  global.CorrectAnswerFeedback = { render, appendDisplay, typeset };
})(window);
