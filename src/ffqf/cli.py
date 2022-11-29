import re
from itertools import chain

import httpx


def main():
    # TODO: validate all incoming accessions
    recognized_accession = re.compile(
        r"^(((SR|ER|DR)[APRSX])|(SAM(N|EA|EG|D))|(PRJ(NA|EB|DB))|(GS[EM]))(\d+)$",
        flags=re.ASCII,
    )
    # TODO: split accessions into studies, submissions, samples, experiments, and runs
    #  because of how the ENA API works.

    # TODO: Make requests to collect run accessions.
    # TODO: Deduplicate accessions.
    # TODO: Make request to ENA for all accessions to get sample sheet.
    # TODO: Make request to NCBI for AWS and GCP links.


SRA_PREFIX = ("SR", "SAMN", "PRJNA")
ENA_PREFIX = ("ER", "SAMEA", "PRJEB")
DDBJ_PREFIX = ("DR", "SAMD", "PRJDB")
GEO_PREFIX = ("GS",)


test_ids = [
    "SAMN11619543",
    "SAMN11619542",
    "SAMN11619539",
    "SAMN11619538",
    "SAMN11619541",
    "SAMN11619540",
]

SRA_IDS = (
    "PRJNA63463",
    "SAMN00765663",
    "SRA023522",
    "SRP003255",
    "SRR390278",
    "SRS282569",
    "SRX111814",
)
ENA_IDS = (
    "PRJEB7743",
    "SAMEA3121481",
    "ERA2421642",
    "ERP120836",
    "ERR674736",
    "ERS4399631",
    "ERX629702",
)
DDBJ_IDS = (
    "PRJDB4176",
    "SAMD00114846",
    "DRA008156",
    "DRP004793",
    "DRR171822",
    "DRS090921",
    "DRX162434",
)
GEO_IDS = ("GSE18729", "GSM465244")

list(chain(SRA_IDS, ENA_IDS, DDBJ_IDS, GEO_IDS))

response = httpx.post(
    "https://www.ebi.ac.uk/ena/portal/api/search",
    data={
        "dataPortal": "ena",
        "fields": ",".join(
            [
                "run_accession",
                "experiment_accession",
                "sample_accession",
                "study_accession",
            ]
        ),
        "format": "tsv",
        "includeAccessionType": "run",
        # "includeAccessions": ",".join(GEO_IDS),
        "includeAccessions": "DRR171822",
        "limit": 0,
        "result": "read_run",
    },
    timeout=10,
)
print(response.status_code)
print(response.text)
