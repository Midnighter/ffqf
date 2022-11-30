from typing import List, cast

import httpx
from pydantic import parse_obj_as

from ffqf.application.service import RunInformationService
from ffqf.domain.model import INSDCRunSet, RunInformation

from .ena_api_portal_request_service import ENAAPIPortalRequestService
from .ena_api_portal_settings import ENAAPIPortalSettings


class ENAAPIPortalRunInformationService(RunInformationService):
    @classmethod
    def prepare_request(
        cls, request_service: ENAAPIPortalRequestService, run_set: INSDCRunSet, **kwargs
    ) -> httpx.Request:
        """"""
        return request_service.client.build_request(
            method="POST",
            url="search",
            data={
                "dataPortal": "ena",
                "fields": ",".join(
                    cast(ENAAPIPortalSettings, request_service.settings).fields
                ),
                "format": "json",
                "includeAccessionType": "run",
                "includeAccessions": ",".join(sorted(run_set)),
                "limit": 0,
                "result": "read_run",
            },
        )

    @classmethod
    def parse_run_info(
        cls, response: httpx.Response, run_set: INSDCRunSet
    ) -> List[RunInformation]:
        response.raise_for_status()
        result = parse_obj_as(List[RunInformation], response.json())
        assert {r.run_accession for r in result} == run_set
        return result
