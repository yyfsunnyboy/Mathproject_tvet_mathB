/**
 * Shared multipart answer controls.
 * The practice page and the live-presentation DOM gate both call this module,
 * so a field count is the number of real input/select controls, not payload parts.
 */
(function (root, factory) {
    const api = factory();
    if (typeof module === "object" && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.MultipartFieldRenderer = api;
    }
}(typeof globalThis !== "undefined" ? globalThis : this, function () {
    "use strict";

    function resolveFields(payload) {
        const cq = payload || {};
        const contract = cq.answer_contract || {};
        const parts = Array.isArray(contract.parts) ? contract.parts : [];
        const fromParts = parts
            .filter((part) => part && (part.key || part.field_key))
            .map((part, index) => ({
                key: String(part.key || part.field_key),
                field_key: String(part.key || part.field_key),
                label: String(part.display_label || part.label || part.prompt || part.key || part.field_key || `欄位 ${index + 1}`),
                prompt: String(part.display_label || part.label || part.prompt || part.key || part.field_key || `欄位 ${index + 1}`),
                group_label: String(part.group_label || ""),
                input_type: String(part.input_type || "text"),
                choices: Array.isArray(part.choices) ? part.choices : [],
                checker: String(part.checker || part.checker_key || ""),
                expected_answer: part.expected_answer == null ? "" : String(part.expected_answer),
                answer_order: part.answer_order ?? index,
            }));
        if (fromParts.length > 0) return fromParts;
        const subqs = Array.isArray(cq.subquestions) ? cq.subquestions : [];
        return subqs
            .filter((sq) => sq && (sq.field_key || sq.key || sq.part))
            .map((sq, index) => ({
                key: String(sq.field_key || sq.key || sq.part || `part_${index + 1}`),
                field_key: String(sq.field_key || sq.key || sq.part || `part_${index + 1}`),
                label: String(sq.prompt || sq.label || sq.part || `欄位 ${index + 1}`),
                prompt: String(sq.prompt || sq.label || sq.part || `欄位 ${index + 1}`),
                answer_order: sq.answer_order ?? index,
                input_type: "text",
                choices: [],
                checker: String(sq.checker || ""),
                expected_answer: sq.expected_answer == null ? "" : String(sq.expected_answer),
                group_label: "",
            }));
    }

    function buildGroups(payload, subqs) {
        const ui = (payload && payload.ui_contract)
            || ((payload && payload.answer_contract && payload.answer_contract.ui_contract) || {});
        const normalizeGroupMarker = (raw) => {
            const text = String(raw || "").trim();
            if (!text) return "";
            if (/^[\(（]\s*\d+\s*[\)）]$/.test(text)) {
                return `(${text.replace(/[^\d]/g, "")})`;
            }
            if (/^\d+$/.test(text)) return `(${text})`;
            return text;
        };
        if (Array.isArray(ui.field_groups) && ui.field_groups.length > 0) {
            return ui.field_groups.map((group) => {
                const fields = (group.fields || [])
                    .map((fieldKey) => subqs.find((sq) => String(sq.field_key || sq.key || "") === String(fieldKey)))
                    .filter(Boolean);
                return {
                    label: normalizeGroupMarker(group.group_label || group.label || ""),
                    fields,
                };
            }).filter((group) => group.fields.length > 0);
        }
        const byPart = new Map();
        subqs.forEach((sq) => {
            const partKey = normalizeGroupMarker(String(sq.group_label || sq.part || "").trim());
            if (!partKey) {
                if (!byPart.has("")) byPart.set("", []);
                byPart.get("").push(sq);
                return;
            }
            if (!byPart.has(partKey)) byPart.set(partKey, []);
            byPart.get(partKey).push(sq);
        });
        const named = Array.from(byPart.entries()).filter(([label]) => label);
        if (named.length > 1 || (named.length === 1 && named[0][1].length > 1)) {
            return named.map(([label, fields]) => ({ label, fields }));
        }
        return [{ label: "", fields: subqs }];
    }

    function figureSlotDisplayLabel(part, fallbackIndex) {
        const key = String((part && (part.key || part.field_key)) || "");
        const fig = key.match(/^fig(\d+)$/i);
        if (fig) {
            const marks = "①②③④⑤⑥⑦⑧⑨⑩";
            const index = Number(fig[1]);
            return marks[index - 1] || `圖${index}`;
        }
        const cmp = key.match(/^cmp(\d+)$/i);
        if (cmp) {
            const marks = "①②③④⑤⑥⑦⑧⑨⑩";
            const index = Number(cmp[1]);
            return `圖${marks[index - 1] || index}`;
        }
        return String((part && (part.label || part.prompt)) || key || `欄位 ${fallbackIndex + 1}`);
    }

    function controlKind(part) {
        const checker = String((part && (part.checker || part.checker_key)) || "").toLowerCase();
        const expected = String((part && part.expected_answer) || "");
        if (checker.includes("inequality") || /[<>≤≥]|\\le|\\ge/.test(expected)) return "inequality";
        if (expected.includes("=") && /[xyk]/i.test(expected)) return "equation";
        if (/sqrt|\\sqrt|√/.test(expected)) return "radical";
        if (expected.includes("/")) return "fraction";
        if (checker.includes("integer") || /^[+-]?\d+$/.test(expected.replace(/\s/g, ""))) return "numeric";
        return "expression";
    }

    function controlKindFromPayload(payload) {
        const contract = (payload && payload.answer_contract) || {};
        const parts = Array.isArray(contract.parts) ? contract.parts : [];
        if (parts.length === 1) return controlKind(parts[0]);
        const semantic = contract.semantic_answer;
        const text = typeof semantic === "string"
            ? semantic
            : String((payload && (payload.display_answer || payload.correct_answer)) || "");
        if (/^[A-D]$/.test(text)) return "expression";
        return controlKind({
            checker: (payload && payload.checker) || contract.checker || "",
            expected_answer: text,
        });
    }

    function applyControlKind(node, kind) {
        if (!node || !node.classList) return;
        ["numeric", "fraction", "expression", "equation", "inequality", "radical"].forEach((name) => {
            node.classList.remove("control-" + name);
        });
        node.classList.add("control-" + (kind || "expression"));
    }

    function createControl(part, index) {
        const fieldKey = String(part.key || part.field_key || `part_${index + 1}`);
        const choices = Array.isArray(part.choices) ? part.choices : [];
        const useSelect = part.input_type === "select" || choices.length > 0
            || /^fig\d+$/i.test(fieldKey) || /^cmp\d+$/i.test(fieldKey);
        let input;
        if (useSelect) {
            input = document.createElement("select");
            const blank = document.createElement("option");
            blank.value = "";
            blank.textContent = "請選擇";
            input.appendChild(blank);
            const options = choices.length
                ? choices
                : (/^cmp\d+$/i.test(fieldKey)
                    ? ["m1>m2", "m1<m2"]
                    : ["m>0", "m=0", "m<0", "m不存在"]);
            options.forEach((item) => {
                const option = document.createElement("option");
                option.value = String(item);
                option.textContent = String(item);
                input.appendChild(option);
            });
        } else {
            input = document.createElement("input");
            input.type = "text";
            input.autocomplete = "off";
        }
        input.id = `multi-part-input-${fieldKey}`;
        input.className = "multi-part-input";
        input.dataset.partIndex = String(index);
        input.dataset.fieldKey = fieldKey;
        input.dataset.answerOrder = String(part.answer_order ?? index);
        applyControlKind(input, controlKind(part));
        return input;
    }

    function appendField(container, part, index) {
        const row = document.createElement("div");
        row.className = "multi-part-row";
        const label = document.createElement("label");
        const fieldKey = String(part.key || part.field_key || `part_${index + 1}`);
        const prompt = figureSlotDisplayLabel(part, index);
        label.textContent = prompt;
        label.setAttribute("for", `multi-part-input-${fieldKey}`);
        row.appendChild(label);
        row.appendChild(createControl(part, index));
        container.appendChild(row);
    }

    function render(container, payload) {
        if (!container) {
            return { fields: [], groups: [] };
        }
        container.innerHTML = "";
        const parts = resolveFields(payload);
        if (!parts.length) {
            return { fields: parts, groups: [] };
        }
        const figParts = parts.filter((part) => /^fig\d+$/i.test(part.key));
        const cmpParts = parts.filter((part) => /^cmp\d+$/i.test(part.key));
        const autoGroups = (figParts.length && cmpParts.length)
            ? [
                { label: "(1) 看下方計算紙圖①～④，選擇斜率", fields: figParts },
                { label: "(2) 看下方計算紙圖①、圖②，比較 m1 與 m2", fields: cmpParts },
            ]
            : null;
        const groups = autoGroups || buildGroups(payload, parts);
        const useGroupedLayout = groups.length > 1
            || (groups[0] && groups[0].label)
            || (groups[0] && groups[0].fields && groups[0].fields.length > 1);
        if (useGroupedLayout) {
            let globalIndex = 0;
            groups.forEach((group) => {
                const groupWrap = document.createElement("div");
                groupWrap.className = "multi-part-group";
                if (group.label) {
                    const groupLabel = document.createElement("span");
                    groupLabel.className = "multi-part-group-label";
                    groupLabel.textContent = group.label;
                    groupWrap.appendChild(groupLabel);
                }
                group.fields.forEach((sq) => {
                    appendField(groupWrap, sq, globalIndex);
                    globalIndex += 1;
                });
                container.appendChild(groupWrap);
            });
        } else {
            parts.forEach((part, index) => appendField(container, part, index));
        }
        return { fields: parts, groups };
    }

    function isInteractiveControl(node) {
        if (!node || !node.tagName) return false;
        const tag = node.tagName.toUpperCase();
        if (tag === "SELECT" || tag === "TEXTAREA") return true;
        if (tag === "INPUT") {
            const type = String(node.getAttribute("type") || "text").toLowerCase();
            return type !== "hidden" && type !== "button" && type !== "submit";
        }
        return false;
    }

    function controlIsVisible(node) {
        if (!isInteractiveControl(node)) return false;
        if (node.disabled && node.tagName.toUpperCase() === "INPUT" && node.type === "hidden") return false;
        const style = window.getComputedStyle ? window.getComputedStyle(node) : null;
        if (style) {
            if (style.display === "none" || style.visibility === "hidden") return false;
            if (Number(style.opacity) === 0) return false;
        }
        const rect = node.getBoundingClientRect ? node.getBoundingClientRect() : null;
        if (!rect) return true;
        return rect.width > 8 && rect.height > 8;
    }

    function countControls(container) {
        const nodes = container
            ? Array.from(container.querySelectorAll("input, select, textarea"))
            : [];
        const interactive = nodes.filter(isInteractiveControl);
        const visible = interactive.filter(controlIsVisible);
        return {
            input_element_count: interactive.length,
            visible_input_element_count: visible.length,
        };
    }

    return {
        resolveFields,
        buildGroups,
        render,
        countControls,
        isInteractiveControl,
        controlIsVisible,
        controlKind,
        controlKindFromPayload,
        applyControlKind,
    };
}));
