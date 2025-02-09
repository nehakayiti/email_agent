import requests
import logging

logger = logging.getLogger(__name__)

def get_userinfo(credentials):
    """Get user info from Google"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise 