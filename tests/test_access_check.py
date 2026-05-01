"""Tests for pure functions in bot/helper/aeon_utils/access_check.py.

Covers is_nsfw and is_nsfw_data.  The async functions (error_check,
token_check, etc.) depend on a live Telegram client and database and are
not tested here.

Note: conftest.py mocks bot.helper.ext_utils.help_messages with a small
representative nsfw_keywords list: ["porn", "nsfw", "adult", "nude",
"hentai", "xnxx", "xvideos"].
"""

import pytest

from bot.helper.aeon_utils.access_check import is_nsfw, is_nsfw_data


class TestIsNsfw:
    def test_clean_text_returns_false(self):
        assert is_nsfw("Download this movie please") is False

    def test_keyword_present_returns_true(self):
        assert is_nsfw("download porn now") is True

    def test_nsfw_keyword(self):
        assert is_nsfw("this content is nsfw") is True

    def test_case_insensitive_upper(self):
        assert is_nsfw("PORN video") is True

    def test_case_insensitive_mixed(self):
        assert is_nsfw("Hentai series") is True

    def test_keyword_at_start(self):
        assert is_nsfw("porn is in the file name") is True

    def test_keyword_at_end(self):
        assert is_nsfw("the file contains adult") is True

    def test_keyword_embedded_in_word_returns_false(self):
        # "adulteration" contains "adult" but not at a word boundary
        assert is_nsfw("adulteration process") is False

    def test_empty_string_returns_false(self):
        assert is_nsfw("") is False

    def test_only_whitespace_returns_false(self):
        assert is_nsfw("   ") is False

    def test_keyword_with_underscore_boundary(self):
        assert is_nsfw("_porn_file") is True

    def test_unrelated_keyword_like_component(self):
        assert is_nsfw("software component test") is False

    def test_multiple_keywords_returns_true(self):
        assert is_nsfw("adult nude content") is True


class TestIsNsfwData:
    # ── list input ──────────────────────────────────────────────────────────

    def test_empty_list_returns_false(self):
        assert is_nsfw_data([]) is False

    def test_list_of_clean_strings(self):
        assert is_nsfw_data(["movie.mp4", "documentary.mkv"]) is False

    def test_list_of_strings_with_nsfw(self):
        assert is_nsfw_data(["movie.mp4", "porn video.mp4"]) is True

    def test_list_of_clean_dicts(self):
        data = [{"name": "movie.mp4"}, {"name": "documentary.mkv"}]
        assert is_nsfw_data(data) is False

    def test_list_of_dicts_with_nsfw_name(self):
        data = [{"name": "movie.mp4"}, {"name": "xnxx clip.mp4"}]
        assert is_nsfw_data(data) is True

    def test_list_of_dicts_missing_name_key(self):
        data = [{"size": 1024}, {"type": "video"}]
        assert is_nsfw_data(data) is False

    def test_mixed_list_str_and_dict_clean(self):
        data = [{"name": "movie.mp4"}, "trailer.mkv"]
        assert is_nsfw_data(data) is False

    def test_mixed_list_str_and_dict_nsfw_in_string(self):
        data = [{"name": "movie.mp4"}, "adult clip.mkv"]
        assert is_nsfw_data(data) is True

    def test_mixed_list_str_and_dict_nsfw_in_dict(self):
        data = [{"name": "nude photo.jpg"}, "clean.mkv"]
        assert is_nsfw_data(data) is True

    # ── dict input ──────────────────────────────────────────────────────────

    def test_dict_with_clean_contents(self):
        data = {"contents": [{"filename": "movie.mp4"}, {"filename": "series.mkv"}]}
        assert is_nsfw_data(data) is False

    def test_dict_with_nsfw_filename(self):
        data = {"contents": [{"filename": "movie.mp4"}, {"filename": "hentai.mkv"}]}
        assert is_nsfw_data(data) is True

    def test_dict_with_empty_contents(self):
        data = {"contents": []}
        assert is_nsfw_data(data) is False

    def test_dict_without_contents_key(self):
        data = {"files": [{"filename": "porn.mp4"}]}
        assert is_nsfw_data(data) is False

    # ── other types ─────────────────────────────────────────────────────────

    def test_non_list_non_dict_returns_false(self):
        assert is_nsfw_data("raw string") is False
        assert is_nsfw_data(None) is False
        assert is_nsfw_data(42) is False
