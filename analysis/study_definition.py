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
  

    chronic_respiratory_disease = patients.with_these_clinical_events(
        codelist = crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    chronic_respiratory_disease_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),
)


measures = [
    Measure(
        id="chronic_respiratory_disease",
        numerator="chronic_respiratory_disease",
        denominator="population",
        group_by=["practice", "chronic_respiratory_disease_event_code"]
    ),

    Measure(
        id="chronic_respiratory_disease_practice_only",
        numerator="chronic_respiratory_disease",
        denominator="population",
        group_by=["practice"]
    )
]
