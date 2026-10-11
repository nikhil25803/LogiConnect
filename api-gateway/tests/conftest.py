import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
