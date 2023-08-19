import asyncio
from typing import Generator, AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import main as run_alembic
from async_asgi_testclient import TestClient

from src.main import app


@pytest.fixture(autouse=True, scope="session")
def run_migrations() -> None:
    run_alembic(["upgrade", "head"])


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "9000"
    scope = {"client": (host, port)}

    async with TestClient(app, scope=scope) as client:
        yield client


# fixtures
from .auth_fixtures import *
from .receipts_fixures import *
