import pytest
import zipfile
import shutil
from pathlib import Path
from any2md.unzipper import Unzipper, _decode_legacy_zip_name


class TestUnzipper:
    def test_decode_legacy_zip_name_gbk(self):
        original = "测试文件.docx"
        mojibake = original.encode("gbk").decode("cp437")
        assert _decode_legacy_zip_name(mojibake) == original

    def test_is_zip_valid(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test.txt", "hello")

        unzipper = Unzipper()
        assert unzipper.is_zip(zip_path)

    def test_is_zip_invalid_extension(self, tmp_path):
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("not a zip")

        unzipper = Unzipper()
        assert not unzipper.is_zip(txt_path)

    def test_is_zip_nonexistent(self, tmp_path):
        unzipper = Unzipper()
        assert not unzipper.is_zip(tmp_path / "nonexistent.zip")

    def test_is_zip_fake_zip(self, tmp_path):
        fake_zip = tmp_path / "fake.zip"
        fake_zip.write_text("not actually a zip file")

        unzipper = Unzipper()
        assert not unzipper.is_zip(fake_zip)

    def test_extract_basic(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")

        output_dir = tmp_path / "output"

        unzipper = Unzipper()
        extracted = unzipper.extract(zip_path, output_dir)

        assert (extracted / "file1.txt").exists()
        assert (extracted / "file2.txt").exists()
        assert (extracted / "file1.txt").read_text() == "content1"

    def test_extract_with_subdirs(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("root.txt", "root content")
            zf.writestr("subdir/nested.txt", "nested content")
            zf.writestr("subdir/deep/file.txt", "deep content")

        with Unzipper() as unzipper:
            extracted = unzipper.extract(zip_path)

            assert (extracted / "root.txt").exists()
            assert (extracted / "subdir" / "nested.txt").exists()
            assert (extracted / "subdir" / "deep" / "file.txt").exists()

    def test_extract_to_temp_dir(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test.txt", "hello")

        with Unzipper() as unzipper:
            extracted = unzipper.extract(zip_path)

            assert extracted.exists()
            assert (extracted / "test.txt").exists()

    def test_extract_recursive(self, tmp_path):
        inner_zip_path = tmp_path / "inner.zip"
        with zipfile.ZipFile(inner_zip_path, "w") as zf:
            zf.writestr("inner_file.txt", "inner content")

        outer_zip_path = tmp_path / "outer.zip"
        with zipfile.ZipFile(outer_zip_path, "w") as zf:
            zf.writestr("outer_file.txt", "outer content")
            zf.write(inner_zip_path, "nested/inner.zip")

        output_dir = tmp_path / "output"

        with Unzipper() as unzipper:
            extracted = unzipper.extract_recursive(outer_zip_path, output_dir)

            assert (extracted / "outer_file.txt").exists()
            assert (extracted / "nested" / "inner" / "inner_file.txt").exists()
            assert not (extracted / "nested" / "inner.zip").exists()

    def test_cleanup(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test.txt", "hello")

        unzipper = Unzipper()
        extracted = unzipper.extract(zip_path)

        assert extracted.exists()

        unzipper.cleanup()

        assert not extracted.exists()

    def test_context_manager_cleanup(self, tmp_path):
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test.txt", "hello")

        with Unzipper() as unzipper:
            extracted = unzipper.extract(zip_path)
            temp_path = extracted
            assert temp_path.exists()

        assert not temp_path.exists()

    def test_multiple_extracts_cleanup(self, tmp_path):
        zip1 = tmp_path / "test1.zip"
        zip2 = tmp_path / "test2.zip"

        for zp in [zip1, zip2]:
            with zipfile.ZipFile(zp, "w") as zf:
                zf.writestr("test.txt", "hello")

        with Unzipper() as unzipper:
            extracted1 = unzipper.extract(zip1)
            extracted2 = unzipper.extract(zip2)

            paths = [extracted1, extracted2]
            assert all(p.exists() for p in paths)

        assert not any(p.exists() for p in paths)
