from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton

from src.services.safe_refuge_api_service import SafeRefugeApiService

class KeyboardService:
    """
    Service class for keyboards.
    """


    @staticmethod
    def get_yes_no_keyboard() -> list:
        """
        Creates a one line yes/no keyboard
        """
        return [['Yes', 'No']]

    
    @staticmethod
    def get_categories_keyboard(except_categories: list = None) -> list:
        """
        Creates a categories of interest keyboard - one line per category
        Return: list of lists of buttons
        """
        if except_categories is None:
            except_categories = []

        return [[KeyboardButton(category)] for category in sorted(SafeRefugeApiService.get_category_list()) if category not in except_categories]

    
    @staticmethod
    def get_categories_inline_keyboard(except_categories: list = None) -> InlineKeyboardMarkup:
        """
        Creates a categories of interest keyboard - one line per category
        Return: InlineKeyboardMarkup of categories
        """
        if except_categories is None:
            except_categories = []
        
        buttons = [[InlineKeyboardButton(text=category, callback_data=str(category))] for category in SafeRefugeApiService.get_category_list() if category not in except_categories]
        return InlineKeyboardMarkup(buttons)

    
    @staticmethod
    def get_location_keyboard() -> list:
        """
        Creates keyboard to get location
        Return: keyboard with 'send' location button and 'skip' button
        """
        return [[KeyboardButton("send", request_location=True)], [KeyboardButton("/skip")]]
