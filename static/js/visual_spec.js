(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.VisualSpecRuntime = api;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    const RENDER_KIND_TOKENS = [
        'graph',
        'chart',
        'plot',
        'histogram',
        'polygon',
        'diagram',
        'number_line',
        'function_graph',
        'coordinate_plane'
    ];

    const DRAWABLE_ARRAY_KEYS = [
        'points',
        'lines',
        'segments',
        'curves',
        'series',
        'bars',
        'data_points',
        'graph_points',
        'nodes',
        'edges',
        'shapes'
    ];

    function hasDrawablePrimitives(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object' || Array.isArray(visualSpec)) {
            return false;
        }
        return DRAWABLE_ARRAY_KEYS.some(function (key) {
            return Array.isArray(visualSpec[key]) && visualSpec[key].length > 0;
        });
    }

    function hasRenderKind(visualSpec) {
        const kind = String(visualSpec.kind || visualSpec.type || '').trim().toLowerCase();
        if (!kind || kind === 'no_visual') {
            return false;
        }
        if (kind.endsWith('_spec') && visualSpec.render_required !== true) {
            return false;
        }
        return visualSpec.render_required === true || RENDER_KIND_TOKENS.some(function (token) {
            return kind === token || kind.indexOf(token) >= 0;
        });
    }

    function requiresVisualRendering(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object' || Array.isArray(visualSpec)) {
            return false;
        }
        if (Object.keys(visualSpec).length === 0) {
            return false;
        }
        return hasRenderKind(visualSpec) && hasDrawablePrimitives(visualSpec);
    }

    function renderToCanvas(canvas, visualSpec) {
        if (!canvas || !requiresVisualRendering(visualSpec)) {
            return false;
        }
        const context = canvas.getContext && canvas.getContext('2d');
        if (!context) {
            return false;
        }
        const axis = visualSpec.axis_range || {};
        const xRange = visualSpec.x_range || [axis.x_min, axis.x_max];
        const yRange = visualSpec.y_range || [axis.y_min, axis.y_max];
        const xMin = Number(xRange[0] ?? axis.x_min ?? -10);
        const xMax = Number(xRange[1] ?? axis.x_max ?? 10);
        const yMin = Number(yRange[0] ?? axis.y_min ?? -10);
        const yMax = Number(yRange[1] ?? axis.y_max ?? 10);
        if (!(xMax > xMin) || !(yMax > yMin)) {
            return false;
        }
        const width = Math.max(320, Number(canvas.clientWidth || canvas.width || 640));
        const height = Math.max(220, Number(canvas.clientHeight || canvas.height || 360));
        const ratio = Number(
            (typeof globalThis !== 'undefined' && globalThis.devicePixelRatio)
            || 1
        );
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        context.clearRect(0, 0, width, height);
        context.fillStyle = '#ffffff';
        context.fillRect(0, 0, width, height);

        const margin = 34;
        const plotWidth = width - margin * 2;
        const plotHeight = height - margin * 2;
        const mapX = function (value) {
            return margin + (Number(value) - xMin) / (xMax - xMin) * plotWidth;
        };
        const mapY = function (value) {
            return height - margin - (Number(value) - yMin) / (yMax - yMin) * plotHeight;
        };

        context.strokeStyle = '#e5e7eb';
        context.lineWidth = 1;
        for (let value = Math.ceil(xMin); value <= Math.floor(xMax); value += 1) {
            context.beginPath();
            context.moveTo(mapX(value), margin);
            context.lineTo(mapX(value), height - margin);
            context.stroke();
        }
        for (let value = Math.ceil(yMin); value <= Math.floor(yMax); value += 1) {
            context.beginPath();
            context.moveTo(margin, mapY(value));
            context.lineTo(width - margin, mapY(value));
            context.stroke();
        }

        context.strokeStyle = '#374151';
        context.lineWidth = 1.5;
        if (xMin <= 0 && xMax >= 0) {
            context.beginPath();
            context.moveTo(mapX(0), margin);
            context.lineTo(mapX(0), height - margin);
            context.stroke();
        }
        if (yMin <= 0 && yMax >= 0) {
            context.beginPath();
            context.moveTo(margin, mapY(0));
            context.lineTo(width - margin, mapY(0));
            context.stroke();
        }

        const primitives = Array.isArray(visualSpec.drawable_primitives)
            ? visualSpec.drawable_primitives
            : [];
        const lines = []
            .concat(Array.isArray(visualSpec.lines) ? visualSpec.lines : [])
            .concat(primitives.filter(function (item) {
                return item && item.type === 'line';
            }));
        context.strokeStyle = '#1565c0';
        context.lineWidth = 2.5;
        lines.forEach(function (line) {
            if (Array.isArray(line.through_points) && line.through_points.length >= 2) {
                const p1 = line.through_points[0];
                const p2 = line.through_points[1];
                const x1 = Number(Array.isArray(p1) ? p1[0] : p1.x);
                const y1 = Number(Array.isArray(p1) ? p1[1] : p1.y);
                const x2 = Number(Array.isArray(p2) ? p2[0] : p2.x);
                const y2 = Number(Array.isArray(p2) ? p2[1] : p2.y);
                if (![x1, y1, x2, y2].every(Number.isFinite)) {
                    return;
                }
                context.beginPath();
                context.moveTo(mapX(x1), mapY(y1));
                context.lineTo(mapX(x2), mapY(y2));
                context.stroke();
                return;
            }
            const equation = line.equation || line;
            const coefficientA = Number(equation.A ?? equation.a);
            const coefficientB = Number(equation.B ?? equation.b);
            const constantC = Number(equation.C ?? equation.c ?? 0);
            if (![coefficientA, coefficientB, constantC].every(Number.isFinite)) {
                return;
            }
            context.beginPath();
            if (coefficientB !== 0) {
                context.moveTo(mapX(xMin), mapY((-coefficientA * xMin - constantC) / coefficientB));
                context.lineTo(mapX(xMax), mapY((-coefficientA * xMax - constantC) / coefficientB));
            } else if (coefficientA !== 0) {
                const xValue = -constantC / coefficientA;
                context.moveTo(mapX(xValue), mapY(yMin));
                context.lineTo(mapX(xValue), mapY(yMax));
            } else {
                return;
            }
            context.stroke();
        });

        const points = Array.isArray(visualSpec.points) ? visualSpec.points : [];
        context.fillStyle = '#dc2626';
        points.forEach(function (point) {
            const xValue = Number(Array.isArray(point) ? point[0] : point.x);
            const yValue = Number(Array.isArray(point) ? point[1] : point.y);
            if (!Number.isFinite(xValue) || !Number.isFinite(yValue)) {
                return;
            }
            context.beginPath();
            context.arc(mapX(xValue), mapY(yValue), 4, 0, Math.PI * 2);
            context.fill();
        });
        return true;
    }

    return {
        hasDrawablePrimitives: hasDrawablePrimitives,
        requiresVisualRendering: requiresVisualRendering,
        renderToCanvas: renderToCanvas
    };
}));
