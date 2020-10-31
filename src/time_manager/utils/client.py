from typing import Any

import aiohttp
from aiohttp import ClientResponse


async def http_request(
    method: str,
    url: str,
    headers: dict,
    cookies: dict,
    raise_for_status: bool,
    **kwargs: Any
) -> ClientResponse:
    async with aiohttp.ClientSession(
        cookies=cookies, headers=headers, raise_for_status=raise_for_status
    ) as http:
        async with http.request(method, url, **kwargs) as response:
            return response


async def http_get(
    url: str,
    headers: dict = {},
    cookies: dict = {},
    raise_for_status: bool = True,
) -> ClientResponse:
    return await http_request(
        "GET", url, headers=headers, cookies=cookies, raise_for_status=raise_for_status
    )


async def http_post(
    url: str, json: dict, headers: dict = {}, cookies: dict = {}, raise_for_status=True
) -> ClientResponse:
    return await http_request(
        "POST",
        url,
        headers=headers,
        cookies=cookies,
        raise_for_status=raise_for_status,
        json=json,
    )


async def http_delete(
    url: str, headers: dict = {}, cookies: dict = {}, raise_for_status=True
) -> ClientResponse:
    return await http_request(
        "DELETE",
        url,
        headers=headers,
        cookies=cookies,
        raise_for_status=raise_for_status,
    )


async def http_put(
    url: str, json: dict, headers: dict = {}, cookies: dict = {}, raise_for_status=True
) -> ClientResponse:
    return await http_request(
        "PUT",
        url,
        headers=headers,
        cookies=cookies,
        raise_for_status=raise_for_status,
        json=json,
    )


async def http_patch(
    url: str, json: dict, headers: dict = {}, cookies: dict = {}, raise_for_status=True
) -> ClientResponse:
    return await http_request(
        "PATCH",
        url,
        headers=headers,
        cookies=cookies,
        raise_for_status=raise_for_status,
        json=json,
    )
