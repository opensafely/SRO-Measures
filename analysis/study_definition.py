# Import functions

from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    Measure
)

# Import codelists

from codelists import *
from datetime import date


start_date = "2020-12-07"
end_date = date.today().isoformat()
# Specifiy study definition

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": start_date, "latest": end_date},
        "rate": "exponential_increase",
        "incidence": 0.1,
    },
    
    population=patients.satisfying(
        """
        registered AND
        (NOT died)
        """
    ),

    registered = patients.registered_as_of(
        start_date,
        return_expectations={"incidence": 0.9},
        ),

    died = patients.died_from_any_cause(
        on_or_before=end_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.1}
    ),

    practice=patients.registered_practice_as_of(
        start_date,
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),
  

    sentinel_measure_x = patients.with_these_clinical_events(
        codelist = holder_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.1}
    )
)


measures = [
    Measure(
        id="sentinel_measure_x",
        numerator="sentinel_measure_x",
        denominator="population",
        group_by="population"
    )
]
