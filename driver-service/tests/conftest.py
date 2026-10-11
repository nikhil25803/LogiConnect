import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient


SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

os.environ.setdefault("DB_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("CELERY_BROKER", "memory://")
os.environ.setdefault("CELERY_BACKEND", "cache+memory://")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")
os.environ.setdefault("USER_SERVICE_URL", "http://user")
os.environ.setdefault("ADMIN_SERVICE_URL", "http://admin")

from config.database import get_db
from main import app


@pytest.fixture
def db():
    result = MagicMock()
    result.scalars.return_value.first.return_value = MagicMock()
    instance = AsyncMock()
    instance.execute.return_value = result
    return instance


@pytest.fixture
def client(db):
    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
