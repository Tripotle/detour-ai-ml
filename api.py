import os
# See https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
import dotenv

# Load environment variables
dotenv.load_dotenv()


def get_api_key() -> str:
    return os.getenv('GOOGLE_MAPS_API_KEY')


def get_openapi_api_key() -> str:
    """
    See https://platform.openai.com/account/api-keys
    :return: api key used to access OpenAPI services including ChatGPT
    """
    return os.getenv('OPENAI_API_KEY')

def get_mapbox_api_key() -> str:
    return os.getenv('MAPBOX_TOKEN')
