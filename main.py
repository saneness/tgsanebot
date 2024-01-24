import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from commands.common import *
from commands.upload import *
from commands.admin import *

def main():
    with open('.token') as f:
        token = f.read().strip()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG, filename='/var/log/pisie/tgsanebot.log', filemode='w+')

    application = Application.builder().base_url('http://localhost:8081/bot').token(token).build()

    # COMMON COMMANDS
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))

    # UPLOAD COMMANDS
    application.add_handler(MessageHandler(filters.Document.ALL | filters.ANIMATION | filters.AUDIO | filters.VIDEO, document))
    application.add_handler(CommandHandler('ls', ls))
    application.add_handler(CommandHandler('rm', rm))
    application.add_handler(CommandHandler('mv', mv))

    # ADMIN COMMANDS
    application.add_handler(CommandHandler('rrc', rrc))
    application.add_handler(CommandHandler('wol', wol))
    application.add_handler(CommandHandler('status', status))

    application.run_polling()

if __name__ == '__main__':
    main()
