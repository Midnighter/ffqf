from functools import partial
from typing import List

import aiometer
import httpx

from ffqf.application.service import RequestService, APISettings


class HTTPService(RequestService):
    def __init__(self, *, settings: APISettings, **kwargs) -> None:
        """"""
        super().__init__(settings=settings, **kwargs)
        self._client = httpx.AsyncClient(base_url=self.settings.api_url)

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


async def test_requests():
    client = HTTPService(
        settings=APISettings(api_url="https://httpbin.org", concurrency=2)
    )
    requests = [
        client.client.build_request("GET", "/status/200"),
        client.client.build_request("GET", "/status/400"),
    ]
    async with client:
        results = await client.perform_requests(requests)
