import logging
import re
import sys
from enum import Enum, unique
from typing import Optional, List, Collection

import anyio
import typer

import ffqf
from ffqf.application import RunInformationApplication
from ffqf.infrastructure.application.service import (
    ENAAPIPortalBioProjectMappingService,
    ENAAPIPortalBioSampleMappingService,
    ENAAPIPortalINSDCStudyMappingService,
    ENAAPIPortalINSDCSampleMappingService,
    ENAAPIPortalINSDCExperimentMappingService,
    ENAAPIPortalINSDCSubmissionMappingService,
    NCBIEutilsFileLinkService,
    ENAAPIPortalRequestService,
    ENAAPIPortalRunInformationService,
    NCBIEutilsRequestService,
)
from ffqf.infrastructure.application.service.ena_api_portal_settings import (
    ENAAPIPortalSettings,
)
from ffqf.infrastructure.application.service.ncbi_eutils_settings import (
    NCBIEutilsSettings,
)

logger = logging.getLogger("ffqf")


@unique
class LogLevel(str, Enum):
    """Define the choices for the log level option."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


app = typer.Typer(
    help="Find FASTQ faster than ffq.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(is_set: bool) -> None:
    """
    Print the tool version if desired.

    Args:
        is_set: Whether the version was requested as a command line option.

    Raises:
        Exit: With default code 0 to signal normal program end.

    """
    if is_set:
        print(ffqf.__version__)
        raise typer.Exit()


def validate_accessions(accessions: Collection[str]) -> None:
    recognized_accession = re.compile(
        r"^(((SR|ER|DR)[APRSX])|(SAM(N|EA|EG|D))|(PRJ(NA|EB|DB))|(GS[EM]))(\d+)$",
        flags=re.ASCII,
    )

    for acc in accessions:
        if not recognized_accession.match(acc):
            logger.error("Invalid or unrecognized accession '%s'. Ignored.", acc)


@app.command()
def main(
    accessions: Optional[List[str]] = typer.Argument(  # noqa: B008
        None,
        metavar="[ACCESSION1 [...]]",
        help="Any number of valid accessions.",
        show_default=False,
    ),
    email: Optional[str] = typer.Option(
        ...,
        help="The email address to use to identify with the NCBI E-utilities.",
        show_default=False,
    ),
    version: Optional[bool] = typer.Option(  # noqa: B008
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print only the current tool version and exit.",
    ),
    log_level: LogLevel = typer.Option(  # noqa: B008
        LogLevel.INFO.value,
        "--log-level",
        "-l",
        case_sensitive=False,
        help="Set the desired log level.",
    ),
    # output: Path = typer.Option(  # noqa: B008
    #     ...,
    #     "--output",
    #     "-o",
    #     help="The desired output file. By default, the file extension will be used to "
    #     "determine the output format.",
    #     show_default=False,
    # ),
):
    """
    Either pass a number of accessions as arguments or pipe them into stdin with one
    accession per line.
    """
    try:
        from rich.logging import RichHandler

        logging.basicConfig(
            level=log_level.name,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[typer])],
        )
    except ModuleNotFoundError:
        logging.basicConfig(level=log_level.name, format="[%(levelname)s] %(message)s")

    if not accessions:
        accessions = [line.strip() for line in sys.stdin.readlines()]

    if not accessions:
        logger.error("No accessions given. Nothing to be done.")
        raise typer.Exit()

    ena_requests = ENAAPIPortalRequestService(settings=ENAAPIPortalSettings())
    ncbi_requests = NCBIEutilsRequestService(settings=NCBIEutilsSettings(email=email))
    run_info_app = RunInformationApplication(
        bio_project_mapping_service=ENAAPIPortalBioProjectMappingService,
        bio_sample_mapping_service=ENAAPIPortalBioSampleMappingService,
        insdc_study_mapping_service=ENAAPIPortalINSDCStudyMappingService,
        insdc_sample_mapping_service=ENAAPIPortalINSDCSampleMappingService,
        insdc_experiment_mapping_service=ENAAPIPortalINSDCExperimentMappingService,
        insdc_submission_mapping_service=ENAAPIPortalINSDCSubmissionMappingService,
        run_information_service=ENAAPIPortalRunInformationService,
        file_link_service=NCBIEutilsFileLinkService,
        ena_request_service=ena_requests,
        ncbi_request_service=ncbi_requests,
    )
    anyio.run(run_info_app.run, accessions)
