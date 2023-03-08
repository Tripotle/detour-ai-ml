import os
# See https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
import dotenv


# Load environment variables
dotenv.load_dotenv()


def get_api_key() -> str:
    return os.getenv('GOOGLE_MAPS_API_KEY')
