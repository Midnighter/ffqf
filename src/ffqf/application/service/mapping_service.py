from abc import ABC, abstractmethod

import httpx

from ffqf.domain.model import INSDCRunSet, AbstractAccessionSet

from .request_service import RequestService


class MappingService(ABC):
    @classmethod
    @abstractmethod
    def prepare_request(
        cls, request_service: RequestService, accessions: AbstractAccessionSet, **kwargs
    ) -> httpx.Request:
        """"""

    @classmethod
    @abstractmethod
    def parse_run_set(
        cls, response: httpx.Response, accessions: AbstractAccessionSet, **kwargs
    ) -> INSDCRunSet:
        """"""
