# MIT License
#
# Copyright (c) 2022 Moritz E. Beber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
from typing import List

import httpx
import pydantic
from pydantic import parse_obj_as

from ffqf.application.service import MappingService
from ffqf.domain.model import INSDCRunSet, INSDCSampleSet

from .ena_api_portal_request_service import ENAAPIPortalRequestService


logger = logging.getLogger(__name__)


class INSDCSample2INSDCRunAssociation(pydantic.BaseModel):

    secondary_sample_accession: pydantic.constr(regex=r"^((SR|ER|DR)S)(\d+)$")
    run_accession: pydantic.constr(regex=r"^((SR|ER|DR)R)(\d+)$")

    class Config:
        frozen = True


class ENAAPIPortalINSDCSampleMappingService(MappingService):
    @classmethod
    def prepare_request(
        cls,
        request_service: ENAAPIPortalRequestService,
        accessions: INSDCSampleSet,
        **kwargs,
    ) -> httpx.Request:
        """"""
        return request_service.client.build_request(
            method="POST",
            url="search",
            data={
                "dataPortal": "ena",
                "query": " OR ".join(
                    [f'secondary_sample_accession="{acc}"' for acc in accessions]
                ),
                "fields": ",".join(INSDCSample2INSDCRunAssociation.__fields__),
                "format": "json",
                "limit": 0,
                "result": "read_run",
            },
        )

    @classmethod
    def parse_run_set(
        cls, response: httpx.Response, accessions: INSDCSampleSet, **kwargs
    ) -> INSDCRunSet:
        response.raise_for_status()
        mapping = parse_obj_as(List[INSDCSample2INSDCRunAssociation], response.json())
        found = {m.secondary_sample_accession for m in mapping}
        if found != accessions:
            logger.error(
                "The following sample accessions could not be mapped: %s",
                ", ".join(accessions.difference(found)),
            )
        return INSDCRunSet.from_accessions(
            accessions=[m.run_accession for m in mapping]
        )
