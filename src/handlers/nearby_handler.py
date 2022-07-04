import json
import logging
import requests

from requests import request
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)

logger = logging.getLogger(__name__)

# TODO: Adding url to the config file / env variable / something
safe_refuge_root_url = "https://c4u-match-org.appspot.com/"

LOCATION, INFO, GET_POINTS = range(3)

def nearby(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their needs."""
    reply_keyboard = [['Food', 'hygiene', 'clothing', 'other']]
    user = update.message.from_user

    logger.info("User %s started the conversation.", user.first_name)

    update.message.reply_text(
        'Hi! What kind of point of interest are you looking for? Please, select the appropriate option so that I can give you more accurate information.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Category:",
            resize_keyboard=True
            )
    )

    return INFO


def info(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user

    logger.info("%s Point of intrest are: %s", user.first_name, update.message.text)

    update.message.reply_text(
        'For helping you find your way, I need you to share your location please.',
        reply_markup=ReplyKeyboardRemove()
    )

    return LOCATION    


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location

    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude)

    api = f'{safe_refuge_root_url}poi/nearby?latitude={user_location.latitude}&longitude={user_location.longitude}&limit=1&max_distance=500000'
    # payload={"latitude":{user_location.latitude}, "longtitude":{user_location.longitude}, "limit":5, "max_distance":500000}
    response = requests.get(api)

    update.message.reply_text(
        f'Nearby points of interest:\n {json.dumps(response.json(), indent=4, sort_keys=True)} \n',
        reply_markup=ReplyKeyboardRemove()
    )

    # return BIO
    return ConversationHandler.END


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return GET_POINTS


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_nearby_handler():
    """Returns the handler for the nearby conversation."""

    nearby_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('nearby', nearby)],
        states={
            INFO: [MessageHandler(Filters.text, info)],            
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location)
            ],
            # GET_POINTS: [MessageHandler(~Filters.all, get_nearby_points)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    return nearby_conv_handler