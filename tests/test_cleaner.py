import pytest
from pathlib import Path
from any2md.cleaner import FilenameCleaner


class TestFilenameCleaner:
    def test_default_config(self):
        cleaner = FilenameCleaner()

        assert cleaner.config["remove_special_chars"] is True
        assert cleaner.config["replace_spaces_with"] == "_"
        assert cleaner.config["lowercase"] is False
        assert cleaner.config["max_length"] == 200

    def test_custom_config(self):
        config = {"lowercase": True, "max_length": 50}
        cleaner = FilenameCleaner(config)

        assert cleaner.config["lowercase"] is True
        assert cleaner.config["max_length"] == 50

    def test_clean_illegal_chars(self):
        cleaner = FilenameCleaner()

        assert cleaner.clean("test<file>.txt") == "testfile.txt"
        assert cleaner.clean("file:name.pdf") == "filename.pdf"
        assert cleaner.clean("a/b\\c.docx") == "abc.docx"
        assert cleaner.clean("file?name*.html") == "filename.html"
        assert cleaner.clean('file"name.md') == "filename.md"

    def test_replace_spaces(self):
        cleaner = FilenameCleaner()

        assert cleaner.clean("my file name.txt") == "my_file_name.txt"
        assert cleaner.clean("multiple   spaces.pdf") == "multiple_spaces.pdf"

    def test_replace_spaces_custom_char(self):
        cleaner = FilenameCleaner({"replace_spaces_with": "-"})

        assert cleaner.clean("my file name.txt") == "my-file-name.txt"

    def test_no_space_replacement(self):
        cleaner = FilenameCleaner({"replace_spaces_with": ""})

        assert cleaner.clean("my file.txt") == "my file.txt"

    def test_lowercase(self):
        cleaner = FilenameCleaner({"lowercase": True})

        assert cleaner.clean("MyFileName.TXT") == "myfilename.txt"

    def test_max_length(self):
        cleaner = FilenameCleaner({"max_length": 10})

        result = cleaner.clean("verylongfilename.txt")
        stem = Path(result).stem
        assert len(stem) <= 10
        assert result.endswith(".txt")

    def test_preserve_extension(self):
        cleaner = FilenameCleaner()

        assert cleaner.clean("file.pdf").endswith(".pdf")
        assert cleaner.clean("file.DOCX").endswith(".DOCX")
        assert cleaner.clean("file.tar.gz").endswith(".gz")

    def test_clean_path(self):
        cleaner = FilenameCleaner()

        path = Path("/some/dir/my file<name>.txt")
        cleaned = cleaner.clean_path(path)

        assert cleaned.parent == Path("/some/dir")
        assert cleaned.name == "my_filename.txt"

    def test_empty_filename(self):
        cleaner = FilenameCleaner()

        result = cleaner.clean(".txt")
        assert result == ".txt"

    def test_multiple_underscores_collapsed(self):
        cleaner = FilenameCleaner()

        result = cleaner.clean("file___name.txt")
        assert result == "file_name.txt"
