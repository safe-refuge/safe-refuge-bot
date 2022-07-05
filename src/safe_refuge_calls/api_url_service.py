import logging

import requests


logger = logging.getLogger(__name__)


class ApiUrlService:
    """
    Service for safe-refuge API.
    """

    api_root_url = 'https://c4u-match-org.appspot.com/'
    # api_current_version = 'v1'

    # Common url
    category_list = f'{api_root_url}common'

    # User url
    user_list = f'{api_root_url}user'

    # Nearby point of interest url
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
    



