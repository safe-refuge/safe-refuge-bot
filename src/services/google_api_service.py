import logging
import os

from googlemaps import Client

from config.settings import Settings

logger = logging.getLogger(__name__)


class GoogleAPI:
    """service for Google API"""
    
    settings = Settings(_env_file="config/.env")


    def __init__(self):
        
        api_key = self.settings.google_api_key
        self.api = Client(api_key)
        logger.info(f"Connected to Google API")