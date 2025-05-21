import telegram
from telegram.constants import ParseMode
from functools import partial
from commands.utils import *
from config import *

openai = partial(whitelist, ids=OPENAI_IDS)

@openai
async def message(update, context):
    prompt = f'"{update.message.text}"'
    command = ['chat', '-u', f'{update.message.chat_id}', '-l', OPENAI_HISTORY, '-p', f'{prompt}']
    text = Utils.subprocess(command)
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

@openai
async def image(update, context):
    if len(context.args) > 0:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Generating image... Please wait...')
        prompt = f'"{" ".join(context.args)}"'
        command = ['generate_image', '-p', f'{prompt}']
        text = Utils.subprocess(command)
    else:
        text = 'Please use following format: `/image {text}`'
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

@openai
async def image_w(update, context):
    if len(context.args) > 0:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Generating image... Please wait...')
        prompt = f'"{" ".join(context.args)}"'
        command = ['generate_image', '-s', '1792x1024', '-p', f'{prompt}']
        text = Utils.subprocess(command)
    else:
        text = 'Please use following format: `/image_w {text}`'
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

@openai
async def clear(update, context):
    command = ['chat', '-u', f'{update.message.chat_id}', '-l', OPENAI_HISTORY, '-c']
    text = Utils.subprocess(command, default='Chat history has been cleared.')
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)