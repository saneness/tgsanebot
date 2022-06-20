import telegram
from telegram.constants import ParseMode

import os
import subprocess
import yaml

from config import *
from commands.utils import *
from functools import partial

route = partial(whitelist, ids=ROUTE_IDS)

@route
async def routes(update, context):
    config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
    if len(config['domains']) > 0:
        text = '\n'.join(config['domains'])
    else:
        text = 'No routes are found.'
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)

@route
async def add(update, context):
    if len(context.args) > 0:
        try:
            config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
            domains = [domain for domain in list(set(context.args)) if domain not in config['domains']]
            if len(domains) > 0:
                config['domains'] = sorted(list(set(config['domains'] + domains)), key=lambda x: x.split('.')[:-1][::-1])
                with open(ROUTES_CONFIG, 'w+') as file:
                    yaml.dump(config, file)
                config_update = config.copy()
                config_update['domains'] = domains
                with open(f'{WORK_DIR}/config_update.yml', 'w+') as file:
                    yaml.dump(config_update, file)
                message_update = await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre('Updating routes...'), parse_mode=ParseMode.MARKDOWN)
                subprocess.check_output([ROUTES_UPDATE, '-c', f'{WORK_DIR}/config_update.yml'], stderr=subprocess.STDOUT).decode('utf-8')
                os.remove(f'{WORK_DIR}/config_update.yml')
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_update.message_id)
                text = 'Routes have been updated!\n\n' + '\n'.join(['> ' + domain + ' <' if domain in domains else domain for domain in config['domains']])
            else:
                text = 'No new domains have been detected. Nothing to do.'
        except:
            text = 'Something went wrong.'
    else:
        text = 'Empty domain list. Nothing to do.'
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)

@route
async def remove(update, context):
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
    await context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=ParseMode.MARKDOWN)