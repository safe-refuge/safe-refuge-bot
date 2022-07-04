import logging

from requests import request
from config.settings import Settings
from telegram.ext import Updater

from src.handlers.nearby_handler import get_nearby_handler
from src.handlers.start_handler import get_start_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def main():
    settings = Settings(_env_file="config/.env")
    
     # Create the Updater and pass it your bot's token.
    updater = Updater(settings.telegram_key)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    start_handler = get_start_handler()
    nearby_handler = get_nearby_handler(    )

    # Add handlers to the dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(nearby_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == "__main__":
    main()