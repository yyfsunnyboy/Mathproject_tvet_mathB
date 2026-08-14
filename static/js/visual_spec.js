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
        'shapes',
        'figures',
        'comparisons'
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

    function isMultiFigureSpec(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object') {
            return false;
        }
        const kind = String(visualSpec.kind || visualSpec.type || '').trim().toLowerCase();
        if (kind === 'coordinate_plane_multi_figure') {
            return true;
        }
        return Array.isArray(visualSpec.figures)
            && visualSpec.figures.length > 0
            && Array.isArray(visualSpec.comparisons)
            && visualSpec.comparisons.length > 0;
    }

    function normalizePointEntry(point, fallbackLabel) {
        if (Array.isArray(point) && point.length >= 2) {
            return { x: Number(point[0]), y: Number(point[1]), label: fallbackLabel || '' };
        }
        if (point && typeof point === 'object') {
            return {
                x: Number(point.x),
                y: Number(point.y),
                label: String(point.label || fallbackLabel || '')
            };
        }
        return null;
    }

    function buildMultiFigurePanels(visualSpec) {
        const axis = visualSpec.axis_range || {};
        const xRange = visualSpec.x_range || [axis.x_min, axis.x_max];
        const yRange = visualSpec.y_range || [axis.y_min, axis.y_max];
        const panels = [];

        (visualSpec.figures || []).forEach(function (fig, index) {
            if (!fig || typeof fig !== 'object') {
                return;
            }
            const rawPoints = Array.isArray(fig.points) ? fig.points : [];
            const points = [];
            rawPoints.forEach(function (pt, ptIndex) {
                const normalized = normalizePointEntry(pt, String.fromCharCode(65 + ptIndex));
                if (normalized && Number.isFinite(normalized.x) && Number.isFinite(normalized.y)) {
                    points.push(normalized);
                }
            });
            const lines = [];
            if (points.length >= 2) {
                lines.push({
                    through_points: [
                        [points[0].x, points[0].y],
                        [points[1].x, points[1].y]
                    ],
                    label: String(fig.id || fig.label || ('fig' + (index + 1)))
                });
            }
            panels.push({
                id: String(fig.id || ('fig' + (index + 1))),
                label: String(fig.label || fig.id || ('圖' + (index + 1))),
                spec: {
                    kind: 'coordinate_plane',
                    points: points,
                    lines: lines,
                    x_range: xRange,
                    y_range: yRange
                }
            });
        });

        (visualSpec.comparisons || []).forEach(function (cmp, index) {
            if (!cmp || typeof cmp !== 'object') {
                return;
            }
            const points = [];
            const lines = [];
            ['L1', 'L2'].forEach(function (key) {
                const seg = cmp[key];
                if (!seg || typeof seg !== 'object') {
                    return;
                }
                const segPoints = Array.isArray(seg.points) ? seg.points : [];
                const resolved = [];
                segPoints.forEach(function (pt) {
                    const normalized = normalizePointEntry(pt);
                    if (normalized && Number.isFinite(normalized.x) && Number.isFinite(normalized.y)) {
                        resolved.push(normalized);
                        points.push(normalized);
                    }
                });
                if (resolved.length >= 2) {
                    lines.push({
                        through_points: [
                            [resolved[0].x, resolved[0].y],
                            [resolved[1].x, resolved[1].y]
                        ],
                        label: key
                    });
                }
            });
            panels.push({
                id: String(cmp.id || ('cmp' + (index + 1))),
                label: String(cmp.label || cmp.id || ('比較' + (index + 1))),
                spec: {
                    kind: 'coordinate_plane',
                    points: points,
                    lines: lines,
                    x_range: xRange,
                    y_range: yRange
                }
            });
        });

        return panels;
    }

    function computeMultiFigureGrid(panelCount, width, height, padding) {
        const outerPad = Number.isFinite(padding) ? padding : 16;
        const gap = width >= 768 ? 10 : 8;
        let cols;
        if (width >= 768) {
            cols = 3;
        } else if (width >= 300) {
            cols = 2;
        } else {
            cols = 1;
        }
        const rows = Math.max(1, Math.ceil(panelCount / cols));
        const innerWidth = Math.max(1, width - outerPad * 2 - gap * (cols - 1));
        const innerHeight = Math.max(1, height - outerPad * 2 - gap * (rows - 1));
        const cellWidth = innerWidth / cols;
        const cellHeight = innerHeight / rows;
        const cells = [];
        for (let index = 0; index < panelCount; index += 1) {
            const row = Math.floor(index / cols);
            const col = index % cols;
            cells.push({
                x: outerPad + col * (cellWidth + gap),
                y: outerPad + row * (cellHeight + gap),
                width: cellWidth,
                height: cellHeight
            });
        }
        return { cols: cols, rows: rows, gap: gap, cells: cells };
    }

    function parseFractionLike(value) {
        if (typeof value === 'number') {
            return value;
        }
        const text = String(value || '').trim();
        if (!text || text === '不存在' || text === '∞') {
            return NaN;
        }
        if (text.indexOf('/') >= 0) {
            const parts = text.split('/');
            const numerator = Number(parts[0]);
            const denominator = Number(parts[1]);
            if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator === 0) {
                return NaN;
            }
            return numerator / denominator;
        }
        return Number(text);
    }

    function resolvePointReference(ref, points) {
        if (Array.isArray(ref)) {
            return {
                x: Number(ref[0]),
                y: Number(ref[1])
            };
        }
        if (ref && typeof ref === 'object' && Number.isFinite(Number(ref.x)) && Number.isFinite(Number(ref.y))) {
            return { x: Number(ref.x), y: Number(ref.y) };
        }
        const label = String(ref || '').trim();
        if (!label) {
            return null;
        }
        for (let i = 0; i < points.length; i += 1) {
            const point = points[i];
            if (String(point.label || '') === label) {
                return {
                    x: Number(Array.isArray(point) ? point[0] : point.x),
                    y: Number(Array.isArray(point) ? point[1] : point.y)
                };
            }
        }
        return null;
    }

    function hasNumericThroughPoints(line, points) {
        if (!Array.isArray(line.through_points) || line.through_points.length < 2) {
            return false;
        }
        const p1 = resolvePointReference(line.through_points[0], points);
        const p2 = resolvePointReference(line.through_points[1], points);
        if (p1 && p2) {
            return [p1.x, p1.y, p2.x, p2.y].every(Number.isFinite);
        }
        const raw1 = line.through_points[0];
        const raw2 = line.through_points[1];
        const x1 = Number(Array.isArray(raw1) ? raw1[0] : raw1.x);
        const y1 = Number(Array.isArray(raw1) ? raw1[1] : raw1.y);
        const x2 = Number(Array.isArray(raw2) ? raw2[0] : raw2.x);
        const y2 = Number(Array.isArray(raw2) ? raw2[1] : raw2.y);
        return [x1, y1, x2, y2].every(Number.isFinite);
    }

    const INTENTIONALLY_BLANK_KINDS = [
        'cartesian_canvas',
        'no_visual',
        'line_graph_choices',
        'cumulative_frequency_table',
        'table'
    ];

    function getVisualKind(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object') {
            return '';
        }
        return String(visualSpec.kind || visualSpec.type || '').trim().toLowerCase();
    }

    function normalizeStringPoints(points) {
        return (Array.isArray(points) ? points : []).map(function (point, index) {
            const normalized = normalizePointEntry(point, String.fromCharCode(65 + index));
            if (normalized && Number.isFinite(normalized.x) && Number.isFinite(normalized.y)) {
                return normalized;
            }
            return null;
        }).filter(Boolean);
    }

    function normalizeDataPoints(rawPoints) {
        return (Array.isArray(rawPoints) ? rawPoints : []).map(function (point) {
            if (Array.isArray(point)) {
                return {
                    x: parseFractionLike(point[0]),
                    y: parseFractionLike(point[1])
                };
            }
            if (point && typeof point === 'object') {
                return {
                    x: parseFractionLike(point.x),
                    y: parseFractionLike(point.y)
                };
            }
            return null;
        }).filter(function (point) {
            return point && Number.isFinite(point.x) && Number.isFinite(point.y);
        });
    }

    function buildCumulativeDataPointsFromRows(visualSpec) {
        const rows = Array.isArray(visualSpec.rows) ? visualSpec.rows : [];
        const cumulativeValues = Array.isArray(visualSpec.cumulative_values)
            ? visualSpec.cumulative_values
            : [];
        const points = [];
        rows.forEach(function (row, index) {
            const xRaw = Array.isArray(row) ? row[0] : row;
            const xValue = parseFractionLike(xRaw);
            const yValue = parseFractionLike(cumulativeValues[index]);
            if (Number.isFinite(xValue) && Number.isFinite(yValue)) {
                points.push({ x: xValue, y: yValue });
            }
        });
        return points;
    }

    function computeNumericRange(values, fallbackMin, fallbackMax, padRatio) {
        const finite = values.filter(Number.isFinite);
        if (!finite.length) {
            return [fallbackMin, fallbackMax];
        }
        const minValue = Math.min.apply(null, finite);
        const maxValue = Math.max.apply(null, finite);
        const span = Math.max(1, maxValue - minValue);
        const pad = span * (Number.isFinite(padRatio) ? padRatio : 0.08);
        return [minValue - pad, maxValue + pad];
    }

    function normalizeVisualSpecForRendering(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object') {
            return null;
        }
        const kind = getVisualKind(visualSpec);
        if (kind === 'coordinate_line_graph' || kind === 'function_graph') {
            const points = normalizeStringPoints(visualSpec.points);
            const primitives = Array.isArray(visualSpec.drawable_primitives)
                ? visualSpec.drawable_primitives
                : [];
            const primitiveLines = primitives.filter(function (item) {
                return item && item.type === 'line';
            });
            const axis = visualSpec.axis_range || {};
            return {
                kind: 'coordinate_plane',
                render_required: true,
                points: points,
                lines: []
                    .concat(Array.isArray(visualSpec.lines) ? visualSpec.lines : [])
                    .concat(primitiveLines),
                x_range: visualSpec.x_range || [axis.x_min ?? -10, axis.x_max ?? 10],
                y_range: visualSpec.y_range || [axis.y_min ?? -10, axis.y_max ?? 10],
                axis_range: axis
            };
        }
        if (kind === 'tiered_linear_graph') {
            const breakpoints = normalizeStringPoints(visualSpec.breakpoints);
            const lines = [];
            for (let index = 0; index < breakpoints.length - 1; index += 1) {
                const start = breakpoints[index];
                const end = breakpoints[index + 1];
                lines.push({
                    through_points: [
                        [start.x, start.y],
                        [end.x, end.y]
                    ]
                });
            }
            const xs = breakpoints.map(function (point) { return point.x; });
            const ys = breakpoints.map(function (point) { return point.y; });
            return {
                kind: 'coordinate_plane',
                render_required: true,
                points: breakpoints,
                lines: lines,
                x_range: computeNumericRange(xs, 0, 10, 0.12),
                y_range: computeNumericRange(ys, 0, 10, 0.12)
            };
        }
        if (kind === 'linear_application_graph') {
            const line = visualSpec.line || {};
            const points = normalizeStringPoints(line.points);
            const lines = [];
            const slope = parseFractionLike(line.slope ?? line.m);
            const intercept = parseFractionLike(line.intercept ?? line.b);
            if (Number.isFinite(slope) && Number.isFinite(intercept)) {
                lines.push({ type: 'slope_intercept', m: slope, b: intercept });
            } else if (points.length >= 2) {
                lines.push({
                    through_points: [
                        [points[0].x, points[0].y],
                        [points[1].x, points[1].y]
                    ]
                });
            }
            const xRange = Array.isArray(visualSpec.x_range) && visualSpec.x_range.length >= 2
                ? [parseFractionLike(visualSpec.x_range[0]), parseFractionLike(visualSpec.x_range[1])]
                : computeNumericRange(points.map(function (point) { return point.x; }), 0, 10, 0.12);
            const yCandidates = points.map(function (point) { return point.y; });
            if (Number.isFinite(slope) && Number.isFinite(intercept)) {
                yCandidates.push(slope * xRange[0] + intercept, slope * xRange[1] + intercept);
            }
            return {
                kind: 'coordinate_plane',
                render_required: true,
                points: points,
                lines: lines,
                x_range: xRange,
                y_range: computeNumericRange(yCandidates, 0, 10, 0.12)
            };
        }
        if (kind === 'collinear_points') {
            const points = normalizeStringPoints(visualSpec.ordered_points);
            const lines = points.length >= 2
                ? [{
                    through_points: [
                        [points[0].x, points[0].y],
                        [points[points.length - 1].x, points[points.length - 1].y]
                    ]
                }]
                : [];
            return {
                kind: 'coordinate_plane',
                render_required: true,
                points: points,
                lines: lines,
                x_range: computeNumericRange(points.map(function (point) { return point.x; }), -10, 10, 0.12),
                y_range: computeNumericRange(points.map(function (point) { return point.y; }), -10, 10, 0.12)
            };
        }
        if (
            kind === 'cumulative_frequency_polygon'
            || kind === 'cumulative_frequency_graph'
            || kind.indexOf('cumulative_frequency') >= 0
        ) {
            let dataPoints = normalizeDataPoints(visualSpec.data_points);
            if (dataPoints.length < 2) {
                dataPoints = buildCumulativeDataPointsFromRows(visualSpec);
            }
            return {
                kind: 'cumulative_frequency_chart',
                render_required: true,
                data_points: dataPoints,
                title: visualSpec.title || '',
                x_label: visualSpec.x_label || '',
                y_label: visualSpec.y_label || ''
            };
        }
        return visualSpec;
    }

    function isChartSpec(visualSpec) {
        return getVisualKind(visualSpec) === 'cumulative_frequency_chart';
    }

    function chartSpecIsRenderable(visualSpec) {
        return isChartSpec(visualSpec)
            && Array.isArray(visualSpec.data_points)
            && visualSpec.data_points.length >= 2;
    }

    function lineIsDrawable(line, points) {
        if (!line || typeof line !== 'object') {
            return false;
        }
        if (hasNumericThroughPoints(line, points)) {
            return true;
        }
        if (String(line.type || '').trim() === 'slope_intercept') {
            const slope = parseFractionLike(line.m);
            if (!Number.isFinite(slope)) {
                return false;
            }
            if (line.b !== null && line.b !== undefined) {
                const intercept = parseFractionLike(line.b);
                if (Number.isFinite(intercept)) {
                    return true;
                }
            }
            return false;
        }
        const equation = line.equation || line;
        const coefficientA = parseFractionLike(equation.A ?? equation.a);
        const coefficientB = parseFractionLike(equation.B ?? equation.b);
        const constantC = parseFractionLike(equation.C ?? equation.c ?? 0);
        return [coefficientA, coefficientB, constantC].every(Number.isFinite)
            && (coefficientA !== 0 || coefficientB !== 0);
    }

    function panelSpecIsRenderable(panelSpec) {
        const points = Array.isArray(panelSpec.points) ? panelSpec.points : [];
        const lines = []
            .concat(Array.isArray(panelSpec.lines) ? panelSpec.lines : [])
            .concat(Array.isArray(panelSpec.segments) ? panelSpec.segments : []);
        if (!lines.length) {
            return false;
        }
        return lines.some(function (line) {
            return lineIsDrawable(line, points);
        });
    }

    function isVisualSpecRenderable(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object' || Array.isArray(visualSpec)) {
            return false;
        }
        const kind = getVisualKind(visualSpec);
        if (INTENTIONALLY_BLANK_KINDS.indexOf(kind) >= 0) {
            return false;
        }
        if (visualSpec.image_base64 && !hasDrawablePrimitives(visualSpec)) {
            return false;
        }
        const normalized = normalizeVisualSpecForRendering(visualSpec);
        if (!normalized) {
            return false;
        }
        if (chartSpecIsRenderable(normalized)) {
            return true;
        }
        if (!hasRenderKind(normalized) && !hasRenderKind(visualSpec)) {
            return false;
        }
        if (!hasDrawablePrimitives(normalized) && !hasDrawablePrimitives(visualSpec)) {
            return false;
        }
        if (isMultiFigureSpec(normalized)) {
            const panels = buildMultiFigurePanels(normalized);
            return panels.length >= 6 && panels.every(function (panel) {
                return panelSpecIsRenderable(panel.spec);
            });
        }
        const points = Array.isArray(normalized.points) ? normalized.points : [];
        const lines = []
            .concat(Array.isArray(normalized.lines) ? normalized.lines : [])
            .concat(Array.isArray(normalized.segments) ? normalized.segments : [])
            .concat(
                Array.isArray(normalized.drawable_primitives)
                    ? normalized.drawable_primitives.filter(function (item) {
                        return item && item.type === 'line';
                    })
                    : []
            );
        if (!lines.length) {
            return false;
        }
        return lines.some(function (line) {
            return lineIsDrawable(line, points);
        });
    }

    function requiresVisualRendering(visualSpec) {
        return isVisualSpecRenderable(visualSpec);
    }

    function normalizeOptions(options) {
        const opts = options && typeof options === 'object' ? options : {};
        return {
            width: Number(opts.width),
            height: Number(opts.height),
            padding: Number.isFinite(opts.padding) ? opts.padding : 20,
            manageCanvasSize: opts.manageCanvasSize !== false,
            backgroundFill: opts.backgroundFill !== undefined ? opts.backgroundFill : '#ffffff',
            visualOpacity: Number.isFinite(opts.visualOpacity) ? opts.visualOpacity : 0.62,
            devicePixelRatio: Number(
                opts.devicePixelRatio
                || (typeof globalThis !== 'undefined' && globalThis.devicePixelRatio)
                || 1
            )
        };
    }

    function resolveCanvasSize(canvas, options) {
        const opts = normalizeOptions(options);
        const cssWidth = Math.max(
            1,
            Number.isFinite(opts.width) && opts.width > 0
                ? opts.width
                : Number(canvas.clientWidth || canvas.width || 640)
        );
        const cssHeight = Math.max(
            1,
            Number.isFinite(opts.height) && opts.height > 0
                ? opts.height
                : Number(canvas.clientHeight || canvas.height || 360)
        );
        return { cssWidth: cssWidth, cssHeight: cssHeight, opts: opts };
    }

    function applyFadedColor(color, opacity) {
        if (opacity >= 1) {
            return color;
        }
        const match = String(color).match(/^#([0-9a-f]{6})$/i);
        if (!match) {
            return color;
        }
        const hex = match[1];
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        return 'rgba(' + r + ',' + g + ',' + b + ',' + opacity + ')';
    }

    function drawLineSegment(context, mapX, mapY, x1, y1, x2, y2) {
        if (![x1, y1, x2, y2].every(Number.isFinite)) {
            return;
        }
        context.beginPath();
        context.moveTo(mapX(x1), mapY(y1));
        context.lineTo(mapX(x2), mapY(y2));
        context.stroke();
    }

    function renderCoordinatePlaneInRect(context, visualSpec, destRect, options) {
        const opts = normalizeOptions(options);
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

        const width = Math.max(1, destRect.width);
        const height = Math.max(1, destRect.height);
        const labelHeight = destRect.showLabel === false ? 0 : 16;
        const padding = Math.max(8, Math.min(opts.padding, Math.min(width, height) * 0.16));
        const plotTop = destRect.y + labelHeight;
        const plotHeight = Math.max(1, height - labelHeight);
        const plotWidth = Math.max(1, width - padding * 2);
        const innerPlotHeight = Math.max(1, plotHeight - padding * 2);
        const opacity = opts.visualOpacity;
        const mapX = function (value) {
            return destRect.x + padding + (Number(value) - xMin) / (xMax - xMin) * plotWidth;
        };
        const mapY = function (value) {
            return plotTop + plotHeight - padding - (Number(value) - yMin) / (yMax - yMin) * innerPlotHeight;
        };

        if (destRect.label) {
            context.fillStyle = applyFadedColor('#374151', Math.min(1, opacity + 0.2));
            context.font = '600 12px sans-serif';
            context.textAlign = 'center';
            context.textBaseline = 'top';
            context.fillText(destRect.label, destRect.x + width / 2, destRect.y + 2);
        }

        context.strokeStyle = applyFadedColor('#e5e7eb', Math.min(1, opacity + 0.15));
        context.lineWidth = 1;
        for (let value = Math.ceil(xMin); value <= Math.floor(xMax); value += 1) {
            context.beginPath();
            context.moveTo(mapX(value), plotTop + padding);
            context.lineTo(mapX(value), plotTop + plotHeight - padding);
            context.stroke();
        }
        for (let value = Math.ceil(yMin); value <= Math.floor(yMax); value += 1) {
            context.beginPath();
            context.moveTo(destRect.x + padding, mapY(value));
            context.lineTo(destRect.x + width - padding, mapY(value));
            context.stroke();
        }

        context.strokeStyle = applyFadedColor('#374151', opacity);
        context.lineWidth = 1.5;
        if (xMin <= 0 && xMax >= 0) {
            context.beginPath();
            context.moveTo(mapX(0), plotTop + padding);
            context.lineTo(mapX(0), plotTop + plotHeight - padding);
            context.stroke();
        }
        if (yMin <= 0 && yMax >= 0) {
            context.beginPath();
            context.moveTo(destRect.x + padding, mapY(0));
            context.lineTo(destRect.x + width - padding, mapY(0));
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
        const points = Array.isArray(visualSpec.points) ? visualSpec.points : [];
        const lineColors = ['#1565c0', '#c2410c'];
        lines.forEach(function (line, lineIndex) {
            context.strokeStyle = applyFadedColor(lineColors[lineIndex % lineColors.length], opacity);
            context.lineWidth = 2.2;
            if (hasNumericThroughPoints(line, points)) {
                const p1 = resolvePointReference(line.through_points[0], points);
                const p2 = resolvePointReference(line.through_points[1], points);
                if (p1 && p2) {
                    drawLineSegment(context, mapX, mapY, p1.x, p1.y, p2.x, p2.y);
                    return;
                }
                const raw1 = line.through_points[0];
                const raw2 = line.through_points[1];
                drawLineSegment(
                    context,
                    mapX,
                    mapY,
                    Number(Array.isArray(raw1) ? raw1[0] : raw1.x),
                    Number(Array.isArray(raw1) ? raw1[1] : raw1.y),
                    Number(Array.isArray(raw2) ? raw2[0] : raw2.x),
                    Number(Array.isArray(raw2) ? raw2[1] : raw2.y)
                );
                return;
            }
            if (String(line.type || '').trim() === 'slope_intercept') {
                const slope = parseFractionLike(line.m);
                const intercept = line.b === null || line.b === undefined
                    ? NaN
                    : parseFractionLike(line.b);
                if (Number.isFinite(slope) && Number.isFinite(intercept)) {
                    drawLineSegment(
                        context,
                        mapX,
                        mapY,
                        xMin,
                        slope * xMin + intercept,
                        xMax,
                        slope * xMax + intercept
                    );
                }
                return;
            }
            const equation = line.equation || line;
            const coefficientA = parseFractionLike(equation.A ?? equation.a);
            const coefficientB = parseFractionLike(equation.B ?? equation.b);
            const constantC = parseFractionLike(equation.C ?? equation.c ?? 0);
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

        context.fillStyle = applyFadedColor('#dc2626', opacity);
        points.forEach(function (point) {
            const xValue = Number(Array.isArray(point) ? point[0] : point.x);
            const yValue = Number(Array.isArray(point) ? point[1] : point.y);
            if (!Number.isFinite(xValue) || !Number.isFinite(yValue)) {
                return;
            }
            context.beginPath();
            context.arc(mapX(xValue), mapY(yValue), 3.5, 0, Math.PI * 2);
            context.fill();
        });
        return true;
    }

    function renderCoordinatePlane(context, visualSpec, width, height, options) {
        return renderCoordinatePlaneInRect(context, visualSpec, {
            x: 0,
            y: 0,
            width: width,
            height: height,
            showLabel: false
        }, options);
    }

    function renderMultiFigureGrid(context, visualSpec, width, height, options) {
        const panels = buildMultiFigurePanels(visualSpec);
        if (!panels.length) {
            return false;
        }
        const grid = computeMultiFigureGrid(panels.length, width, height, options && options.padding);
        panels.forEach(function (panel, index) {
            const cell = grid.cells[index];
            if (!cell) {
                return;
            }
            renderCoordinatePlaneInRect(context, panel.spec, {
                x: cell.x,
                y: cell.y,
                width: cell.width,
                height: cell.height,
                label: panel.label,
                showLabel: true
            }, Object.assign({}, options, { padding: 12 }));
        });
        return true;
    }

    function renderCumulativeFrequencyChart(context, visualSpec, width, height, options) {
        const opts = normalizeOptions(options);
        const dataPoints = normalizeDataPoints(visualSpec.data_points);
        if (dataPoints.length < 2) {
            return false;
        }
        const cssWidth = Math.max(1, Number(width) || 1);
        const cssHeight = Math.max(1, Number(height) || 1);
        const padding = Math.max(12, Math.min(opts.padding, Math.min(cssWidth, cssHeight) * 0.16));
        const plotLeft = padding;
        const plotTop = padding + 12;
        const plotWidth = Math.max(1, cssWidth - padding * 2);
        const plotHeight = Math.max(1, cssHeight - padding * 2 - 12);
        const xValues = dataPoints.map(function (point) { return point.x; });
        const yValues = dataPoints.map(function (point) { return point.y; });
        const xRange = computeNumericRange(xValues, 0, 10, 0.08);
        const yRange = computeNumericRange(yValues, 0, 10, 0.08);
        const opacity = opts.visualOpacity;
        const mapX = function (value) {
            return plotLeft + (Number(value) - xRange[0]) / (xRange[1] - xRange[0]) * plotWidth;
        };
        const mapY = function (value) {
            return plotTop + plotHeight - (Number(value) - yRange[0]) / (yRange[1] - yRange[0]) * plotHeight;
        };

        context.strokeStyle = applyFadedColor('#e5e7eb', Math.min(1, opacity + 0.15));
        context.lineWidth = 1;
        for (let tick = Math.ceil(xRange[0]); tick <= Math.floor(xRange[1]); tick += 1) {
            context.beginPath();
            context.moveTo(mapX(tick), plotTop);
            context.lineTo(mapX(tick), plotTop + plotHeight);
            context.stroke();
        }
        for (let tick = Math.ceil(yRange[0]); tick <= Math.floor(yRange[1]); tick += 1) {
            context.beginPath();
            context.moveTo(plotLeft, mapY(tick));
            context.lineTo(plotLeft + plotWidth, mapY(tick));
            context.stroke();
        }

        context.strokeStyle = applyFadedColor('#374151', opacity);
        context.lineWidth = 1.5;
        context.beginPath();
        context.moveTo(mapX(xRange[0]), mapY(yRange[0]));
        context.lineTo(mapX(xRange[0]), mapY(yRange[1]));
        context.lineTo(mapX(xRange[1]), mapY(yRange[1]));
        context.stroke();

        context.strokeStyle = applyFadedColor('#1565c0', opacity);
        context.lineWidth = 2.4;
        context.beginPath();
        dataPoints.forEach(function (point, index) {
            const xPos = mapX(point.x);
            const yPos = mapY(point.y);
            if (index === 0) {
                context.moveTo(xPos, yPos);
            } else {
                context.lineTo(xPos, yPos);
            }
        });
        context.stroke();

        context.fillStyle = applyFadedColor('#dc2626', opacity);
        dataPoints.forEach(function (point) {
            context.beginPath();
            context.arc(mapX(point.x), mapY(point.y), 3.5, 0, Math.PI * 2);
            context.fill();
        });
        return true;
    }

    function renderToContext(context, visualSpec, width, height, options) {
        if (!context || !isVisualSpecRenderable(visualSpec)) {
            return false;
        }
        const normalized = normalizeVisualSpecForRendering(visualSpec);
        const opts = normalizeOptions(options);
        const cssWidth = Math.max(1, Number(width) || 1);
        const cssHeight = Math.max(1, Number(height) || 1);
        context.setTransform(1, 0, 0, 1, 0, 0);
        context.clearRect(0, 0, cssWidth, cssHeight);
        if (opts.backgroundFill) {
            context.fillStyle = opts.backgroundFill;
            context.fillRect(0, 0, cssWidth, cssHeight);
        }
        if (isChartSpec(normalized)) {
            return renderCumulativeFrequencyChart(context, normalized, cssWidth, cssHeight, opts);
        }
        if (isMultiFigureSpec(normalized)) {
            return renderMultiFigureGrid(context, normalized, cssWidth, cssHeight, opts);
        }
        return renderCoordinatePlane(context, normalized, cssWidth, cssHeight, opts);
    }

    function renderToCanvas(canvas, visualSpec, options) {
        if (!canvas || !isVisualSpecRenderable(visualSpec)) {
            return false;
        }
        const context = canvas.getContext && canvas.getContext('2d');
        if (!context) {
            return false;
        }
        const resolved = resolveCanvasSize(canvas, options);
        const opts = resolved.opts;
        if (opts.manageCanvasSize) {
            canvas.width = Math.round(resolved.cssWidth * opts.devicePixelRatio);
            canvas.height = Math.round(resolved.cssHeight * opts.devicePixelRatio);
            context.setTransform(opts.devicePixelRatio, 0, 0, opts.devicePixelRatio, 0, 0);
        }
        return renderToContext(context, visualSpec, resolved.cssWidth, resolved.cssHeight, opts);
    }

    function computeContainRect(naturalWidth, naturalHeight, containerWidth, containerHeight, padding) {
        const pad = Number.isFinite(padding) ? padding : 20;
        const innerWidth = Math.max(1, containerWidth - pad * 2);
        const innerHeight = Math.max(1, containerHeight - pad * 2);
        const nw = Math.max(1, Number(naturalWidth) || 1);
        const nh = Math.max(1, Number(naturalHeight) || 1);
        const scale = Math.min(innerWidth / nw, innerHeight / nh);
        const drawWidth = nw * scale;
        const drawHeight = nh * scale;
        return {
            x: (containerWidth - drawWidth) / 2,
            y: (containerHeight - drawHeight) / 2,
            width: drawWidth,
            height: drawHeight,
            scale: scale
        };
    }

    return {
        hasDrawablePrimitives: hasDrawablePrimitives,
        getVisualKind: getVisualKind,
        normalizeVisualSpecForRendering: normalizeVisualSpecForRendering,
        isVisualSpecRenderable: isVisualSpecRenderable,
        requiresVisualRendering: requiresVisualRendering,
        isMultiFigureSpec: isMultiFigureSpec,
        buildMultiFigurePanels: buildMultiFigurePanels,
        computeMultiFigureGrid: computeMultiFigureGrid,
        renderToContext: renderToContext,
        renderToCanvas: renderToCanvas,
        computeContainRect: computeContainRect
    };
}));
