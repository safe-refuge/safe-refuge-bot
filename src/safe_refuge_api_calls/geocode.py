import logging
from src.services.google_api_service import GoogleAPI

logger = logging.getLogger(__name__)

gmaps = GoogleAPI()

# TODO: Refactoring needed - change to be service class
def get_geocode(address):
    """Gets a geocode from the Google API based on address"""

    geocode = gmaps.api.geocode(address)
    if geocode == []:
        logger.info(f"Geocode did not recognise address")

        return []
    else:
        returned_address = geocode[0]["formatted_address"]
        location = geocode[0]["geometry"]["location"]
        logger.info(f"Geocode recognised address as {returned_address}, and returned {location}")
    
        return [returned_address, location]