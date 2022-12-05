import json
import sys
from pathlib import Path
from typing import List, Optional

from pydantic.json import pydantic_encoder

from ffqf.application.service import RunInformationOutputWriter
from ffqf.domain.model import RunInformation


class RunInformationJSONOutputWriter(RunInformationOutputWriter):
    @classmethod
    def write(
        cls, run_info: List[RunInformation], output: Optional[Path] = None, **kwargs
    ) -> None:
        """"""
        if output:
            with output.open(mode="w") as handle:
                json.dump(run_info, handle, default=pydantic_encoder, **kwargs)
        else:
            json.dump(run_info, sys.stdout, default=pydantic_encoder, **kwargs)
