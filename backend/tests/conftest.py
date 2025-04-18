import os
from dotenv import load_dotenv

def pytest_configure():
    # Load .env.test from the backend directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.test')
    load_dotenv(dotenv_path=env_path, override=True) 