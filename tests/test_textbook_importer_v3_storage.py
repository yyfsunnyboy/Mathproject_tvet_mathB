# -*- coding: utf-8 -*-
import io
from pathlib import Path
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from core.textbook_importer_v3_storage import (
    resolve_source_directory,
    save_textbook_source_batch,
    upload_textbook_source_batch,
)


def _make_file(filename: str, content: bytes = b"demo") -> FileStorage:
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type="application/octet-stream",
    )


def _metadata():
    return {
        "curriculum": "vocational",
        "publisher": "longteng",
        "grade": 10,
        "volume": "數學B2",
    }


class TestResolveSourceDirectory:
    @pytest.mark.parametrize(
        ("volume", "expected_dir"),
        [
            ("數學B1", "math_B1"),
            ("數學B2", "math_B2"),
            ("數學B3", "math_B3"),
            ("數學B4", "math_B4"),
        ],
    )
    def test_maps_curriculum_and_volume(self, tmp_path: Path, volume: str, expected_dir: str):
        absolute, relative = resolve_source_directory(tmp_path, "vocational", volume)
        assert relative == f"textbook_import/source/vocational/{expected_dir}"
        assert absolute == tmp_path / "textbook_import/source/vocational" / expected_dir

    def test_invalid_curriculum(self, tmp_path: Path):
        with pytest.raises(ValueError) as exc:
            resolve_source_directory(tmp_path, "../../etc/passwd", "數學B2")
        assert exc.value.args[0] == "invalid_curriculum"

    def test_invalid_volume(self, tmp_path: Path):
        with pytest.raises(ValueError) as exc:
            resolve_source_directory(tmp_path, "vocational", "../secret")
        assert exc.value.args[0] == "invalid_volume"


