# Attribution for vendored MTEF parser

The `core/mtef` package is adapted from:

- AndyQsmart/MTEF-py (https://github.com/AndyQsmart/MTEF-py)
- which references zhexiao/mtef-go

Adaptations in this repository:
- use `olefile` for OLE / Equation Native extraction
- harden EOF / FONT_STYLE_DEF handling
- add tmOBAR LaTeX rendering
- improve Greek / symbol / degree char mapping
- remove debug prints / Word COM dependencies

Pipeline remains deterministic:
  MTEF binary → records → MtAST → LaTeX
