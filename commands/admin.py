import telegram
from telegram.constants import ParseMode
from functools import partial
from commands.utils import *
from config import *

admin = partial(whitelist, ids=ADMIN_IDS)

@admin
async def rrc(update, context):
    if len(context.args) > 0:
        command = context.args
        text = Utils.subprocess(command)
    else:
        text = 'Empty command. Nothing to do.'
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(' '.join(command), title='command'), parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)

@admin
async def wol(update, context):
    command = ['wol']
    text = Utils.subprocess(command)
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)