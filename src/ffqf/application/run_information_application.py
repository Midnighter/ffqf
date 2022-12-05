import logging
from functools import partial
from typing import Dict, Iterable, List, Type

import anyio
import httpx

from ffqf.domain.model import FileDescription, INSDCRunSet, RunInformation

from .service import (
    FileLinkService,
    MappingService,
    RequestService,
    RunInformationService,
    SetBuilder,
)


logger = logging.getLogger(__name__)


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
        run_information_service: Type[RunInformationService],
        file_link_service: Type[FileLinkService],
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
        self.file_link_service = file_link_service
        self.ena_request_service = ena_request_service
        self.ncbi_request_service = ncbi_request_service
        self.builder = SetBuilder()

    async def run(self, accessions: Iterable[str]) -> List[RunInformation]:
        """"""
        self.builder.from_accessions(accessions)

        async with self.ena_request_service, self.ncbi_request_service:
            logger.info("Map all accessions to run accessions.")
            runs = await self._map2runs()
            logger.info("Get run information for %d accessions.", len(runs))
            result = await self._get_run_information(runs)
        return result

    async def _map2runs(self) -> INSDCRunSet:
        ena_requests = []
        ncbi_requests = []
        ena_processors = []
        ncbi_processors = []
        if self.builder.bio_projects:
            if self.bio_project_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.bio_project_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.bio_projects
                    )
                )
                ena_processors.append(
                    partial(
                        self.bio_project_mapping_service.parse_run_set,
                        accessions=self.builder.bio_projects,
                    )
                )

        if self.builder.bio_samples:
            if self.bio_sample_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.bio_sample_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.bio_samples
                    )
                )
                ena_processors.append(
                    partial(
                        self.bio_sample_mapping_service.parse_run_set,
                        accessions=self.builder.bio_samples,
                    )
                )

        if self.builder.studies:
            if self.insdc_study_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_study_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.studies
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_study_mapping_service.parse_run_set,
                        accessions=self.builder.studies,
                    )
                )

        if self.builder.samples:
            if self.insdc_sample_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_sample_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.samples
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_sample_mapping_service.parse_run_set,
                        accessions=self.builder.samples,
                    )
                )

        if self.builder.experiments:
            if self.insdc_experiment_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_experiment_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.experiments
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_experiment_mapping_service.parse_run_set,
                        accessions=self.builder.experiments,
                    )
                )

        if self.builder.submissions:
            if self.insdc_submission_mapping_service.__name__.startswith("ENA"):
                ena_requests.append(
                    self.insdc_submission_mapping_service.prepare_request(
                        self.ena_request_service, self.builder.submissions
                    )
                )
                ena_processors.append(
                    partial(
                        self.insdc_submission_mapping_service.parse_run_set,
                        accessions=self.builder.submissions,
                    )
                )

        # Collect all responses.
        ena_responses = await self.ena_request_service.perform_requests(ena_requests)
        # Parse run accessions from responses with the correct processors.
        runs = INSDCRunSet()
        for proc, response in zip(ena_processors, ena_responses):
            runs.update(proc(response))
        return runs

    async def _get_run_information(self, runs: INSDCRunSet) -> List[RunInformation]:
        ena_request = self.run_information_service.prepare_request(
            self.ena_request_service, runs
        )
        ncbi_request = self.file_link_service.prepare_request(
            self.ncbi_request_service, runs
        )
        run_info: List[RunInformation] = []
        file_links: Dict[str, List[FileDescription]] = {}
        async with anyio.create_task_group() as group:
            group.start_soon(self._wrap_run_info, [ena_request], runs, run_info)
            # Enrich with AWS and GCP links.
            group.start_soon(self._wrap_file_links, [ncbi_request], runs, file_links)
        for run in run_info:
            run.files.extend(file_links.get(run.run_accession, []))
        return run_info

    async def _wrap_run_info(
        self,
        requests: List[httpx.Request],
        runs: INSDCRunSet,
        run_info: List[RunInformation],
    ) -> None:
        """"""
        responses = await self.ena_request_service.perform_requests(requests)
        run_info.extend(self.run_information_service.parse_run_info(responses[0], runs))

    async def _wrap_file_links(
        self,
        requests: List[httpx.Request],
        runs: INSDCRunSet,
        file_links: Dict[str, List[FileDescription]],
    ) -> None:
        """"""
        responses = await self.ncbi_request_service.perform_requests(requests)
        file_links.update(self.file_link_service.parse_file_links(responses[0], runs))
