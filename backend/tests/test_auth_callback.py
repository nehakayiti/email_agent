# tests/test_auth_callback.py

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
import logging

logger = logging.getLogger(__name__)

# A simple dummy flow that simulates the behavior of the real Flow.
class DummyFlow:
    def __init__(self, dummy_credentials):
        self.redirect_uri = None
        self.credentials = dummy_credentials

    def fetch_token(self, code):
        # In the dummy flow, nothing is done.
        pass

# A dummy credentials class.
class DummyCredentials:
    def __init__(self):
        self.id_token = {"email": "test@example.com", "name": "Test User"}
        self.token = "dummy_token"
        self.refresh_token = "dummy_refresh_token"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.client_id = "dummy_client_id"
        self.client_secret = "dummy_client_secret"

# A dummy flow factory that returns a DummyFlow.
def dummy_flow_factory():
    return DummyFlow(DummyCredentials())

@pytest.fixture
def client():
    return TestClient(app)
