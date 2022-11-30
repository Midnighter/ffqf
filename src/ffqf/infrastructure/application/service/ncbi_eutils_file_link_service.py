import logging
import re
from typing import List, Dict

import httpx
from lxml import etree

from ffqf.application.service import FileLinkService
from ffqf.domain.model import INSDCRunSet, FileDescription, URLType
from .ncbi_eutils_request_service import NCBIEutilsRequestService


logger = logging.getLogger(__name__)


class NCBIEutilsFileLinkService(FileLinkService):
    @classmethod
    def prepare_request(
        cls, request_service: NCBIEutilsRequestService, run_set: INSDCRunSet, **kwargs
    ) -> httpx.Request:
        """"""
        return request_service.client.build_request(
            method="POST",
            url="efetch.fcgi",
            data={
                "db": "sra",
                "id": ",".join(sorted(run_set)),
            },
        )

    @classmethod
    def parse_file_links(
        cls, response: httpx.Response, run_set: INSDCRunSet
    ) -> Dict[str, List[FileDescription]]:
        response.raise_for_status()
        fastq_pattern = re.compile(r"\.(fastq|fq)(.gz)?$")
        result: Dict[str, List[FileDescription]] = {}
        with open("/tmp/ncbi.xml", "wb") as handle:
            handle.write(response.content)
        root: etree._Element = etree.fromstring(response.content)
        assert root.tag == "EXPERIMENT_PACKAGE_SET"
        for run in root.iter("RUN"):  # type: etree._Element
            # NCBI returns experiment packages which may contain unrequested runs.
            if run.get("accession") not in run_set:
                logger.warning(
                    "Run accession '%s' not in the requested set.", run["accession"]
                )
                continue
            clouds = [
                (cloud_file.get("provider"), cloud_file.get("location"))
                for cloud_file in run.iter("CloudFile")
            ]
            files = []
            for sra_file in run.iter("SRAFile"):  # type: etree._Element
                for alt in sra_file.iter("Alternatives"):  # type: etree._Element
                    zone = None
                    for scheme, location in clouds:
                        if alt.get("url").startswith(scheme):
                            zone = location
                    if alt.get("url").endswith("bam"):
                        file_type = "bam"
                    elif fastq_pattern.search(alt.get("url")):
                        file_type = "fastq"
                    else:
                        file_type = "sra"
                    files.append(
                        FileDescription(
                            name=sra_file.get("filename"),
                            type=file_type,
                            size=int(sra_file.get("size")),
                            md5=sra_file.get("md5"),
                            url=alt.get("url"),
                            urltype=URLType(alt.get("org").lower()),
                            zone=zone,
                        )
                    )
                # run["total_spots"],
                # run["total_bases"],
            result[run.get("accession")] = files
        # assert result == run_set
        return result
