import telegram

import subprocess
import time
import yaml

from config import *
from commands.utils import *
from functools import partial

admin = partial(Utils.whitelist, ids=ADMIN_IDS)

@admin
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

@admin
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

@admin
def routes(update, context):
    config = yaml.load(open(ROUTES_CONFIG).read(), Loader=yaml.Loader)
    if len(config['domains']) > 0:
        text = '\n'.join(config['domains'])
    else:
        text = 'No routes are found.'
    context.bot.send_message(chat_id=update.message.chat_id, text=Utils.pre(text), parse_mode=telegram.ParseMode.MARKDOWN)

@admin
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

@admin
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