from typing import NamedTuple
from unittest.mock import patch

import pandas
import pytest
from pandas import testing
from pandas.api.types import is_datetime64_dtype

from notebooks import utilities


class MeasureTableRow(NamedTuple):
    """Represents a row in a measure table."""

    practice: int  # group_by 0 (PK)
    systolic_bp_event_code: float  # group_by 1 (PK)
    systolic_bp: float  # numerator
    population: float  # denominator
    value: float  # numerator / denominator
    date: str  # index_date (PK)


@pytest.fixture
def measure_table_from_csv():
    """Returns a measure table that could have been read from a CSV file.

    Practice ID #1 is irrelevant; that is, it has zero events during
    the study period.
    """
    return pandas.DataFrame(
        [
            MeasureTableRow(1, 1.0, 0.0, 1.0, 0.0, "2019-01-01"),
            MeasureTableRow(2, 1.0, 1.0, 1.0, 1.0, "2019-01-01"),
            MeasureTableRow(3, 2.0, 1.0, 1.0, 1.0, "2019-01-01"),
            MeasureTableRow(1, 1.0, 0.0, 1.0, 0.0, "2019-02-01"),
            MeasureTableRow(2, 1.0, 1.0, 1.0, 1.0, "2019-02-01"),
        ]
    )


class CodelistTableRow(NamedTuple):
    """Represents a row in a codelist table."""

    code: int
    term: str


@pytest.fixture
def codelist_table_from_csv():
    """Returns a codelist table the could have been read from a CSV file."""
    return pandas.DataFrame(
        [
            CodelistTableRow(1.0, "Code 1"),
            CodelistTableRow(2.0, "Code 2"),
        ]
    )


class TestLoadAndDrop:
    def test_practice_is_false(self, tmp_path, measure_table_from_csv):
        # What's going on here, then? We are patching, or temporarily
        # replacing, `utilities.OUTPUT_DIR` with `tmp_path`, which is
        # a pytest fixture that returns a temporary directory as
        # a `pathlib.Path` object.
        with patch.object(utilities, "OUTPUT_DIR", tmp_path):
            measure = "systolic_bp"
            f_name = f"measure_{measure}.csv"
            measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)

            obs = utilities.load_and_drop(measure)
            assert is_datetime64_dtype(obs.date)
            assert all(obs.practice.values == [2, 3, 2])

    def test_practice_is_true(self, tmp_path, measure_table_from_csv):
        with patch.object(utilities, "OUTPUT_DIR", tmp_path):
            measure = "systolic_bp"
            f_name = f"measure_{measure}_practice_only.csv"
            measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)

            obs = utilities.load_and_drop(measure, practice=True)
            assert is_datetime64_dtype(obs.date)
            assert all(obs.practice.values == [2, 3, 2])


class TestDropIrrelevantPractices:
    def test_irrelevant_practices_dropped(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        # Practice ID #1, which is irrelevant, has been dropped from
        # the measure table.
        assert all(obs.practice.values == [2, 3, 2])

    def test_return_copy(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        assert id(obs) != id(measure_table_from_csv)


def test_get_child_codes(measure_table_from_csv):
    obs = utilities.get_child_codes(measure_table_from_csv, "systolic_bp")
    # Dicts keep insertion order from Python 3.7.
    assert list(obs.keys()) == [1, 2]
    assert list(obs.values()) == [2, 1]


def test_create_child_table(measure_table_from_csv, codelist_table_from_csv):
    obs = utilities.create_child_table(
        measure_table_from_csv,
        codelist_table_from_csv,
        "code",
        "term",
        "systolic_bp",
    )
    exp = pandas.DataFrame(
        [
            {
                "code": 1,
                "Events": 2.0,
                "Events (thousands)": 0.002,
                "Description": "Code 1",
            },
            {
                "code": 2,
                "Events": 1.0,
                "Events (thousands)": 0.001,
                "Description": "Code 2",
            },
        ],
    )
    testing.assert_frame_equal(obs, exp)
