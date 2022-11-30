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


"""Provide an abstract interface for sets of accessions."""


from __future__ import annotations

from abc import ABC
from typing import ClassVar, Iterable, Pattern, Set, Union


class AbstractAccessionSet(ABC):
    """"""

    _validation_pattern: ClassVar[Pattern]

    def __init__(self, **kwargs) -> None:
        """"""
        super().__init__(**kwargs)
        self._accessions: Set[str] = set()

    @classmethod
    def from_accessions(cls, accessions: Iterable[str]) -> AbstractAccessionSet:
        """"""
        result = cls()
        result.update(accessions=accessions)
        return result

    def __iter__(self) -> Iterable[str]:
        """"""
        return iter(self._accessions)

    def __contains__(self, accession: str) -> bool:
        """"""
        return accession in self._accessions

    def __len__(self) -> int:
        return len(self._accessions)

    def __eq__(self, other: Union[AbstractAccessionSet, Set]) -> bool:
        if isinstance(other, AbstractAccessionSet):
            return other._accessions == self._accessions
        else:
            return other == self._accessions

    def add(self, accession: str) -> None:
        """"""
        if self._validation_pattern.match(accession):
            self._accessions.add(accession)
        else:
            raise ValueError(f"Invalid accession '{accession}'.")

    def update(self, accessions: Iterable[str]) -> None:
        for acc in accessions:
            self.add(acc)

    def difference(self, other: Iterable[str]) -> AbstractAccessionSet:
        return self.from_accessions(self._accessions.difference(other))
