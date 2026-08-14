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

    const DEFAULT_PADDING = 20;
    const IMAGE_OPACITY = 0.72;

    let storedVisualSpec = null;
    let storedQuestionImage = null;
    let storedImageSource = null;

    function computeContainRect(naturalWidth, naturalHeight, containerWidth, containerHeight, padding) {
        const pad = Number.isFinite(padding) ? padding : DEFAULT_PADDING;
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

    function resetQuestionBackground() {
        storedVisualSpec = null;
        storedQuestionImage = null;
        storedImageSource = null;
    }

    function hasQuestionBackground() {
        return Boolean(storedVisualSpec || storedQuestionImage);
    }

    function getStoredBackground() {
        return {
            visualSpec: storedVisualSpec,
            questionImage: storedQuestionImage,
            imageSource: storedImageSource
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
        const rect = computeContainRect(
            storedQuestionImage.naturalWidth,
            storedQuestionImage.naturalHeight,
            cssWidth,
            cssHeight,
            DEFAULT_PADDING
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
        return true;
    }

    function drawStoredVisualSpecBackground(ctx, cssWidth, cssHeight, visualRuntime) {
        const runtime = visualRuntime || (root && root.VisualSpecRuntime);
        if (!storedVisualSpec || !runtime || !runtime.renderToCanvas || !ctx) {
            return false;
        }
        return runtime.renderToCanvas(ctx.canvas, storedVisualSpec, {
            width: cssWidth,
            height: cssHeight,
            padding: DEFAULT_PADDING,
            manageCanvasSize: false,
            backgroundFill: '#ffffff',
            visualOpacity: 0.62
        });
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
        return false;
    }

    function clearBackgroundCanvas(backgroundCtx, cssWidth, cssHeight) {
        if (!backgroundCtx) {
            return;
        }
        const width = Math.max(1, Number(cssWidth) || backgroundCtx.canvas.clientWidth || 1);
        const height = Math.max(1, Number(cssHeight) || backgroundCtx.canvas.clientHeight || 1);
        paintBackgroundBase(backgroundCtx, width, height);
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

    return {
        DEFAULT_PADDING: DEFAULT_PADDING,
        IMAGE_OPACITY: IMAGE_OPACITY,
        computeContainRect: computeContainRect,
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
