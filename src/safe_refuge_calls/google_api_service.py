import logging
from googlemaps import Client

logger = logging.getLogger(__name__)


class GoogleAPI:
    """service for Google API"""
 
    def __init__(self):

        api_key = "AIzaSyAouHHZ8x9dD1SasZgHKjJva2oYrNEuY1w" #This is my key
        self.api = Client(api_key)
        logger.info(f"Connected to Google API")