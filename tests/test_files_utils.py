"""Tests for pure functions in bot/helper/ext_utils/files_utils.py.

Covers archive detection helpers and get_base_name.  The async I/O functions
are not tested here — they require real filesystem access and subprocess calls.
"""

import pytest

from bot.helper.ext_utils.exceptions import NotSupportedExtractionArchive
from bot.helper.ext_utils.files_utils import (
    get_base_name,
    is_archive,
    is_archive_split,
    is_first_archive_split,
)


class TestIsArchive:
    def test_zip(self):
        assert is_archive("file.zip") is True

    def test_tar_gz(self):
        assert is_archive("archive.tar.gz") is True

    def test_rar(self):
        assert is_archive("archive.rar") is True

    def test_7z(self):
        assert is_archive("archive.7z") is True

    def test_bz2(self):
        assert is_archive("file.bz2") is True

    def test_tar(self):
        assert is_archive("file.tar") is True

    def test_gz(self):
        assert is_archive("file.gz") is True

    def test_iso(self):
        assert is_archive("disk.iso") is True

    def test_deb(self):
        assert is_archive("package.deb") is True

    def test_zst(self):
        assert is_archive("file.zst") is True

    def test_case_insensitive_upper(self):
        assert is_archive("FILE.ZIP") is True

    def test_case_insensitive_mixed(self):
        assert is_archive("Archive.Tar.Gz") is True

    def test_mp4_not_archive(self):
        assert is_archive("video.mp4") is False

    def test_mkv_not_archive(self):
        assert is_archive("video.mkv") is False

    def test_pdf_not_archive(self):
        assert is_archive("document.pdf") is False

    def test_no_extension(self):
        assert is_archive("filename") is False

    def test_path_with_archive_extension(self):
        assert is_archive("/some/path/archive.zip") is True

    def test_whitespace_around_name(self):
        assert is_archive("  archive.zip  ") is True


class TestIsFirstArchiveSplit:
    def test_part01_rar(self):
        assert is_first_archive_split("archive.part01.rar") is True

    def test_part001_rar(self):
        assert is_first_archive_split("archive.part001.rar") is True

    def test_7z_01(self):
        assert is_first_archive_split("archive.7z.01") is True

    def test_7z_001(self):
        assert is_first_archive_split("archive.7z.001") is True

    def test_zip_01(self):
        assert is_first_archive_split("archive.zip.01") is True

    def test_single_rar_no_part_number(self):
        assert is_first_archive_split("archive.rar") is True

    def test_part02_rar_not_first(self):
        assert is_first_archive_split("archive.part02.rar") is False

    def test_part10_rar_not_first(self):
        assert is_first_archive_split("archive.part10.rar") is False

    def test_7z_02_not_first(self):
        assert is_first_archive_split("archive.7z.02") is False

    def test_zip_file_not_split(self):
        assert is_first_archive_split("archive.zip") is False

    def test_mp4_not_split(self):
        assert is_first_archive_split("video.mp4") is False


class TestIsArchiveSplit:
    def test_r_extension(self):
        assert is_archive_split("archive.r01") is True

    def test_r_extension_large_num(self):
        assert is_archive_split("archive.r99") is True

    def test_7z_numbered(self):
        assert is_archive_split("archive.7z.001") is True

    def test_z_numbered(self):
        assert is_archive_split("archive.z01") is True

    def test_zip_numbered(self):
        assert is_archive_split("archive.zip.002") is True

    def test_partN_rar(self):
        assert is_archive_split("archive.part2.rar") is True

    def test_part01_rar(self):
        assert is_archive_split("archive.part01.rar") is True

    def test_regular_rar_not_split(self):
        assert is_archive_split("archive.rar") is False

    def test_regular_zip_not_split(self):
        assert is_archive_split("archive.zip") is False

    def test_mp4_not_split(self):
        assert is_archive_split("video.mp4") is False

    def test_case_insensitive(self):
        assert is_archive_split("archive.R01") is True


class TestGetBaseName:
    def test_tar_gz(self):
        assert get_base_name("path/to/file.tar.gz") == "path/to/file"

    def test_zip(self):
        assert get_base_name("archive.zip") == "archive"

    def test_rar(self):
        assert get_base_name("archive.rar") == "archive"

    def test_7z(self):
        assert get_base_name("archive.7z") == "archive"

    def test_tar(self):
        assert get_base_name("file.tar") == "file"

    def test_gz(self):
        assert get_base_name("file.gz") == "file"

    def test_full_path(self):
        assert get_base_name("/downloads/movie.zip") == "/downloads/movie"

    def test_case_insensitive_extension(self):
        assert get_base_name("archive.ZIP") == "archive"

    def test_tar_bz2(self):
        assert get_base_name("file.tar.bz2") == "file"

    def test_unsupported_extension_raises(self):
        with pytest.raises(NotSupportedExtractionArchive):
            get_base_name("video.mp4")

    def test_no_extension_raises(self):
        with pytest.raises(NotSupportedExtractionArchive):
            get_base_name("justfilename")

    def test_pdf_raises(self):
        with pytest.raises(NotSupportedExtractionArchive):
            get_base_name("document.pdf")
