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
  

  
    qrisk2=patients.with_these_clinical_events(
        codelist=qrisk_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    qrisk2_event_code=patients.with_these_clinical_events(
        codelist=qrisk_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

  
    asthma=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    asthma_event_code=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(270442000): 0.6, str(390872009): 0.2, str(390877003): 0.2}}, }
    ),

    copd=patients.with_these_clinical_events(
        codelist=copd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    copd_event_code=patients.with_these_clinical_events(
        codelist=copd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(394703002): 0.6, str(760601000000107): 0.2, str(760621000000103): 0.2}}, }
    ),
)


measures = [
   
    Measure(
        id="qrisk2",
        numerator="qrisk2",
        denominator="population",
        group_by=["practice", "qrisk2_event_code"]
    ),

    Measure(
        id="qrisk2_practice_only",
        numerator="qrisk2",
        denominator="population",
        group_by=["practice"]
    ),

   
    Measure(
        id="asthma",
        numerator="asthma",
        denominator="population",
        group_by=["practice", "asthma_event_code"]
    ),

    Measure(
        id="asthma_practice_only",
        numerator="asthma",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="copd",
        numerator="copd",
        denominator="population",
        group_by=["practice", "copd_event_code"]
    ),

    Measure(
        id="copd_practice_only",
        numerator="copd",
        denominator="population",
        group_by=["practice"]
    ),
]
