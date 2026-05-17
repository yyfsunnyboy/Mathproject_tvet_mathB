#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check local environment for PDF visual enrich (local-only)."""

from __future__ import annotations

import json
import shutil


def can_import(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def main() -> int:
    pymupdf_available = can_import("fitz")
    fitz_available = pymupdf_available
    pytesseract_available = can_import("pytesseract")
    tesseract_binary_available = shutil.which("tesseract") is not None
    easyocr_available = can_import("easyocr")
    paddleocr_available = can_import("paddleocr")
    torch_available = can_import("torch")
    pix2tex_available = can_import("pix2tex")
    latex_ocr_available = pix2tex_available

    recommended_ocr_backend = "none"
    if pytesseract_available and tesseract_binary_available:
        recommended_ocr_backend = "pytesseract"
    elif easyocr_available:
        recommended_ocr_backend = "easyocr"
    elif paddleocr_available:
        recommended_ocr_backend = "paddleocr"

    can_run_pdf_visual_enrich_local = bool(fitz_available and recommended_ocr_backend != "none")
    recommended_formula_ocr_backend = "pix2tex" if pix2tex_available else "none"
    can_run_formula_ocr_local = bool(torch_available and pix2tex_available)
    payload = {
        "pymupdf_available": pymupdf_available,
        "fitz_available": fitz_available,
        "pytesseract_available": pytesseract_available,
        "tesseract_binary_available": tesseract_binary_available,
        "easyocr_available": easyocr_available,
        "paddleocr_available": paddleocr_available,
        "pix2tex_available": pix2tex_available,
        "latex_ocr_available": latex_ocr_available,
        "torch_available": torch_available,
        "recommended_ocr_backend": recommended_ocr_backend,
        "recommended_formula_ocr_backend": recommended_formula_ocr_backend,
        "can_run_pdf_visual_enrich_local": can_run_pdf_visual_enrich_local,
        "can_run_formula_ocr_local": can_run_formula_ocr_local,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
