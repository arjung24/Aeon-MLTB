"""
Mocks for bot-package imports so the real source modules can be imported
cleanly in tests without a running Telegram client or database.

All sys.modules entries are set at module-load time so they are in place
before pytest imports any test file.
"""

import logging
import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

_logger = logging.getLogger("aeon_test")


def _mod(name: str, **attrs) -> ModuleType:
    """Create a plain ModuleType, register it in sys.modules, return it."""
    m = ModuleType(name)
    m.__spec__ = None
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m


# ── third-party stubs ─────────────────────────────────────────────────────────

_mod("uvloop", install=MagicMock())
_mod("apscheduler")
_mod("apscheduler.schedulers")
_mod("apscheduler.schedulers.asyncio", AsyncIOScheduler=MagicMock())
_mod("pytz", timezone=MagicMock())
_mod("sabnzbdapi", SabnzbdClient=MagicMock())

# aiofiles & aioshutil
_mod("aiofiles")
_mod(
    "aiofiles.os",
    listdir=AsyncMock(),
    remove=AsyncMock(),
    rmdir=AsyncMock(),
    symlink=AsyncMock(),
    makedirs=AsyncMock(),
    readlink=AsyncMock(),
    path=MagicMock(),
)
_mod("aioshutil", rmtree=AsyncMock(), move=AsyncMock())

# python-magic
_mod("magic", Magic=MagicMock())

# langcodes – Language.get(code).display_name() → "English" by default
_lang_instance = MagicMock()
_lang_instance.display_name.return_value = "English"
_Language = MagicMock()
_Language.get.return_value = _lang_instance
_mod("langcodes", Language=_Language)

# pyrogram
_pyrogram_errors = _mod(
    "pyrogram.errors",
    PeerIdInvalid=type(
        "PeerIdInvalid", (Exception,), {"NAME": "PeerIdInvalid", "MESSAGE": ""}
    ),
    RPCError=type("RPCError", (Exception,), {"NAME": "RPCError", "MESSAGE": ""}),
    UserNotParticipant=type("UserNotParticipant", (Exception,), {}),
)
_mod("pyrogram.enums")
_mod("pyrogram")

# ── bot package ───────────────────────────────────────────────────────────────

_bot = _mod(
    "bot",
    DOWNLOAD_DIR="/tmp/aeon_test_downloads/",
    LOGGER=_logger,
    user_data={},
    excluded_extensions=[],
    intervals={},
    multi_tags=set(),
    task_dict={},
    task_dict_lock=MagicMock(),
    cpu_eater_lock=MagicMock(),
)
_bot.__path__ = ["/home/user/Aeon-MLTB/bot"]
_bot.__package__ = "bot"

_bot_core = _mod("bot.core")
_bot_core.__path__ = ["/home/user/Aeon-MLTB/bot/core"]
_bot_core.__package__ = "bot.core"

_mod("bot.core.aeon_client", TgClient=MagicMock(NAME="testbot"))
# bot.core.config_manager is NOT mocked — the real module has only stdlib deps
# and must be importable as-is so test_config_manager.py tests the real class.
_mod("bot.core.torrent_manager", TorrentManager=MagicMock())

_bot_helper = _mod("bot.helper")
_bot_helper.__path__ = ["/home/user/Aeon-MLTB/bot/helper"]
_bot_helper.__package__ = "bot.helper"

_bot_ext = _mod("bot.helper.ext_utils")
_bot_ext.__path__ = ["/home/user/Aeon-MLTB/bot/helper/ext_utils"]
_bot_ext.__package__ = "bot.helper.ext_utils"

_mod(
    "bot.helper.ext_utils.bot_utils",
    cmd_exec=AsyncMock(),
    sync_to_async=AsyncMock(),
    get_size_bytes=MagicMock(),
    new_task=MagicMock(),
)
_mod(
    "bot.helper.ext_utils.status_utils",
    get_readable_file_size=MagicMock(return_value="1.0 GB"),
    get_readable_time=MagicMock(return_value="1h 0m"),
)
_mod("bot.helper.ext_utils.db_handler", database=MagicMock())

# nsfw_keywords: a small representative subset used in access_check tests
_mod(
    "bot.helper.ext_utils.help_messages",
    nsfw_keywords=["porn", "nsfw", "adult", "nude", "hentai", "xnxx", "xvideos"],
)

_bot_aeon = _mod("bot.helper.aeon_utils")
_bot_aeon.__path__ = ["/home/user/Aeon-MLTB/bot/helper/aeon_utils"]
_bot_aeon.__package__ = "bot.helper.aeon_utils"

_mod(
    "bot.helper.aeon_utils.shorteners",
    short=AsyncMock(return_value="https://short.url/token"),
)

_mod("bot.helper.telegram_helper")
_mod("bot.helper.telegram_helper.bot_commands", BotCommands=MagicMock())
_mod("bot.helper.telegram_helper.button_build", ButtonMaker=MagicMock())
