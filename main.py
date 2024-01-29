from telegram.ext import Application, CommandHandler, MessageHandler, filters
from commands.common import *
from commands.upload import *
from commands.openai import *
from commands.admin import *
from config import *
import logging

import os

def main():
    with open('.token') as f:
        token = f.read().strip()

    os.environ['PYTHONPATH']=PYTHONPATH
    os.environ['OPENAI_API_KEY']=open(OPENAI_API_KEY).read().strip()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/pisie/tgsanebot.log', filemode='w+')

    application = Application.builder().base_url('http://localhost:8081/bot').token(token).build()

    # COMMON COMMANDS
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('status', status))

    # OPENAI COMMANDS
    application.add_handler(CommandHandler('image', image))
    application.add_handler(CommandHandler('image_w', image_w))

    # UPLOAD COMMANDS
    application.add_handler(MessageHandler(filters.Document.ALL | filters.ANIMATION | filters.AUDIO | filters.VIDEO, document))
    application.add_handler(CommandHandler('ls', ls))
    application.add_handler(CommandHandler('rm', rm))
    application.add_handler(CommandHandler('mv', mv))

    # ADMIN COMMANDS
    application.add_handler(CommandHandler('rrc', rrc))
    application.add_handler(CommandHandler('wol', wol))

    application.run_polling()

if __name__ == '__main__':
    main()
