import telegram
from telegram.constants import ParseMode

import asyncio
import os
import subprocess

from config import *
from commands.utils import *
from functools import partial

admin = partial(whitelist, ids=ADMIN_IDS)

@admin
async def rrc(update, context):
    if len(context.args) > 0:
        command = ' '.join(context.args)
        try:
            result = subprocess.check_output(command.split(), stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as err:
            result = err.output.decode('utf-8')
        except Exception as err:
            result = str(err)
        except:
            result = 'Something went wrong.'
    else:
        result = 'Empty command. Nothing to do.'
    # await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(command, title='command'), parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(result), parse_mode=ParseMode.MARKDOWN)

@admin
async def wol(update, context):
    command = 'wol'
    try:
        result = subprocess.check_output(command.split(), stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as err:
        result = err.output.decode('utf-8')
    except Exception as err:
        result = str(err)
    except:
        result = 'Something went wrong.'
    # await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    message_result = await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(result), parse_mode=ParseMode.MARKDOWN)

@admin
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
