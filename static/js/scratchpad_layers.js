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
    const REGION_WIDTH_RATIO = 0.7;
    const REGION_HEIGHT_RATIO = 0.68;
    const IMAGE_OPACITY = 0.86;

    let storedVisualSpec = null;
    let storedQuestionImage = null;
    let storedImageSource = null;
    let storedQuestionImages = [];
    let storedImageSources = [];
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

    function computeFullCanvasRegion(canvasWidth, canvasHeight, edgePadding) {
        const pad = Number.isFinite(edgePadding) ? edgePadding : REGION_EDGE_PADDING;
        const cw = Math.max(1, Number(canvasWidth) || 1);
        const ch = Math.max(1, Number(canvasHeight) || 1);
        return {
            x: pad,
            y: pad,
            width: Math.max(1, cw - pad * 2),
            height: Math.max(1, ch - pad * 2),
            edgePadding: pad,
            quadrantWidth: cw,
            quadrantHeight: ch,
            canvasWidth: cw,
            canvasHeight: ch
        };
    }

    function computeImageGrid(imageCount, canvasWidth, canvasHeight, edgePadding) {
        const count = Math.max(0, Math.floor(Number(imageCount) || 0));
        const region = computeFullCanvasRegion(canvasWidth, canvasHeight, edgePadding);
        if (!count) {
            return { cols: 0, rows: 0, cells: [], region: region };
        }
        const gap = 12;
        const cols = count === 1 ? 1 : (region.width < 520 ? 1 : Math.min(2, count));
        const rows = Math.ceil(count / cols);
        const cellWidth = Math.max(1, (region.width - gap * (cols - 1)) / cols);
        const cellHeight = Math.max(1, (region.height - gap * (rows - 1)) / rows);
        const cells = [];
        for (let index = 0; index < count; index += 1) {
            const col = index % cols;
            const row = Math.floor(index / cols);
            cells.push({
                x: region.x + col * (cellWidth + gap),
                y: region.y + row * (cellHeight + gap),
                width: cellWidth,
                height: cellHeight
            });
        }
        return { cols: cols, rows: rows, cells: cells, region: region, gap: gap };
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
        storedQuestionImages = [];
        storedImageSources = [];
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
            questionImages: storedQuestionImages.slice(),
            imageSources: storedImageSources.slice(),
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
        const images = storedQuestionImages.length
            ? storedQuestionImages
            : (storedQuestionImage ? [storedQuestionImage] : []);
        if (!images.length || !ctx) {
            return false;
        }
        const isMulti = images.length > 1;
        const region = isMulti
            ? computeFullCanvasRegion(cssWidth, cssHeight)
            : computeQuestionBackgroundRegion(cssWidth, cssHeight);
        const grid = isMulti ? computeImageGrid(images.length, cssWidth, cssHeight) : null;
        const rects = images.map(function (image, index) {
            const cell = isMulti ? grid.cells[index] : region;
            return computeContainRect(
                image.naturalWidth,
                image.naturalHeight,
                cell.width,
                cell.height,
                isMulti ? 6 : region.edgePadding,
                cell.x,
                cell.y
            );
        });
        ctx.save();
        ctx.globalAlpha = IMAGE_OPACITY;
        rects.forEach(function (rect, index) {
            ctx.drawImage(images[index], rect.x, rect.y, rect.width, rect.height);
        });
        ctx.restore();
        const minX = Math.min.apply(null, rects.map(function (rect) { return rect.x; }));
        const minY = Math.min.apply(null, rects.map(function (rect) { return rect.y; }));
        const maxX = Math.max.apply(null, rects.map(function (rect) { return rect.x + rect.width; }));
        const maxY = Math.max.apply(null, rects.map(function (rect) { return rect.y + rect.height; }));
        setLastRenderBounds({
            minX: minX,
            minY: minY,
            maxX: maxX,
            maxY: maxY,
            width: maxX - minX,
            height: maxY - minY
        });
        setLastRenderMeta({
            scaleMode: isMulti ? 'multi_image_contain' : 'image_contain',
            equalUnits: false,
            imageCount: images.length,
            imageScales: rects.map(function (rect) { return rect.scale; }),
            gridCols: isMulti ? grid.cols : 1,
            gridRows: isMulti ? grid.rows : 1
        });
        return true;
    }

    function drawStoredVisualSpecBackground(ctx, cssWidth, cssHeight, visualRuntime) {
        const runtime = visualRuntime || (root && root.VisualSpecRuntime);
        if (!storedVisualSpec || !runtime || !runtime.renderToCanvas || !ctx) {
            return false;
        }
        const isMulti = runtime.isMultiFigureSpec && runtime.isMultiFigureSpec(storedVisualSpec);
        const region = isMulti
            ? computeFullCanvasRegion(cssWidth, cssHeight)
            : computeQuestionBackgroundRegion(cssWidth, cssHeight);
        const ok = runtime.renderToCanvas(ctx.canvas, storedVisualSpec, {
            width: cssWidth,
            height: cssHeight,
            layoutRegion: region,
            padding: isMulti ? 12 : Math.min(region.edgePadding, 10),
            manageCanvasSize: false,
            backgroundFill: null,
            visualOpacity: isMulti ? 0.95 : 0.88
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
            storedQuestionImages = [];
            storedImageSources = [];
            if (backgroundCtx) {
                clearBackgroundCanvas(backgroundCtx, cssWidth, cssHeight);
            }
            return false;
        }
        storedVisualSpec = visualSpec || null;
        storedQuestionImage = null;
        storedImageSource = null;
        storedQuestionImages = [];
        storedImageSources = [];
        if (!backgroundCtx) {
            return false;
        }
        return redrawQuestionBackground(backgroundCtx, cssWidth, cssHeight, visualRuntime);
    }

    function setImageBackground(image, imageSource, backgroundCtx, cssWidth, cssHeight) {
        return setImagesBackground(
            image ? [image] : [],
            imageSource ? [imageSource] : [],
            backgroundCtx,
            cssWidth,
            cssHeight
        );
    }

    function setImagesBackground(images, imageSources, backgroundCtx, cssWidth, cssHeight) {
        storedQuestionImages = Array.isArray(images) ? images.filter(Boolean) : [];
        storedImageSources = Array.isArray(imageSources) ? imageSources.filter(Boolean) : [];
        storedQuestionImage = storedQuestionImages[0] || null;
        storedImageSource = storedImageSources[0] || null;
        storedVisualSpec = null;
        if (!backgroundCtx || !storedQuestionImages.length) {
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

    function loadImageBackgrounds(imageSources) {
        const sources = Array.isArray(imageSources) ? imageSources.filter(Boolean) : [];
        return Promise.all(sources.map(loadImageBackground));
    }

    function hideQuestionMediaContainer(container) {
        if (!container) {
            return;
        }
        container.innerHTML = '';
        container.style.display = 'none';
    }

    function extractImagesFromPayload(payload) {
        if (!payload || typeof payload !== 'object') {
            return [];
        }
        const candidates = [];
        function add(value) {
            const source = String(value || '').trim();
            if (!source) return;
            const key = source.replace(/^\/+/, '');
            if (!candidates.some(function (item) { return item.key === key; })) {
                candidates.push({ key: key, source: source });
            }
        }
        function addObject(item) {
            if (!item || typeof item !== 'object') return;
            add(item.url || item.src || item.image_url || item.image_base64
                || item.value || item.asset_path || item.display_path || item.path);
        }

        add(payload.image_base64);
        add(payload.image_url);
        const visualSpec = payload.visual_spec;
        if (visualSpec && typeof visualSpec === 'object') {
            addObject(visualSpec);
        }
        const tableData = payload.table_data;
        if (tableData && typeof tableData === 'object') {
            addObject(tableData);
        }
        if (Array.isArray(payload.image_assets)) {
            payload.image_assets.forEach(addObject);
        }
        if (payload.visual_aids) {
            if (typeof payload.visual_aids === 'string') {
                add(payload.visual_aids);
            } else if (Array.isArray(payload.visual_aids)) {
                payload.visual_aids.forEach(addObject);
            } else {
                addObject(payload.visual_aids);
            }
        }
        return candidates.map(function (item) { return item.source; });
    }

    function extractImageFromPayload(payload) {
        const images = extractImagesFromPayload(payload);
        return images[0] || '';
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
        const rawImages = extractImagesFromPayload(payload);
        if (rawImages.length) {
            return {
                kind: rawImages.length > 1 ? 'multi_image' : 'image',
                rawImage: rawImages[0],
                rawImages: rawImages
            };
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
        computeFullCanvasRegion: computeFullCanvasRegion,
        computeImageGrid: computeImageGrid,
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
        setImagesBackground: setImagesBackground,
        loadImageBackground: loadImageBackground,
        loadImageBackgrounds: loadImageBackgrounds,
        extractImageFromPayload: extractImageFromPayload,
        extractImagesFromPayload: extractImagesFromPayload,
        hideQuestionMediaContainer: hideQuestionMediaContainer,
        shouldRenderBackgroundForPayload: shouldRenderBackgroundForPayload,
        clearInkLayer: clearInkLayer
    };
}));
