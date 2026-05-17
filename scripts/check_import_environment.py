#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check whether current host is suitable for formal textbook import."""

from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path


def has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def main() -> int:
    machine = (platform.machine() or "").lower()
    arch_bits = "64" if "64" in str(platform.architecture()[0]) else "32"
    is_arm64 = ("arm" in machine) or ("aarch64" in machine)
    is_x86_x64 = not is_arm64

    converter_available = any([has_cmd("soffice"), has_cmd("magick"), has_cmd("inkscape")])
    tesseract_available = has_cmd("tesseract")
    soffice_available = has_cmd("soffice")
    imagemagick_available = has_cmd("magick")
    can_process_vector_formula_assets = converter_available

    if is_arm64:
        recommendation = "ARM64: 不建議正式教材匯入；可做檢視與管理。"
    elif is_x86_x64 and converter_available:
        recommendation = "x86/x64 + converter 可用：可正式教材匯入。"
    else:
        recommendation = "x86/x64 但 converter 不足：先補齊 soffice/magick/inkscape。"

    payload = {
        "machine": machine,
        "arch_bits": arch_bits,
        "is_x86_x64": is_x86_x64,
        "is_arm64": is_arm64,
        "converter_available": converter_available,
        "tesseract_available": tesseract_available,
        "soffice_available": soffice_available,
        "imagemagick_available": imagemagick_available,
        "can_process_vector_formula_assets": can_process_vector_formula_assets,
        "recommendation": recommendation,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

