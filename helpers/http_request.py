from typing import Any
import requests
import aiohttp
import asyncio
from helpers.http_error import UnsupportedMethodError, UnsupportedContentTypeError, RequestFailedError, error_map, \
    retryable_exceptions, ClientError, MaximumRetriesError


# noinspection PyTypeChecker,PydanticTypeChecker
def make_request(
        method: str,
        url: str,
        **kwargs
) -> tuple[Any, int]:
    request_map = {
        'get': requests.get,
        'post': requests.post,
        'delete': requests.delete,
        'put': requests.put,
    }
    if method not in request_map:
        raise UnsupportedMethodError(method)

    method = request_map[method.lower()]

    try:
        response = method(url=url, **kwargs)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if content_type.startswith("application/json"):
            return response.json(), response.status_code
        elif content_type.startswith("text"):
            return response.text(), response.status_code
        elif content_type.startswith("application/pdf"):
            return response.read(), response.status_code
        else:
            raise UnsupportedContentTypeError(content_type)

    except requests.exceptions.RequestException as req_err:
        print(f"Request failed: {req_err}")
        return {"error": str(req_err)}, 500

    except Exception as e:
        print('Error occurred:', e)
        return {"error": str(e)}, 500


async def make_request_async(
        method: str,
        url: str,
        session: aiohttp.ClientSession,
        max_retries: int = 3,
        delay: int = 2,
        **kwargs,
) -> tuple[Any, int]:
    # noinspection PyTypeChecker,PydanticTypeChecker
    def _get_request_func():
        request_map_async = {
            'get': session.get,
            'post': session.post,
            'delete': session.delete,
            'put': session.put,
        }

        method_lower = method.lower()
        if method_lower not in request_map_async:
            raise UnsupportedMethodError

        return request_map_async[method_lower]

    method_func = _get_request_func()

    if not method:
        raise UnsupportedMethodError(method)

    for attempt in range(max_retries):

        try:
            async with method_func(url=url, **kwargs) as response:  # type: aiohttp.ClientResponse

                # Check if the response status is in the error map
                if response.status in error_map:
                    exception = error_map[response.status](response.status, response.reason)

                    # Retry the request if the exception is in the retryable exceptions list
                    if exception in retryable_exceptions:
                        await asyncio.sleep(delay ** attempt)  # Exponential backoff
                        continue

                    raise exception

                # Validate the response status
                if not (200 <= response.status < 300):
                    raise RequestFailedError(response.status, response.reason)

                # Parse the response content
                content_type = response.headers.get("Content-Type", "").lower()

                if content_type.startswith("application/json"):
                    return await response.json(), response.status
                elif content_type.startswith("text"):
                    return await response.text(), response.status
                elif content_type.startswith("application/pdf"):
                    return await response.read(), response.status
                elif content_type.startswith("image"):
                    return await response.read(), response.status
                elif content_type.startswith("application/octet-stream"):
                    return await response.read(), response.status
                elif content_type.startswith("application/xml"):
                    return await response.text(), response.status
                else:
                    raise UnsupportedContentTypeError(content_type)

        except aiohttp.ClientError as e:

            if hasattr(e, 'status'):
                raise ClientError(e.status, str(e))
            else:
                raise RequestFailedError(500, str(e))

        except Exception as e:

            if hasattr(e, 'status'):
                raise RequestFailedError(e.status)
            else:
                print(str(e))
                raise RequestFailedError(500)

    raise MaximumRetriesError  # 504


async def request_batch_async(
        url: str,
        method: str,
        data: list[dict],
        retries: int = 3,
        delay: int = 2,
        **kwargs
) -> list[tuple[dict, int]]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            make_request_async(
                method=method,
                url=url,
                session=session,
                retries=retries,
                delay=delay,
                json=item,
                **kwargs
            ) for item in data
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    return responses
