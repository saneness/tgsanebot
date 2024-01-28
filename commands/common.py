import telegram
from telegram.constants import ParseMode

import os
import subprocess

from config import *
from commands.utils import *
from functools import partial

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
        '`/image_w ` generate wide image from prompt\n\n' \
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
    os.environ['PYTHONPATH']=PYTHONPATH
    command = 'monitor -c'
    try:
        result = subprocess.check_output(command.split(), stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as err:
        result = err.output.decode('utf-8')
    except Exception as err:
        result = str(err)
    except:
        result = 'Something went wrong.'
    os.environ['PYTHONPATH']=''
    # await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    message_result = await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(result), parse_mode=ParseMode.MARKDOWN)
