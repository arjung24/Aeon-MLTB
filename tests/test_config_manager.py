"""Tests for bot/core/config_manager.py — Config._convert and _normalize_value.

config_manager has no external dependencies so it can be imported directly
without any sys.modules mocking.
"""

import pytest

from bot.core.config_manager import Config


@pytest.fixture(autouse=True)
def _reset_config():
    """Restore Config class attributes after every test."""
    original = {k: getattr(Config, k) for k in Config.__annotations__}
    yield
    for k, v in original.items():
        setattr(Config, k, v)


# ── Config._convert ────────────────────────────────────────────────────────────


class TestConvertBool:
    def test_true_strings(self):
        for val in ("true", "True", "TRUE", "1", "yes", "Yes"):
            assert Config._convert("IS_TEAM_DRIVE", val) is True, (
                f"failed for {val!r}"
            )

    def test_false_strings(self):
        for val in ("false", "False", "0", "no", "random"):
            assert Config._convert("IS_TEAM_DRIVE", val) is False, (
                f"failed for {val!r}"
            )

    def test_native_bool_passthrough(self):
        assert Config._convert("IS_TEAM_DRIVE", True) is True
        assert Config._convert("IS_TEAM_DRIVE", False) is False

    def test_none_returns_none(self):
        assert Config._convert("IS_TEAM_DRIVE", None) is None


class TestConvertInt:
    def test_string_to_int(self):
        assert Config._convert("OWNER_ID", "12345") == 12345

    def test_native_int_passthrough(self):
        assert Config._convert("OWNER_ID", 99) == 99

    def test_invalid_string_raises(self):
        with pytest.raises(TypeError):
            Config._convert("OWNER_ID", "not_a_number")

    def test_none_returns_none(self):
        assert Config._convert("OWNER_ID", None) is None


class TestConvertStr:
    def test_string_passthrough(self):
        assert Config._convert("BOT_TOKEN", "abc123") == "abc123"

    def test_none_returns_none(self):
        assert Config._convert("BOT_TOKEN", None) is None


class TestConvertDict:
    def test_valid_json_string(self):
        result = Config._convert("FFMPEG_CMDS", '{"cmd1": ["arg1", "arg2"]}')
        assert result == {"cmd1": ["arg1", "arg2"]}

    def test_native_dict_passthrough(self):
        d = {"key": "value"}
        assert Config._convert("FFMPEG_CMDS", d) == d

    def test_empty_string_returns_empty_dict(self):
        assert Config._convert("FFMPEG_CMDS", "") == {}

    def test_invalid_string_raises(self):
        with pytest.raises(TypeError):
            Config._convert("FFMPEG_CMDS", "not a dict")

    def test_list_string_for_dict_raises(self):
        with pytest.raises(TypeError):
            Config._convert("FFMPEG_CMDS", '["a", "b"]')


class TestConvertLeechDumpChat:
    def test_single_string_id(self):
        assert Config._convert("LEECH_DUMP_CHAT", "-1001234567") == ["-1001234567"]

    def test_list_string_parses_to_list(self):
        result = Config._convert("LEECH_DUMP_CHAT", '["-1001", "-1002"]')
        assert result == ["-1001", "-1002"]

    def test_native_list_passthrough(self):
        result = Config._convert("LEECH_DUMP_CHAT", ["-1001", "-1002"])
        assert result == ["-1001", "-1002"]

    def test_list_with_ints_converted_to_strings(self):
        result = Config._convert("LEECH_DUMP_CHAT", [-1001, -1002])
        assert result == ["-1001", "-1002"]

    def test_empty_string_returns_empty_list(self):
        assert Config._convert("LEECH_DUMP_CHAT", "") == []

    def test_whitespace_only_string_returns_empty_list(self):
        assert Config._convert("LEECH_DUMP_CHAT", "   ") == []

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError):
            Config._convert("LEECH_DUMP_CHAT", 12345)


# ── Config._normalize_value ────────────────────────────────────────────────────


class TestNormalizeDefaultUpload:
    def test_valid_values_accepted(self):
        assert Config._normalize_value("DEFAULT_UPLOAD", "gd") == "gd"
        assert Config._normalize_value("DEFAULT_UPLOAD", "yt") == "yt"
        assert Config._normalize_value("DEFAULT_UPLOAD", "rc") == "rc"

    def test_case_insensitive(self):
        assert Config._normalize_value("DEFAULT_UPLOAD", "GD") == "gd"
        assert Config._normalize_value("DEFAULT_UPLOAD", "YT") == "yt"

    def test_invalid_value_falls_back_to_gd(self):
        assert Config._normalize_value("DEFAULT_UPLOAD", "s3") == "gd"
        assert Config._normalize_value("DEFAULT_UPLOAD", "") == "gd"


class TestNormalizeUrlFields:
    def test_base_url_trailing_slash_stripped(self):
        assert (
            Config._normalize_value("BASE_URL", "https://example.com/")
            == "https://example.com"
        )

    def test_base_url_multiple_slashes_stripped(self):
        assert (
            Config._normalize_value("BASE_URL", "https://example.com///")
            == "https://example.com"
        )

    def test_rclone_serve_url_trailing_slash_stripped(self):
        assert (
            Config._normalize_value("RCLONE_SERVE_URL", "http://host:8080/")
            == "http://host:8080"
        )

    def test_index_url_trailing_slash_stripped(self):
        assert (
            Config._normalize_value("INDEX_URL", "https://index.example.com/")
            == "https://index.example.com"
        )

    def test_url_without_trailing_slash_unchanged(self):
        assert (
            Config._normalize_value("BASE_URL", "https://example.com")
            == "https://example.com"
        )


class TestNormalizeWhitespace:
    def test_string_values_stripped(self):
        assert Config._normalize_value("BOT_TOKEN", "  abc123  ") == "abc123"

    def test_non_string_values_unchanged(self):
        assert Config._normalize_value("OWNER_ID", 42) == 42
        assert Config._normalize_value("IS_TEAM_DRIVE", True) is True


class TestNormalizeUsenetServers:
    def test_valid_server_list_accepted(self):
        servers = [{"host": "news.example.com", "port": 119}]
        assert Config._normalize_value("USENET_SERVERS", servers) == servers

    def test_empty_list_returns_empty(self):
        assert Config._normalize_value("USENET_SERVERS", []) == []

    def test_list_without_host_key_returns_empty(self):
        assert Config._normalize_value("USENET_SERVERS", [{"port": 119}]) == []

    def test_non_list_returns_empty(self):
        assert Config._normalize_value("USENET_SERVERS", "news.example.com") == []


# ── Config.set / Config.get round-trip ────────────────────────────────────────


class TestConfigSetGet:
    def test_set_and_get_bool(self):
        Config.set("IS_TEAM_DRIVE", "true")
        assert Config.get("IS_TEAM_DRIVE") is True

    def test_set_and_get_int(self):
        Config.set("OWNER_ID", "99999")
        assert Config.get("OWNER_ID") == 99999

    def test_set_and_get_str(self):
        Config.set("BOT_TOKEN", "mytoken123")
        assert Config.get("BOT_TOKEN") == "mytoken123"

    def test_set_unknown_key_raises(self):
        with pytest.raises(KeyError):
            Config.set("NONEXISTENT_KEY", "value")

    def test_get_unknown_key_returns_none(self):
        assert Config.get("NONEXISTENT_KEY") is None

    def test_get_all_returns_all_annotated_keys(self):
        result = Config.get_all()
        assert isinstance(result, dict)
        for key in Config.__annotations__:
            assert key in result
