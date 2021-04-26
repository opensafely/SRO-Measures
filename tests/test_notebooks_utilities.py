from typing import NamedTuple

import pandas
import pytest

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
            MeasureTableRow(1, 1.0, 0.0, 1.0, 0.0, "2019-02-01"),
            MeasureTableRow(2, 1.0, 1.0, 1.0, 1.0, "2019-02-01"),
        ]
    )


class TestDropIrrelevantPractices:
    def test_irrelevant_practices_dropped(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        # Practice ID #1, which is irrelevant, has been dropped from
        # the measure table.
        assert all(obs.practice.values == [2, 2])

    def test_return_copy(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        assert id(obs) != id(measure_table_from_csv)
