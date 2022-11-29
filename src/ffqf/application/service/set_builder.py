import logging
import re
from typing import Iterable

from ffqf.domain.model import (
    BioProjectSet,
    BioSampleSet,
    INSDCStudySet,
    INSDCSampleSet,
    INSDCExperimentSet,
    INSDCSubmissionSet,
    INSDCRunSet,
)


logger = logging.getLogger(__name__)


class SetBuilder:

    recognized_accession = re.compile(
        r"^(((SR|ER|DR)[APRSX])|(SAM(N|EA|EG|D))|(PRJ(NA|EB|DB))|(GS[EM]))(\d+)$",
        flags=re.ASCII,
    )
    BIO_PROJECT_PREFIX = "PRJ"
    BIO_SAMPLE_PREFIX = "SAM"
    study_pattern = re.compile(r"^(SR|ER|DR)P")
    sample_pattern = re.compile(r"^(SR|ER|DR)S")
    experiment_pattern = re.compile(r"^(SR|ER|DR)X")
    run_pattern = re.compile(r"^(SR|ER|DR)R")
    submission_pattern = re.compile(r"^(SR|ER|DR)A")

    def __init__(self, **kwargs) -> None:
        """"""
        super().__init__(**kwargs)
        self.bio_projects = BioProjectSet()
        self.bio_samples = BioSampleSet()
        self.studies = INSDCStudySet()
        self.samples = INSDCSampleSet()
        self.experiments = INSDCExperimentSet()
        self.runs = INSDCRunSet()
        self.submissions = INSDCSubmissionSet()

    def from_accessions(self, accessions: Iterable[str]):
        """"""
        for acc in accessions:
            if not self.recognized_accession.match(acc):
                logger.error("Invalid or unrecognized accession '%s'. Ignored.", acc)

            if acc.startswith(self.BIO_PROJECT_PREFIX):
                self.bio_projects.add(acc)
            elif acc.startswith(self.BIO_SAMPLE_PREFIX):
                self.bio_samples.add(acc)
            elif self.study_pattern.match(acc):
                self.studies.add(acc)
            elif self.study_pattern.match(acc):
                self.studies.add(acc)
            elif self.sample_pattern.match(acc):
                self.samples.add(acc)
            elif self.experiment_pattern.match(acc):
                self.experiments.add(acc)
            elif self.run_pattern.match(acc):
                self.runs.add(acc)
            elif self.submission_pattern.match(acc):
                self.submissions.add(acc)
            else:
                raise RuntimeError(f"Could not match accession '{acc}'. Unexpected.")
