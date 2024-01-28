import telegram
from telegram.constants import ParseMode

import os
import subprocess

from config import *
from commands.utils import *
from functools import partial

openai = partial(whitelist, ids=OPENAI_IDS)

@openai
async def image(update, context):
    try:
        if len(context.args) > 0:
            os.environ['PYTHONPATH']=PYTHONPATH
            os.environ['OPENAI_API_KEY']=open(OPENAI_TOKEN).read().strip()
            prompt = f'"{" ".join(context.args)}"'
            command = ['generate_image', '-p', f'{prompt}']
            await context.bot.send_message(chat_id=update.message.chat_id, text='Generating image... Please wait...')
            text = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        else:
            text = 'Please use following format: `/image {text}`'
    except subprocess.CalledProcessError as err:
        text = Utils.pre(err.output.decode('utf8'))
    except e:
        text = Utils.pre(err.output.decode('utf8'))
    os.environ['PYTHONPATH']=''
    os.environ['OPENAI_API_KEY']=''
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

@openai
async def image_w(update, context):
    try:
        if len(context.args) > 0:
            os.environ['PYTHONPATH']=PYTHONPATH
            os.environ['OPENAI_API_KEY']=open(OPENAI_TOKEN).read().strip()
            prompt = f'"{" ".join(context.args)}"'
            command = ['generate_image', '-s', '1792x1024', '-p', f'{prompt}']
            await context.bot.send_message(chat_id=update.message.chat_id, text='Generating image... Please wait...')
            text = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        else:
            text = 'Please use following format: `/image_w {text}`'
    except subprocess.CalledProcessError as err:
        text = Utils.pre(err.output.decode('utf8'))
    except e:
        text = Utils.pre(err.output.decode('utf8'))
    os.environ['PYTHONPATH']=''
    os.environ['OPENAI_API_KEY']=''
    await context.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
