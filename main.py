import json
import logging
import os
import psutil
import subprocess
import telegram
import time
import yaml

from config import *
from functools import wraps
from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/pisie/tgsanebot.log', filemode='w+')

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


def admins(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in ADMIN_IDS:
            text = 'Permission denied.'
            context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapper

def uploads(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in UPLOAD_IDS:
            text = 'Permission denied.'
            context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapper

def common(func):
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        chat_id = update.message.chat_id
        if chat_id not in COMMON_IDS:
            text = 'Permission denied.'
            context.bot.send_message(chat_id=chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapper

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
        '`admin commands:`\n' \
        '`/rrc     ` run remote command\n' \
        '`/pxlpass ` show pxl password\n' \
        '`/routes  ` list routed domains\n' \
        '`/add     ` add domain(s) to routing\n' \
        '`/remove  ` remove domain(s) from routing'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

@uploads
def upload(update, context):
    disk = psutil.disk_usage('/')
    if 100.0 * (disk.used + update.message.effective_attachment.file_size) / disk.total < MAX_DISK_USAGE:
        chat_id = update.message.chat_id
        username = UPLOAD_IDS[chat_id]
        file_path = f'{FILE_ROOT}'
        domain_path = f'{DOMAIN_ROOT}'
        message_id = update.message.message_id
        file_id = update.message.effective_attachment.file_id
        file_name = update.message.effective_attachment.file_name.replace(' ', '_')
        file_data = context.bot.get_file(file_id)
        if not os.path.exists(f'{file_path}/'):
            os.makedirs(f'{file_path}/')
        file_location = f'{file_path}/{file_name}'
        file_data.download(file_location)
        text = 'Upload complete!\n' \
            f'Your file location: {domain_path}/{file_name}'
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        context.bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
    else:
        text = f'Disk usage is over {MAX_DISK_USAGE}%. Please ask the administrator to free some space before trying again!'
        context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@uploads
def ls(update, context):
    chat_id = update.message.chat_id
    username = UPLOAD_IDS[chat_id]
    file_path = f'{FILE_ROOT}'
    domain_path = f'{DOMAIN_ROOT}'
    files = sorted([file for file in os.listdir(file_path) if file[0] != '.'])
    if len(files) > 0:
        text = 'Your files available:\n'
        for i, file in enumerate(files, start=1):
            text += f'`({i})` [{file}]({domain_path}/{file})\n'
    else:
        text = 'Sorry, you have no uploaded files!'
    context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)

@uploads
def rm(update, context):
    chat_id = update.message.chat_id
    username = UPLOAD_IDS[chat_id]
    file_path = f'{FILE_ROOT}'
    files = sorted([file for file in os.listdir(file_path) if file[0] != '.'])
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
                    os.remove(f'{file_path}/{file}')
                text = 'Removed files:\n`* ' + '`\n`* '.join(files_found) + '`'
                context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            text = 'Please use following format: `/rm {index}`'
            context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

@uploads
def mv(update, context):
    chat_id = update.message.chat_id
    username = UPLOAD_IDS[chat_id]
    file_path = f'{FILE_ROOT}'
    files = sorted([file for file in os.listdir(file_path) if file[0] != '.'])
    if len(files) > 0:
        if len(context.args) == 2 and context.args[0].isdigit():
            index, new_name = int(context.args[0]), context.args[1]
            if index - 1 < len(files) and index > 0:
                old_name = files[index - 1]
                os.rename(f'{file_path}/{old_name}', f'{file_path}/{new_name}')
                text = f'Moved file:\n`* {old_name} -> {new_name}`'
                context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                text = f'Can\'t find file with index: {index}.\nNothing has been moved!'
                context.bot.send_message(chat_id=update.message.chat_id, text=text)
        else:
            text = 'Please use following format: `/mv {index} {new_name}`'
            context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

@admins
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

@admins
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

@admins
def routes(update, context):
    config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
    text = '\n'.join(config['domains'])
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@admins
def add(update, context):
    if len(context.args) > 0:
        try:
            config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
            domains = [domain for domain in list(set(context.args)) if domain not in config['domains']]
            if len(domains) > 0:
                config['domains'] = sorted(list(set(config['domains'] + domains)), key=lambda x: x.split('.')[:-1][::-1])
                with open(ROUTES_CONFIG, 'w+') as file:
                    yaml.dump(config, file)
                message_update = context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre('Updating routes...'), parse_mode=telegram.ParseMode.MARKDOWN)
                subprocess.check_output(ROUTES_UPDATE, stderr=subprocess.STDOUT).decode('utf-8')
                context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_update.message_id)
                text = 'Routes have been updated!\n\n' + '\n'.join(['> ' + domain + ' <' if domain in domains else domain for domain in config['domains']])
            else:
                text = 'No new domains have been detected. Nothing to do.'
        except:
            text = 'Something went wrong.'
    else:
        text = 'Empty domain list. Nothing to do.'
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@admins
def remove(update, context):
    if len(context.args) > 0:
        try:
            config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
            domains = [domain for domain in list(set(context.args)) if domain in config['domains']]
            if len(domains) > 0:
                config['domains'] = sorted([domain for domain in list(set(config['domains'])) if domain not in domains], key=lambda x: x.split('.')[:-1][::-1])
                with open(ROUTES_CONFIG, 'w+') as file:
                    yaml.dump(config, file)
                text = 'Following routes have been removed:\n\n' + '\n'.join(domains)
            else:
                text = 'No existing domains have been detected. Nothing to do.'
        except:
            text = 'Something went wrong.'
    else:
        text = 'Empty domain list. Nothing to do.'
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    with open('.token') as f:
        token = f.read().strip()

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # COMMON COMMANDS
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    # UPLOAD COMMANDS
    dispatcher.add_handler(MessageHandler(Filters.document, upload))
    dispatcher.add_handler(CommandHandler('ls', ls))
    dispatcher.add_handler(CommandHandler('rm', rm))
    dispatcher.add_handler(CommandHandler('mv', mv))

    # ADMIN COMMANDS
    dispatcher.add_handler(CommandHandler('rrc', rrc))
    dispatcher.add_handler(CommandHandler('pxlpass', pxlpass))
    dispatcher.add_handler(CommandHandler('routes', routes))
    dispatcher.add_handler(CommandHandler('add', add))
    dispatcher.add_handler(CommandHandler('remove', remove))
    updater.start_polling()

if __name__ == '__main__':
    main()
