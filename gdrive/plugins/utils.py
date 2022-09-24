"""utilities plugins."""

import shutil
from os import execl
from sys import executable
from time import sleep

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from gdrive import DOWNLOAD_DIRECTORY, LOGGER, SUDO_USERS


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(["log"])
    & filters.user(SUDO_USERS),
    group=2,
)
def _send_log(client: Client, message: Message):
    with open("log.txt", "rb") as f:
        try:
            client.send_document(
                chat_id=message.chat.id,
                document=f,
                file_name=f.name,
                reply_to_message_id=message.id,
            )
            LOGGER.info(f"Log file sent to {message.from_user.id}")
        except FloodWait as e:
            sleep(e.value)
        except RPCError as e:
            message.reply_text(e, quote=True)


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(["restart"])
    & filters.user(SUDO_USERS),
    group=2,
)
def _restart(client: Client, message: Message):
    shutil.rmtree(DOWNLOAD_DIRECTORY)
    LOGGER.info("Deleted DOWNLOAD_DIRECTORY successfully.")
    message.reply_text("**♻️Restarted Successfully !**", quote=True)
    LOGGER.info(f"{message.from_user.id}: Restarting...")
    execl(executable, executable, "-m", "gdrive")
