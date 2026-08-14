(function (root, factory) {
    const api = factory(root);
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.ScratchpadBackgroundLayer = api;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
    'use strict';

    const REGION_EDGE_PADDING = 14;
    const REGION_WIDTH_RATIO = 0.5;
    const REGION_HEIGHT_RATIO = 0.5;
    const IMAGE_OPACITY = 0.72;

    let storedVisualSpec = null;
    let storedQuestionImage = null;
    let storedImageSource = null;
    let lastRenderBounds = null;
    let lastRenderMeta = null;

    function computeQuestionBackgroundRegion(canvasWidth, canvasHeight, edgePadding) {
        const pad = Number.isFinite(edgePadding) ? edgePadding : REGION_EDGE_PADDING;
        const cw = Math.max(1, Number(canvasWidth) || 1);
        const ch = Math.max(1, Number(canvasHeight) || 1);
        const quadrantWidth = cw * REGION_WIDTH_RATIO;
        const quadrantHeight = ch * REGION_HEIGHT_RATIO;
        return {
            x: pad,
            y: pad,
            width: Math.max(1, quadrantWidth - pad),
            height: Math.max(1, quadrantHeight - pad),
            edgePadding: pad,
            quadrantWidth: quadrantWidth,
            quadrantHeight: quadrantHeight,
            canvasWidth: cw,
            canvasHeight: ch
        };
    }

    function computeContainRect(naturalWidth, naturalHeight, regionWidth, regionHeight, innerPadding, regionOffsetX, regionOffsetY) {
        const pad = Number.isFinite(innerPadding) ? innerPadding : REGION_EDGE_PADDING;
        const baseX = Number.isFinite(regionOffsetX) ? regionOffsetX : 0;
        const baseY = Number.isFinite(regionOffsetY) ? regionOffsetY : 0;
        const innerWidth = Math.max(1, regionWidth - pad * 2);
        const innerHeight = Math.max(1, regionHeight - pad * 2);
        const nw = Math.max(1, Number(naturalWidth) || 1);
        const nh = Math.max(1, Number(naturalHeight) || 1);
        const scale = Math.min(innerWidth / nw, innerHeight / nh);
        const drawWidth = nw * scale;
        const drawHeight = nh * scale;
        return {
            x: baseX + pad + (innerWidth - drawWidth) / 2,
            y: baseY + pad + (innerHeight - drawHeight) / 2,
            width: drawWidth,
            height: drawHeight,
            scale: scale
        };
    }

    function setLastRenderBounds(bounds) {
        lastRenderBounds = bounds || null;
    }

    function getLastRenderBounds() {
        return lastRenderBounds;
    }

    function getLastRenderMeta() {
        return lastRenderMeta;
    }

    function setLastRenderMeta(meta) {
        lastRenderMeta = meta || null;
    }

    function measureBackgroundContentBounds(ctx, cssWidth, cssHeight, threshold) {
        if (!ctx || !ctx.canvas || typeof ctx.getImageData !== 'function') {
            return null;
        }
        const canvas = ctx.canvas;
        let sampleW = Math.max(1, Math.floor(cssWidth));
        let sampleH = Math.max(1, Math.floor(cssHeight));
        let sampleCtx = ctx;
        if (sampleW !== canvas.width || sampleH !== canvas.height) {
            if (typeof document !== 'undefined' && document.createElement) {
                const off = document.createElement('canvas');
                off.width = sampleW;
                off.height = sampleH;
                const offCtx = off.getContext('2d');
                if (!offCtx) {
                    return null;
                }
                offCtx.drawImage(canvas, 0, 0, sampleW, sampleH);
                sampleCtx = offCtx;
            } else {
                sampleW = canvas.width;
                sampleH = canvas.height;
            }
        }
        let imageData;
        try {
            imageData = sampleCtx.getImageData(0, 0, sampleW, sampleH);
        } catch (_err) {
            return null;
        }
        const data = imageData.data;
        const limit = Number.isFinite(threshold) ? threshold : 248;
        let minX = sampleW;
        let minY = sampleH;
        let maxX = 0;
        let maxY = 0;
        let found = false;
        for (let y = 0; y < sampleH; y += 1) {
            for (let x = 0; x < sampleW; x += 1) {
                const index = (y * sampleW + x) * 4;
                if (data[index] < limit || data[index + 1] < limit || data[index + 2] < limit) {
                    found = true;
                    minX = Math.min(minX, x);
                    minY = Math.min(minY, y);
                    maxX = Math.max(maxX, x);
                    maxY = Math.max(maxY, y);
                }
            }
        }
        if (!found) {
            return null;
        }
        return {
            minX: minX,
            minY: minY,
            maxX: maxX,
            maxY: maxY,
            width: maxX - minX + 1,
            height: maxY - minY + 1
        };
    }

    function resetQuestionBackground() {
        storedVisualSpec = null;
        storedQuestionImage = null;
        storedImageSource = null;
        lastRenderBounds = null;
        lastRenderMeta = null;
    }

    function hasQuestionBackground() {
        return Boolean(storedVisualSpec || storedQuestionImage);
    }

    function getStoredBackground() {
        return {
            visualSpec: storedVisualSpec,
            questionImage: storedQuestionImage,
            imageSource: storedImageSource,
            lastRenderBounds: lastRenderBounds,
            lastRenderMeta: lastRenderMeta
        };
    }

    function paintBackgroundBase(ctx, width, height) {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, width, height);
    }

    function drawStoredImageBackground(ctx, cssWidth, cssHeight) {
        if (!storedQuestionImage || !ctx) {
            return false;
        }
        const region = computeQuestionBackgroundRegion(cssWidth, cssHeight);
        const rect = computeContainRect(
            storedQuestionImage.naturalWidth,
            storedQuestionImage.naturalHeight,
            region.width,
            region.height,
            region.edgePadding,
            region.x,
            region.y
        );
        ctx.save();
        ctx.globalAlpha = IMAGE_OPACITY;
        ctx.drawImage(
            storedQuestionImage,
            rect.x,
            rect.y,
            rect.width,
            rect.height
        );
        ctx.restore();
        setLastRenderBounds({
            minX: rect.x,
            minY: rect.y,
            maxX: rect.x + rect.width,
            maxY: rect.y + rect.height,
            width: rect.width,
            height: rect.height
        });
        setLastRenderMeta({
            scaleMode: 'image_contain',
            equalUnits: false,
            imageScale: rect.scale
        });
        return true;
    }

    function drawStoredVisualSpecBackground(ctx, cssWidth, cssHeight, visualRuntime) {
        const runtime = visualRuntime || (root && root.VisualSpecRuntime);
        if (!storedVisualSpec || !runtime || !runtime.renderToCanvas || !ctx) {
            return false;
        }
        const region = computeQuestionBackgroundRegion(cssWidth, cssHeight);
        const ok = runtime.renderToCanvas(ctx.canvas, storedVisualSpec, {
            width: cssWidth,
            height: cssHeight,
            layoutRegion: region,
            padding: Math.min(region.edgePadding, 10),
            manageCanvasSize: false,
            backgroundFill: null,
            visualOpacity: 0.62
        });
        const measured = measureBackgroundContentBounds(ctx, cssWidth, cssHeight);
        const tracked = runtime.getLastRenderBounds && runtime.getLastRenderBounds();
        const trackedMeta = runtime.getLastRenderMeta && runtime.getLastRenderMeta();
        if (tracked) {
            setLastRenderBounds(tracked);
        } else if (measured) {
            setLastRenderBounds(measured);
        }
        if (trackedMeta) {
            setLastRenderMeta(trackedMeta);
        }
        return ok;
    }

    function redrawQuestionBackground(backgroundCtx, cssWidth, cssHeight, visualRuntime) {
        if (!backgroundCtx || !backgroundCtx.canvas) {
            return false;
        }
        const width = Math.max(1, Number(cssWidth) || backgroundCtx.canvas.clientWidth || 1);
        const height = Math.max(1, Number(cssHeight) || backgroundCtx.canvas.clientHeight || 1);
        paintBackgroundBase(backgroundCtx, width, height);
        if (storedVisualSpec) {
            return drawStoredVisualSpecBackground(backgroundCtx, width, height, visualRuntime);
        }
        if (storedQuestionImage) {
            return drawStoredImageBackground(backgroundCtx, width, height);
        }
        setLastRenderBounds(null);
        setLastRenderMeta(null);
        return false;
    }

    function clearBackgroundCanvas(backgroundCtx, cssWidth, cssHeight) {
        if (!backgroundCtx) {
            return;
        }
        const width = Math.max(1, Number(cssWidth) || backgroundCtx.canvas.clientWidth || 1);
        const height = Math.max(1, Number(cssHeight) || backgroundCtx.canvas.clientHeight || 1);
        paintBackgroundBase(backgroundCtx, width, height);
        setLastRenderBounds(null);
        setLastRenderMeta(null);
    }

    function setVisualSpecBackground(visualSpec, backgroundCtx, cssWidth, cssHeight, visualRuntime) {
        const runtime = visualRuntime || (root && root.VisualSpecRuntime);
        if (!runtime || !runtime.isVisualSpecRenderable || !runtime.isVisualSpecRenderable(visualSpec)) {
            storedVisualSpec = null;
            storedQuestionImage = null;
            storedImageSource = null;
            if (backgroundCtx) {
                clearBackgroundCanvas(backgroundCtx, cssWidth, cssHeight);
            }
            return false;
        }
        storedVisualSpec = visualSpec || null;
        storedQuestionImage = null;
        storedImageSource = null;
        if (!backgroundCtx) {
            return false;
        }
        return redrawQuestionBackground(backgroundCtx, cssWidth, cssHeight, visualRuntime);
    }

    function setImageBackground(image, imageSource, backgroundCtx, cssWidth, cssHeight) {
        storedQuestionImage = image || null;
        storedImageSource = imageSource || null;
        storedVisualSpec = null;
        if (!backgroundCtx || !storedQuestionImage) {
            return false;
        }
        return redrawQuestionBackground(backgroundCtx, cssWidth, cssHeight, null);
    }

    function loadImageBackground(imageSource) {
        return new Promise(function (resolve, reject) {
            if (!imageSource || String(imageSource).trim() === '') {
                resolve(null);
                return;
            }
            const img = new Image();
            img.onload = function () {
                resolve(img);
            };
            img.onerror = function (err) {
                reject(err || new Error('question image load failed'));
            };
            img.src = imageSource;
        });
    }

    function hideQuestionMediaContainer(container) {
        if (!container) {
            return;
        }
        container.innerHTML = '';
        container.style.display = 'none';
    }

    function extractImageFromPayload(payload) {
        if (!payload || typeof payload !== 'object') {
            return '';
        }
        let rawImage = payload.image_base64;
        const visualSpec = payload.visual_spec;
        if ((!rawImage || String(rawImage).trim() === '') && visualSpec && typeof visualSpec === 'object') {
            rawImage = visualSpec.image_base64;
        }
        const tableData = payload.table_data;
        if ((!rawImage || String(rawImage).trim() === '') && tableData && typeof tableData === 'object') {
            rawImage = tableData.image_base64;
        }
        if ((!rawImage || String(rawImage).trim() === '') && payload.image_url) {
            rawImage = payload.image_url;
        }
        if (!rawImage && payload.visual_aids) {
            if (typeof payload.visual_aids === 'string') {
                rawImage = payload.visual_aids;
            } else if (payload.visual_aids.plot_base64) {
                rawImage = payload.visual_aids.plot_base64;
            } else if (Array.isArray(payload.visual_aids)) {
                const imgObj = payload.visual_aids.find(function (item) {
                    return item && item.type === 'image/png';
                });
                if (imgObj) {
                    rawImage = imgObj.value;
                }
            }
        }
        return rawImage && String(rawImage).trim() !== '' ? rawImage : '';
    }

    function shouldRenderBackgroundForPayload(payload, visualRuntime) {
        const runtime = visualRuntime || (root && root.VisualSpecRuntime);
        if (!payload || typeof payload !== 'object') {
            return { kind: 'none' };
        }
        const visualSpec = payload.visual_spec;
        if (runtime && runtime.isVisualSpecRenderable && runtime.isVisualSpecRenderable(visualSpec)) {
            return { kind: 'visual_spec', visualSpec: visualSpec };
        }
        const rawImage = extractImageFromPayload(payload);
        if (rawImage) {
            return { kind: 'image', rawImage: rawImage };
        }
        return { kind: 'none' };
    }

    function clearInkLayer(ctx, cssWidth, cssHeight) {
        if (!ctx) {
            return;
        }
        const width = Math.max(1, Number(cssWidth) || 1);
        const height = Math.max(1, Number(cssHeight) || 1);
        ctx.clearRect(0, 0, width, height);
    }

    function validateQuadrantBounds(bounds, cssWidth, cssHeight, edgePadding, layoutRegion) {
        if (!bounds) {
            return { ok: false, reason: 'missing-bounds' };
        }
        const region = layoutRegion || computeQuestionBackgroundRegion(cssWidth, cssHeight, edgePadding);
        const pad = region.edgePadding;
        const checks = {
            minXAtLeastPadding: bounds.minX >= region.x - 2,
            minYAtLeastPadding: bounds.minY >= region.y - 2,
            widthWithinHalf: bounds.width <= region.quadrantWidth + 1,
            heightWithinHalf: bounds.height <= region.quadrantHeight + 1,
            maxXWithinQuadrant: bounds.maxX <= region.x + region.width + 2,
            maxYWithinQuadrant: bounds.maxY <= region.y + region.height + 2
        };
        checks.ok = Object.keys(checks).every(function (key) {
            return key === 'ok' || checks[key] === true;
        });
        return checks;
    }

    return {
        REGION_EDGE_PADDING: REGION_EDGE_PADDING,
        REGION_WIDTH_RATIO: REGION_WIDTH_RATIO,
        REGION_HEIGHT_RATIO: REGION_HEIGHT_RATIO,
        IMAGE_OPACITY: IMAGE_OPACITY,
        computeQuestionBackgroundRegion: computeQuestionBackgroundRegion,
        computeContainRect: computeContainRect,
        measureBackgroundContentBounds: measureBackgroundContentBounds,
        validateQuadrantBounds: validateQuadrantBounds,
        getLastRenderBounds: getLastRenderBounds,
        getLastRenderMeta: getLastRenderMeta,
        resetQuestionBackground: resetQuestionBackground,
        hasQuestionBackground: hasQuestionBackground,
        getStoredBackground: getStoredBackground,
        redrawQuestionBackground: redrawQuestionBackground,
        clearBackgroundCanvas: clearBackgroundCanvas,
        setVisualSpecBackground: setVisualSpecBackground,
        setImageBackground: setImageBackground,
        loadImageBackground: loadImageBackground,
        extractImageFromPayload: extractImageFromPayload,
        hideQuestionMediaContainer: hideQuestionMediaContainer,
        shouldRenderBackgroundForPayload: shouldRenderBackgroundForPayload,
        clearInkLayer: clearInkLayer
    };
}));
