import requests
from src.safe_refuge_calls.api_url_service import ApiUrlService

api = ApiUrlService()

def get_category_list():
    """
    Get a list of categories from safe-refuge API.
    """
    response = requests.get(api.category_list)
    cat_list = [item['category'] for item in response.json()['items']]
    return cat_list
