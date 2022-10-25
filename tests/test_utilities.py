import json
from unittest.mock import patch
import pandas
import pytest
from pandas import testing
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype

from analysis import utilities


@pytest.fixture
def measure_table_from_csv():
    """Returns a measure table that could have been read from a CSV file.

    Practice ID #1 is irrelevant; that is, it has zero events during
    the study period.
    """
    return pandas.DataFrame(
        {
            "practice": pandas.Series([1, 2, 3, 1, 2]),
            "systolic_bp_event_code": pandas.Series([1, 1, 2, 1, 1]),
            "systolic_bp": pandas.Series([0, 1, 1, 0, 1]),
            "population": pandas.Series([1, 1, 1, 1, 1]),
            "value": pandas.Series([0, 1, 1, 0, 1]),
            "date": pandas.Series(
                [
                    "2019-01-01",
                    "2019-01-01",
                    "2019-01-01",
                    "2019-02-01",
                    "2019-02-01",
                ]
            ),
        }
    )


@pytest.fixture
def measure_table():
    """Returns a measure table that could have been read by calling `load_and_drop`."""
    mt = pandas.DataFrame(
        {
            "practice": pandas.Series([2, 3, 2]),
            "systolic_bp_event_code": pandas.Series([1, 2, 1]),
            "systolic_bp": pandas.Series([1, 1, 1]),
            "population": pandas.Series([1, 1, 1]),
            "value": pandas.Series([1, 1, 1]),
            "date": pandas.Series(["2019-01-01", "2019-01-01", "2019-02-01"]),
        }
    )
    mt["date"] = pandas.to_datetime(mt["date"])
    return mt


@pytest.fixture
def codelist_table_from_csv():
    """Returns a codelist table the could have been read from a CSV file."""
    return pandas.DataFrame(
        {
            "code": pandas.Series([1, 2]),
            "term": pandas.Series(["Code 1", "Code 2"]),
        }
    )


class TestLoadAndDrop:
    def test_practice_is_false(self, tmp_path, measure_table_from_csv):
        # What's going on here, then? We are patching, or temporarily
        # replacing, `utilities.OUTPUT_DIR` with `tmp_path`, which is
        # a pytest fixture that returns a temporary directory as
        # a `pathlib.Path` object.
        with patch.object(utilities, "OUTPUT_DIR", tmp_path):
            measure = "systolic_bp"
            f_name = f"measure_{measure}_rate.csv"
            measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)
            obs = utilities.load_and_drop(measure)
            assert is_datetime64_dtype(obs.date)
            assert all(obs.practice.values == [2, 3, 2])

    def test_practice_is_true(self, tmp_path, measure_table_from_csv):
        with patch.object(utilities, "OUTPUT_DIR", tmp_path):
            measure = "systolic_bp"
            f_name = f"measure_{measure}_practice_only_rate.csv"
            measure_table_from_csv.to_csv(utilities.OUTPUT_DIR / f_name)
            obs = utilities.load_and_drop(measure, practice=True)
            assert is_datetime64_dtype(obs.date)
            print(obs.columns.values)
            assert obs.columns.values.all() in ['rate', 'date']


def test_calculate_rate():
    mt = pandas.DataFrame(
        {
            "systolic_bp": pandas.Series([1, 2]),
            "population": pandas.Series([1_000, 2_000]),
        }
    )
    testing.assert_index_equal(
        mt.columns,
        pandas.Index(["systolic_bp", "population"]),
    )

    utilities.calculate_rate(mt, "systolic_bp", "population")

    testing.assert_index_equal(
        mt.columns,
        pandas.Index(["systolic_bp", "population", "rate"]),
    )
    testing.assert_series_equal(
        mt.rate,
        pandas.Series([1.0, 1.0], name="rate"),
    )


