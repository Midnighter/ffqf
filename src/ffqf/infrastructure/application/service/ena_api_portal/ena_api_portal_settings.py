from typing import Collection

from pydantic import HttpUrl

from ffqf.application.service import APISettings


class ENAAPIPortalSettings(APISettings):

    api_url: HttpUrl = "https://www.ebi.ac.uk/ena/portal/api/"
    concurrency: int = 10
    fields: Collection[str] = (
        "run_accession",
        "experiment_accession",
        "sample_accession",
        "secondary_sample_accession",
        "study_accession",
        "secondary_study_accession",
        "parent_study",
        "submission_accession",
        "run_alias",
        "experiment_alias",
        "sample_alias",
        "study_alias",
        "library_layout",
        "library_selection",
        "library_source",
        "library_strategy",
        "library_name",
        "instrument_model",
        "instrument_platform",
        "base_count",
        "read_count",
        "tax_id",
        "scientific_name",
        "sample_title",
        "experiment_title",
        "study_title",
        "description",
        "sample_description",
        "fastq_md5",
        "fastq_bytes",
        "fastq_ftp",
        "fastq_galaxy",
        "fastq_aspera",
    )
