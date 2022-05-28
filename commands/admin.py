import telegram

import subprocess
import time

from config import *
from commands.utils import *
from functools import partial

admin = partial(Utils.whitelist, ids=ADMIN_IDS)

@admin
def rrc(update, context):
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
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(command), parse_mode=telegram.ParseMode.MARKDOWN)
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(result), parse_mode=telegram.ParseMode.MARKDOWN)

@admin
def pxlpass(update, context):
    command = 'cat /root/.pxlpass'
    try:
        result = subprocess.check_output(command.split(), stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as err:
        result = err.output.decode('utf-8')
    except Exception as err:
        result = str(err)
    except:
        result = 'Something went wrong.'
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    message_result = context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(result), parse_mode=telegram.ParseMode.MARKDOWN)
    time.sleep(10)
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_result.message_id)