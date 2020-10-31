import time
import json
import logging
import telegram
import subprocess
from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import psutil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/tgsanebot.log', filemode='w+')

ADMIN_USERS = ['saneness']
DOWNLOAD_USERS = ['saneness', 'protosaaph', 'dzakharova', 'akhneva']

# Utils
class Utils:
    # Pre
    def pre(text):
        return '```\n' + text + '\n```'

    # Table
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

# Handlers
def rrc(update, context):
    if update.message.from_user.username in ADMIN_USERS:
        if len(context.args) > 0:
            command = ' '.join(context.args)
            try:
                result = subprocess.check_output(context.args, stderr=subprocess.STDOUT).decode('utf-8')
                text = '$ ' + '\n'.join([command, result])
            except subprocess.CalledProcessError as err:
                text = '$ ' + '\n'.join([command, err.output.decode('utf-8')])
            except Exception as err:
                text = '$ ' + '\n'.join([command, str(err)])
            except:
                text = '$ ' + '\n'.join([command, 'Something went wrong.'])
        else:
            text = 'Empty command. Nothing to do.'
    else:
        text = 'Permission denied.'
    context.bot.delete_message(chat_id=update.message.chat_id,
                               message_id=update.message.message_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def start(update, context):
    if len(context.args) > 0 and context.args[0] == 'keyboard':
        custom_keyboard = [['/start', '/help'], ['/system', '/service']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    else:
        reply_markup = telegram.ReplyKeyboardRemove()

    text = 'I\'m a `TGSaneBot`! What do you want?'

    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)

def help(update, context):
    text = '' \
        '/start - initialize me again (add \'keyboard\' to enable keyboard buttons)\n' \
        '/help - show all commands\n' \
        '/system - show system info\n' \
        '/service - show service info\n' \
        '/rrc - run remote command (restricted access)'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

def system(update, context):
    memory = psutil.virtual_memory()
    memory_used = memory.used / 1024 / 1024
    memory_total = memory.total / 1024 / 1024
    disk = psutil.disk_usage('/')
    disk_used = disk.used / 1024 / 1024 / 1024
    disk_total = disk.total / 1024 / 1024 / 1024
    
    system_status = [
        ['memory', f'{memory_used:.2f} / {memory_total:.2f} MB'],
        ['disk', f'{disk_used:.2f} / {disk_total:.2f} GB']
    ]

    text = Utils.table(system_status, header=['system', 'status'], widths=[8, 18])

    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def service(update, context):
    def get_status(service):
        return str(subprocess.call(['systemctl', 'is-active', '--quiet', service]))

    def row(data):
        return '|'.join(data) + '\n'

    status = {'0': 'running', '1': 'error', '3': 'stopped'}

    service_list = ['nginx', 'apache2', 'mtproxy-faketls', 'openvpn', 'tgsanebot']
    service_status = [[service, status[get_status(service)]] for service in service_list]
    text = Utils.table(service_status, header=['service', 'status'], widths=[16, 10])

    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def download_photo(update, context):
    if update.message.from_user.username in DOWNLOAD_USERS:
        file_data = context.bot.get_file(update.message.photo[len(update.message.photo) - 1].file_id)
        src = '/root/downloads/tgsanebot/photo/' + update.message.photo[1].file_id
        file_data.download(src)
    
        text = 'Download complete!'

        context.bot.delete_message(chat_id=update.message.chat_id,
                                   message_id=update.message.message_id)
        reply = context.bot.send_message(chat_id=update.message.chat_id, text=text)
        time.sleep(0.5)
        context.bot.delete_message(chat_id=update.message.chat_id,
                                   message_id=reply.message_id)
    else:
        text = 'Permission denied.'
        context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

# Main
def main():
    with open('.token') as f:
        token = f.read().strip()
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('rrc', rrc))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('system', system))
    dispatcher.add_handler(CommandHandler('service', service))

    dispatcher.add_handler(MessageHandler(Filters.photo, download_photo));

    updater.start_polling()

if __name__ == '__main__':
    main()
