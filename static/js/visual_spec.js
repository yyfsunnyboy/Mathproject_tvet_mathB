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

    return {
        hasDrawablePrimitives: hasDrawablePrimitives,
        requiresVisualRendering: requiresVisualRendering
    };
}));
