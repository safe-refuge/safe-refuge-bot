import logging
from googlemaps import Client

logger = logging.getLogger(__name__)


class GoogleAPI:
    """service for Google API"""
 
    def __init__(self):

        api_key = "SECRET"
        self.api = Client(api_key)
        logger.info(f"Connected to Google API")