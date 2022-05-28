import telegram

from config import *
from commands.utils import *
from functools import partial

common = partial(Utils.whitelist, ids=COMMON_IDS)

@common
def start(update, context):
    reply_markup = telegram.ReplyKeyboardRemove()
    text = 'I\'m a `TGSaneBot`! What do you want?'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)

@common
def help(update, context):
    text = \
        '`common commands:`\n' \
        '`/start ` (re)start bot\n' \
        '`/help  ` show this message\n\n' \
        '`upload commands:`\n' \
        '`/ls ` list file(s)\n' \
        '`/rm ` remove file(s)\n' \
        '`/mv ` move file\n' \
        '`(to upload a file just send it)`\n\n' \
        '`route commands:`\n' \
        '`/routes  ` list routed domains\n' \
        '`/add     ` add domain(s) to routing\n' \
        '`/remove  ` remove domain(s) from routing\n\n' \
        '`admin commands:`\n' \
        '`/rrc     ` run remote command\n' \
        '`/pxlpass ` show pxl password'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)