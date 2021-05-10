import json
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


@pytest.fixture
def measure_table():
    """Returns a measure table that could have been read by calling `load_and_drop`."""
    mt = pandas.DataFrame(
        [
            MeasureTableRow(2, 1.0, 1.0, 1.0, 1.0, "2019-01-01"),
            MeasureTableRow(3, 2.0, 1.0, 1.0, 1.0, "2019-01-01"),
            MeasureTableRow(2, 1.0, 1.0, 1.0, 1.0, "2019-02-01"),
        ]
    )
    mt["date"] = pandas.to_datetime(mt["date"])
    return mt


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


def test_get_number_practices(measure_table_from_csv):
    assert utilities.get_number_practices(measure_table_from_csv) == 3


def test_get_percentage_practices(tmp_path, measure_table_from_csv):
    with patch.object(utilities, "OUTPUT_DIR", tmp_path):
        with open(utilities.OUTPUT_DIR / "practice_count.json", "w") as f:
            json.dump({"num_practices": 3}, f)

        obs = utilities.get_percentage_practices(measure_table_from_csv)
        assert obs == 100


def test_get_number_events_mil(measure_table_from_csv):
    obs = utilities.get_number_events_mil(
        measure_table_from_csv,
        "systolic_bp",
    )
    assert obs == 0.0


def test_get_number_patients(tmp_path):
    measure = "systolic_bp"

    with patch.object(utilities, "OUTPUT_DIR", tmp_path):
        with open(utilities.OUTPUT_DIR / "patient_count.json", "w") as f:
            json.dump({"num_patients": {measure: 3}}, f)

        obs = utilities.get_number_patients(measure)
        assert obs == 3


class TestGenerateSentinelMeasure:
    def test_print_to_stdout(
        self,
        capsys,  # pytest fixture that captures output stdout and stderr
        measure_table,
        codelist_table_from_csv,
    ):
        measure = "systolic_bp"
        data_dict = {measure: measure_table}
        data_dict_practice = {measure: measure_table}
        codelist_dict = {measure: codelist_table_from_csv}
        code_column = "code"
        term_column = "term"
        dates_list = None
        interactive = False

        # It's easier to patch each function that returns a value
        # that's printed to stdout than it is to patch each file
        # upon which each function depends.
        with patch(
            "notebooks.utilities.get_number_practices", return_value=1
        ), patch(
            "notebooks.utilities.get_percentage_practices", return_value=100
        ), patch(
            "notebooks.utilities.get_number_events_mil", return_value=0.0
        ), patch(
            "notebooks.utilities.get_number_patients", return_value=1
        ):
            utilities.generate_sentinel_measure(
                data_dict,
                data_dict_practice,
                codelist_dict,
                measure,
                code_column,
                term_column,
                dates_list,
                interactive,
            )
            captured = capsys.readouterr()
            assert captured.out.startswith(
                "Practices included: 1 (100%)\nTotal patients: 1.00M (0.00M events)\n"
            )
