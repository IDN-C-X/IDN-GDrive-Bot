"""help plugins."""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message 

from gdrive import SUPPORT_CHAT_LINK
from gdrive.config import Messages as tr


@Client.on_message(filters.private & filters.incoming & filters.command(['start']), group=2)
def _start(client: Client, message: Message):
    client.send_message(chat_id = message.chat.id,
        text = tr.START_MSG.format(message.from_user.mention),
        reply_to_message_id = message.id
    )


@Client.on_message(filters.private & filters.incoming & filters.command(['help']), group=2)
def _help(client: Client, message: Message):
    client.send_message(chat_id = message.chat.id,
        text = tr.HELP_MSG[1],
        reply_markup = InlineKeyboardMarkup(map(1)),
        reply_to_message_id = message.id
    )

help_callback_filter = filters.create(lambda _, __, query: query.data.startswith('help+'))

@Client.on_callback_query(help_callback_filter)
def help_answer(c: Client, cb: CallbackQuery):
    chat_id = cb.from_user.id
    message_id = cb.message.id
    msg = int(cb.data.split('+')[1])
    c.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text = tr.HELP_MSG[msg],
        reply_markup = InlineKeyboardMarkup(map(msg))
    )


def map(pos):
    if (pos==1):
        return [
            [InlineKeyboardButton(text = '-->', callback_data = "help+2")]
        ]
    elif pos==len(tr.HELP_MSG)-1:

        return [
            [
             InlineKeyboardButton(text = 'Support Chat', url = SUPPORT_CHAT_LINK),
             InlineKeyboardButton(text = 'Channel Update', url = "t.me/IDNCoder")
            ],
            [InlineKeyboardButton(text = '<--', callback_data = f"help+{pos-1}")]

        ]
    else:
        return [
            [
                InlineKeyboardButton(text = '<--', callback_data = f"help+{pos-1}"),
                InlineKeyboardButton(text = '-->', callback_data = f"help+{pos+1}")
            ],
        ]
