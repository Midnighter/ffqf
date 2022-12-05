from functools import partial
from typing import List, cast

import aiometer
import httpx

from ffqf.application.service import RequestService

from .ena_api_portal_settings import ENAAPIPortalSettings


class ENAAPIPortalRequestService(RequestService):
    def __init__(self, *, settings: ENAAPIPortalSettings, **kwargs) -> None:
        """"""
        super().__init__(settings=settings, **kwargs)
        self._client = httpx.AsyncClient(
            base_url=self.settings.api_url, timeout=self.settings.timeout
        )

    @property
    def settings(self) -> ENAAPIPortalSettings:
        """"""
        return cast(ENAAPIPortalSettings, self._settings)

    async def perform_requests(
        self, requests: List[httpx.Request]
    ) -> List[httpx.Response]:
        """"""
        # We want to get responses in order such that we can process them in the
        # right way in that order again.
        return await aiometer.run_all(
            [partial(self._make_request, self.client, r) for r in requests],
            max_at_once=self.settings.concurrency,
            max_per_second=self.settings.concurrency,
        )
