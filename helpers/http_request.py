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
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in GET request to {url}: {e}")
            return None, 500
    logger.error(f"Failed GET request to {url} after {max_retries} attempts")
    return None, latest_error


async def get_async(session: aiohttp.ClientSession, url: str, max_retries=3, **kwargs):
    latest_error = None
    async with session.get(url, **kwargs):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, **kwargs)
                if response.status_code in retryable_errors:
                    raise RetryableError(response.status_code)
                response.raise_for_status()
                response = await response.json()
                return response, response.status_code
            except RetryableError as e:
                latest_error = e.status_code
                logger.error(f"Error {e.status_code} in GET request to {url}. Attempt {attempt + 1} of {max_retries}")
                sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                logger.error(f"Error in GET request to {url}: {e}")
                return None, 500
        logger.error(f"Failed GET request to {url} after {max_retries} attempts")
        return None, latest_error
