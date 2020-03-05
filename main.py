import json
import logging
import os
import telegram
import subprocess
from telegram.ext import Updater, CommandHandler

import psutil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/tgsanebot.log', filemode='w+')

class Utils:
    def pre(text):
        return '```\n' + text + '\n```'
    def table(array, widths, header):
        pass

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
    
    text = 'MEMORY\n Used: {memory_used:6.2f} MB\n Total: {memory_total:6.2f} MB \n' \
           'DISK  \n Used: {disk_used:6.2f} GB  \n Total: {disk_total:6.2f} GB'  \
           ''.format(memory_used=memory_used, memory_total=memory_total,
                     disk_used=disk_used, disk_total=disk_total)

    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def service(update, context):
    def get_status(service):
        return str(subprocess.call(['systemctl', 'is-active', '--quiet', service]))

    def row(data):
        return '|'.join(data) + '\n'

    status = {'0': 'running', '1': 'error', '3': 'stopped'}

    service_list = ['nginx', 'apache2', 'privoxy', 'mtproxy', 'openvpn', 'tgsanebot']
    service_status = {service: status[get_status(service)] for service in service_list}
    
    text = row(['service   ', 'status    '])
    text += row(['----------', '----------'])
    for service in service_list:
        text += row(['{:10s}'.format(service), '{:10s}'.format(service_status[service])])

    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    with open('.token') as f:
        token = f.read()
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
