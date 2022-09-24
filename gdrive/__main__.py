"""gdrive-bot main bot."""

import logging
import os

from pyrogram.client import Client
from pyrogram.enums import ParseMode

from gdrive import API_HASH, APP_ID, BOT_TOKEN, DOWNLOAD_DIRECTORY

logging.basicConfig(level=logging.DEBUG, format="[IDN-GDrive-Bot] - %(message)s")
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


if __name__ == "__main__":
    if not os.path.isdir(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
    plugins = dict(root="gdrive/plugins")
    app = Client(
        name="IDN-GDrive-Bot",
        bot_token=BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH,
        plugins=plugins,
        parse_mode=ParseMode.MARKDOWN,
        workdir=DOWNLOAD_DIRECTORY,
        in_memory=True,
    )
    LOGGER.info("Starting Bot !")
    app.run()
    LOGGER.info("Bot Stopped !")
