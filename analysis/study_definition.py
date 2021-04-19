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


start_date = "2019-01-01"
end_date = date.today().isoformat()
# Specifiy study definition





study = StudyDefinition(
    index_date="2019-01-01",
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
        "index_date",
        return_expectations={"incidence": 0.9},
        ),

    died = patients.died_from_any_cause(
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.1}
    ),

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={"int" : {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence" : 0.5}
    ),
  
    systolic_bp=patients.with_these_clinical_events(
        codelist=systolic_bp_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    systolic_bp_event_code=patients.with_these_clinical_events(
        codelist=systolic_bp_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),
    
  
    qrisk2=patients.with_these_clinical_events(
        codelist=qrisk_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    qrisk2_event_code=patients.with_these_clinical_events(
        codelist=qrisk_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    cholesterol=patients.with_these_clinical_events(
        codelist=cholesterol_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    cholesterol_event_code=patients.with_these_clinical_events(
        codelist=cholesterol_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),
    
    bilirubin=patients.with_these_clinical_events(
        codelist=bilirubin_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    bilirubin_event_code=patients.with_these_clinical_events(
        codelist=bilirubin_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    tsh=patients.with_these_clinical_events(
        codelist=tsh_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    tsh_event_code=patients.with_these_clinical_events(
        codelist=tsh_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    rbc=patients.with_these_clinical_events(
        codelist=rbc_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    rbc_event_code=patients.with_these_clinical_events(
        codelist=rbc_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    hba1c=patients.with_these_clinical_events(
        codelist=hba1c_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    hba1c_event_code=patients.with_these_clinical_events(
        codelist=hba1c_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    sodium=patients.with_these_clinical_events(
        codelist=sodium_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    sodium_event_code=patients.with_these_clinical_events(
        codelist=sodium_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1085871000000105): 0.6, str(450759008): 0.2, str(718087004): 0.2}}, }
    ),

    asthma=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    asthma_event_code=patients.with_these_clinical_events(
        codelist=asthma_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(270442000): 0.6, str(390872009): 0.2, str(390877003): 0.2}}, }
    ),

    copd=patients.with_these_clinical_events(
        codelist=copd_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    copd_event_code=patients.with_these_clinical_events(
        codelist=copd_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(394703002): 0.6, str(760601000000107): 0.2, str(760621000000103): 0.2}}, }
    ),
)


measures = [
    
    Measure(
        id="systolic_bp",
        numerator="systolic_bp",
        denominator="population",
        group_by=["practice", "systolic_bp_event_code"]
    ),

    Measure(
        id="systolic_bp_practice_only",
        numerator="systolic_bp",
        denominator="population",
        group_by=["practice"]
    ),

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
        id="serum_cholesterol",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice", "cholesterol_event_code"]
    ),

    Measure(
        id="serum_cholesterol_practice_only",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice"]
    ),
   
    Measure(
        id="serum_bilirubin",
        numerator="bilirubin",
        denominator="population",
        group_by=["practice", "bilirubin_event_code"]
    ),

    Measure(
        id="serum_bilirubin_practice_only",
        numerator="bilirubin",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="serum_tsh",
        numerator="tsh",
        denominator="population",
        group_by=["practice", "tsh_event_code"]
    ),

    Measure(
        id="serum_tsh_practice_only",
        numerator="tsh",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="rbc",
        numerator="rbc",
        denominator="population",
        group_by=["practice", "rbc_event_code"]
    ),

    Measure(
        id="rbc_practice_only",
        numerator="tsh",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="hba1c",
        numerator="hba1c",
        denominator="population",
        group_by=["practice", "hba1c_event_code"]
    ),

    Measure(
        id="hba1c_practice_only",
        numerator="hba1c",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="serum_sodium",
        numerator="sodium",
        denominator="population",
        group_by=["practice", "sodium_event_code"]
    ),

    Measure(
        id="serum_sodium_practice_only",
        numerator="sodium",
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
