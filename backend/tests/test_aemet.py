import aiohttp
import pytest

from backend.src.clients import AEMETClient

client = AEMETClient()

@pytest.mark.asyncio
async def test_get_municipio():

    async with aiohttp.ClientSession() as session:
        result = await client.get_municipio(session, "id28079")

    assert result is not None
    assert len(result) > 0

@pytest.mark.asyncio
async def test_get_estacion_data():

    async with aiohttp.ClientSession() as session:
        result = await client.get_tiempo_actual(session)

    assert result is not None
    assert len(result) > 0
