from common import http_request
import pytest
import aiohttp

@pytest.mark.asyncio
async def test_get_async():
    async with aiohttp.ClientSession() as session:
        response, status_code = await http_request.get_async(session, "https://jsonplaceholder.typicode.com/posts/1")
    assert response is not None
    assert status_code == 200
    assert response['userId'] == 1
    assert response['id'] == 1

def test_get():
    response, status_code = http_request.get("https://jsonplaceholder.typicode.com/posts/1")
    assert response is not None
    assert status_code == 200
    assert response['userId'] == 1
    assert response['id'] == 1
