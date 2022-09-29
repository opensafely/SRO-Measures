import pytest
import pandas as pd

from analysis import utilities

input_df_params = [
    #patient 2 has left. none have joined
    {
        "obs": {
            "patient_id": pd.Series([1, 3, 4, 5]),
            "age": pd.Series([20, 40, 50, 60]),
            "age_start": pd.Series([20, 40, 50, 60]),
            "ethnicity": pd.Series([3, 2, 1, 3])
        },
        "exp_joined": {
            "patient_id": pd.Series([], dtype="int64"),
            "ethnicity": pd.Series([], dtype="int64"),
            "ehr_provider": pd.Series([], dtype="object")
        },
        "exp_left": {
            "patient_id": pd.Series([2]),
            "ethnicity": pd.Series([4]),
            "ehr_provider": pd.Series(["EMIS"])
        }
    },

    # patient 6 has joined. Patient 7 has joined (but because they fit age criteria). none have left
    {
        "obs": {
            "patient_id": pd.Series([1, 2, 3, 4, 5, 6, 7]),
            "age": pd.Series([20, 30, 40, 50, 60, 70, 18]),
            "age_start": pd.Series([20, 30, 40, 50, 60, 70, 17]),
            "ethnicity": pd.Series([3, 4, 2, 1, 3, 1, 4])
        },
        "exp_left": {
            "patient_id": pd.Series([], dtype="int64"),
            "ethnicity": pd.Series([], dtype="int64"),
            "ehr_provider": pd.Series([], dtype="object")
        },
        "exp_joined": {
            "patient_id": pd.Series([6]),
            "ethnicity": pd.Series([1]),
            "ehr_provider": pd.Series(["TPP"])
        }
    },

    # patient 8 has joined. Patient 7 has joined (but because they fit age criteria). patient 2 has left
    {
        "obs": {
            "patient_id": pd.Series([1, 3, 4, 5, 6, 7, 8]),
            "age": pd.Series([20, 40, 50, 60, 70, 18, 40]),
            "age_start": pd.Series([20, 40, 50, 60, 70, 17, 40]),
            "ethnicity": pd.Series([3, 2, 1, 3, 1, 4, 5])
        },
        "exp_left": {
            "patient_id": pd.Series([2], dtype="int64"),
            "ethnicity": pd.Series([4], dtype="int64"),
            "ehr_provider": pd.Series(["EMIS"], dtype="object")
        },
        "exp_joined": {
            "patient_id": pd.Series([6, 8]),
            "ethnicity": pd.Series([1, 5]),
            "ehr_provider": pd.Series(["TPP", "TPP"])
        }
    }

]

@pytest.fixture()
def input_df_comparator():
    """Returns an input like dataframe"""
    return pd.DataFrame(
        {
            "patient_id": pd.Series([1, 2, 3, 4, 5]),
            "age": pd.Series([20, 30, 40, 50, 60]),
            "age_start": pd.Series([20, 30, 40, 50, 60]),
            "ethnicity": pd.Series([3, 4, 2, 1, 3])
        }
    )

@pytest.mark.parametrize("input_df_params", input_df_params)
class TestGetMovedPatients:
    def test_get_patients_joined_tpp(self, input_df_params, input_df_comparator):
        obs = utilities.get_patients_joined_tpp(pd.DataFrame(input_df_params["obs"]), input_df_comparator, "age", "age_start", ["ethnicity"])
        exp = pd.DataFrame(input_df_params["exp_joined"])
        pd.testing.assert_frame_equal(obs, exp)

    def test_get_patients_left_tpp(self,input_df_params, input_df_comparator):
        obs = utilities.get_patients_left_tpp(pd.DataFrame(input_df_params["obs"]), input_df_comparator, ["ethnicity"])
        exp = pd.DataFrame(input_df_params["exp_left"])
        pd.testing.assert_frame_equal(obs, exp)