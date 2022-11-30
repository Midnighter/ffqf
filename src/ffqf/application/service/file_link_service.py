from abc import ABC, abstractmethod
from typing import List

import httpx

from ffqf.domain.model import INSDCRunSet, RunInformation

from .request_service import RequestService


class FileLinkService(ABC):
    @classmethod
    @abstractmethod
    async def prepare_request(
        cls, request_service: RequestService, run_set: INSDCRunSet, **kwargs
    ) -> httpx.Request:
        """"""

    @classmethod
    @abstractmethod
    def parse_file_links(cls, response: httpx.Response, run_set: INSDCRunSet) -> List:
        """"""
