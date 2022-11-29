import asyncio
from functools import partial
from typing import List, Iterable, Type

from .service import (
    MappingService,
    RunInformationService,
)
from .service import SetBuilder, RequestService
from ffqf.domain.model import RunInformation, INSDCRunSet


class RunInformationApplication:
    def __init__(
        self,
        *,
        bio_project_mapping_service: Type[MappingService],
        bio_sample_mapping_service: Type[MappingService],
        insdc_study_mapping_service: Type[MappingService],
        insdc_sample_mapping_service: Type[MappingService],
        insdc_experiment_mapping_service: Type[MappingService],
        insdc_submission_mapping_service: Type[MappingService],
        run_information_service: RunInformationService,
        ena_request_service: RequestService,
        ncbi_request_service: RequestService,
        **kwargs
    ) -> None:
        """"""
        super().__init__(**kwargs)
        self.bio_project_mapping_service = bio_project_mapping_service
        self.bio_sample_mapping_service = bio_sample_mapping_service
        self.insdc_study_mapping_service = insdc_study_mapping_service
        self.insdc_sample_mapping_service = insdc_sample_mapping_service
        self.insdc_experiment_mapping_service = insdc_experiment_mapping_service
        self.insdc_submission_mapping_service = insdc_submission_mapping_service
        self.run_information_service = run_information_service
        self.ena_request_service = ena_request_service
        self.ncbi_request_service = ncbi_request_service

    def run(self, accessions: Iterable[str]) -> List[RunInformation]:
        """"""
        builder = SetBuilder()
        builder.from_accessions(accessions)

        ena_requests = []
        ncbi_requests = []
        ena_processors = []
        ncbi_processors = []
        if builder.bio_projects:
            if self.bio_project_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.bio_project_mapping_service.prepare_request(
                        builder.bio_projects
                    )
                )
                ena_processors.append(
                    partial(
                        self.bio_project_mapping_service.parse_run_set,
                        accessions=builder.bio_projects,
                    )
                )

        if builder.bio_samples:
            if self.bio_sample_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.bio_sample_mapping_service.prepare_request(builder.bio_samples)
                )
                ena_processors.append(
                    partial(
                        self.bio_sample_mapping_service.parse_run_set,
                        accessions=builder.bio_samples,
                    )
                )

        if builder.studies:
            if self.insdc_study_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_study_mapping_service.prepare_request(builder.studies)
                )
                ena_processors.append(
                    partial(
                        self.insdc_study_mapping_service.parse_run_set,
                        accessions=builder.studies,
                    )
                )

        if builder.samples:
            if self.insdc_sample_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_sample_mapping_service.prepare_request(builder.samples)
                )
                ena_processors.append(
                    partial(
                        self.insdc_sample_mapping_service.parse_run_set,
                        accessions=builder.samples,
                    )
                )

        if builder.experiments:
            if self.insdc_experiment_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_experiment_mapping_service.prepare_request(
                        builder.experiments
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_experiment_mapping_service.parse_run_set,
                        accessions=builder.experiments,
                    )
                )

        if builder.submissions:
            if self.insdc_submission_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_submission_mapping_service.prepare_request(
                        builder.submissions
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_submission_mapping_service.parse_run_set,
                        accessions=builder.submissions,
                    )
                )

        # Collect all responses.
        ena_responses = asyncio.run(
            self.ena_request_service.perform_requests(ena_requests)
        )
        # Parse run accessions from responses with the correct processors.
        runs = INSDCRunSet()
        for proc, response in zip(ena_processors, ena_responses):
            runs.update(proc(response))
        # Fetch run information.
        self.run_information_service.to_run_info(runs)
        # Enrich with AWS and GCP links.
