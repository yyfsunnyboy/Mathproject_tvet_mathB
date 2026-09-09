from __future__ import annotations

import json
import sys
import traceback
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.mtef import MTEF
from core.mtef.record import RecordType
from core.textbook_importer_v3_docx import parse_docx_structure
from core.textbook_mathtype_converter import extract_equation_native


SOURCE = Path(__file__).with_name("第一章 1-2 銳角三角函數-課本.docx")
TARGETS = {198, 199, 200, 201, *range(204, 215), 270, 271, 278, 279, 337, 338}
RECORD_NAMES = {
    value: name
    for name, value in vars(RecordType).items()
    if name.isupper() and isinstance(value, int)
}


def ast_dict(node):
    value = node.value
    details = {}
    for attr in ("selector", "variation", "options", "mtcode", "typeface", "null"):
        if value is not None and hasattr(value, attr):
            details[attr] = getattr(value, attr)
    return {
        "record": RECORD_NAMES.get(node.tag, node.tag),
        **details,
        "children": [ast_dict(child) for child in (node.children or [])],
    }


def main():
    parsed = parse_docx_structure(SOURCE.read_bytes(), filename=SOURCE.name, include_blocks=True)
    by_index = {
        int(item["formula_index"]): item
        for item in parsed.get("mathtype_oles", [])
        if int(item["formula_index"]) in TARGETS
    }
    results = []
    with zipfile.ZipFile(SOURCE) as zf:
        for index in sorted(TARGETS):
            item = by_index[index]
            ole_bytes = zf.read(item["embedding_path"])
            native, native_error = extract_equation_native(ole_bytes)
            entry = {
                "formula_index": index,
                "embedding_path": item["embedding_path"],
                "location": item.get("location"),
                "ole_size": len(ole_bytes),
                "native_error": native_error,
                "native_size": len(native or b""),
            }
            if native is not None:
                eqn, open_error = MTEF.OpenEquationNative(native)
                entry["open_error"] = open_error
                if eqn is not None:
                    entry["header"] = {
                        "mtef_version": eqn.mMtefVer,
                        "platform": eqn.mPlatform,
                        "product": eqn.mProduct,
                        "version": eqn.mVersion,
                        "version_sub": eqn.mVersionSub,
                        "application": eqn.mApplication.decode("latin1", errors="replace")
                        if isinstance(eqn.mApplication, bytes)
                        else str(eqn.mApplication),
                        "inline": eqn.mInline,
                        "valid_after_records": eqn.Valid,
                        "unknown_record": getattr(eqn, "_unknown_record", None),
                        "unknown_offset": getattr(eqn, "_unknown_offset", None),
                    }
                    entry["node_sequence"] = [
                        {
                            "record": RECORD_NAMES.get(node.tag, node.tag),
                            **(
                                {"selector": node.value.selector, "variation": node.value.variation}
                                if node.tag == RecordType.TMPL
                                else {}
                            ),
                            **(
                                {"mtcode": node.value.mtcode, "typeface": node.value.typeface}
                                if node.tag == RecordType.CHAR
                                else {}
                            ),
                        }
                        for node in eqn.nodes
                    ]
                    entry["ast"] = ast_dict(eqn.ast)
                    try:
                        entry["latex"] = eqn.Translate()
                        entry["failure_stage"] = "translate_empty" if not entry["latex"].strip() else None
                    except Exception as exc:
                        entry["latex"] = ""
                        entry["failure_stage"] = "ast_to_latex"
                        entry["exception"] = f"{type(exc).__name__}: {exc}"
                        entry["traceback"] = traceback.format_exc()
            results.append(entry)
    output = Path(__file__).with_name("remaining_21_inspection.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in results:
        h = row.get("header") or {}
        templates = [
            (n.get("selector"), n.get("variation"))
            for n in row.get("node_sequence", [])
            if n.get("record") == "TMPL"
        ]
        print(
            row["formula_index"],
            "valid=", h.get("valid_after_records"),
            "unknown=", (h.get("unknown_record"), h.get("unknown_offset")),
            "nodes=", len(row.get("node_sequence", [])),
            "templates=", templates,
            "stage=", row.get("failure_stage"),
            "exception=", row.get("exception"),
            "latex=", repr(row.get("latex")),
        )


if __name__ == "__main__":
    main()
