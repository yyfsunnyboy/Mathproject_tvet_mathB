# -*- coding: utf-8 -*-
from pathlib import Path
import re

src = Path("scratch/mtef_ref/mtef.py").read_text(encoding="utf-8")
src = src.replace(
    "from .ole_util.helper import Helper\nfrom .ole_util.ole import Ole\nfrom .record import",
    "from .record import",
)
src = src.replace(
    "from .chars import Chars, SpecialChar",
    "from .chars import Chars, SpecialChar\nfrom .helper import Helper",
)

# Replace print(...) statements with pass when they are the only statement in a block body.
# Safer: convert all print lines to `pass  # silenced`
src = re.sub(r"^([ \t]*)print\(.*\)\s*$", r"\1pass  # silenced", src, flags=re.M)

open_impl = '''
    @classmethod
    def OpenEquationNative(cls, eqn_native_bytes):
        """Parse MathType 'Equation Native' stream bytes (including 28-byte OLE header)."""
        if eqn_native_bytes is None or len(eqn_native_bytes) < oleCbHdr:
            return None, "MTEF.OpenEquationNative: stream too short"

        hdr_reader = BytesIO(eqn_native_bytes[:oleCbHdr])
        cb_hdr = Helper.bytes2int(hdr_reader.read(2))
        if cb_hdr is None or cb_hdr != oleCbHdr:
            return None, "MTEF.OpenEquationNative: invalid cbHdr"

        # ignore version:u32 and cf:u16
        hdr_reader.seek(4 + 2, 1)
        cb_size = Helper.bytes2int(hdr_reader.read(4))
        if cb_size is None or cb_size <= 0:
            return None, "MTEF.OpenEquationNative: invalid cbSize"

        body_start = cb_hdr
        body_end = body_start + cb_size
        if body_end > len(eqn_native_bytes):
            return None, "MTEF.OpenEquationNative: truncated body"

        eqn = MTEF()
        eqn.reader = BytesIO(eqn_native_bytes[body_start:body_end])
        eqn.readRecord()
        eqn.makeAST()
        return eqn, None

    @classmethod
    def OpenBytes(cls, bts):
        """Open raw OLE compound bytes and parse Equation Native."""
        try:
            import olefile
        except ImportError:
            return None, "MTEF.OpenBytes: olefile is required"

        try:
            ole = olefile.OleFileIO(BytesIO(bts))
        except Exception as exc:
            return None, f"MTEF.OpenBytes: ole open failed: {exc}"

        stream_names = []
        for entry in ole.listdir():
            name = "/".join(entry)
            stream_names.append(name)
            if entry[-1] == "Equation Native":
                raw = ole.openstream(entry).read()
                ole.close()
                return cls.OpenEquationNative(raw)

        ole.close()
        return None, f"MTEF.OpenBytes: Equation Native not found in {stream_names}"

    @classmethod
    def Open(cls, reader):
        data = reader.read() if hasattr(reader, "read") else reader
        return cls.OpenBytes(data)
'''

src = re.sub(
    r"    @classmethod\n    def OpenBytes\(cls, bts\):[\s\S]*$",
    open_impl.rstrip() + "\n",
    src,
)

Path("core/mtef/mtef.py").write_text(src, encoding="utf-8")
import ast
ast.parse(src)
print("syntax ok", len(src))
