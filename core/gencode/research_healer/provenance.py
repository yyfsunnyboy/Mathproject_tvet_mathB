# -*- coding: utf-8 -*-
"""Research provenance of the vendored MathProject AST Research Healer.

Every file under ``vendor/`` is the research source with exactly the import
substitutions in ``IMPORT_SUBSTITUTIONS`` applied; nothing else differs.
``verify_vendored_files`` proves it without access to the research repository
by reversing the substitutions and comparing the LF-normalized SHA-256.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

RESEARCH_REPOSITORY = "https://github.com/yyfsunnyboy/MathProject_AST_Research_HealerBoundary"
RESEARCH_COMMIT = "f499a7472a739666fb3ba54e806bfc85f71eba75"
RESEARCH_SOURCE_DIR = "agent_tools/finals_rebuild"
VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
VENDOR_PACKAGE = "core.gencode.research_healer.vendor"

# (research text, vendored text); applied longest research text first.
IMPORT_SUBSTITUTIONS: tuple[tuple[str, str], ...] = (
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l1_delimiter_extended",
        f"{VENDOR_PACKAGE}.rules_l1_delimiter_extended",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l2_kwargs_bag_inline",
        f"{VENDOR_PACKAGE}.rules_l2_kwargs_bag_inline",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l2_json_dumps_unwrap",
        f"{VENDOR_PACKAGE}.rules_l2_json_dumps_unwrap",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l1_paren_close",
        f"{VENDOR_PACKAGE}.rules_l1_paren_close",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l1_prose_narrow",
        f"{VENDOR_PACKAGE}.rules_l1_prose_narrow",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_protocol",
        f"{VENDOR_PACKAGE}.protocol",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l1",
        f"{VENDOR_PACKAGE}.rules_l1",
    ),
    (
        "agent_tools.finals_rebuild.ce115_research_healer_rules_l2",
        f"{VENDOR_PACKAGE}.rules_l2",
    ),
    (
        "from agent_tools.finals_rebuild.math_boundary_pilot import classify_response",
        f"from {VENDOR_PACKAGE}.evaluator_unavailable import classify_response",
    ),
    (
        "from scripts.run_math16_latex_v1_gemini_live import classify_math16_response",
        f"from {VENDOR_PACKAGE}.evaluator_unavailable import classify_math16_response",
    ),
)

# vendored file -> research source file, git blob, LF-normalized SHA-256, last research commit touching it.
PORTED_FILES: dict[str, dict[str, str]] = {
    "protocol.py": {
        "source": "ce115_research_healer_protocol.py",
        "git_blob": "eec3435a0326e8101fb844ccb81466341be426e3",
        "source_sha256_lf": "e22f486af3c5e78de5bd47a6ddaba1b4658c8b6157fb8572d5b63a02cfaa2f43",
        "last_commit": "83b03c15",
    },
    "runner.py": {
        "source": "ce115_research_healer_runner.py",
        "git_blob": "99aa3d5d3cbfb826709cc723a9f7db7add8b1ebf",
        "source_sha256_lf": "f7f8d2db3159e051d209f0132e558b904d3ef7cee481f9310ae48f3860afaac6",
        "last_commit": "3203cc32",
    },
    "rules_l1.py": {
        "source": "ce115_research_healer_rules_l1.py",
        "git_blob": "9376c34acf9fadc701183c8c1c9e5744014f542c",
        "source_sha256_lf": "86ff0b3b70fa9fb217e4de98f48bbf0eee3989578c40cc186464f512b99aa6ff",
        "last_commit": "9e1dabde",
    },
    "rules_l1_paren_close.py": {
        "source": "ce115_research_healer_rules_l1_paren_close.py",
        "git_blob": "898bc583094c9603c6e0dba216f3d39da44b21a4",
        "source_sha256_lf": "4e68a0b488b87d26865c94c6271def373f5bf6ba257298947586f99c01d4de1d",
        "last_commit": "36126ce4",
    },
    "rules_l1_delimiter_extended.py": {
        "source": "ce115_research_healer_rules_l1_delimiter_extended.py",
        "git_blob": "40b3d0c9bd273a07dcbb7bf718cbdea8f5959841",
        "source_sha256_lf": "ddad91f867fc9bed2cd5eb6549631f0e83fa6f84f464490e8b5e22c860a6826d",
        "last_commit": "36126ce4",
    },
    "rules_l1_prose_narrow.py": {
        "source": "ce115_research_healer_rules_l1_prose_narrow.py",
        "git_blob": "98b0594b17866519441d9f27c69066104e541caa",
        "source_sha256_lf": "a8ea5f1198c073d0c5e9971ea541e48ae5c4072f9a7315850726f0ba6ea2d1eb",
        "last_commit": "36126ce4",
    },
    "rules_l2.py": {
        "source": "ce115_research_healer_rules_l2.py",
        "git_blob": "7cd65171db79165d2531052be3f01c534656ecde",
        "source_sha256_lf": "b3385a3f1c0da0032ac895d44367e09a66b9817e121920b9a499d92f18387f29",
        "last_commit": "9e1dabde",
    },
    "rules_l2_kwargs_bag_inline.py": {
        "source": "ce115_research_healer_rules_l2_kwargs_bag_inline.py",
        "git_blob": "ec28d7e709ab5b1839911259f3bd7802e145716f",
        "source_sha256_lf": "8a89c099e2a491ca45826e5fb7a6c9ff7b53ce6bda2eaa3f29c138c1035a1896",
        "last_commit": "1f016ef1",
    },
    "rules_l2_json_dumps_unwrap.py": {
        "source": "ce115_research_healer_rules_l2_json_dumps_unwrap.py",
        "git_blob": "65fc1956215af29897e4029d4e6b16d03cada62c",
        "source_sha256_lf": "7aeecce7e86468c08f872e09c03fcf067de3077eac4eaf4cdcca7c0fe5539046",
        "last_commit": "1f016ef1",
    },
}


def _lf(text: str) -> str:
    return text.replace("\r\n", "\n")


def sha256_lf(text: str) -> str:
    return hashlib.sha256(_lf(text).encode("utf-8")).hexdigest()


def vendor_text(research_text: str) -> str:
    text = _lf(research_text)
    for research, vendored in sorted(IMPORT_SUBSTITUTIONS, key=lambda p: -len(p[0])):
        text = text.replace(research, vendored)
    return text


def restore_research_text(vendored_text: str) -> str:
    text = _lf(vendored_text)
    for research, vendored in sorted(IMPORT_SUBSTITUTIONS, key=lambda p: -len(p[1])):
        text = text.replace(vendored, research)
    return text


def verify_vendored_files(vendor_dir: Path = VENDOR_DIR) -> dict[str, Any]:
    """Return per-file verdicts; ``ok`` only when every vendored file maps back to its research SHA."""
    files: dict[str, dict[str, Any]] = {}
    for name, meta in PORTED_FILES.items():
        path = vendor_dir / name
        if not path.is_file():
            files[name] = {"ok": False, "reason": "missing"}
            continue
        vendored = path.read_text(encoding="utf-8")
        restored_sha = sha256_lf(restore_research_text(vendored))
        leftover = "agent_tools.finals_rebuild" in vendored or "scripts.run_math16" in vendored
        files[name] = {
            "ok": restored_sha == meta["source_sha256_lf"] and not leftover,
            "restored_sha256_lf": restored_sha,
            "expected_sha256_lf": meta["source_sha256_lf"],
            "research_import_left": leftover,
        }
    return {"ok": all(v["ok"] for v in files.values()), "files": files}
