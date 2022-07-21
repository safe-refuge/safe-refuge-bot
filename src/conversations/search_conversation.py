import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters    
)

from src.safe_refuge_calls.common import get_category_list
from src.safe_refuge_calls.points_of_interest import get_points_of_interest


logger = logging.getLogger(__name__)

LOCATION, INFO, GET_POINTS, ADDITEMS, DONE = range(5)

# Holding all user possible interests
categories_keyboard = get_category_list()
yes_no_keyboard =[['Yes', 'No']]

def make_keyboard():
    keyboard = [InlineKeyboardButton(text = cat, callback_data=cat) for cat in categories_keyboard]
    print(f'keyboard = {keyboard}')
    return keyboard

# Holding all the user-selected interests
# TODO: Check for collisions
user_categories_choice = {} 

def search(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their needs."""
    user = update.message.from_user
    user_categories_choice = {} # reset the user categories choice
    logger.info(f'User {user.first_name} started the conversation.')

    #   categories_keyboard,
    #     one_time_keyboard=True,
    #     input_field_placeholder="Category:",
    #     resize_keyboard=True
    # mark = ReplyKeyboardMarkup(categories_keyboard).from_column(make_keyboard())
    # print(f'mark = {mark}')

    update.message.reply_text(
        'Hi! What kind of point of interest are you looking for? Please, select the appropriate option so that I can give you more accurate information.',
        reply_markup = ReplyKeyboardMarkup(
            categories_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Category:"
        )
    )

    return INFO


def info(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    global user_categories_choice
    user_categories_choice[update.message.text] = update.message.text

    logger.info(f'{user.first_name} Point of intrest are: {update.message.text}')
    
    # TODO: If the user do not wants to add categories, send all!
    update.message.reply_text(
        'There is another category of interest are you looking for?',
        reply_markup=ReplyKeyboardMarkup(
            yes_no_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Please choose:",
            resize_keyboard=True
            )
    )

    return ADDITEMS


def add_point_of_inerest(update: Update, context: CallbackContext) -> int:
    """
    Recheck the user's points of interest.
    """
    user = update.message.from_user
    user_answer = update.message.text
    global user_categories_choice

    if user_answer.lower() in ['No', 'no']:
        categories_choice_len = len(user_categories_choice)
        logger.info(f'User {user.first_name} interests in this {categories_choice_len} categories: {user_categories_choice.values()}')

        update.message.reply_text(
        'OK! For helping you find your way, I need you to share your location please.',
        reply_markup=ReplyKeyboardRemove() 
        )

        return LOCATION

    elif user_answer.lower() in ['Yes', 'yes']:
        update.message.reply_text(
            'OK, select another category.',
            reply_markup=ReplyKeyboardMarkup(
                categories_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Please choose:",
            )
        )

        return INFO
    
    elif user_answer == '/cancel':
        return cancel(update, context)

    else:
        update.message.reply_text(
        'Sorry, I did not understand your answer. There is another point of interest are you looking for? Please, choose Yes or No.',
        reply_markup=ReplyKeyboardMarkup(
                categories_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Please choose:",
                resize_keyboard=True
            )
        )

        return ADDITEMS


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    global user_categories_choice
    
    # TODO: get the location automatically
    logger.info(f'Location of { user.first_name}: {user_location.latitude} / {user_location.longitude}')

    if points := get_points_of_interest(chat_id=update.message.chat_id, skip=0, limit=20, latitude=user_location.latitude, longitude=user_location.longitude, min_distance=0, max_distance=500000, categories=user_categories_choice.values(), organizations=None, city=None, country=None, approved=None, active=None, author=None, admin=None, add_distance=True, fields="basic"):
        update.message.reply_text(f'Here are the points of interest near you:\n')
        for name, location in points.items(): 
            update.message.reply_text(f'{name}:\n')
            update.message.reply_location(location=location)    

        # TODO: Handle the end of the conversation - Yet not working!!!
        return DONE

    update.message.reply_text(
        'Sorry, I could not find any points of interest near you. Maybe you want to look for another points of interest?',
        reply_markup=ReplyKeyboardMarkup(
                yes_no_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Please choose:",
                resize_keyboard=True
            )
        )

    return ADDITEMS


def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} did not send a location.')
    
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return GET_POINTS


def end_of_conversation(update: Update, context: CallbackContext):
    """Ends the conversation."""
    logger.info('The user ends the conversation.')
    
    update.message.reply_text(
        'I hope this information will be helpful for you. I will be here if you need me ☻',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    
    update.message.reply_text(
        'The command /search has been cancelled. Anything else I can do for you? Send /help for a list of commands.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_search_conv_handler() -> ConversationHandler:
    """Returns the handler for the search conversation."""

    return ConversationHandler(
        entry_points=[CommandHandler('search', search)],
        states={
            INFO: [MessageHandler(Filters.text, info)],
            ADDITEMS: [MessageHandler(Filters.text, add_point_of_inerest)],            
            LOCATION: [
                MessageHandler(Filters.location | Filters.text, location),
                CommandHandler('skip', skip_location)
            ],
            DONE: [MessageHandler(Filters.text, end_of_conversation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )