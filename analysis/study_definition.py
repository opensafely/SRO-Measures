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
  

    systolic_bp = patients.with_these_clinical_events(
        codelist = crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    systolic_bp_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
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
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    serum_cholesterol=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    serum_cholesterol_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    serum_bilirubin=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    serum_bilirubin_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    serum_tsh=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    serum_tsh_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    rbc=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    rbc_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    hba1c=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    hba1c_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
    ),

    serum_sodium=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    serum_sodium_event_code=patients.with_these_clinical_events(
        codelist=crd_codelist,
        between=[start_date, end_date],
        returning="code",
        return_expectations={"category": {
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
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
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
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
            "ratios": {"23E5.": 0.6, "663K.": 0.2, "7450.": 0.2}}, }
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
        numerator="serum_cholesterol",
        denominator="population",
        group_by=["practice", "serum_cholesterol_event_code"]
    ),

    Measure(
        id="serum_cholesterol_practice_only",
        numerator="serum_cholesterol",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="serum_bilirubin",
        numerator="serum_bilirubin",
        denominator="population",
        group_by=["practice", "serum_bilirubin_event_code"]
    ),

    Measure(
        id="serum_bilirubin_practice_only",
        numerator="serum_bilirubin",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="serum_tsh",
        numerator="serum_tsh",
        denominator="population",
        group_by=["practice", "serum_tsh_event_code"]
    ),

    Measure(
        id="serum_tsh_practice_only",
        numerator="serum_tsh",
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
        numerator="rbc",
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
        numerator="serum_sodium",
        denominator="population",
        group_by=["practice", "serum_sodium_event_code"]
    ),

    Measure(
        id="serum_sodium_practice_only",
        numerator="serum_sodium",
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
