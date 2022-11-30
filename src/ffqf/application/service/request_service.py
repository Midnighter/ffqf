from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Coroutine, Any

import httpx

from .api_settings import APISettings


logger = logging.getLogger(__name__)


class RequestService(ABC):
    def __init__(self, *, settings: APISettings, **kwargs) -> None:
        """"""
        super().__init__(**kwargs)
        self._settings = settings
        self._client = httpx.AsyncClient()

    @property
    def settings(self) -> APISettings:
        """"""
        return self._settings

    @property
    def client(self) -> httpx.AsyncClient:
        """"""
        return self._client

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> RequestService:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        return await self._client.__aexit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    async def perform_requests(
        self, requests: List[httpx.Request]
    ) -> List[httpx.Response]:
        """"""

    @classmethod
    async def _make_request(
        cls, client: httpx.AsyncClient, request: httpx.Request
    ) -> httpx.Response:
        logger.debug(str(request))
        logger.debug(request.content.decode("ASCII"))
        return await client.send(request)
