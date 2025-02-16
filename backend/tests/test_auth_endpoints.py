# tests/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="module")
def client():
    """Create a test client"""
    return TestClient(app)


