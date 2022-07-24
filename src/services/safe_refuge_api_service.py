import logging
import os
import requests

from telegram import Location
from urllib.parse import unquote
from config.settings import Settings

logger = logging.getLogger(__name__)


class SafeRefugeApiService:
    """
    Service for safe-refuge API.
    """

    settings = Settings(_env_file="config/.env")

    api_root_url = settings.safe_refuge_root_url
    # api_current_version = 'v1'

    # Common urls
    category_list = f'{api_root_url}common'

    # User urls
    user_list = f'{api_root_url}user'

    # Nearby point of interest urls
    point_of_interest = f'{api_root_url}poi/'
    nearby = f'{point_of_interest}nearby'
    search = f'{point_of_interest}search'

    
    @staticmethod
    def generate_url_address(url, params):
        """
        Generate the url address with the params.
        Args:
            url: url address.
            params: params to add to the url.
        Returns:
            str: url address with the params.
        """
        params = {k: v for k, v in params.items() if v is not None}
        logger.info(f"Request params: {params}")
        return f'{url}?{requests.compat.urlencode(params)}'
    
    @staticmethod
    def get_category_list():
        """
        Get a list of categories from safe-refuge API.
        """
        response = requests.get(SafeRefugeApiService.category_list)
        return [item['category'] for item in response.json()['items']]

    @staticmethod
    def get_remaining_categories(except_categories: list = None) -> list:
        """
        Get a list of categories, filtered by except_categories (= categories that already chosen by the user)
        Return: list of categories
        """

        if except_categories is None:
            except_categories = []

        categories = SafeRefugeApiService.get_category_list()
        return [category for category in categories if category not in except_categories]

    @staticmethod
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

        api_url = SafeRefugeApiService.generate_url_address(SafeRefugeApiService.search, params)
        response = requests.get(api_url)
        logger.info(f'Calling API: {api_url}')

        items = response.json()["items"]
        return {item["name"]:Location(item["geo"]["coordinates"][0], item["geo"]["coordinates"][1]) for item in items}

