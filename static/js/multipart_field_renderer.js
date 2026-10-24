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
                canvas: part.canvas && typeof part.canvas === "object" ? part.canvas : null,
                choices: Array.isArray(part.choices) ? part.choices : [],
                checker: String(part.checker || part.checker_key || ""),
                expected_answer: part.expected_answer == null ? "" : String(part.expected_answer),
                answer_order: part.answer_order == null ? index : part.answer_order,
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
                answer_order: sq.answer_order == null ? index : sq.answer_order,
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
            const generic = text.match(GENERIC_PART_LABEL);
            return generic ? `(${Number(generic[1])})` : text;
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

    // Positional names such as part_1 / Part 1 / 欄位 1 / 第（1）小題 carry no
    // meaning for students; they are shown as (1).  Semantic labels pass through.
    const GENERIC_PART_LABEL = /^(?:part|欄位|第)?[\s_\-]*[\(（]?\s*(\d{1,2})\s*[\)）]?[\s_\-]*(?:小題|題)?$/i;
    const SIGNED_PART_LABEL = /^part[\s_\-]*(\d{1,2})[\s_\-]+(pos|neg)$/i;

    function studentLabel(text, fallbackIndex) {
        const raw = String(text == null ? "" : text).trim();
        if (!raw) return `(${fallbackIndex + 1})`;
        const generic = raw.match(GENERIC_PART_LABEL);
        if (generic) return `(${Number(generic[1])})`;
        const signed = raw.match(SIGNED_PART_LABEL);
        if (signed) return `(${Number(signed[1])}) ${signed[2].toLowerCase() === "pos" ? "正" : "負"}`;
        return raw;
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
        return studentLabel((part && (part.label || part.prompt)) || key, fallbackIndex);
    }

    function controlKind(part) {
        const checker = String((part && (part.checker || part.checker_key)) || "").toLowerCase();
        const expected = String((part && part.expected_answer) || "");
        if (checker.includes("inequality") || /[<>≤≥]|\\le|\\ge/.test(expected)) return "inequality";
        if (expected.includes("=") && /[xyk]/i.test(expected)) return "equation";
        if (/sqrt|\\sqrt|√/.test(expected)) return "radical";
        if (expected.includes("/")) return "fraction";
        if (/^\s*\(?\s*[+-]?\d+(?:\.\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?\s*\)?\s*$/.test(expected)) return "coordinate";
        if (checker.includes("integer") || /^[+-]?\d+$/.test(expected.replace(/\s/g, ""))) return "numeric";
        if (/[\u4e00-\u9fff]/.test(expected)) return "text";
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
        ["numeric", "coordinate", "fraction", "expression", "equation", "inequality", "radical", "text"].forEach((name) => {
            node.classList.remove("control-" + name);
        });
        node.classList.add("control-" + (kind || "expression"));
    }

    // Independent drawing canvas for a part (answer_contract part with input_type "canvas").
    // Grid/axes are a non-interactive background; the answer value is a JSON string
    // {composite, strokes} kept in a hidden .multi-part-input so collectMultiPartAnswers() is unchanged.
    function createCanvasControl(part, index) {
        const fieldKey = String(part.key || part.field_key || `part_${index + 1}`);
        const range = (part.canvas && part.canvas.axis_range) || { x_min: -6, x_max: 6, y_min: -6, y_max: 6 };
        const cssW = 300;
        const cssH = 260;
        const ratio = (typeof window !== "undefined" && window.devicePixelRatio) || 1;
        const wrap = document.createElement("div");
        wrap.className = "multi-part-canvas-wrap";
        wrap.style.cssText = "position:relative;display:inline-block;width:" + cssW + "px;max-width:100%;";
        const stage = document.createElement("div");
        stage.style.cssText = "position:relative;width:" + cssW + "px;max-width:100%;aspect-ratio:" + cssW + " / " + cssH + ";height:auto;border:1px solid #bbb;background:#fff;";
        const make = () => {
            const c = document.createElement("canvas");
            c.width = Math.round(cssW * ratio);
            c.height = Math.round(cssH * ratio);
            // The page-wide `canvas { background: #fff }` rule would hide the grid canvas under the ink canvas.
            c.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;background:transparent;";
            return c;
        };
        const bg = make();
        const ink = make();
        ink.id = `multi-part-canvas-${fieldKey}`;
        ink.className = "multi-part-canvas";
        ink.dataset.fieldKey = fieldKey;
        ink.style.touchAction = "none";
        ink.style.cursor = "crosshair";
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.id = `multi-part-input-${fieldKey}`;
        hidden.className = "multi-part-input multi-part-canvas-value";
        hidden.dataset.partIndex = String(index);
        hidden.dataset.fieldKey = fieldKey;
        hidden.dataset.answerOrder = String(part.answer_order == null ? index : part.answer_order);

        const xMin = Number(range.x_min), xMax = Number(range.x_max), yMin = Number(range.y_min), yMax = Number(range.y_max);
        const mapX = (x) => ((x - xMin) / (xMax - xMin)) * cssW;
        const mapY = (y) => cssH - ((y - yMin) / (yMax - yMin)) * cssH;
        const line = (ctx, x1, y1, x2, y2) => { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); };
        const bctx = bg.getContext("2d");
        bctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        bctx.fillStyle = "#fff";
        bctx.fillRect(0, 0, cssW, cssH);
        bctx.strokeStyle = "#e5e7eb";
        bctx.lineWidth = 1;
        for (let x = Math.ceil(xMin); x <= Math.floor(xMax); x += 1) line(bctx, mapX(x), 0, mapX(x), cssH);
        for (let y = Math.ceil(yMin); y <= Math.floor(yMax); y += 1) line(bctx, 0, mapY(y), cssW, mapY(y));
        bctx.strokeStyle = "#374151";
        bctx.lineWidth = 1.5;
        if (xMin <= 0 && xMax >= 0) line(bctx, mapX(0), 0, mapX(0), cssH);
        if (yMin <= 0 && yMax >= 0) line(bctx, 0, mapY(0), cssW, mapY(0));
        bctx.fillStyle = "#374151";
        bctx.font = "10px sans-serif";
        for (let x = Math.ceil(xMin); x <= Math.floor(xMax); x += 2) { if (x !== 0) bctx.fillText(String(x), mapX(x) + 2, Math.min(cssH - 2, mapY(0) + 11)); }
        for (let y = Math.ceil(yMin); y <= Math.floor(yMax); y += 2) { if (y !== 0 && mapY(y) > 22) bctx.fillText(String(y), Math.max(2, mapX(0) + 3), mapY(y) - 2); }
        bctx.fillText("x", cssW - 10, Math.min(cssH - 3, mapY(0) - 3));
        bctx.fillText("y", Math.min(cssW - 8, mapX(0) + 4), 10);

        const ictx = ink.getContext("2d");
        ictx.setTransform(ratio, 0, 0, ratio, 0, 0);
        ictx.lineCap = "round";
        ictx.lineJoin = "round";
        ictx.lineWidth = 2.5;
        ictx.strokeStyle = "#1d4ed8";
        let drawing = false;
        let dirty = false;
        const pos = (event) => {
            const rect = ink.getBoundingClientRect();
            return { x: ((event.clientX - rect.left) / rect.width) * cssW, y: ((event.clientY - rect.top) / rect.height) * cssH };
        };
        const commit = () => {
            if (!dirty) { hidden.value = ""; return; }
            const comp = document.createElement("canvas");
            comp.width = ink.width;
            comp.height = ink.height;
            const cctx = comp.getContext("2d");
            cctx.drawImage(bg, 0, 0);
            cctx.drawImage(ink, 0, 0);
            hidden.value = JSON.stringify({ composite: comp.toDataURL("image/png"), strokes: ink.toDataURL("image/png") });
            hidden.dispatchEvent(new Event("input", { bubbles: true }));
        };
        ink.addEventListener("pointerdown", (event) => {
            if (hidden.disabled) return;
            drawing = true;
            if (ink.setPointerCapture) ink.setPointerCapture(event.pointerId);
            const p = pos(event);
            ictx.beginPath();
            ictx.moveTo(p.x, p.y);
            ictx.lineTo(p.x + 0.01, p.y + 0.01);
            ictx.stroke();
            dirty = true;
            event.preventDefault();
        });
        ink.addEventListener("pointermove", (event) => {
            if (!drawing) return;
            const p = pos(event);
            ictx.lineTo(p.x, p.y);
            ictx.stroke();
            event.preventDefault();
        });
        const stop = () => { if (drawing) { drawing = false; commit(); } };
        ink.addEventListener("pointerup", stop);
        ink.addEventListener("pointercancel", stop);
        const clear = document.createElement("button");
        clear.type = "button";
        clear.textContent = "清除此圖";
        clear.className = "multi-part-canvas-clear";
        clear.addEventListener("click", () => {
            ictx.clearRect(0, 0, cssW, cssH);
            dirty = false;
            commit();
        });
        stage.appendChild(bg);
        stage.appendChild(ink);
        wrap.appendChild(stage);
        wrap.appendChild(clear);
        wrap.appendChild(hidden);
        return wrap;
    }

    function createControl(part, index) {
        if (part.input_type === "canvas") {
            return createCanvasControl(part, index);
        }
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
                // choices may be plain strings or {label, value, text} objects (answer_contract parts)
                const isObject = item !== null && typeof item === "object";
                const value = isObject ? (item.value ?? item.label ?? item.text ?? "") : item;
                const text = isObject ? (item.text ?? item.value ?? item.label ?? "") : item;
                option.value = String(value);
                option.textContent = String(text);
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
        input.dataset.answerOrder = String(part.answer_order == null ? index : part.answer_order);
        applyControlKind(input, controlKind(part));
        return input;
    }

    // A generator may hand over a label that is raw TeX (y=x^{3}, \frac{..}{..}); it is shown as math, never as source.
    const RAW_TEX = /\\[a-zA-Z]{2,}|[\^_]\{/;
    const TEX_DELIMITED = /\$|\\\(|\\\[/;

    function mathSafeLabel(text) {
        const raw = String(text == null ? "" : text);
        if (!RAW_TEX.test(raw) || TEX_DELIMITED.test(raw) || /[一-鿿]/.test(raw)) return raw;
        const marker = raw.match(/^\s*([\(（]\s*\d{1,2}\s*[\)）])\s*(.*)$/);
        return marker ? marker[1] + " \\(" + marker[2] + "\\)" : "\\(" + raw + "\\)";
    }

    function appendField(container, part, index, groupLabel) {
        const row = document.createElement("div");
        row.className = "multi-part-row" + (part.input_type === "canvas" ? " multi-part-row--canvas" : "");
        const fieldKey = String(part.key || part.field_key || `part_${index + 1}`);
        const prompt = figureSlotDisplayLabel(part, index);
        const control = createControl(part, index);
        if (groupLabel && prompt === groupLabel) {
            control.setAttribute("aria-label", prompt);
        } else {
            const label = document.createElement("label");
            label.textContent = mathSafeLabel(prompt);
            label.setAttribute("for", `multi-part-input-${fieldKey}`);
            row.appendChild(label);
        }
        row.appendChild(control);
        container.appendChild(row);
    }

    // Consecutive independent canvases share one strip: side by side while they fit, wrapping below each other,
    // and always on a line of their own so numeric fields never float beside a canvas.
    function appendPartField(container, part, index, groupLabel) {
        if (part.input_type !== "canvas") {
            appendField(container, part, index, groupLabel);
            return;
        }
        let strip = container.lastElementChild;
        if (!strip || !strip.classList || !strip.classList.contains("multi-part-canvas-strip")) {
            strip = document.createElement("div");
            strip.className = "multi-part-canvas-strip";
            container.appendChild(strip);
        }
        appendField(strip, part, index, groupLabel);
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
                    appendPartField(groupWrap, sq, globalIndex, group.label);
                    globalIndex += 1;
                });
                container.appendChild(groupWrap);
            });
        } else {
            parts.forEach((part, index) => appendPartField(container, part, index));
        }
        return { fields: parts, groups };
    }

    // The answer strip wraps naturally, but a submit button that lands alone on
    // the next line wastes a full row.  When that happens the strip retries with
    // the narrower (still typeable) compact widths and keeps them only if the
    // button then follows the last field or the strip needs fewer lines.
    function lineCount(nodes) {
        const centers = nodes
            .map((node) => { const r = node.getBoundingClientRect(); return r.top + r.height / 2; })
            .sort((a, b) => a - b);
        let lines = 0;
        let last = -Infinity;
        centers.forEach((center) => {
            if (center - last > 6) lines += 1;
            last = center;
        });
        return lines;
    }

    function fitAnswerStrip(block) {
        if (!block || !block.classList) return false;
        block.classList.remove("answer-strip-compact");
        const submit = block.querySelector("#submit-button");
        const controls = Array.from(block.querySelectorAll(".multi-part-input"))
            .filter((node) => node.offsetParent !== null);
        if (!submit || submit.offsetParent === null || controls.length < 2) return false;
        const lastControl = controls[controls.length - 1];
        const submitFollowsLast = () => lineCount([lastControl, submit]) === 1;
        if (submitFollowsLast()) return false;
        const before = lineCount(controls.concat(submit));
        block.classList.add("answer-strip-compact");
        if (submitFollowsLast() || lineCount(controls.concat(submit)) < before) return true;
        block.classList.remove("answer-strip-compact");
        return false;
    }

    function isInteractiveControl(node) {
        if (!node || !node.tagName) return false;
        const tag = node.tagName.toUpperCase();
        if (tag === "SELECT" || tag === "TEXTAREA") return true;
        if (tag === "CANVAS") return String(node.className || "").indexOf("multi-part-canvas") >= 0;
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
            ? Array.from(container.querySelectorAll("input, select, textarea, canvas.multi-part-canvas"))
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
        studentLabel,
        mathSafeLabel,
        figureSlotDisplayLabel,
        fitAnswerStrip,
    };
}));
