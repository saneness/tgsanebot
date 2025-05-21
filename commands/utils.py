import telegram
from telegram.constants import ParseMode
from functools import wraps
import subprocess

class Utils:
    @staticmethod
    def pre(text, title='result'):
        return f'```{title}\n' + text + '\n```'

    @staticmethod
    def table(array, header=None, widths=None):
        n = len(array[0])
        if header:
            table = ['|'.join([f' {header[i]:{widths[i]}s}' for i in range(n)])]
            table += ['|'.join(['-' * (widths[i] + 1) for i in range(n)])]
        else:
            table = []
        for item in array:
            table += ['|'.join([f' {item[i]:{widths[i]}s}' for i in range(n)])]
        return '\n'.join(table)

    @staticmethod
    def subprocess(command, default=None):
        try:
            text = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as err:
            text = err.output.decode('utf8')
        except Exception as err:
            text = err.output.decode('utf8')
        except:
            text = 'Something went wrong.'
        if not default:
            return text
        else:
            return default

def whitelist(func, ids):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in ids:
            text = 'Permission denied.'
            await context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def blacklist(func, ids):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id in ids:
            text = 'Permission denied.'
            await context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper