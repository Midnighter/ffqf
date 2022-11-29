from functools import partial
from typing import List

import aiometer
import httpx
import pydantic

from ffqf.application.service import RequestService


class ENAAPIPortalRequestService(RequestService):
    def __init__(self, *, settings: pydantic.BaseSettings, **kwargs) -> None:
        """"""
        super().__init__(settings=settings, **kwargs)

    async def perform_requests(
        self, requests: List[httpx.Request]
    ) -> List[httpx.Response]:
        """"""
        async with httpx.AsyncClient(
            # TODO: use settings here
        ) as client:
            # We want to get responses in order such that we can process them in the
            # right way in that order again.
            # TODO: possibly modify request headers to inject headers etc.
            results = await aiometer.run_all(
                [partial(self._make_request, client, r) for r in requests],
                # TODO: apply further settings here
            )
        return results
