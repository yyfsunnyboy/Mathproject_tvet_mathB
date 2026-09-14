from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _template_source():
    return (ROOT / "templates" / "index.html").read_text(encoding="utf-8")


def test_ai_check_recaptures_current_canvas_without_undo_restore():
    source = _template_source()
    start = source.index("async function captureHandwritingImageForRecognition()")
    end = source.index("function isDrawingQuestion", start)
    capture = source[start:end]
    assert 'getInkCanvasEl()' in capture
    assert "document.createElement('canvas')" in capture
    assert 'ect.drawImage(ink' in capture
    assert "exportCanvas.toDataURL('image/png')" in capture
    assert "undoStack" not in capture
    assert "restoreInkSnapshotForCapture" not in source


def test_eraser_deletes_pixels_from_same_ink_canvas_used_for_export():
    source = _template_source()
    assert "ctx.globalCompositeOperation = isErasing ? 'destination-out' : 'source-over'" in source
    assert 'const ink = getInkCanvasEl();' in source
    assert "return document.getElementById('handwriting-canvas') || canvas;" in source


def test_each_ai_request_marks_capture_as_fresh_and_identifies_canvas():
    source = _template_source()
    assert 'const imageDataUrl = await captureHandwritingImageForRecognition();' in source
    assert "image_data_url: imageDataUrl" in source
    assert "image_base64: imageDataUrl" in source
