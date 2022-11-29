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


"""Provide a container model for INSDC study accessions."""


from __future__ import annotations

import re
from typing import ClassVar, Pattern

from .abstract_accession_set import AbstractAccessionSet


class INSDCRunSet(AbstractAccessionSet):
    """
    Define the container model for INSDC study accessions.

    > The International Nucleotide Sequence Database Collaboration (INSDC) is a
    long-standing foundational initiative that operates between DDBJ, EMBL-EBI (ENA),
    and NCBI.

    > INSDC covers the spectrum of data raw reads, through alignments and assemblies to
    functional annotation, enriched with contextual information relating to samples and
    experimental configurations.

    https://www.insdc.org/

    """

    _validation_pattern: ClassVar[Pattern] = re.compile(
        r"^((SR|ER|DR)R)(\d+)$",
        flags=re.ASCII,
    )
