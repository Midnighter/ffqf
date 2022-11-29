from abc import ABC, abstractmethod

import httpx

from ffqf.domain.model import INSDCRunSet, AbstractAccessionSet


class MappingService(ABC):
    @classmethod
    @abstractmethod
    def prepare_request(
        cls, accessions: AbstractAccessionSet, **kwargs
    ) -> httpx.Request:
        """"""

    @classmethod
    @abstractmethod
    def parse_run_set(
        cls, response: httpx.Response, accessions: AbstractAccessionSet, **kwargs
    ) -> INSDCRunSet:
        """"""
