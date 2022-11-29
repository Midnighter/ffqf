from abc import ABC, abstractmethod
from typing import List

from ffqf.domain.model import INSDCRunSet, RunInformation


class RunInformationService(ABC):
    @abstractmethod
    async def to_run_info(self, run_set: INSDCRunSet, **kwargs) -> List[RunInformation]:
        """"""
