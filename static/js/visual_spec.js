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

    function fitPanelAxisRange(points, fallbackX, fallbackY) {
        const fbX = Array.isArray(fallbackX) && fallbackX.length >= 2 ? fallbackX : [-5, 5];
        const fbY = Array.isArray(fallbackY) && fallbackY.length >= 2 ? fallbackY : [-5, 5];
        if (!Array.isArray(points) || !points.length) {
            return { x_range: fbX, y_range: fbY };
        }
        let xMin = Math.min.apply(null, points.map(function (point) { return point.x; }));
        let xMax = Math.max.apply(null, points.map(function (point) { return point.x; }));
        let yMin = Math.min.apply(null, points.map(function (point) { return point.y; }));
        let yMax = Math.max.apply(null, points.map(function (point) { return point.y; }));
        if (xMin === xMax) {
            xMin -= 1;
            xMax += 1;
        }
        if (yMin === yMax) {
            yMin -= 1;
            yMax += 1;
        }
        xMin = Math.min(xMin, 0);
        xMax = Math.max(xMax, 0);
        yMin = Math.min(yMin, 0);
        yMax = Math.max(yMax, 0);
        const padX = Math.max(1.6, (xMax - xMin) * 0.55);
        const padY = Math.max(1.6, (yMax - yMin) * 0.55);
        return {
            x_range: [xMin - padX, xMax + padX],
            y_range: [yMin - padY, yMax + padY]
        };
    }

    function collectFitPoints(points, lines) {
        const fitPoints = (points || []).slice();
        (lines || []).forEach(function (line) {
            (line.through_points || []).forEach(function (pt) {
                const normalized = normalizePointEntry(pt);
                if (normalized && Number.isFinite(normalized.x) && Number.isFinite(normalized.y)) {
                    fitPoints.push(normalized);
                }
            });
        });
        return fitPoints;
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
                const fallback = (Array.isArray(pt) || (pt && pt.label)) ? (pt && pt.label) || '' : String.fromCharCode(65 + ptIndex);
                const normalized = normalizePointEntry(pt, fallback);
                if (normalized && Number.isFinite(normalized.x) && Number.isFinite(normalized.y)) {
                    points.push(normalized);
                }
            });
            const lines = [];
            const rawLines = Array.isArray(fig.lines) ? fig.lines : [];
            if (rawLines.length) {
                rawLines.forEach(function (line) {
                    if (!line || typeof line !== 'object') {
                        return;
                    }
                    lines.push({
                        through_points: line.through_points,
                        extend: line.extend !== false,
                        label: String(line.label || '')
                    });
                });
            } else {
                const endpoints = points.filter(function (point) {
                    return point.label !== 'O';
                });
                if (endpoints.length >= 2) {
                    lines.push({
                        through_points: [
                            [endpoints[0].x, endpoints[0].y],
                            [endpoints[1].x, endpoints[1].y]
                        ],
                        extend: true,
                        label: ''
                    });
                }
            }
            const fitted = fitPanelAxisRange(collectFitPoints(points, lines), xRange, yRange);
            panels.push({
                id: String(fig.id || ('fig' + (index + 1))),
                label: String(fig.label || fig.id || ('圖' + (index + 1))),
                spec: {
                    kind: 'coordinate_plane',
                    scale_mode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
                    points: points,
                    lines: lines,
                    right_angle_marks: Array.isArray(fig.right_angle_marks) ? fig.right_angle_marks : [],
                    hide_unlabeled_points: true,
                    x_range: fitted.x_range,
                    y_range: fitted.y_range
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
                        extend: true,
                        label: key
                    });
                }
            });
            if (!points.some(function (point) { return point.label === 'O'; })) {
                points.push({ x: 0, y: 0, label: 'O' });
            }
            const fitted = fitPanelAxisRange(points, xRange, yRange);
            panels.push({
                id: String(cmp.id || ('cmp' + (index + 1))),
                label: String(cmp.label || cmp.id || ('圖' + (index + 1))),
                spec: {
                    kind: 'coordinate_plane',
                    scale_mode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
                    points: points,
                    lines: lines,
                    hide_unlabeled_points: true,
                    x_range: fitted.x_range,
                    y_range: fitted.y_range
                }
            });
        });

        return panels;
    }

    function computeMultiFigureGrid(panelCount, width, height, padding) {
        const outerPad = Math.max(4, Math.min(Number.isFinite(padding) ? padding : 16, width * 0.06, height * 0.06));
        const gap = width >= 360 ? 8 : (width >= 180 ? 5 : 3);
        if (panelCount === 4 && width >= 360) {
            const cols = 2;
            const rows = 2;
            const innerWidth = Math.max(1, width - outerPad * 2 - gap);
            const innerHeight = Math.max(1, height - outerPad * 2 - gap);
            const cellWidth = innerWidth / cols;
            const cellHeight = innerHeight / rows;
            const cells = [];
            for (let index = 0; index < 4; index += 1) {
                const row = Math.floor(index / cols);
                const col = index % cols;
                cells.push({
                    x: outerPad + col * (cellWidth + gap),
                    y: outerPad + row * (cellHeight + gap),
                    width: cellWidth,
                    height: cellHeight
                });
            }
            return { cols: cols, rows: rows, gap: gap, cells: cells, outerPad: outerPad };
        }
        if (panelCount === 2 && width >= 280) {
            const cols = 2;
            const rows = 1;
            const innerWidth = Math.max(1, width - outerPad * 2 - gap);
            const innerHeight = Math.max(1, height - outerPad * 2);
            const cellWidth = innerWidth / cols;
            const cells = [];
            for (let index = 0; index < 2; index += 1) {
                cells.push({
                    x: outerPad + index * (cellWidth + gap),
                    y: outerPad,
                    width: cellWidth,
                    height: innerHeight
                });
            }
            return { cols: cols, rows: rows, gap: gap, cells: cells, outerPad: outerPad };
        }
        if (panelCount === 6 && width >= 720) {
            const cols = 3;
            const rows = 2;
            const innerWidth = Math.max(1, width - outerPad * 2 - gap * (cols - 1));
            const innerHeight = Math.max(1, height - outerPad * 2 - gap);
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
            return { cols: cols, rows: rows, gap: gap, cells: cells, outerPad: outerPad };
        }
        if (panelCount === 6 && width >= 160) {
            const cols = 2;
            const rows = 3;
            const innerWidth = Math.max(1, width - outerPad * 2 - gap);
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
            return { cols: cols, rows: rows, gap: gap, cells: cells, outerPad: outerPad };
        }
        let cols;
        if (width >= 360) {
            cols = 3;
        } else if (width >= 160) {
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
        return { cols: cols, rows: rows, gap: gap, cells: cells, outerPad: outerPad };
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

    const SCALE_MODE = {
        CARTESIAN_EQUAL_UNITS: 'cartesian_equal_units',
        CHART_INDEPENDENT_AXES: 'chart_independent_axes',
        IMAGE_CONTAIN: 'image_contain'
    };

    const CARTESIAN_EQUAL_KINDS = [
        'coordinate_plane',
        'coordinate_plane_spec',
        'coordinate_plane_multi_figure',
        'coordinate_line_graph',
        'function_graph',
        'linear_application_graph',
        'collinear_points'
    ];

    const CHART_INDEPENDENT_KINDS = [
        'cumulative_frequency_chart',
        'cumulative_frequency_polygon',
        'cumulative_frequency_graph',
        'histogram',
        'frequency_polygon',
        'statistical_chart',
        'line_chart'
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

    function normalizeExplicitScaleMode(value) {
        const mode = String(value || '').trim();
        if (mode === SCALE_MODE.CARTESIAN_EQUAL_UNITS
            || mode === SCALE_MODE.CHART_INDEPENDENT_AXES
            || mode === SCALE_MODE.IMAGE_CONTAIN) {
            return mode;
        }
        return '';
    }

    function resolveTieredLinearScaleMode(visualSpec) {
        const explicit = normalizeExplicitScaleMode(visualSpec.scale_mode);
        if (explicit) {
            return explicit;
        }
        const axisSemantics = visualSpec.axis_semantics || visualSpec.axisSemantics || {};
        const explicitSemantic = normalizeExplicitScaleMode(axisSemantics.scale_mode);
        if (explicitSemantic) {
            return explicitSemantic;
        }
        if (axisSemantics.equal_units === true || axisSemantics.same_coordinate_plane === true) {
            return SCALE_MODE.CARTESIAN_EQUAL_UNITS;
        }
        if (axisSemantics.equal_units === false || axisSemantics.independent_axes === true) {
            return SCALE_MODE.CHART_INDEPENDENT_AXES;
        }
        const labels = visualSpec.labels || {};
        const xAxis = String(labels.x_axis || labels.xAxis || axisSemantics.x_unit || '').trim();
        const yAxis = String(labels.y_axis || labels.yAxis || axisSemantics.y_unit || '').trim();
        const xSem = String(visualSpec.x_axis_semantics || axisSemantics.x || axisSemantics.x_axis || '').trim();
        const ySem = String(visualSpec.y_axis_semantics || axisSemantics.y || axisSemantics.y_axis || '').trim();
        if ((xAxis && yAxis && xAxis !== yAxis) || (xSem && ySem && xSem !== ySem)) {
            return SCALE_MODE.CHART_INDEPENDENT_AXES;
        }
        if (xAxis || yAxis || xSem || ySem) {
            return SCALE_MODE.CHART_INDEPENDENT_AXES;
        }
        return SCALE_MODE.CARTESIAN_EQUAL_UNITS;
    }

    function resolveScaleMode(visualSpec) {
        if (!visualSpec || typeof visualSpec !== 'object') {
            return null;
        }
        const explicit = normalizeExplicitScaleMode(visualSpec.scale_mode);
        if (explicit) {
            return explicit;
        }
        if (visualSpec.image_base64 && !hasDrawablePrimitives(visualSpec)) {
            return SCALE_MODE.IMAGE_CONTAIN;
        }
        const kind = getVisualKind(visualSpec);
        if (kind === 'tiered_linear_graph') {
            return resolveTieredLinearScaleMode(visualSpec);
        }
        if (CHART_INDEPENDENT_KINDS.indexOf(kind) >= 0 || kind.indexOf('cumulative_frequency') >= 0) {
            return SCALE_MODE.CHART_INDEPENDENT_AXES;
        }
        if (CARTESIAN_EQUAL_KINDS.indexOf(kind) >= 0 || kind.indexOf('coordinate_plane') >= 0) {
            return SCALE_MODE.CARTESIAN_EQUAL_UNITS;
        }
        if (isMultiFigureSpec(visualSpec)) {
            return SCALE_MODE.CARTESIAN_EQUAL_UNITS;
        }
        return null;
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
                scale_mode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
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
            const scaleMode = resolveTieredLinearScaleMode(visualSpec);
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
                kind: 'line_chart',
                render_required: true,
                scale_mode: scaleMode,
                points: breakpoints,
                lines: lines,
                labels: visualSpec.labels || {},
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
                scale_mode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
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
                scale_mode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
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
                scale_mode: SCALE_MODE.CHART_INDEPENDENT_AXES,
                data_points: dataPoints,
                title: visualSpec.title || '',
                x_label: visualSpec.x_label || '',
                y_label: visualSpec.y_label || '',
                x_axis_semantics: visualSpec.x_axis_semantics || '',
                y_axis_semantics: visualSpec.y_axis_semantics || ''
            };
        }
        const resolvedMode = resolveScaleMode(visualSpec);
        if (resolvedMode && !visualSpec.scale_mode) {
            return Object.assign({}, visualSpec, { scale_mode: resolvedMode });
        }
        return visualSpec;
    }

    function isLineChartSpec(visualSpec) {
        const kind = getVisualKind(visualSpec);
        return kind === 'line_chart'
            || kind === 'cumulative_frequency_chart'
            || (Array.isArray(visualSpec.data_points) && visualSpec.data_points.length >= 2);
    }

    function isChartSpec(visualSpec) {
        return isLineChartSpec(visualSpec)
            && resolveScaleMode(visualSpec) === SCALE_MODE.CHART_INDEPENDENT_AXES;
    }

    function chartSpecIsRenderable(visualSpec) {
        if (isLineChartSpec(visualSpec)) {
            const dataPoints = normalizeDataPoints(visualSpec.data_points);
            if (dataPoints.length >= 2) {
                return true;
            }
            if (buildCumulativeDataPointsFromRows(visualSpec).length >= 2) {
                return true;
            }
        }
        const points = Array.isArray(visualSpec.points) ? visualSpec.points : [];
        const lines = Array.isArray(visualSpec.lines) ? visualSpec.lines : [];
        return points.length >= 2 || lines.some(function (line) {
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
        const scaleMode = normalized.scale_mode || resolveScaleMode(normalized);
        if (scaleMode === SCALE_MODE.CHART_INDEPENDENT_AXES && chartSpecIsRenderable(normalized)) {
            return true;
        }
        if (scaleMode === SCALE_MODE.CARTESIAN_EQUAL_UNITS && isMultiFigureSpec(normalized)) {
            const panels = buildMultiFigurePanels(normalized);
            return panels.length >= 6 && panels.every(function (panel) {
                return panelSpecIsRenderable(panel.spec);
            });
        }
        if (!hasRenderKind(normalized) && !hasRenderKind(visualSpec)) {
            return false;
        }
        if (!hasDrawablePrimitives(normalized) && !hasDrawablePrimitives(visualSpec)) {
            if (!chartSpecIsRenderable(normalized)) {
                return false;
            }
        }
        if (isMultiFigureSpec(normalized)) {
            const panels = buildMultiFigurePanels(normalized);
            return panels.length >= 6 && panels.every(function (panel) {
                return panelSpecIsRenderable(panel.spec);
            });
        }
        if (isLineChartSpec(normalized) && chartSpecIsRenderable(normalized)) {
            return true;
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
            visualOpacity: Number.isFinite(opts.visualOpacity) ? opts.visualOpacity : 0.88,
            layoutRegion: opts.layoutRegion || null,
            devicePixelRatio: Number(
                opts.devicePixelRatio
                || (typeof globalThis !== 'undefined' && globalThis.devicePixelRatio)
                || 1
            )
        };
    }

    let lastRenderBounds = null;
    let lastRenderMeta = null;

    function setLastRenderBounds(bounds) {
        lastRenderBounds = bounds || null;
    }

    function getLastRenderBounds() {
        return lastRenderBounds;
    }

    function setLastRenderMeta(meta) {
        lastRenderMeta = meta || null;
    }

    function getLastRenderMeta() {
        return lastRenderMeta;
    }

    function mergeRenderBounds(existing, next) {
        if (!next) {
            return existing;
        }
        if (!existing) {
            return next;
        }
        const minX = Math.min(existing.minX, next.minX);
        const minY = Math.min(existing.minY, next.minY);
        const maxX = Math.max(existing.maxX, next.maxX);
        const maxY = Math.max(existing.maxY, next.maxY);
        return {
            minX: minX,
            minY: minY,
            maxX: maxX,
            maxY: maxY,
            width: maxX - minX + 1,
            height: maxY - minY + 1
        };
    }

    function trackRenderBounds(next) {
        lastRenderBounds = mergeRenderBounds(lastRenderBounds, next);
        return next;
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

    function clipPixelLine(x1, y1, x2, y2, box) {
        if (!box) {
            return { x1: x1, y1: y1, x2: x2, y2: y2 };
        }
        const minX = box.minX;
        const minY = box.minY;
        const maxX = box.maxX;
        const maxY = box.maxY;
        function outCode(x, y) {
            let code = 0;
            if (x < minX) code |= 1;
            if (x > maxX) code |= 2;
            if (y < minY) code |= 4;
            if (y > maxY) code |= 8;
            return code;
        }
        let c1 = outCode(x1, y1);
        let c2 = outCode(x2, y2);
        for (let step = 0; step < 8; step += 1) {
            if (!(c1 | c2)) {
                return { x1: x1, y1: y1, x2: x2, y2: y2 };
            }
            if (c1 & c2) {
                return null;
            }
            const code = c1 || c2;
            let x = x1;
            let y = y1;
            if (c2 - c1 === 0 && x2 === x1 && y2 === y1) {
                return null;
            }
            if (code & 8) {
                x = x1 + (x2 - x1) * (maxY - y1) / ((y2 - y1) || 1e-9);
                y = maxY;
            } else if (code & 4) {
                x = x1 + (x2 - x1) * (minY - y1) / ((y2 - y1) || 1e-9);
                y = minY;
            } else if (code & 2) {
                y = y1 + (y2 - y1) * (maxX - x1) / ((x2 - x1) || 1e-9);
                x = maxX;
            } else {
                y = y1 + (y2 - y1) * (minX - x1) / ((x2 - x1) || 1e-9);
                x = minX;
            }
            if (code === c1) {
                x1 = x;
                y1 = y;
                c1 = outCode(x1, y1);
            } else {
                x2 = x;
                y2 = y;
                c2 = outCode(x2, y2);
            }
        }
        return null;
    }

    function drawLineSegment(context, mapX, mapY, x1, y1, x2, y2, clipBox) {
        if (![x1, y1, x2, y2].every(Number.isFinite)) {
            return;
        }
        const clipped = clipPixelLine(mapX(x1), mapY(y1), mapX(x2), mapY(y2), clipBox);
        if (!clipped) {
            return;
        }
        context.beginPath();
        context.moveTo(clipped.x1, clipped.y1);
        context.lineTo(clipped.x2, clipped.y2);
        context.stroke();
    }

    function extendLineToBounds(p1, p2, xMin, xMax, yMin, yMax) {
        if (!p1 || !p2) {
            return null;
        }
        if (Math.abs(p1.x - p2.x) < 1e-9) {
            return { x1: p1.x, y1: yMin, x2: p1.x, y2: yMax };
        }
        if (Math.abs(p1.y - p2.y) < 1e-9) {
            return { x1: xMin, y1: p1.y, x2: xMax, y2: p1.y };
        }
        const slope = (p2.y - p1.y) / (p2.x - p1.x);
        const intercept = p1.y - slope * p1.x;
        return {
            x1: xMin,
            y1: slope * xMin + intercept,
            x2: xMax,
            y2: slope * xMax + intercept
        };
    }

    function drawRightAngleMark(context, mapX, mapY, mark, opacity) {
        if (!mark) {
            return;
        }
        const at = mark.at || mark;
        const ax = Number(Array.isArray(at) ? at[0] : at.x);
        const ay = Number(Array.isArray(at) ? at[1] : at.y);
        if (!Number.isFinite(ax) || !Number.isFinite(ay)) {
            return;
        }
        const size = Number.isFinite(Number(mark.size)) ? Number(mark.size) : 0.45;
        const axes = String(mark.axes || mark.orientation || '').toLowerCase();
        let dx = size;
        let dy = size;
        if (axes === 'y' || axes === 'horizontal') {
            dx = size;
            dy = ay >= 0 ? -size : size;
        } else {
            dx = ax >= 0 ? -size : size;
            dy = size;
        }
        context.strokeStyle = applyFadedColor('#374151', Math.min(1, opacity + 0.2));
        context.lineWidth = 1.4;
        context.beginPath();
        context.moveTo(mapX(ax + dx), mapY(ay));
        context.lineTo(mapX(ax + dx), mapY(ay + dy));
        context.lineTo(mapX(ax), mapY(ay + dy));
        context.stroke();
    }

    function drawLineLabel(context, mapX, mapY, x1, y1, x2, y2, label, color, opacity) {
        if (!label) {
            return;
        }
        const t = 0.78;
        const x = x1 + (x2 - x1) * t;
        const y = y1 + (y2 - y1) * t;
        context.fillStyle = applyFadedColor(color || '#1565c0', Math.min(1, opacity + 0.25));
        context.font = '600 11px sans-serif';
        context.textAlign = 'left';
        context.textBaseline = 'bottom';
        context.fillText(label, mapX(x) + 4, mapY(y) - 2);
    }

    function buildEqualScalePlotMapper(destRect, xMin, xMax, yMin, yMax, options) {
        const opts = normalizeOptions(options);
        const width = Math.max(1, destRect.width);
        const height = Math.max(1, destRect.height);
        const labelHeight = destRect.showLabel === false ? 0 : (width < 180 ? 12 : 14);
        const padding = Math.max(6, Math.min(opts.padding, Math.min(width, height) * 0.12));
        const plotTop = destRect.y + labelHeight;
        const plotHeight = Math.max(1, height - labelHeight);
        const innerWidth = Math.max(1, width - padding * 2);
        const innerHeight = Math.max(1, plotHeight - padding * 2);
        const xSpan = Math.max(1e-6, xMax - xMin);
        const ySpan = Math.max(1e-6, yMax - yMin);
        const scaleX = innerWidth / xSpan;
        const scaleY = innerHeight / ySpan;
        const unitScale = Math.min(scaleX, scaleY);
        const usedWidth = xSpan * unitScale;
        const usedHeight = ySpan * unitScale;
        const plotLeft = destRect.x + padding + (innerWidth - usedWidth) / 2;
        const plotBottom = plotTop + plotHeight - padding - (innerHeight - usedHeight) / 2;
        return {
            scaleMode: SCALE_MODE.CARTESIAN_EQUAL_UNITS,
            labelHeight: labelHeight,
            padding: padding,
            plotTop: plotTop,
            plotHeight: plotHeight,
            plotLeft: plotLeft,
            plotBottom: plotBottom,
            unitScale: unitScale,
            unitScaleX: unitScale,
            unitScaleY: unitScale,
            usedWidth: usedWidth,
            usedHeight: usedHeight,
            mapX: function (value) {
                return plotLeft + (Number(value) - xMin) * unitScale;
            },
            mapY: function (value) {
                return plotBottom - (Number(value) - yMin) * unitScale;
            }
        };
    }

    function buildIndependentAxesPlotMapper(destRect, xMin, xMax, yMin, yMax, options) {
        const opts = normalizeOptions(options);
        const width = Math.max(1, destRect.width);
        const height = Math.max(1, destRect.height);
        const labelHeight = destRect.showLabel === false ? 0 : (width < 180 ? 12 : 14);
        const padding = Math.max(6, Math.min(opts.padding, Math.min(width, height) * 0.12));
        const plotTop = destRect.y + labelHeight;
        const plotHeight = Math.max(1, height - labelHeight);
        const innerWidth = Math.max(1, width - padding * 2);
        const innerHeight = Math.max(1, plotHeight - padding * 2);
        const xSpan = Math.max(1e-6, xMax - xMin);
        const ySpan = Math.max(1e-6, yMax - yMin);
        const unitScaleX = innerWidth / xSpan;
        const unitScaleY = innerHeight / ySpan;
        const plotLeft = destRect.x + padding;
        const plotBottom = plotTop + plotHeight - padding;
        return {
            scaleMode: SCALE_MODE.CHART_INDEPENDENT_AXES,
            labelHeight: labelHeight,
            padding: padding,
            plotTop: plotTop,
            plotHeight: plotHeight,
            plotLeft: plotLeft,
            plotBottom: plotBottom,
            unitScale: null,
            unitScaleX: unitScaleX,
            unitScaleY: unitScaleY,
            usedWidth: innerWidth,
            usedHeight: innerHeight,
            mapX: function (value) {
                return plotLeft + (Number(value) - xMin) * unitScaleX;
            },
            mapY: function (value) {
                return plotBottom - (Number(value) - yMin) * unitScaleY;
            }
        };
    }

    function buildPlotMapper(destRect, xMin, xMax, yMin, yMax, options, scaleMode) {
        if (scaleMode === SCALE_MODE.CHART_INDEPENDENT_AXES) {
            return buildIndependentAxesPlotMapper(destRect, xMin, xMax, yMin, yMax, options);
        }
        return buildEqualScalePlotMapper(destRect, xMin, xMax, yMin, yMax, options);
    }

    function recordPlotRenderMeta(plot, visualSpec) {
        setLastRenderMeta({
            scaleMode: plot.scaleMode || resolveScaleMode(visualSpec) || null,
            unitScaleX: plot.unitScaleX,
            unitScaleY: plot.unitScaleY,
            unitScale: plot.unitScale,
            equalUnits: plot.unitScaleX === plot.unitScaleY
        });
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
        const scaleMode = visualSpec.scale_mode || resolveScaleMode(visualSpec) || SCALE_MODE.CARTESIAN_EQUAL_UNITS;
        const plot = buildPlotMapper(destRect, xMin, xMax, yMin, yMax, opts, scaleMode);
        const mapX = plot.mapX;
        const mapY = plot.mapY;
        const opacity = opts.visualOpacity;
        const plotTop = plot.plotTop;
        const plotHeight = plot.plotHeight;
        const padding = plot.padding;
        const gridLeft = plot.plotLeft;
        const gridRight = plot.plotLeft + plot.usedWidth;
        const gridTop = plotTop + padding;
        const gridBottom = plot.plotBottom;

        if (destRect.label) {
            context.fillStyle = applyFadedColor('#374151', Math.min(1, opacity + 0.2));
            context.font = width < 180 ? '600 10px sans-serif' : '600 12px sans-serif';
            context.textAlign = 'center';
            context.textBaseline = 'top';
            context.fillText(destRect.label, destRect.x + width / 2, destRect.y + 1);
        }

        const clipBox = {
            minX: destRect.x + 1,
            minY: destRect.y + (destRect.label ? 13 : 1),
            maxX: destRect.x + width - 1,
            maxY: destRect.y + height - 1
        };
        const canClip = typeof context.save === 'function' && typeof context.restore === 'function';
        if (canClip) {
            context.save();
            if (typeof context.rect === 'function' && typeof context.clip === 'function') {
                context.beginPath();
                context.rect(clipBox.minX, clipBox.minY, Math.max(1, clipBox.maxX - clipBox.minX), Math.max(1, clipBox.maxY - clipBox.minY));
                context.clip();
            }
        }

        context.strokeStyle = applyFadedColor('#e5e7eb', Math.min(1, opacity + 0.15));
        context.lineWidth = 1;
        for (let value = Math.ceil(xMin); value <= Math.floor(xMax); value += 1) {
            context.beginPath();
            context.moveTo(mapX(value), gridTop);
            context.lineTo(mapX(value), gridBottom);
            context.stroke();
        }
        for (let value = Math.ceil(yMin); value <= Math.floor(yMax); value += 1) {
            context.beginPath();
            context.moveTo(gridLeft, mapY(value));
            context.lineTo(gridRight, mapY(value));
            context.stroke();
        }

        context.strokeStyle = applyFadedColor('#374151', opacity);
        context.lineWidth = 1.5;
        if (xMin <= 0 && xMax >= 0) {
            context.beginPath();
            context.moveTo(mapX(0), gridTop);
            context.lineTo(mapX(0), gridBottom);
            context.stroke();
        }
        if (yMin <= 0 && yMax >= 0) {
            context.beginPath();
            context.moveTo(gridLeft, mapY(0));
            context.lineTo(gridRight, mapY(0));
            context.stroke();
        }

        const marks = Array.isArray(visualSpec.right_angle_marks) ? visualSpec.right_angle_marks : [];
        marks.forEach(function (mark) {
            drawRightAngleMark(context, mapX, mapY, mark, opacity);
        });

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
            const color = lineColors[lineIndex % lineColors.length];
            context.strokeStyle = applyFadedColor(color, opacity);
            context.lineWidth = 2.2;
            if (hasNumericThroughPoints(line, points)) {
                const p1 = resolvePointReference(line.through_points[0], points);
                const p2 = resolvePointReference(line.through_points[1], points);
                if (p1 && p2) {
                    const extended = line.extend === false
                        ? { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y }
                        : (extendLineToBounds(p1, p2, xMin, xMax, yMin, yMax) || { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y });
                    drawLineSegment(context, mapX, mapY, extended.x1, extended.y1, extended.x2, extended.y2, clipBox);
                    drawLineLabel(context, mapX, mapY, extended.x1, extended.y1, extended.x2, extended.y2, line.label, color, opacity);
                    return;
                }
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
                        slope * xMax + intercept,
                        clipBox
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
            if (coefficientB !== 0) {
                drawLineSegment(
                    context,
                    mapX,
                    mapY,
                    xMin,
                    (-coefficientA * xMin - constantC) / coefficientB,
                    xMax,
                    (-coefficientA * xMax - constantC) / coefficientB,
                    clipBox
                );
            } else if (coefficientA !== 0) {
                const xValue = -constantC / coefficientA;
                drawLineSegment(context, mapX, mapY, xValue, yMin, xValue, yMax, clipBox);
            }
        });

        const hideUnlabeled = visualSpec.hide_unlabeled_points === true;
        points.forEach(function (point) {
            const xValue = Number(Array.isArray(point) ? point[0] : point.x);
            const yValue = Number(Array.isArray(point) ? point[1] : point.y);
            const label = String(Array.isArray(point) ? '' : (point.label || ''));
            if (!Number.isFinite(xValue) || !Number.isFinite(yValue)) {
                return;
            }
            if (hideUnlabeled && !label) {
                return;
            }
            context.fillStyle = applyFadedColor('#111827', opacity);
            context.beginPath();
            context.arc(mapX(xValue), mapY(yValue), width < 180 ? 2 : 2.5, 0, Math.PI * 2);
            context.fill();
            if (label) {
                context.font = width < 180 ? '600 10px sans-serif' : '600 12px sans-serif';
                context.textAlign = xValue >= 0 ? 'left' : 'right';
                context.textBaseline = yValue >= 0 ? 'top' : 'bottom';
                const dx = xValue >= 0 ? 5 : -5;
                const dy = yValue >= 0 ? 4 : -3;
                context.fillText(label, mapX(xValue) + dx, mapY(yValue) + dy);
            }
        });
        if (canClip) {
            context.restore();
        }
        trackRenderBounds({
            minX: plot.plotLeft,
            minY: destRect.y + (destRect.showLabel === false ? 0 : plot.labelHeight),
            maxX: plot.plotLeft + plot.usedWidth,
            maxY: plot.plotBottom,
            width: plot.usedWidth,
            height: plot.plotBottom - (destRect.y + (destRect.showLabel === false ? 0 : plot.labelHeight)) + 1
        });
        recordPlotRenderMeta(plot, visualSpec);
        return true;
    }

    function renderCoordinatePlane(context, visualSpec, width, height, options, destRect) {
        const rect = destRect || { x: 0, y: 0, width: width, height: height, showLabel: false };
        return renderCoordinatePlaneInRect(context, visualSpec, rect, options);
    }

    function renderMultiFigureGrid(context, visualSpec, width, height, options) {
        const panels = buildMultiFigurePanels(visualSpec);
        if (!panels.length) {
            return false;
        }
        const opts = normalizeOptions(options);
        const offsetX = Number.isFinite(opts.offsetX) ? opts.offsetX : 0;
        const offsetY = Number.isFinite(opts.offsetY) ? opts.offsetY : 0;
        const grid = computeMultiFigureGrid(panels.length, width, height, opts.padding);
        let bounds = null;
        panels.forEach(function (panel, index) {
            const cell = grid.cells[index];
            if (!cell) {
                return;
            }
            renderCoordinatePlaneInRect(context, panel.spec, {
                x: offsetX + cell.x,
                y: offsetY + cell.y,
                width: cell.width,
                height: cell.height,
                label: panel.label,
                showLabel: true
            }, Object.assign({}, opts, { padding: Math.max(4, Math.min(opts.padding, 8)) }));
            bounds = mergeRenderBounds(bounds, getLastRenderBounds());
        });
        trackRenderBounds(bounds);
        return true;
    }

    function renderLineChartInRect(context, visualSpec, destRect, options) {
        const opts = normalizeOptions(options);
        let dataPoints = normalizeDataPoints(visualSpec.data_points);
        if (dataPoints.length < 2) {
            dataPoints = buildCumulativeDataPointsFromRows(visualSpec);
        }
        if (dataPoints.length < 2) {
            const points = Array.isArray(visualSpec.points) ? visualSpec.points : [];
            dataPoints = points.map(function (point) {
                return {
                    x: Number(Array.isArray(point) ? point[0] : point.x),
                    y: Number(Array.isArray(point) ? point[1] : point.y)
                };
            }).filter(function (point) {
                return Number.isFinite(point.x) && Number.isFinite(point.y);
            });
        }
        if (dataPoints.length < 2) {
            return false;
        }
        const xRange = Array.isArray(visualSpec.x_range) && visualSpec.x_range.length >= 2
            ? [Number(visualSpec.x_range[0]), Number(visualSpec.x_range[1])]
            : computeNumericRange(dataPoints.map(function (point) { return point.x; }), 0, 10, 0.08);
        const yRange = Array.isArray(visualSpec.y_range) && visualSpec.y_range.length >= 2
            ? [Number(visualSpec.y_range[0]), Number(visualSpec.y_range[1])]
            : computeNumericRange(dataPoints.map(function (point) { return point.y; }), 0, 10, 0.08);
        const plot = buildIndependentAxesPlotMapper(destRect, xRange[0], xRange[1], yRange[0], yRange[1], opts);
        const mapX = plot.mapX;
        const mapY = plot.mapY;
        const opacity = opts.visualOpacity;

        context.strokeStyle = applyFadedColor('#e5e7eb', Math.min(1, opacity + 0.15));
        context.lineWidth = 1;
        for (let tick = Math.ceil(xRange[0]); tick <= Math.floor(xRange[1]); tick += 1) {
            context.beginPath();
            context.moveTo(mapX(tick), plot.plotTop + plot.padding);
            context.lineTo(mapX(tick), plot.plotBottom);
            context.stroke();
        }
        for (let tick = Math.ceil(yRange[0]); tick <= Math.floor(yRange[1]); tick += 1) {
            context.beginPath();
            context.moveTo(plot.plotLeft, mapY(tick));
            context.lineTo(plot.plotLeft + plot.usedWidth, mapY(tick));
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
        context.lineWidth = 2.2;
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

        const lines = Array.isArray(visualSpec.lines) ? visualSpec.lines : [];
        lines.forEach(function (line) {
            if (!hasNumericThroughPoints(line, dataPoints)) {
                return;
            }
            const p1 = resolvePointReference(line.through_points[0], dataPoints);
            const p2 = resolvePointReference(line.through_points[1], dataPoints);
            if (!p1 || !p2) {
                return;
            }
            context.beginPath();
            context.moveTo(mapX(p1.x), mapY(p1.y));
            context.lineTo(mapX(p2.x), mapY(p2.y));
            context.stroke();
        });

        context.fillStyle = applyFadedColor('#dc2626', opacity);
        dataPoints.forEach(function (point) {
            context.beginPath();
            context.arc(mapX(point.x), mapY(point.y), destRect.width < 180 ? 2.5 : 3.5, 0, Math.PI * 2);
            context.fill();
        });
        trackRenderBounds({
            minX: plot.plotLeft,
            minY: plot.plotTop,
            maxX: plot.plotLeft + plot.usedWidth,
            maxY: plot.plotBottom,
            width: plot.usedWidth,
            height: plot.plotBottom - plot.plotTop + 1
        });
        recordPlotRenderMeta(plot, visualSpec);
        return true;
    }

    function renderCumulativeFrequencyChartInRect(context, visualSpec, destRect, options) {
        return renderLineChartInRect(context, visualSpec, destRect, options);
    }

    function renderToContext(context, visualSpec, width, height, options) {
        if (!context || !isVisualSpecRenderable(visualSpec)) {
            return false;
        }
        const normalized = normalizeVisualSpecForRendering(visualSpec);
        const opts = normalizeOptions(options);
        const cssWidth = Math.max(1, Number(width) || 1);
        const cssHeight = Math.max(1, Number(height) || 1);
        const region = opts.layoutRegion || {
            x: 0,
            y: 0,
            width: cssWidth,
            height: cssHeight
        };
        setLastRenderBounds(null);
        setLastRenderMeta(null);
        if (!opts.layoutRegion) {
            context.setTransform(1, 0, 0, 1, 0, 0);
            context.clearRect(0, 0, cssWidth, cssHeight);
            if (opts.backgroundFill) {
                context.fillStyle = opts.backgroundFill;
                context.fillRect(0, 0, cssWidth, cssHeight);
            }
        }
        const scaleMode = normalized.scale_mode || resolveScaleMode(normalized);
        if (scaleMode === SCALE_MODE.CHART_INDEPENDENT_AXES && chartSpecIsRenderable(normalized)) {
            return renderLineChartInRect(context, normalized, region, opts);
        }
        if (isMultiFigureSpec(normalized)) {
            return renderMultiFigureGrid(
                context,
                normalized,
                region.width,
                region.height,
                Object.assign({}, opts, { offsetX: region.x, offsetY: region.y })
            );
        }
        return renderCoordinatePlaneInRect(context, normalized, {
            x: region.x,
            y: region.y,
            width: region.width,
            height: region.height,
            showLabel: false
        }, opts);
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
        SCALE_MODE: SCALE_MODE,
        hasDrawablePrimitives: hasDrawablePrimitives,
        getVisualKind: getVisualKind,
        resolveScaleMode: resolveScaleMode,
        normalizeVisualSpecForRendering: normalizeVisualSpecForRendering,
        isVisualSpecRenderable: isVisualSpecRenderable,
        requiresVisualRendering: requiresVisualRendering,
        isMultiFigureSpec: isMultiFigureSpec,
        isChartSpec: isChartSpec,
        buildMultiFigurePanels: buildMultiFigurePanels,
        computeMultiFigureGrid: computeMultiFigureGrid,
        buildEqualScalePlotMapper: buildEqualScalePlotMapper,
        buildIndependentAxesPlotMapper: buildIndependentAxesPlotMapper,
        buildPlotMapper: buildPlotMapper,
        getLastRenderBounds: getLastRenderBounds,
        getLastRenderMeta: getLastRenderMeta,
        renderToContext: renderToContext,
        renderToCanvas: renderToCanvas,
        computeContainRect: computeContainRect
    };
}));
