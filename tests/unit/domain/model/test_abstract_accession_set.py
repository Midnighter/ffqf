import re

from ffqf.domain.model import AbstractAccessionSet


class ConcreteAccessionSet(AbstractAccessionSet):

    _validation_pattern = re.compile(r".*", flags=re.ASCII)


def test_eq_true():
    expected = {"foo", "bar"}
    acc_set = ConcreteAccessionSet.from_accessions(expected)
    assert expected == acc_set


def test_eq_false():
    expected = {"foo", "bar"}
    acc_set = ConcreteAccessionSet.from_accessions(expected)
    expected.add("baz")
    assert expected != acc_set


def test_contains():
    expected = ["foo", "bar"]
    acc_set = ConcreteAccessionSet.from_accessions(expected)
    for acc in expected:
        assert acc in acc_set


def test_len():
    expected = ["foo", "bar"]
    acc_set = ConcreteAccessionSet.from_accessions(expected)
    assert len(acc_set) == 2
