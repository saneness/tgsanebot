import telegram
from telegram.constants import ParseMode
from functools import partial
from commands.utils import *
from config import *

common = partial(blacklist, ids=COMMON_IDS_BLACKLIST)

@common
async def start(update, context):
    reply_markup = telegram.ReplyKeyboardRemove()
    text = 'I\'m a `TGSaneBot`! What do you want?'
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

@common
async def help(update, context):
    text = \
        '`common commands:`\n' \
        '`/start   ` (re)start bot\n' \
        '`/help    ` show this message\n' \
        '`/status  ` show host status\n\n' \
        '`openai commands:`\n' \
        '`/image   ` generate image from prompt\n' \
        '`/image_w ` generate wide image from prompt\n' \
        '`/clear   ` clear history for your chat\n' \
        '`(to have a chat just sent a message)`\n\n' \
        '`upload commands:`\n' \
        '`/ls      ` list file(s)\n' \
        '`/rm      ` remove file(s)\n' \
        '`/mv      ` move file\n' \
        '`(to upload a file just send it)`\n\n' \
        '`admin commands:`\n' \
        '`/rrc     ` run remote command\n' \
        '`/wol     ` start pc'
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

@common
async def status(update, context):
    command = ['monitor', '-c']
    text = Utils.subprocess(command)
    message_result = await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)