class TestDropIrrelevantPractices:
    def test_irrelevant_practices_dropped(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        # Practice ID #1, which is irrelevant, has been dropped from
        # the measure table.
        assert all(obs.practice.values == [2, 3, 2])

    def test_return_copy(self, measure_table_from_csv):
        obs = utilities.drop_irrelevant_practices(measure_table_from_csv)
        assert id(obs) != id(measure_table_from_csv)


def test_create_child_table(measure_table, codelist_table_from_csv):
    obs, obs_with_count = utilities.create_child_table(
        measure_table,
        codelist_table_from_csv,
        "code",
        "term",
        "systolic_bp",
    )

    exp = pandas.DataFrame(
        [
            {
                "code": 1,
                "Description": "Code 1",
                "Proportion of codes (%)": 66.67
            },
            {
                "code": 2,
                "Description": "Code 2",
                "Proportion of codes (%)": 33.33 
                
            },
        ],
    )

    exp_with_count = pandas.DataFrame(
        [
            {
                "code": 1,
                "Description": "Code 1",
                "Events": 2,
                "Proportion of codes (%)": 66.67
            },
            {
                "code": 2,
                "Description": "Code 2",
                "Events": 1,
                "Proportion of codes (%)": 33.33 
                
            },
        ],
    )

    testing.assert_frame_equal(obs, exp, check_dtype=False)
    testing.assert_frame_equal(obs_with_count, exp_with_count, check_dtype=False)

def test_get_number_practices(measure_table):
    assert utilities.get_number_practices(measure_table) == 2


def test_get_percentage_practices(tmp_path, measure_table):
    with patch.object(utilities, "OUTPUT_DIR", tmp_path):
        with open(utilities.OUTPUT_DIR / "practice_count.json", "w") as f:
            json.dump({"num_practices": 2}, f)

        obs = utilities.get_percentage_practices(measure_table)
        assert obs == 100


def test_get_number_events_mil(measure_table):
    _,obs = utilities.get_number_events_mil(
        measure_table,
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


@pytest.mark.parametrize(
    "has_outer_percentiles,num_rows",
    [
        (True, 54),  # Fifteen percentiles for two dates
        (False, 18),  # Nine deciles for two dates
    ],
)
def test_compute_deciles(measure_table, has_outer_percentiles, num_rows):
    obs = utilities.compute_deciles(
        measure_table,
        "date",
        "value",
        has_outer_percentiles=has_outer_percentiles,
    )
    # We expect Pandas to check that it computes deciles correctly,
    # leaving us to check the shape and the type of the data.
    testing.assert_index_equal(
        obs.columns,
        pandas.Index(["date", "percentile", "value"]),
    )
    assert len(obs) == num_rows
    assert is_datetime64_dtype(obs.date)
    assert is_numeric_dtype(obs.percentile)
    assert is_numeric_dtype(obs.value)



input_df_params = [
    #patient 2 has left. none have joined
    {
        "obs": {
            "patient_id": pandas.Series([1, 3, 4, 5]),
            "age": pandas.Series([20, 40, 50, 60]),
            "age_start": pandas.Series([20, 40, 50, 60]),
            "ethnicity": pandas.Series([3, 2, 1, 3])
        },
        "exp_joined": {
            "patient_id": pandas.Series([], dtype="int64"),
            "ethnicity": pandas.Series([], dtype="int64"),
            "ehr_provider": pandas.Series([], dtype="object")
        },
        "exp_left": {
            "patient_id": pandas.Series([2]),
            "ethnicity": pandas.Series([4]),
            "ehr_provider": pandas.Series(["EMIS"])
        }
    },

    # patient 6 has joined. Patient 7 has joined (but because they fit age criteria). none have left
    {
        "obs": {
            "patient_id": pandas.Series([1, 2, 3, 4, 5, 6, 7]),
            "age": pandas.Series([20, 30, 40, 50, 60, 70, 18]),
            "age_start": pandas.Series([20, 30, 40, 50, 60, 70, 17]),
            "ethnicity": pandas.Series([3, 4, 2, 1, 3, 1, 4])
        },
        "exp_left": {
            "patient_id": pandas.Series([], dtype="int64"),
            "ethnicity": pandas.Series([], dtype="int64"),
            "ehr_provider": pandas.Series([], dtype="object")
        },
        "exp_joined": {
            "patient_id": pandas.Series([6]),
            "ethnicity": pandas.Series([1]),
            "ehr_provider": pandas.Series(["TPP"])
        }
    },

    # patient 8 has joined. Patient 7 has joined (but because they fit age criteria). patient 2 has left
    {
        "obs": {
            "patient_id": pandas.Series([1, 3, 4, 5, 6, 7, 8]),
            "age": pandas.Series([20, 40, 50, 60, 70, 18, 40]),
            "age_start": pandas.Series([20, 40, 50, 60, 70, 17, 40]),
            "ethnicity": pandas.Series([3, 2, 1, 3, 1, 4, 5])
        },
        "exp_left": {
            "patient_id": pandas.Series([2], dtype="int64"),
            "ethnicity": pandas.Series([4], dtype="int64"),
            "ehr_provider": pandas.Series(["EMIS"], dtype="object")
        },
        "exp_joined": {
            "patient_id": pandas.Series([6, 8]),
            "ethnicity": pandas.Series([1, 5]),
            "ehr_provider": pandas.Series(["TPP", "TPP"])
        }
    }
]

@pytest.fixture()
def input_df_comparator():
    """Returns an input like dataframe"""
    return pandas.DataFrame(
        {
            "patient_id": pandas.Series([1, 2, 3, 4, 5]),
            "age": pandas.Series([20, 30, 40, 50, 60]),
            "age_start": pandas.Series([20, 30, 40, 50, 60]),
            "ethnicity": pandas.Series([3, 4, 2, 1, 3])
        }
    )

@pytest.mark.parametrize("input_df_params", input_df_params)
class TestGetMovedPatients:
    def test_get_patients_joined_tpp(self, input_df_params, input_df_comparator):
        obs = utilities.get_patients_joined_tpp(pandas.DataFrame(input_df_params["obs"]), input_df_comparator, "age", "age_start", ["ethnicity"])
        exp = pandas.DataFrame(input_df_params["exp_joined"])
        pandas.testing.assert_frame_equal(obs, exp)

    def test_get_patients_left_tpp(self,input_df_params, input_df_comparator):
        obs = utilities.get_patients_left_tpp(pandas.DataFrame(input_df_params["obs"]), input_df_comparator, ["ethnicity"])
        exp = pandas.DataFrame(input_df_params["exp_left"])
        pandas.testing.assert_frame_equal(obs, exp)
