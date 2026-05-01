"""Tests for bot/helper/ext_utils/links_utils.py.

All functions are pure (regex / string checks) with no external dependencies.
"""

import pytest

from bot.helper.ext_utils.links_utils import (
    is_gdrive_id,
    is_gdrive_link,
    is_magnet,
    is_rclone_path,
    is_share_link,
    is_telegram_link,
    is_url,
)


class TestIsMagnet:
    def test_valid_btih_40_char(self):
        uri = "magnet:?xt=urn:btih:ABCDEF1234567890ABCDEF1234567890ABCDEF12&dn=test"
        assert is_magnet(uri) is True

    def test_valid_btih_32_char(self):
        uri = "magnet:?xt=urn:btih:ABCDEF1234567890ABCDEF1234567890"
        assert is_magnet(uri) is True

    def test_valid_btmh(self):
        uri = "magnet:?xt=urn:btmh:abcdefghijklmnopqrstuvwxyz234567"
        assert is_magnet(uri) is True

    def test_invalid_no_xt(self):
        assert is_magnet("magnet:?dn=test") is False

    def test_invalid_wrong_scheme(self):
        assert is_magnet("https://example.com") is False

    def test_invalid_empty_string(self):
        assert is_magnet("") is False

    def test_invalid_hash_too_short(self):
        assert is_magnet("magnet:?xt=urn:btih:ABCD") is False


class TestIsUrl:
    def test_https(self):
        assert is_url("https://example.com") is True

    def test_http(self):
        assert is_url("http://example.com/path?q=1") is True

    def test_ftp(self):
        assert is_url("ftp://files.example.com/file.zip") is True

    def test_rtmp(self):
        assert is_url("rtmp://stream.example.com/live") is True

    def test_with_port(self):
        assert is_url("https://example.com:8080/path") is True

    def test_with_auth(self):
        assert is_url("https://user:pass@example.com") is True

    def test_plain_string(self):
        assert is_url("not a url") is False

    def test_empty_string(self):
        assert is_url("") is False

    def test_only_domain(self):
        assert is_url("example.com") is True

    def test_local_path(self):
        assert is_url("/local/file/path") is False


class TestIsGdriveLink:
    def test_drive_google_com(self):
        assert is_gdrive_link("https://drive.google.com/file/d/abc123") is True

    def test_drive_usercontent_google_com(self):
        assert is_gdrive_link("https://drive.usercontent.google.com/download?id=abc") is True

    def test_regular_google(self):
        assert is_gdrive_link("https://docs.google.com/spreadsheets") is False

    def test_other_url(self):
        assert is_gdrive_link("https://example.com") is False

    def test_partial_match_in_path(self):
        assert is_gdrive_link("https://fake.com/drive.google.com/") is True


class TestIsTelegramLink:
    def test_t_me_link(self):
        assert is_telegram_link("https://t.me/somechannel/123") is True

    def test_tg_openmessage(self):
        assert is_telegram_link("tg://openmessage?user_id=12345&message_id=99") is True

    def test_other_https(self):
        assert is_telegram_link("https://example.com") is False

    def test_empty_string(self):
        assert is_telegram_link("") is False

    def test_partial_prefix(self):
        assert is_telegram_link("http://t.me/channel") is False


class TestIsShareLink:
    def test_gdtot_domain(self):
        assert is_share_link("https://example.gdtot.xyz/file") is True

    def test_filepress(self):
        assert is_share_link("https://filepress.online/file/abc") is True

    def test_filebee(self):
        assert is_share_link("https://filebee.online/file/xyz") is True

    def test_appdrive(self):
        assert is_share_link("https://appdrive.info/file/abc") is True

    def test_gdflix(self):
        assert is_share_link("https://gdflix.site/file/abc") is True

    def test_regular_url(self):
        assert is_share_link("https://example.com/file") is False

    def test_empty_string(self):
        assert is_share_link("") is False


class TestIsRclonePath:
    def test_simple_remote_path(self):
        assert is_rclone_path("gdrive:path/to/folder") is True

    def test_mrcc_prefixed(self):
        assert is_rclone_path("mrcc:gdrive:path/to/folder") is True

    def test_rcl_shorthand(self):
        assert is_rclone_path("rcl") is True

    def test_magnet_not_rclone(self):
        assert is_rclone_path("magnet:?xt=urn:btih:abc") is False

    def test_mtp_prefix_not_rclone(self):
        assert is_rclone_path("mtp:something") is False

    def test_sa_prefix_not_rclone(self):
        assert is_rclone_path("sa:something") is False

    def test_tp_prefix_not_rclone(self):
        assert is_rclone_path("tp:something") is False

    def test_local_absolute_path(self):
        assert is_rclone_path("/local/path") is False

    def test_remote_with_http(self):
        assert is_rclone_path("remote://path") is False


class TestIsGdriveId:
    def test_33_char_id(self):
        assert is_gdrive_id("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs") is True

    def test_19_char_id(self):
        assert is_gdrive_id("1BxiMVs0XRA5nFMdKvB") is True

    def test_gdl_shorthand(self):
        assert is_gdrive_id("gdl") is True

    def test_root(self):
        assert is_gdrive_id("root") is True

    def test_tp_root(self):
        assert is_gdrive_id("tp:root") is True

    def test_mtp_root(self):
        assert is_gdrive_id("mtp:root") is True

    def test_sa_prefixed_id(self):
        assert is_gdrive_id("sa:1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs") is True

    def test_tp_prefixed_id(self):
        assert is_gdrive_id("tp:1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs") is True

    def test_too_short(self):
        assert is_gdrive_id("short") is False

    def test_too_long(self):
        assert is_gdrive_id("A" * 34) is False

    def test_empty_string(self):
        assert is_gdrive_id("") is False

    def test_url_not_id(self):
        assert is_gdrive_id("https://drive.google.com/file/d/abc") is False
