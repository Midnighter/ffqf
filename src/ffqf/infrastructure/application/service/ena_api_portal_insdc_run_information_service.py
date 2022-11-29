from typing import List, Iterable

import httpx
from pydantic import parse_obj_as

from ffqf.application.service import RunInformationService
from ffqf.domain.model import INSDCRunSet, RunInformation


class ENAAPIPortalRunInformationService(RunInformationService):
    def __init__(self, *, client: httpx.AsyncClient, **kwargs) -> None:
        """"""
        super().__init__(**kwargs)
        self._client = client

    async def to_run_info(
        self, run_set: INSDCRunSet, *, fields: Iterable[str], **kwargs
    ) -> List[RunInformation]:
        """"""
        response = await self._client.post(
            url="search",
            data={
                "dataPortal": "ena",
                "fields": ",".join(fields),
                "format": "json",
                "includeAccessionType": "run",
                "includeAccessions": ",".join(sorted(run_set)),
                "limit": 0,
                "result": "read_run",
            },
        )
        response.raise_for_status()
        return parse_obj_as(List[RunInformation], response.json())
