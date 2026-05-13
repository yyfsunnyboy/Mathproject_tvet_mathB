from core.textbook_filename_parser import parse_textbook_filename_metadata

filenames = [
    "第一章 1-1 數線與絕對值-課本.docx",
    "1-1_-.pdf",
    "1-2 平面坐標系與線型函數-課本.docx",
    "第一章 自我評量-課本.docx"
]

for f in filenames:
    meta = parse_textbook_filename_metadata(f)
    print(f"File: {f}")
    print(f"Meta: {meta}")
    print("-" * 30)
