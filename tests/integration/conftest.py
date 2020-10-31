import asyncio
from multiprocessing import Process

import pytest
import uvicorn
from aiohttp.client_exceptions import ClientConnectionError
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from time_manager.db.sql.models.base import Base
from time_manager.main import app
from time_manager.settings import DB_URL
from time_manager.utils.client import http_get
from time_manager.utils.settings import Server


def run():
    uvicorn.run(app=app, host="0.0.0.0", port=Server.port)


@pytest.fixture
def session():
    engine = create_engine(DB_URL)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(engine)


@pytest.fixture
async def instance():
    proc = Process(target=run, args=(), daemon=True)
    proc.start()

    for i in range(30):
        try:
            response = await http_get(f"{Server.root}/ping")
        except ClientConnectionError:
            await asyncio.sleep(0.1)

    assert response
    assert response.status == status.HTTP_200_OK

    yield

    proc.terminate()
