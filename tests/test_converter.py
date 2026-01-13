import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from any2md.converter import Any2MDConverter, ConvertResult


class TestAny2MDConverter:
    def test_can_convert_supported_formats(self):
        converter = Any2MDConverter()

        assert converter.can_convert(Path("test.pdf"))
        assert converter.can_convert(Path("test.docx"))
        assert converter.can_convert(Path("test.html"))
        assert converter.can_convert(Path("test.xlsx"))
        assert converter.can_convert(Path("test.pptx"))
        assert converter.can_convert(Path("test.zip"))

    def test_can_convert_case_insensitive(self):
        converter = Any2MDConverter()

        assert converter.can_convert(Path("test.PDF"))
        assert converter.can_convert(Path("test.DOCX"))
        assert converter.can_convert(Path("test.Html"))

    def test_cannot_convert_unsupported_formats(self):
        converter = Any2MDConverter()

        assert not converter.can_convert(Path("test.exe"))
        assert not converter.can_convert(Path("test.dll"))
        assert not converter.can_convert(Path("test.unknown"))
        assert not converter.can_convert(Path("test.py"))

    def test_convert_nonexistent_file(self):
        converter = Any2MDConverter()
        result = converter.convert_file(Path("/nonexistent/file.pdf"))

        assert not result.success
        assert result.error is not None
        assert "不存在" in result.error

    def test_convert_unsupported_format(self, tmp_path):
        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")

        converter = Any2MDConverter()
        result = converter.convert_file(test_file)

        assert not result.success
        assert "不支持" in result.error

    @patch("any2md.converter.MarkItDown")
    def test_convert_file_success(self, mock_markitdown_class, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")
        output_dir = tmp_path / "output"

        mock_result = Mock()
        mock_result.text_content = "# Hello World"
        mock_result.title = "Test"

        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        result = converter.convert_file(test_file, output_dir)

        assert result.success
        assert result.markdown == "# Hello World"
        assert result.output_path.exists()
        assert result.output_path.read_text() == "# Hello World"

    @patch("any2md.converter.MarkItDown")
    def test_convert_file_exception(self, mock_markitdown_class, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        mock_md = Mock()
        mock_md.convert.side_effect = Exception("Conversion failed")
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        result = converter.convert_file(test_file)

        assert not result.success
        assert "Conversion failed" in result.error

    @patch("any2md.converter.MarkItDown")
    def test_convert_doc_via_soffice_then_markitdown(self, mock_markitdown_class, tmp_path):
        test_file = tmp_path / "test.doc"
        test_file.write_bytes(b"fake doc")

        converted = tmp_path / "converted.docx"
        converted.write_bytes(b"fake docx")

        mock_result = Mock()
        mock_result.text_content = "converted markdown"
        mock_result.title = "Converted"

        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        converter._convert_via_soffice = Mock(return_value=converted)

        result = converter.convert_file(test_file)

        assert result.success
        mock_md.convert.assert_called_once_with(str(converted))

    @patch("any2md.converter.MarkItDown")
    def test_convert_doc_windows_fallback(self, mock_markitdown_class, tmp_path):
        test_file = tmp_path / "test.doc"
        test_file.write_bytes(b"fake doc")

        converted = tmp_path / "converted.docx"
        converted.write_bytes(b"fake docx")

        mock_result = Mock()
        mock_result.text_content = "converted markdown"
        mock_result.title = "Converted"

        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        converter._convert_via_soffice = Mock(side_effect=RuntimeError("no soffice"))
        converter._convert_via_windows_com = Mock(return_value=converted)

        with patch("any2md.converter.sys.platform", "win32"):
            result = converter.convert_file(test_file)

        assert result.success
        converter._convert_via_windows_com.assert_called_once()
        mock_md.convert.assert_called_once_with(str(converted))

    @patch("any2md.converter.MarkItDown")
    def test_convert_directory(self, mock_markitdown_class, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "file1.txt").write_text("content1")
        (input_dir / "file2.html").write_text("<p>content2</p>")
        (input_dir / "subdir").mkdir()
        (input_dir / "subdir" / "file3.docx").write_bytes(b"docx content")

        output_dir = tmp_path / "output"

        mock_result = Mock()
        mock_result.text_content = "converted"
        mock_result.title = None

        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        results = converter.convert_directory(input_dir, output_dir, recursive=True)

        assert len(results) == 3
        assert all(r.success for r in results)

    @patch("any2md.converter.MarkItDown")
    def test_convert_directory_non_recursive(self, mock_markitdown_class, tmp_path):
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "file1.txt").write_text("content1")
        (input_dir / "subdir").mkdir()
        (input_dir / "subdir" / "file2.txt").write_text("content2")

        output_dir = tmp_path / "output"

        mock_result = Mock()
        mock_result.text_content = "converted"
        mock_result.title = None

        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown_class.return_value = mock_md

        converter = Any2MDConverter()
        results = converter.convert_directory(input_dir, output_dir, recursive=False)

        assert len(results) == 1


class TestConvertResult:
    def test_success_result(self):
        result = ConvertResult(
            success=True,
            input_path=Path("test.pdf"),
            output_path=Path("test.md"),
            markdown="# Test",
            title="Test Title",
        )

        assert result.success
        assert result.error is None

    def test_failure_result(self):
        result = ConvertResult(
            success=False, input_path=Path("test.pdf"), error="Something went wrong"
        )

        assert not result.success
        assert result.output_path is None
        assert result.markdown == ""
