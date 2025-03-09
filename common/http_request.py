import asyncio
from time import sleep
import aiohttp
import requests

from common.logger import setup_logger

logger = setup_logger('http_requests')

retryable_errors = [408, 429, 500, 502, 503, 504]


class RetryableError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


def _make_request(method: str, url: str, max_retries: int =3, **kwargs):
    latest_error = None
    for attempt in range(max_retries):
        try:
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"Method {method} not supported")

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

def get(url: str, max_retries=3, **kwargs):
    return _make_request('get', url, max_retries, **kwargs)

def post(url: str, max_retries=3, **kwargs):
    return _make_request('post', url, max_retries, **kwargs)

async def get_async(
        session: aiohttp.ClientSession,
        url: str,
        max_retries: int = 3,
        delay: int = 2,
        **kwargs
):

    for attempt in range(max_retries + 1):

        if attempt == max_retries:
            raise ValueError("Max retries reached.")

        logger.info(f"Attempt {attempt + 1}/{max_retries}")

        try:

            async with session.get(url, **kwargs) as response:

                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()

                if "application/json" in content_type:
                    data = await response.json()
                else:
                    data = await response.text()

                logger.info(f"Response: {data}")

                return data, response.status

        except Exception as e:
            logger.error(f"Error in GET request to {url}: {e}")

            if response.status not in retryable_errors:
                return None, response.status

            logger.info(f"Retrying in {delay} seconds...")

            await asyncio.sleep(delay)
            delay *= 2
            continue

    return None, 500
