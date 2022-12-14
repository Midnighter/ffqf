from abc import ABC, abstractmethod
from typing import List

import httpx

from ffqf.domain.model import INSDCRunSet, RunInformation

from .request_service import RequestService


class RunInformationService(ABC):
    @classmethod
    @abstractmethod
    def prepare_request(
        cls, request_service: RequestService, run_set: INSDCRunSet, **kwargs
    ) -> httpx.Request:
        """"""

    @classmethod
    @abstractmethod
    def parse_run_info(
        cls, response: httpx.Response, run_set: INSDCRunSet
    ) -> List[RunInformation]:
        """"""
