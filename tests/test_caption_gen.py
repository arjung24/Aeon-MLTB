"""Tests for pure helpers in bot/helper/aeon_utils/caption_gen.py.

Covers get_video_quality, parse_audio_language, parse_subtitle_language,
and calculate_md5.  The async generate_caption function is not tested here
as it requires mediainfo to be installed and a real file on disk.
"""

import hashlib

from bot.helper.aeon_utils.caption_gen import (
    calculate_md5,
    get_video_quality,
    parse_audio_language,
    parse_subtitle_language,
)


class TestGetVideoQuality:
    def test_exact_480(self):
        assert get_video_quality(480) == "480p"

    def test_exact_540(self):
        assert get_video_quality(540) == "540p"

    def test_exact_720(self):
        assert get_video_quality(720) == "720p"

    def test_exact_1080(self):
        assert get_video_quality(1080) == "1080p"

    def test_exact_2160(self):
        assert get_video_quality(2160) == "2160p"

    def test_exact_4320(self):
        assert get_video_quality(4320) == "4320p"

    def test_exact_8640(self):
        assert get_video_quality(8640) == "8640p"

    def test_below_480_maps_to_480p(self):
        assert get_video_quality(1) == "480p"
        assert get_video_quality(240) == "480p"
        assert get_video_quality(479) == "480p"

    def test_between_480_and_540(self):
        assert get_video_quality(481) == "540p"
        assert get_video_quality(539) == "540p"

    def test_between_540_and_720(self):
        assert get_video_quality(541) == "720p"

    def test_between_720_and_1080(self):
        assert get_video_quality(721) == "1080p"

    def test_above_8640_returns_unknown(self):
        assert get_video_quality(8641) == "Unknown"
        assert get_video_quality(99999) == "Unknown"

    def test_none_returns_unknown(self):
        assert get_video_quality(None) == "Unknown"

    def test_zero_returns_unknown(self):
        assert get_video_quality(0) == "Unknown"

    def test_string_height_coerced(self):
        assert get_video_quality("1080") == "1080p"


class TestParseAudioLanguage:
    def test_adds_language_to_empty_string(self):
        result = parse_audio_language("", {"Language": "en"})
        assert result == "English"

    def test_no_language_key_returns_unchanged(self):
        result = parse_audio_language("", {})
        assert result == ""

    def test_no_language_key_preserves_existing(self):
        result = parse_audio_language("English", {})
        assert result == "English"

    def test_no_duplicate_added(self):
        result = parse_audio_language("English", {"Language": "en"})
        assert result == "English"
        assert result.count("English") == 1

    def test_none_language_value_returns_unchanged(self):
        result = parse_audio_language("", {"Language": None})
        assert result == ""

    def test_strips_trailing_comma(self):
        result = parse_audio_language("", {"Language": "en"})
        assert not result.endswith(",")
        assert not result.endswith(", ")


class TestParseSubtitleLanguage:
    def test_adds_language_to_empty_string(self):
        result = parse_subtitle_language("", {"Language": "en"})
        assert result == "English"

    def test_no_language_key_returns_unchanged(self):
        result = parse_subtitle_language("", {})
        assert result == ""

    def test_no_duplicate_added(self):
        result = parse_subtitle_language("English", {"Language": "en"})
        assert result == "English"
        assert result.count("English") == 1

    def test_none_language_value_returns_unchanged(self):
        result = parse_subtitle_language("", {"Language": None})
        assert result == ""

    def test_strips_trailing_comma(self):
        result = parse_subtitle_language("", {"Language": "fr"})
        assert not result.endswith(",")
        assert not result.endswith(", ")


class TestCalculateMd5:
    def test_known_hash(self, tmp_path):
        data = b"hello world"
        f = tmp_path / "test.txt"
        f.write_bytes(data)
        expected = hashlib.md5(data).hexdigest()
        assert calculate_md5(str(f)) == expected

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        expected = hashlib.md5(b"").hexdigest()
        assert calculate_md5(str(f)) == expected

    def test_large_file_chunked(self, tmp_path):
        data = b"x" * (4096 * 3 + 500)
        f = tmp_path / "large.bin"
        f.write_bytes(data)
        expected = hashlib.md5(data).hexdigest()
        assert calculate_md5(str(f)) == expected

    def test_returns_hex_string(self, tmp_path):
        f = tmp_path / "data.bin"
        f.write_bytes(b"test")
        result = calculate_md5(str(f))
        assert isinstance(result, str)
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)
