import telegram

import os
import psutil

from config import *
from commands.utils import *
from functools import partial

upload = partial(Utils.whitelist, ids=UPLOAD_IDS)

@upload
def document(update, context):
    disk = psutil.disk_usage('/')
    if 100.0 * (disk.used + update.message.effective_attachment.file_size) / disk.total < MAX_DISK_USAGE:
        chat_id = update.message.chat_id
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

@upload
def ls(update, context):
    chat_id = update.message.chat_id
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

@upload
def rm(update, context):
    chat_id = update.message.chat_id
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

@upload
def mv(update, context):
    chat_id = update.message.chat_id
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