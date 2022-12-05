from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ffqf.domain.model import RunInformation


class RunInformationOutputWriter(ABC):
    @classmethod
    @abstractmethod
    def write(
        cls, run_info: List[RunInformation], output: Optional[Path] = None, **kwargs
    ) -> None:
        """"""
