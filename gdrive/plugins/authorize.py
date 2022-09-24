"""authority plugins."""


from httplib2 import Http
from oauth2client.client import FlowExchangeError, OAuth2WebServerFlow
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from gdrive import G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET, LOGGER
from gdrive.config import BotCommands, Messages
from gdrive.helpers.sql_helper import gDriveDB
from gdrive.helpers.utils import CustomFilters

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

flow = None


@Client.on_message(
    filters.private & filters.incoming & filters.command(BotCommands.Authorize)
)
async def _auth(client: Client, message: Message):
    user_id = message.from_user.id
    creds = gDriveDB.search(user_id)
    if creds is not None:
        creds.refresh(Http())
        gDriveDB._set(user_id, creds)
        await message.reply_text(Messages.ALREADY_AUTH, quote=True)
    else:
        global flow
        try:
            flow = OAuth2WebServerFlow(
                G_DRIVE_CLIENT_ID,
                G_DRIVE_CLIENT_SECRET,
                OAUTH_SCOPE,
                redirect_uri=REDIRECT_URI,
            )
            auth_url = flow.step1_get_authorize_url()
            LOGGER.info(f"AuthURL:{user_id}")
            await message.reply_text(
                text=Messages.AUTH_TEXT.format(auth_url),
                quote=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Authorization URL", url=auth_url)]]
                ),
            )
        except Exception as e:
            await message.reply_text(f"**ERROR:** ```{e}```", quote=True)


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(BotCommands.Revoke)
    & CustomFilters.auth_users
)
def _revoke(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        gDriveDB._clear(user_id)
        LOGGER.info(f"Revoked:{user_id}")
        message.reply_text(Messages.REVOKED, quote=True)
    except Exception as e:
        message.reply_text(f"**ERROR:** ```{e}```", quote=True)


@Client.on_message(
    filters.private & filters.incoming & filters.text & ~CustomFilters.auth_users
)
async def _token(client: Client, message: Message):
    token = message.text.split()[-1]
    WORD = len(token)
    if WORD == 62 and token[1] == "/":
        creds = None
        global flow
        if flow:
            try:
                user_id = message.from_user.id
                sent_message = await message.reply_text(
                    "🕵️**Checking received code...**", quote=True
                )
                creds = flow.step2_exchange(message.text)
                gDriveDB._set(user_id, creds)
                LOGGER.info(f"AuthSuccess: {user_id}")
                await sent_message.edit(Messages.AUTH_SUCCESSFULLY)
                flow = None
            except FlowExchangeError:
                await sent_message.edit(Messages.INVALID_AUTH_CODE)
            except Exception as e:
                await sent_message.edit(f"**ERROR:** ```{e}```")
        else:
            await message.reply_text(Messages.FLOW_IS_NONE, quote=True)
