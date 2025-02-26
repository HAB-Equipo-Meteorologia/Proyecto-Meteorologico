import asyncio
from time import sleep
import aiohttp
import requests
from helpers.logging import setup_logger

logger = setup_logger('http_requests')

retryable_errors = [408, 429, 500, 502, 503, 504]


class RetryableError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


def get(url: str, max_retries=3, **kwargs):
    latest_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, **kwargs)
            if response.status_code in retryable_errors:
                raise RetryableError(response.status_code)
            response.raise_for_status()
            return response.json(), response.status_code
        except RetryableError as e:
            latest_error = e.status_code
            logger.error(f"Error {e.status_code} in GET request to {url}. Attempt {attempt + 1} of {max_retries}")
            sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Error in GET request to {url}: {e}")
            return None, 500
    logger.error(f"Failed GET request to {url} after {max_retries} attempts")
    return None, latest_error


async def get_async(session: aiohttp.ClientSession, url: str, max_retries=3, **kwargs):
    latest_error = None
    for attempt in range(max_retries):
        try:
            async with session.get(url, **kwargs) as response:
                if response.status in retryable_errors:
                    raise RetryableError(response.status)

                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if content_type.startswith("application/json"):
                    data = await response.json()
                else:
                    data = await response.text()

                return data, response.status

        except RetryableError as e:
            latest_error = e
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # exponential backoff

    if latest_error:
        raise latest_error
