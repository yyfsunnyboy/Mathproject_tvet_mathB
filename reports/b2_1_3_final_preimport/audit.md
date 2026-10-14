# B2 1-3 Final Preimport Audit

Scope: isolated DOCX conversion and importer dry-run, memory-only registry copy.
Production database is opened read-only for backup and its SHA256 is checked
unchanged by both integration tests. No Gencode, commit, push, or B2 1-1/1-2 edits.

## Findings and minimal repair

Phase 1 passed Paragraph.text to whitespace normalization. python-docx omits
w:sym nodes. Both original and converted sources contain Symbol/F02D immediately
before 135 and 420 in the affected table-cell paragraphs. The shared paragraph
reader now decodes Symbol plus/minus on an XML copy, in source order, before
normalization. Unknown symbols retain explicit parse-failure markers.
All 22 source Symbol nodes are supported; original XML is unchanged.

Chapter-end begins at body paragraph index 120 with `1-3 習題`. The only groups
are `基礎題` and `進階題`, followed by questions numbered 1 through 10. There
are no unique skill headings or explicit heading references in this region.
Source order does not define a one-to-one mapping from ten exercises to seven
headings. All ten remain unresolved. No semantic or capability guesses were made.

Naming authority: core/textbook_processor_v2.py::_mathb_hash_fallback_en_id
explicitly deprecates hashes for Math B formal skills.
_fallback_en_id_from_concept_code already defines SubSection_<chapter>_<section>_<heading>.
core/textbook_formal_concept.py::build_formal_skill_id_from_en_id accepts that
suffix and core/utils.py::normalize_vocational_math_skill_id supplies the
vh_數學B<volume>_ namespace. The deterministic path now reuses this policy;
existing registry bindings take priority and occupied coordinates are rejected.
No seven-name English translation table was introduced. Seven IDs are stable
across repeated runs and across unavailable/invalid Gemini configurations.

## Verification

Final focused suite: 8 passed, 0 failed. Initial setup lacked a parent directory;
that was created. An initial document-wide parse assertion also exposed an
existing non-question formula failure, MATH_PARSE_FAILED_276. The final test
checks all 29 question blocks (0 parse failures); full-document conversion still
reports one failure and is not claimed fully clean.

Evidence: audit.json and pytest_run3/test_real_section_pipeline_wit*/verification.json.
Production import is NOT ready: 10 chapter-end bindings lack unique structural
evidence. Full-document formula failure is additionally recorded for source review.

Changed implementation: core/textbook_processor_v2.py (shared paragraph reader),
core/textbook_structural_metadata.py (coordinate naming).
Tests: tests/test_docx_symbol_fidelity.py, tests/test_textbook_structural_metadata.py.
Runtime impact is restricted to importer text extraction and new structural IDs;
no routing, progression, remediation, generator or production records changed.