class TestSourceStorage:
    def test_create_directory_when_missing_and_save_pairs(self, tmp_path: Path):
        docx = _make_file("1-1 角度的基本性質-課本.docx", b"docx-bytes")
        pdf = _make_file("1-1 角度的基本性質-課本.pdf", b"pdf-bytes")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[docx],
            pdf_files=[pdf],
            **_metadata(),
        )

        assert status == 200
        assert payload["ok"] is True
        assert payload["storage"]["directory"] == "textbook_import/source/vocational/math_B2"
        assert payload["storage"]["files_saved"] == 2
        assert payload["pairs"][0]["docx_path"].endswith("1-1 角度的基本性質-課本.docx")
        assert payload["pairs"][0]["pdf_path"].endswith("1-1 角度的基本性質-課本.pdf")

        target = tmp_path / "textbook_import/source/vocational/math_B2"
        assert target.is_dir()
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"docx-bytes"
        assert (target / "1-1 角度的基本性質-課本.pdf").read_bytes() == b"pdf-bytes"

    def test_use_existing_directory(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        (target / ".keep").write_text("x", encoding="utf-8")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-2 三角比-課本.docx", b"a")],
            pdf_files=[_make_file("1-2 三角比-課本.pdf", b"b")],
            **_metadata(),
        )

        assert status == 200
        assert (target / "1-2 三角比-課本.docx").exists()

    def test_save_multiple_pairs(self, tmp_path: Path):
        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[
                _make_file("1-1 角度的基本性質-課本.docx", b"d1"),
                _make_file("1-2 三角比-課本.docx", b"d2"),
            ],
            pdf_files=[
                _make_file("1-1 角度的基本性質-課本.pdf", b"p1"),
                _make_file("1-2 三角比-課本.pdf", b"p2"),
            ],
            **_metadata(),
        )

        assert status == 200
        assert payload["storage"]["files_saved"] == 4
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        assert len(list(target.iterdir())) == 4

    def test_add_when_directory_has_unrelated_files(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        unrelated = target / "舊教材-其他章.docx"
        unrelated.write_bytes(b"keep-me")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx", b"d1")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf", b"p1")],
            **_metadata(),
        )

        assert status == 200
        assert payload["ok"] is True
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"d1"
        assert unrelated.read_bytes() == b"keep-me"

    def test_conflict_requires_confirmation_without_write(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        (target / "1-2 三角比-課本.pdf").write_bytes(b"old")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[
                _make_file("1-1 角度的基本性質-課本.docx", b"d1"),
                _make_file("1-2 三角比-課本.docx", b"d2"),
            ],
            pdf_files=[
                _make_file("1-1 角度的基本性質-課本.pdf", b"p1"),
                _make_file("1-2 三角比-課本.pdf", b"p2"),
            ],
            **_metadata(),
        )

        assert status == 409
        assert payload["error"] == "source_file_already_exists"
        assert payload["requires_confirmation"] is True
        assert payload["volume"] == "數學B2"
        assert payload["target_directory"] == "textbook_import/source/vocational/math_B2"
        assert "1-2 三角比-課本.pdf" in payload["files"]
        assert not (target / "1-1 角度的基本性質-課本.docx").exists()
        assert (target / "1-2 三角比-課本.pdf").read_bytes() == b"old"

    def test_without_overwrite_flag_does_not_overwrite(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        (target / "1-1 角度的基本性質-課本.docx").write_bytes(b"old-docx")
        (target / "1-1 角度的基本性質-課本.pdf").write_bytes(b"old-pdf")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx", b"new-docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf", b"new-pdf")],
            **_metadata(),
        )

        assert status == 409
        assert payload["requires_confirmation"] is True
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"old-docx"
        assert (target / "1-1 角度的基本性質-課本.pdf").read_bytes() == b"old-pdf"

    def test_overwrite_existing_true_replaces_batch(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        unrelated = target / "其他教材.pdf"
        unrelated.write_bytes(b"unrelated")
        (target / "1-1 角度的基本性質-課本.docx").write_bytes(b"old-docx")
        (target / "1-1 角度的基本性質-課本.pdf").write_bytes(b"old-pdf")

        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx", b"new-docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf", b"new-pdf")],
            overwrite_existing=True,
            **_metadata(),
        )

        assert status == 200
        assert payload["ok"] is True
        assert payload["storage"]["overwritten"] is True
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"new-docx"
        assert (target / "1-1 角度的基本性質-課本.pdf").read_bytes() == b"new-pdf"
        assert unrelated.read_bytes() == b"unrelated"

    def test_overwrite_failure_restores_previous_and_keeps_unrelated(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        unrelated = target / "其他教材.pdf"
        unrelated.write_bytes(b"unrelated")
        (target / "1-1 角度的基本性質-課本.docx").write_bytes(b"old-docx")
        (target / "1-1 角度的基本性質-課本.pdf").write_bytes(b"old-pdf")

        original_write_bytes = Path.write_bytes
        call_count = {"n": 0}

        def flaky_write_bytes(self, data):
            call_count["n"] += 1
            # First successful overwrite is DOCX; fail on PDF write.
            if call_count["n"] == 2:
                raise OSError("disk full")
            return original_write_bytes(self, data)

        with patch.object(Path, "write_bytes", flaky_write_bytes):
            payload, status = upload_textbook_source_batch(
                project_root=tmp_path,
                docx_files=[_make_file("1-1 角度的基本性質-課本.docx", b"new-docx")],
                pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf", b"new-pdf")],
                overwrite_existing=True,
                **_metadata(),
            )

        assert status == 500
        assert payload["error"] == "source_save_failed"
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"old-docx"
        assert (target / "1-1 角度的基本性質-課本.pdf").read_bytes() == b"old-pdf"
        assert unrelated.read_bytes() == b"unrelated"

    def test_invalid_curriculum_rejected(self, tmp_path: Path):
        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            curriculum="../../evil",
            publisher="longteng",
            grade=10,
            volume="數學B2",
        )
        assert status == 400
        assert payload["error"] == "invalid_curriculum"

    def test_invalid_volume_rejected(self, tmp_path: Path):
        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            curriculum="vocational",
            publisher="longteng",
            grade=10,
            volume="../../secret",
        )
        assert status == 400
        assert payload["error"] == "invalid_volume"

    def test_path_traversal_filename_rejected(self, tmp_path: Path):
        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("../evil.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] in {"unsafe_filename", "source_pair_validation_failed"}

    def test_rollback_on_save_failure(self, tmp_path: Path):
        docx = _make_file("1-1 角度的基本性質-課本.docx", b"d1")
        pdf = _make_file("1-1 角度的基本性質-課本.pdf", b"p1")
        original_write_bytes = Path.write_bytes
        call_count = {"n": 0}

        def flaky_write_bytes(self, data):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise OSError("disk full")
            return original_write_bytes(self, data)

        with patch.object(Path, "write_bytes", flaky_write_bytes):
            payload, status = upload_textbook_source_batch(
                project_root=tmp_path,
                docx_files=[docx],
                pdf_files=[pdf],
                **_metadata(),
            )

        assert status == 500
        assert payload["error"] == "source_save_failed"
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        if target.exists():
            assert list(target.glob("*")) == []

    def test_saved_bytes_match_upload(self, tmp_path: Path):
        docx_bytes = b"docx-original-content"
        pdf_bytes = b"pdf-original-content"
        payload, status = upload_textbook_source_batch(
            project_root=tmp_path,
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx", docx_bytes)],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf", pdf_bytes)],
            **_metadata(),
        )
        assert status == 200
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == docx_bytes
        assert (target / "1-1 角度的基本性質-課本.pdf").read_bytes() == pdf_bytes

    def test_save_textbook_source_batch_direct_conflict(self, tmp_path: Path):
        target = tmp_path / "textbook_import/source/vocational/math_B2"
        target.mkdir(parents=True)
        (target / "1-1 角度的基本性質-課本.docx").write_bytes(b"old")

        docx_map = {"1-1 角度的基本性質-課本": _make_file("1-1 角度的基本性質-課本.docx", b"new")}
        pdf_map = {"1-1 角度的基本性質-課本": _make_file("1-1 角度的基本性質-課本.pdf", b"new")}

        payload, status = save_textbook_source_batch(
            project_root=tmp_path,
            pairs=[{"base_name": "1-1 角度的基本性質-課本"}],
            docx_map=docx_map,
            pdf_map=pdf_map,
            curriculum="vocational",
            volume="數學B2",
        )
        assert status == 409
        assert payload["error"] == "source_file_already_exists"
        assert payload["requires_confirmation"] is True
        assert payload["volume"] == "數學B2"
        assert payload["target_directory"] == "textbook_import/source/vocational/math_B2"
        assert (target / "1-1 角度的基本性質-課本.docx").read_bytes() == b"old"
