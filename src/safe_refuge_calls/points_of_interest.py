import logging
import requests

from telegram import Location
from urllib.parse import unquote

from src.safe_refuge_calls.api_url_service import ApiUrlService


logger = logging.getLogger(__name__)

# TODO: Dependancy injection? check for better solution. Maybe use a decorator / other Design pattern?
api = ApiUrlService()

def get_points_of_interest(chat_id: int, skip: int = 0, limit: int = 20, latitude: float = None,
    longitude: float = None, min_distance: int = 0, max_distance: int = 500000, categories: dict = None, organizations: str = None,
    city: str = None, country: str = None, approved: bool = None, active: bool = None, author: str = None, admin: str = None,
    add_distance: bool = True,  fields: str = "basic"):
    """
    Search point. Nearby and/or by filtering.
    Get a list of points of interest from safe-refuge API.

    Args:
        chat_id: chat id.
        skip: skip items (Pagination start item index). Default: 0
        limit: Limit the number of items to return (Pagination page size). Default: 20
        latitude: Geo latitude for nearby search. Like: 32.0897. Default: None
        longitude: Geo longitude for nearby search. Like: 34.4597. Default: None
        min_distance: Minimum distance in meters for nearby search. Default: 0
        max_distance: Minimum distance in meters for nearby search. Default: 500000 (500 KM)
        categories: Filter the points by Categories. Comma separated list. Like: Food, Clothes. Default: None.
        organizations: Filter the points by Organizations. Comma separated list. Default: None.
        city: Get points within a city. Like: Paris. Default: None.
        country: Get points within a Country. Like: France. Default: None.
        approved: Get only approved (true) or not-approved (false) points. Default: None. Ignore the approved state.
        active: Get only active (true) or non-active (false) points. Default: None. Ignore the active state.
        author: Get points for specific auther. By username. Default: None.
        admin: Get points for specific admin. By username. Default: None.
        add_distance: Add distance from the nearby-search location. True by default.
        fields: (optional) Format of the returned points. "compact", "basic" or "full". Default: "basic"

    Returns:
        Dictionary: points of interest dict -> {"location name:Location object", ...}
    """

    params = {
        "skip": skip,
        "limit": limit,
        "latitude": latitude,
        "longitude": longitude,
        "min_distance": min_distance,
        "max_distance": max_distance,
        "categories":  unquote(", ".join(categories)) if categories else None,
        "organizations": organizations,
        "city": city,
        "country": country,
        "approved": approved,
        "active": active,
        "author": author,
        "admin": admin,
        "add_distance": add_distance,
        "fields": fields
    }

    api_url = api.generate_url_address(api.search, params)
    response = requests.get(api_url)
    logger.info(f'Calling API: {api_url}')

    items = response.json()["items"]
    return {item["name"]:Location(item["geo"]["coordinates"][0], item["geo"]["coordinates"][1]) for item in items}

