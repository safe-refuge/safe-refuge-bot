import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)

from src.services.safe_refuge_api_service import SafeRefugeApiService
from src.safe_refuge_api_calls.geocode import get_geocode
from src.services.keyboards_service import KeyboardService

logger = logging.getLogger(__name__)
LOCATION, CHECK_INFO, GET_POINTS, ADD_CATEGORY, DONE = range(5)


# Dynamic keyboards:
categories_keyboard = None

# Fixed keyboards:
yes_no_keyboard = KeyboardService.get_yes_no_keyboard()
location_keyboard = KeyboardService.get_location_keyboard()
search_keyboard = [['/search']]

# TODO: Check for collisions in parallel requests
user_categories_choice = None # Holding all the user-selected interests

# Helper functions (for clarity):
def invalid_category_selected_msg(update) -> None:
    """
    Invalid category selected.
    Updates the user to select another category.

    Args:
        update: The update object.
    """
    update.message.reply_text(
        'It looks like you choose an invalid category. Please, choose one of the available categories.',
        reply_markup=ReplyKeyboardMarkup(
            categories_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Please choose:",
            resize_keyboard=True
        )
    )

def all_categories_selected_msg(update) -> None:
    """
    Checks if the user has selected all the categories.
    """
    update.message.reply_text(
        'You have selected all the categories.\nNow we need your location to provide the closest available assistance for your needs. If you see the prompt, please click "Allow" or alternatively you can press skip and manually enter your address',
        reply_markup=ReplyKeyboardMarkup(
            location_keyboard,
            one_time_keyboard=True,
            input_field_placholder="Please choose:",
            resize_keyboard=True
        )     
    
    )

def ask_for_location(update, user) -> None | int:
    """
    Asks the user to send their location.
    """
    categories_choice_len = len(user_categories_choice)
    logger.info(f'User {user.first_name} interests in this {categories_choice_len} categories: {list(user_categories_choice.keys())}')

    # Checks if the user already shared his location
    if update.message.location:
        return DONE

    update.message.reply_text(
        'We need your location to provide the closest available assistance for your needs. If you see the prompt, please click "Allow" or alternatively you can press skip and manually enter your address',
        reply_markup=ReplyKeyboardMarkup(
            location_keyboard,
            one_time_keyboard=True,
            input_field_placholder="Please choose:",
            resize_keyboard=True
        )     
    
    )

def cant_find_POI_msg(update) -> None:
    """
    Can't find the point of interest message.
    """
    update.message.reply_text(
        'Sorry, I could not find any points of interest near you. Maybe you want to look for another points of interest?',
        reply_markup=ReplyKeyboardMarkup(
            yes_no_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Please choose:",
            resize_keyboard=True
        )
    )

def ask_for_more_info(update) -> None:
    """
    Checks if the user has selected yes.
    """
    update.message.reply_text(
            'OK, select another category.',
            reply_markup=ReplyKeyboardMarkup(
                categories_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Please choose:",
                resize_keyboard=True
            )
        )

def would_you_search_again_msg(update) -> None:
    """
    Checks if the user wants to search again.
    """
    update.message.reply_text(
        'Would you like to start a new search?', 
        reply_markup=ReplyKeyboardMarkup(
            yes_no_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Please choose:",
            resize_keyboard=True
        )
    )

def invalid_answer_msg(update, keyboard_type, extra_text = "") -> None:
    """
    Invalid answer - will return a clarification message to the user
    """
    update.message.reply_text(
        f'Sorry, I did not understand your answer.\
        Please follow the instructions:\n\
        {extra_text}',
        reply_markup=ReplyKeyboardMarkup(
            keyboard_type,
            one_time_keyboard=True,
            input_field_placeholder="please click:",
            resize_keyboard=True
        )
    )

def send_locations_to_user(update, points) -> None:
    """
    Sends the user the nearest available points of interest.
    """
    update.message.reply_text(
            'Here are the nearest points of interest:\n', 
            quote=True,  
            reply_markup=ReplyKeyboardRemove()
        )

    for name, location in points.items():
        update.message.reply_text(f'{name}:\n')
        update.message.reply_location(location=location, reply_markup=ReplyKeyboardRemove())   


