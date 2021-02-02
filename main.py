import os
import time
import json
import psutil
import logging
import telegram
import subprocess
from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps
from config import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/tgsanebot.log', filemode='w+')

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


def admin(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in ADMIN_IDS:
            text = 'Permission denied.'
            context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapper

def family(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in FAMILY_IDS:
            text = 'Permission denied.'
            context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapper

@admin
def rrc(update, context):
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
    context.bot.delete_message(chat_id=update.message.chat_id,
                               message_id=update.message.message_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def start(update, context):
    reply_markup = telegram.ReplyKeyboardRemove()
    text = 'I\'m a `TGSaneBot`! What do you want?'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)

@admin
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

@admin
def service(update, context):
    def get_status(service):
        return str(subprocess.call(['systemctl', 'is-active', '--quiet', service]))

    status = {'0': 'running', '1': 'error', '3': 'stopped'}
    service_list = ['nginx', 'openvpn', 'tgsanebot']
    service_status = [[service, status[get_status(service)]] for service in service_list]
    text = Utils.table(service_status, header=['service', 'status'], widths=[12, 10])
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@family
def upload(update, context):
    disk = psutil.disk_usage('/')
    if 100.0 * (disk.used + update.message.effective_attachment.file_size) / disk.total < MAX_DISK_USAGE:
        chat_id = update.message.chat_id
        username = FAMILY_IDS[chat_id]
        message_id = update.message.message_id
        file_id = update.message.effective_attachment.file_id
        file_name = update.message.effective_attachment.file_name.replace(' ', '_')
        file_data = context.bot.get_file(file_id)
        if not os.path.exists(f'{FILE_ROOT}/{username}/'):
            os.makedirs(f'{FILE_ROOT}/{username}/')
        file_path = f'{FILE_ROOT}/{username}/{file_name}'
        file_data.download(file_path)
        text = 'Upload complete!\n' \
            f'Your file location: {DOMAIN_ROOT}/{username}/{file_name}'
        context.bot.delete_message(chat_id=chat_id,
                                    message_id=message_id)
        context.bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
    else:
        text = f'Disk usage is over {MAX_DISK_USAGE}%. Please ask the administrator to free some space before trying again!'
        context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@family
def files(update, context):
    chat_id = update.message.chat_id
    username = FAMILY_IDS[chat_id]
    file_path = f'{FILE_ROOT}/{username}'
    files = sorted(os.listdir(file_path))
    if len(files) > 0:
        text = 'Your files available:\n'
        for i, file in enumerate(files, start=1):
            text += f'`({i})` [{file}]({DOMAIN_ROOT}/{username}/{file})\n'
    else:
        text = 'Sorry, you have no uploaded files!'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)

@family
def delete(update, context):
    chat_id = update.message.chat_id
    username = FAMILY_IDS[chat_id]
    file_path = f'{FILE_ROOT}/{username}'
    files = sorted(os.listdir(file_path))
    if len(files) > 0:
        if len(context.args) > 0:
            files_not_found = []
            files_found = []
            for arg in context.args:
                if arg not in [str(i) for i in range(1, len(files) + 1)]:
                    files_not_found.append(arg)
                else:
                    files_found.append(files[int(arg) - 1])
            if len(files_not_found) > 0:
                text = 'Can\'t find files with indexes: ' + ' '.join(files_not_found) + '.\nNothing has been removed!'
                context.bot.send_message(chat_id=update.message.chat_id, text=text)
            else:
                for file in files_found:
                    os.remove(f'{FILE_ROOT}/{username}/{file}')
                text = 'Deleted files:\n`* ' + '`\n`* '.join(files_found) + '`'
                context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            text = 'Please use following format: `/delete {index}`'
            context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

@family
def rename(update, context):
    chat_id = update.message.chat_id
    username = FAMILY_IDS[chat_id]
    file_path = f'{FILE_ROOT}/{username}'
    files = sorted(os.listdir(file_path))
    if len(files) > 0:
        if len(context.args) == 2 and context.args[0].isdigit():
            index, new_name = int(context.args[0]), context.args[1]
            if index - 1 < len(files) and index > 0:
                old_name = files[index - 1]
                os.rename(f'{FILE_ROOT}/{username}/{old_name}', f'{FILE_ROOT}/{username}/{new_name}')
                text = f'Renamed file:\n`* {old_name} -> {new_name}`'
                context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                text = f'Can\'t find file with index: {index}.\nNothing has been renamed!'
                context.bot.send_message(chat_id=update.message.chat_id, text=text)
        else:
            text = 'Please use following format: `/rename {index} {new_name}`'
            context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)


def main():
    with open('.token') as f:
        token = f.read().strip()

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('rrc', rrc))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('system', system))
    dispatcher.add_handler(CommandHandler('service', service))
    dispatcher.add_handler(CommandHandler('files', files))
    dispatcher.add_handler(CommandHandler('delete', delete))
    dispatcher.add_handler(CommandHandler('rename', rename))
    dispatcher.add_handler(MessageHandler(Filters.document, upload))
    updater.start_polling()

if __name__ == '__main__':
    main()
