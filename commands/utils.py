import telegram

from functools import wraps

class Utils:
    @staticmethod
    def pre(text):
        return '```\n' + text + '\n```'

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
    def whitelist(func, ids):
        @wraps(func)
        def wrapper(update, context, *args, **kwargs):
            chat_id = update.message.chat_id
            if chat_id not in ids:
                text = 'Permission denied.'
                context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
                return
            return func(update, context, *args, **kwargs)
        return wrapper