# Conversation functions:
def search(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their needs."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} started the conversation.')

    global categories_keyboard
    global user_categories_choice
    categories_keyboard = KeyboardService.get_categories_keyboard()
    # inline_categories_keyboard = keyboard_service.get_categories_inline_keyboard()
    user_categories_choice = {} # reset the user categories choice

    update.message.reply_text(
        'Hi! What kind of point of interest are you looking for?\nPlease, select the appropriate option so that I can give you more accurate information.',
        reply_markup=ReplyKeyboardMarkup(
            categories_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Category:",
            resize_keyboard=True
            )
        # reply_markup=inline_categories_keyboard
    )

    return CHECK_INFO

def check_info(update: Update, context: CallbackContext) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    user_answer = update.message.text
    logger.info(f'{user.first_name} Point of interest are: {update.message.text}')

    global user_categories_choice
    global categories_keyboard

    # Checks that the selected category is valid
    remaining_cat = SafeRefugeApiService.get_remaining_categories(user_categories_choice)
    user_choice = user_categories_choice.values()

    if user_answer not in [*remaining_cat, *user_choice]:
        invalid_category_selected_msg(update)
        return CHECK_INFO

    user_categories_choice[update.message.text] = update.message.text
    categories_keyboard = KeyboardService.get_categories_keyboard(list(user_categories_choice))
    
    # Checks if all categories are selected
    if categories_keyboard == []:
        all_categories_selected_msg(update)
        return LOCATION

    update.message.reply_text(
        'There is another category of interest are you looking for? ',
        reply_markup=ReplyKeyboardMarkup(
            yes_no_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Please choose:",
            resize_keyboard=True
            )
    )

    return ADD_CATEGORY

def add_category(update: Update, context: CallbackContext) -> int:
    """
    Recheck the user's category of interest.
    """
    user = update.message.from_user
    user_answer = update.message.text

    if user_answer.lower() in ['No', 'no']:
        ask_for_location(update, user)
        return LOCATION
        
    elif user_answer.lower() in ['Yes', 'yes']:
        ask_for_more_info(update)
        return CHECK_INFO
        
    else:
        invalid_answer_msg(update, yes_no_keyboard, 'Please select Yes or No')
        return ADD_CATEGORY

def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and looks for POIs (ONLY if user sent location)"""
    
    user = update.message.from_user
    user_location = update.message.location
    logger.info(f'Location of { user.first_name}: {user_location.latitude} / {user_location.longitude}')

    points = SafeRefugeApiService.get_points_of_interest(chat_id=update.message.chat_id, latitude=user_location.latitude, longitude=user_location.longitude, categories=user_categories_choice.values())
    
    if not points:   
        cant_find_POI_msg(update)
        return ADD_CATEGORY 
        
    # TODO: to return locations table too.
    send_locations_to_user(update, points)
    would_you_search_again_msg(update)
    return DONE

def skip_location(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} did not send a location.')
    
    update.message.reply_text(
        "Ok, please type in an address close to yours so I can give you the relevant points of interest, otherwise I won't be able to help you.",
         reply_markup=ReplyKeyboardRemove()
    )

    return GET_POINTS

def get_points(update: Update, context: CallbackContext) -> int:
    """Uses geolocation to turn the address into coordinates"""    
    user = update.message.from_user
    user_address = update.message.text
    logger.info(f'User {user.first_name} sent {user_address} as an address close to them.')    
    
    result = get_geocode(user_address)

    if result == []:
        update.message.reply_text(
            'Sorry, I could not recognise that address. Maybe retype the address?',
            reply_markup=ReplyKeyboardRemove()
        )

        return GET_POINTS

    else:
        update.message.reply_text(
            f'You have inputted {result[0]} as your address. Looking for points of interest...',
            reply_markup=ReplyKeyboardRemove()
        )

        lat, lng = result[1]["lat"], result[1]["lng"]
        points = SafeRefugeApiService.get_points_of_interest(chat_id=update.message.chat_id, latitude=lat, longitude=lng, categories=user_categories_choice.values())
        
        if points:    
            send_locations_to_user(update, points)
            would_you_search_again_msg(update)
            return DONE

        cant_find_POI_msg()
        return ADD_CATEGORY

def end_of_conversation(update: Update, context: CallbackContext):
    """Ends the conversation."""
    user = update.message.from_user
    user_answer = update.message.text
    
    if user_answer.lower() in ['No', 'no']:
        update.message.reply_text(
            'I hope this information will be helpful for you.\nsee you soon!',
            reply_markup=ReplyKeyboardMarkup(
                search_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="For starting a new search, please click:",
                resize_keyboard=True
            )
        )
        
        return ConversationHandler.END

    elif user_answer.lower() in ['Yes', 'yes']:
        return search(update, context)
    
    else:
        
        invalid_answer_msg(update, search_keyboard, 'For starting a new search, please click /search.')
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    
    update.message.reply_text(
        'The current search has been cancelled. Anything else I can do for you?\
            \n\nSend /help for a list of commands, or /start to get more information.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_search_conv_handler() -> ConversationHandler:
    """Returns the handler for the search conversation."""

    return ConversationHandler(
        entry_points=[CommandHandler('search', search)],
        states={
            CHECK_INFO: [MessageHandler(Filters.text, check_info)],
            ADD_CATEGORY: [MessageHandler(Filters.text, add_category)],            
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location)
            ],
            # TODO: adding edge cases - if users recant, allow them to send location again.
            GET_POINTS: [MessageHandler(Filters.text, get_points)],
            DONE: [MessageHandler(Filters.text, end_of_conversation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
