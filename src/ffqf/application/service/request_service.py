from abc import ABC, abstractmethod
from typing import List

import httpx
import pydantic


class RequestService(ABC):
    def __init__(self, *, settings: pydantic.BaseSettings, **kwargs) -> None:
        """"""
        super().__init__(**kwargs)
        self._settings = settings

    @abstractmethod
    async def perform_requests(
        self, requests: List[httpx.Request]
    ) -> List[httpx.Response]:
        """"""

    @classmethod
    async def _make_request(
        cls, client: httpx.AsyncClient, request: httpx.Request
    ) -> httpx.Response:
        return await client.send(request)
