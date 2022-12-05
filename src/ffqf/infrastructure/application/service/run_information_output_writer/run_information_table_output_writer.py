import csv
import sys
from pathlib import Path
from typing import List, Optional, TextIO

from ffqf.application.service import RunInformationOutputWriter
from ffqf.domain.model import RunInformation, URLType


class RunInformationTableOutputWriter(RunInformationOutputWriter):
    @classmethod
    def write(
        cls, run_info: List[RunInformation], output: Optional[Path] = None, **kwargs
    ) -> None:
        """"""
        if "fieldnames" not in kwargs:
            kwargs["fieldnames"] = header = list(run_info[0].dict(exclude={"files"}))
            header.extend(["aws_files", "aws_md5", "gcp_files", "gcp_md5"])
        if "dialect" not in kwargs:
            kwargs["dialect"] = "excel-tab"
        if "quoting" not in kwargs:
            kwargs["quoting"] = csv.QUOTE_NONNUMERIC
        if output:
            with output.open(mode="w", newline="") as handle:
                cls._write(run_info, handle, **kwargs)
        else:
            cls._write(run_info, sys.stdout, **kwargs)

    @classmethod
    def _write(cls, run_info: List[RunInformation], handle: TextIO, **kwargs) -> None:
        writer = csv.DictWriter(handle, **kwargs)
        writer.writeheader()
        for run in run_info:
            writer.writerow(cls._prepare_row(run))

    @classmethod
    def _prepare_row(cls, run: RunInformation) -> dict:
        result = run.dict(exclude={"files"})
        aws_files = []
        aws_md5 = []
        gcp_files = []
        gcp_md5 = []
        for desc in run.files:
            if desc.type != "fastq":
                continue
            if desc.urltype is URLType.AWS:
                aws_files.append(str(desc.url))
                aws_md5.append(desc.md5)
            elif desc.urltype is URLType.GCP:
                gcp_files.append(str(desc.url))
                gcp_md5.append(desc.md5)
        if aws_files:
            result["aws_files"] = ";".join(aws_files)
        if aws_md5:
            result["aws_md5"] = ";".join(aws_md5)
        if gcp_files:
            result["gcp_files"] = ";".join(gcp_files)
        if gcp_md5:
            result["gcp_md5"] = ";".join(gcp_md5)
        return result
