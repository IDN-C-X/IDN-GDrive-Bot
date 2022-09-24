"""download plugins."""

import os

from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from gdrive import DOWNLOAD_DIRECTORY, LOGGER
from gdrive.config import BotCommands, Messages
from gdrive.helpers.downloader import download_file, utube_dl
from gdrive.helpers.gdrive_utils import GoogleDrive
from gdrive.helpers.utils import CustomFilters, humanbytes


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.text
    & (filters.command(BotCommands.Download) | filters.regex("^(ht|f)tp*"))
    & CustomFilters.auth_users
)
def _download(client: Client, message: Message):
    if message.media:
        return
    user_id = message.from_user.id
    sent_message = message.reply_text("🕵️**Checking link...**", quote=True)
    link = message.command[1] if message.command else message.text
    if "drive.google.com" in link:
        sent_message.edit(Messages.CLONING.format(link))
        LOGGER.info(f"Copy:{user_id}: {link}")
        msg = GoogleDrive(user_id).clone(link)
        sent_message.edit(msg)
    else:
        if "|" in link:
            link, filename = link.split("|")
            link = link.strip()
            filename.strip()
            dl_path = os.path.join(f"{DOWNLOAD_DIRECTORY}/{filename}")
        else:
            link = link.strip()
            filename = os.path.basename(link)
            dl_path = DOWNLOAD_DIRECTORY
        LOGGER.info(f"Download:{user_id}: {link}")
        sent_message.edit(Messages.DOWNLOADING.format(link))
        result, file_path = download_file(link, dl_path)
        if result == True:
            sent_message.edit(
                Messages.DOWNLOADED_SUCCESSFULLY.format(
                    os.path.basename(file_path), humanbytes(os.path.getsize(file_path))
                )
            )
            msg = GoogleDrive(user_id).upload_file(file_path)
            sent_message.edit(msg)
            LOGGER.info(f"Deleteing: {file_path}")
            os.remove(file_path)
        else:
            sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))


@Client.on_message(
    filters.private
    & filters.incoming
    & (filters.document | filters.audio | filters.video | filters.photo)
    & CustomFilters.auth_users
)
def _telegram_file(client: Client, message: Message):
    user_id = message.from_user.id
    sent_message = message.reply_text("🕵️**Checking File...**", quote=True)
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    elif message.photo:
        file = message.photo
        file.mime_type = "images/png"
        file.file_name = f"IMG-{user_id}-{message.id}.png"
    sent_message.edit(
        Messages.DOWNLOAD_TG_FILE.format(
            file.file_name, humanbytes(file.file_size), file.mime_type
        )
    )
    LOGGER.info(f"Download:{user_id}: {file.file_id}")
    try:
        file_path = message.download(file_name=DOWNLOAD_DIRECTORY)
        sent_message.edit(
            Messages.DOWNLOADED_SUCCESSFULLY.format(
                os.path.basename(file_path), humanbytes(os.path.getsize(file_path))
            )
        )
        msg = GoogleDrive(user_id).upload_file(file_path, file.mime_type)
        sent_message.edit(msg)
    except RPCError:
        sent_message.edit(Messages.WENT_WRONG)
    LOGGER.info(f"Deleteing: {file_path}")
    os.remove(file_path)


@Client.on_message(
    filters.incoming
    & filters.private
    & filters.command(BotCommands.YtDl)
    & CustomFilters.auth_users
)
def _ytdl(client: Client, message: Message):
    if len(message.command) > 1:
        sent_message = message.reply_text("🕵️**Checking Link...**", quote=True)
        link = message.command[1]
        user_id = message.from_user.id
        LOGGER.info(f"YTDL:{user_id}: {link}")
        sent_message.edit(Messages.DOWNLOADING.format(link))
        result, file_path = utube_dl(link)
        if result:
            sent_message.edit(
                Messages.DOWNLOADED_SUCCESSFULLY.format(
                    os.path.basename(file_path), humanbytes(os.path.getsize(file_path))
                )
            )
            msg = GoogleDrive(user_id).upload_file(file_path)
            sent_message.edit(msg)
            LOGGER.info(f"Deleteing: {file_path}")
            os.remove(file_path)
        else:
            sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))
    else:
        message.reply_text(Messages.PROVIDE_YTDL_LINK, quote=True)
