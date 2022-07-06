import logging

from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def help(update: Update, context: CallbackContext) -> None:
    """
    Send a message when the command /help is issued.
    Args:
        update:
        context:
    Returns:
    """
    return update.message.reply_text(
        "The following commands are available: \n"
        "/start - Return brief of the bot options.\n"
        "/nearby - Return a list of nearby points of interest.\n"
        "/help - Show this message."
    )