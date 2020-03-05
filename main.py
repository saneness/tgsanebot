import json
import logging
import os
import telegram
import subprocess
from telegram.ext import Updater, CommandHandler

import psutil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/tgsanebot.log', filemode='w+')

# Utils
class Utils:
    # Pre
    def pre(text):
        return '```\n' + text + '\n```'

    # Table
    def table(array, header=None, widths=None):
        n = len(array[0])
        print(n)
        if not widths:
             widths = [12] * n
        print(widths)
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
    if update.message.from_user.username == 'saneness':
        command = ' '.join(context.args)
        stream = os.popen('{command}'.format(command=command))
        text = '$ ' + '\n'.join([command, stream.read()])
    else:
        text = 'Permission denied.'
    context.bot.delete_message(chat_id=update.message.chat_id,
                               message_id=update.message.message_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def start(update, context):
    custom_keyboard = [['/start', '/help'], ['/system', '/service']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    text = 'I\'m a `TGSaneBot`! What do you want?'

    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)

def help(update, context):
    text = '/start - initialize me again\n/help - show this message\n/system - show system info\n/service - show service info'
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

    service_list = ['nginx', 'apache2', 'privoxy', 'mtproxy', 'openvpn', 'tgsanebot']
    service_status = [[service, status[get_status(service)]] for service in service_list]
    text = Utils.table(service_status, header=['service', 'status'])

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

    updater.start_polling()

if __name__ == '__main__':
    main()
