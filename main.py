import logging

from telegram import bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from commands.common import *
from commands.upload import *
from commands.admin import *

def main():
    with open('.token') as f:
        token = f.read().strip()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/pisie/tgsanebot.log', filemode='w+')

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # COMMON COMMANDS
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    # UPLOAD COMMANDS
    dispatcher.add_handler(MessageHandler(Filters.document, document))
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
