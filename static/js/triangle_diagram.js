(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) module.exports = api;
    if (root) root.TriangleDiagramRuntime = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    const POINTS = {
        A: { x: 45, y: 190, labelX: 25, labelY: 214 },
        B: { x: 118, y: 35, labelX: 108, labelY: 25 },
        C: { x: 330, y: 190, labelX: 338, labelY: 214 }
    };

    function escapeXml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    }

    function isTriangleSpec(spec) {
        return !!spec && spec.version === 1 && spec.type === 'triangle'
            && Array.isArray(spec.vertices) && spec.vertices.join(',') === 'A,B,C'
            && spec.side_vertices && typeof spec.side_vertices === 'object';
    }

    function createSvgMarkup(spec) {
        if (!isTriangleSpec(spec)) return '';
        const parameters = spec.parameters || {};
        const angles = parameters.angles_deg || {};
        const sides = parameters.sides || {};
        const show = spec.show || {};
        const shownAngles = Array.isArray(show.angles) ? show.angles : [];
        const shownSides = Array.isArray(show.sides) ? show.sides : [];
        const unknownSides = Array.isArray(show.unknown_sides) ? show.unknown_sides : [];
        const sideVertices = spec.side_vertices || {};
        const sideOffsets = { a: { x: 10, y: -8 }, b: { x: 0, y: 21 }, c: { x: -25, y: -5 } };
        function sideLabelPosition(side) {
            const names = sideVertices[side];
            if (!Array.isArray(names) || names.length !== 2 || !POINTS[names[0]] || !POINTS[names[1]]) return null;
            const first = POINTS[names[0]];
            const second = POINTS[names[1]];
            const offset = sideOffsets[side] || { x: 0, y: 0 };
            return { x: (first.x + second.x) / 2 + offset.x, y: (first.y + second.y) / 2 + offset.y };
        }
        const anglePosition = {
            A: { x: 68, y: 176 }, B: { x: 121, y: 62 }, C: { x: 297, y: 177 }
        };
        const labels = [];
        shownAngles.forEach(function (vertex) {
            if (angles[vertex] === undefined) return;
            const p = anglePosition[vertex];
            labels.push(`<text class="triangle-angle" x="${p.x}" y="${p.y}">${escapeXml(angles[vertex])}°</text>`);
        });
        shownSides.forEach(function (side) {
            if (sides[side] === undefined) return;
            const p = sideLabelPosition(side);
            if (!p) return;
            labels.push(`<text class="triangle-side" x="${p.x}" y="${p.y}">${escapeXml(side)} = ${escapeXml(sides[side])}</text>`);
        });
        unknownSides.forEach(function (side) {
            const p = sideLabelPosition(side);
            if (!p) return;
            labels.push(`<text class="triangle-unknown" x="${p.x}" y="${p.y}">${escapeXml(side)} = ?</text>`);
        });
        const vertices = Object.keys(POINTS).map(function (name) {
            const p = POINTS[name];
            return `<circle cx="${p.x}" cy="${p.y}" r="3.5"/><text class="triangle-vertex" x="${p.labelX}" y="${p.labelY}">${name}</text>`;
        }).join('');
        return `<svg class="deterministic-triangle" viewBox="0 0 380 235" role="img" aria-label="依題目參數繪製的三角形 ABC" xmlns="http://www.w3.org/2000/svg">`
            + '<style>.deterministic-triangle{max-width:440px;width:100%;height:auto}.deterministic-triangle polygon{fill:#eff6ff;stroke:#172554;stroke-width:3}.deterministic-triangle circle{fill:#172554}.deterministic-triangle text{font-family:Arial,"Noto Sans TC",sans-serif;fill:#111827;font-size:17px}.deterministic-triangle .triangle-vertex{font-weight:700;font-size:19px}.deterministic-triangle .triangle-unknown{fill:#b91c1c;font-weight:700}</style>'
            + '<polygon points="45,190 118,35 330,190"/>' + vertices + labels.join('') + '</svg>';
    }

    function render(container, spec) {
        const markup = createSvgMarkup(spec);
        if (!container || !markup) return false;
        container.innerHTML = markup;
        container.style.display = 'block';
        return true;
    }

    return { isTriangleSpec, createSvgMarkup, render };
}));
