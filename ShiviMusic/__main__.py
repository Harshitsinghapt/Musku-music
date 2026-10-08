import asyncio
import importlib
import os

from aiohttp import web
from pyrogram import idle
from pyrogram.errors import NoActiveGroupCall

import config
from ShiviMusic import LOGGER, app, userbot
from ShiviMusic.core.call import Shivi
from ShiviMusic.misc import sudo
from ShiviMusic.plugins import ALL_MODULES
from ShiviMusic.utils.database import get_banned_users, get_banned
from config import BANNED_USERS


async def health(request):
    return web.Response(text="OK")


async def start_web_server():
    web_app = web.Application()
    web_app.router.add_get("/", health)
    web_app.router.add_get("/health", health)

    runner = web.AppRunner(web_app)
    await runner.setup()

    port = int(os.environ.get("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    LOGGER(__name__).info(f"WEB SERVER STARTED ON PORT {port}")
    return runner


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "STRING SESSION NOT FILLED, PLEASE FILL A PYROGRAM SESSION."
        )
        exit()

    await sudo()

    web_runner = await start_web_server()

    try:
        users = await get_banned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("ShiviMusic.plugins." + all_module)

    LOGGER("ShiviMusic.plugins").info(
        "ALL PLUGINS LOADED SUCCESSFULLY..."
    )

    await userbot.start()
    await Shivi.start()

    try:
        await Shivi.stream_call(
            "https://telegra.ph/file/29f784eb49d230ab62e9e.mp4"
        )
    except NoActiveGroupCall:
        LOGGER(__name__).error(
            "PLEASE START YOUR LOG GROUP/CHANNEL VOICECHAT."
        )
        exit()
    except Exception:
        pass

    await Shivi.decorators()

    LOGGER("ShiviMusic").info(
        "MUSIC BOT STARTED SUCCESSFULLY..."
    )

    await idle()

    await web_runner.cleanup()
    await app.stop()
    await userbot.stop()

    LOGGER("ShiviMusic").info("STOP MUSIC BOT...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
