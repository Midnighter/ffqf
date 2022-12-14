import logging
import re
import sys
from enum import Enum, unique
from pathlib import Path
from typing import Collection, List, Optional

import anyio
import typer

import ffqf
from ffqf.application import RunInformationApplication
from ffqf.infrastructure.application.service import (
    ENAAPIPortalBioProjectMappingService,
    ENAAPIPortalBioSampleMappingService,
    ENAAPIPortalINSDCExperimentMappingService,
    ENAAPIPortalINSDCSampleMappingService,
    ENAAPIPortalINSDCStudyMappingService,
    ENAAPIPortalINSDCSubmissionMappingService,
    ENAAPIPortalRequestService,
    ENAAPIPortalRunInformationService,
    ENAAPIPortalSettings,
    NCBIEutilsFileLinkService,
    NCBIEutilsRequestService,
    NCBIEutilsSettings,
    RunInformationJSONOutputWriter,
    RunInformationTableOutputWriter,
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


@unique
class OutputFormat(str, Enum):
    """Define the choices for the output format option."""

    TSV = "TSV"
    CSV = "CSV"
    JSON = "JSON"


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
    email: Optional[str] = typer.Option(  # noqa: B008
        ...,
        help="The email address to use to identify with the NCBI E-utilities.",
        show_default=False,
    ),
    output: Optional[Path] = typer.Option(  # noqa: B008
        None,
        "--output",
        "-o",
        help="If you want to write the result to a file instead of to stdout. The file "
        "extension is used to determine the format if none is specified explicitly.",
        show_default=False,
    ),
    output_format: OutputFormat = typer.Option(  # noqa: B008
        default=OutputFormat.JSON,
        help="Explicitly set the output format; applies to stdout or file output.",
        case_sensitive=False,
        show_default=True,
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
    result = anyio.run(run_info_app.run, accessions)
    if output_format is OutputFormat.JSON:
        RunInformationJSONOutputWriter.write(result, output)
    elif output_format is OutputFormat.TSV:
        RunInformationTableOutputWriter.write(result, output)
    elif output_format is OutputFormat.CSV:
        RunInformationTableOutputWriter.write(result, output, dialect="excel")
