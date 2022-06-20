import telegram
from telegram.constants import ParseMode

import os
import psutil

from config import *
from commands.utils import *
from functools import partial

upload = partial(whitelist, ids=UPLOAD_IDS)

@upload
async def document(update, context):
    disk = psutil.disk_usage('/')
    if 100.0 * (disk.used + update.message.effective_attachment.file_size) / disk.total < MAX_DISK_USAGE:
        file_path = f'{FILE_ROOT}'
        domain_path = f'{DOMAIN_ROOT}'
        message_id = update.message.message_id
        file_id = update.message.effective_attachment.file_id
        file_name = update.message.effective_attachment.file_name.replace(' ', '_')
        file_data = await context.bot.get_file(file_id)
        if not os.path.exists(f'{file_path}/'):
            os.makedirs(f'{file_path}/')
        file_location = f'{file_path}/{file_name}'
        await file_data.download(file_location)
        text = 'Upload complete!\n' \
            f'Your file location: {domain_path}/{file_name}'
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_id)
        await context.bot.send_message(chat_id=update.message.chat_id, text=text, disable_web_page_preview=True)
    else:
        text = f'Disk usage is over {MAX_DISK_USAGE}%. Please ask the administrator to free some space before trying again!'
        await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)

@upload
async def ls(update, context):
    file_path = f'{FILE_ROOT}'
    domain_path = f'{DOMAIN_ROOT}'
    files = sorted([file for file in os.listdir(file_path) if file[0] != '.'])
    if len(files) > 0:
        text = 'Your files available:\n'
        for i, file in enumerate(files, start=1):
            text += f'`({i})` [{file}]({domain_path}/{file})\n'
    else:
        text = 'Sorry, you have no uploaded files!'
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@upload
async def rm(update, context):
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
                await context.bot.send_message(chat_id=update.message.chat_id, text=text)
            else:
                for file in files_found:
                    os.remove(f'{file_path}/{file}')
                text = 'Removed files:\n`* ' + '`\n`* '.join(files_found) + '`'
                await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
        else:
            text = 'Please use following format: `/rm {index}`'
            await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        await context.bot.send_message(chat_id=update.message.chat_id, text=text)

@upload
async def mv(update, context):
    file_path = f'{FILE_ROOT}'
    files = sorted([file for file in os.listdir(file_path) if file[0] != '.'])
    if len(files) > 0:
        if len(context.args) == 2 and context.args[0].isdigit():
            index, new_name = int(context.args[0]), context.args[1]
            if index - 1 < len(files) and index > 0:
                old_name = files[index - 1]
                os.rename(f'{file_path}/{old_name}', f'{file_path}/{new_name}')
                text = f'Moved file:\n`* {old_name} -> {new_name}`'
                await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
            else:
                text = f'Can\'t find file with index: {index}.\nNothing has been moved!'
                await context.bot.send_message(chat_id=update.message.chat_id, text=text)
        else:
            text = 'Please use following format: `/mv {index} {new_name}`'
            await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
    else:
        text = 'Sorry, you have no uploaded files!'
        await context.bot.send_message(chat_id=update.message.chat_id, text=text)