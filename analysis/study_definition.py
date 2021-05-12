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
end_date = "2021-04-30"
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
        """,

        registered = patients.registered_as_of(
        "index_date",
        return_expectations={"incidence": 0.9},
        ),

        died = patients.died_from_any_cause(
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.1}
        ),
    ),

    


    age=patients.age_as_of(
        "index_date",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),

    age_band=patients.categorised_as(
        {
            "missing": "DEFAULT",
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.125,
                }
            },
        },

    ),


    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.5, "U": 0.01}},
        }
    ),

    region=patients.registered_practice_as_of(
        "index_date",
        returning="nuts1_region_name",
        return_expectations={"category": {"ratios": {
            "North East": 0.1,
            "North West": 0.1,
            "Yorkshire and the Humber": 0.1,
            "East Midlands": 0.1,
            "West Midlands": 0.1,
            "East of England": 0.1,
            "London": 0.2,
            "South East": 0.2, }}}
    ),
    
    imd=patients.address_as_of(
        "index_date",
        returning="index_of_multiple_deprivation",
        round_to_nearest=100,
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"100": 0.2, "200": 0.2, "300": 0.2, "400": 0.2, "500": 0.2}},
        },
    ),

    learning_disability=patients.with_these_clinical_events(
        ld_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01, },
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
            "ratios": {str(198081000000101): 0.6, str(251070002): 0.2, str(271649006): 0.2}}, }
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
            "ratios": {str(1005671000000105): 0.8, str(1017161000000104): 0.2}}, }
    ),
    
    alt=patients.with_these_clinical_events(
        codelist=alt_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={"incidence": 0.5}
    ),

    alt_event_code=patients.with_these_clinical_events(
        codelist=alt_codelist,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="code",
        return_expectations={"category": {
            "ratios": {str(1013211000000103): 0.8, str(1018251000000107): 0.2}}, }
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
            "ratios": {str(1022791000000101): 0.8, str(1022801000000102): 0.2}}, }
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
            "ratios": {str(1022451000000103): 1}}, }
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
            "ratios": {str(1003671000000109): 0.6, str(144176003): 0.2, str(166902009): 0.2}}, }
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
            "ratios": {str(1000661000000107): 0.6, str(1017381000000106): 0.4}}, }
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
        id="cholesterol",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice", "cholesterol_event_code"]
    ),

    Measure(
        id="cholesterol_practice_only",
        numerator="cholesterol",
        denominator="population",
        group_by=["practice"]
    ),
   
    Measure(
        id="alt",
        numerator="alt",
        denominator="population",
        group_by=["practice", "alt_event_code"]
    ),

    Measure(
        id="alt_practice_only",
        numerator="alt",
        denominator="population",
        group_by=["practice"]
    ),

    Measure(
        id="tsh",
        numerator="tsh",
        denominator="population",
        group_by=["practice", "tsh_event_code"]
    ),

    Measure(
        id="tsh_practice_only",
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
        id="sodium",
        numerator="sodium",
        denominator="population",
        group_by=["practice", "sodium_event_code"]
    ),

    Measure(
        id="sodium_practice_only",
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

demographics = ['region', 'sex', 'imd', 'learning_disability', 'age_band']
sentinel_measures = ['systolic_bp', 'qrisk2', 'cholesterol', 'alt', 'tsh', 'rbc', 'hba1c', 'sodium', 'asthma', 'copd']

# for sentinel_measure in sentinel_measures:
#     for d in demographics:
#         if d=='age_band':
#             m = Measure(
#             id=f'{sentinel_measure}_{d}',
#             numerator=sentinel_measure,
#             denominator="population",
#             group_by=["age_band", "practice"]
#             )
                
            

        
#         else:

#             m = Measure(
#                 id=f'{sentinel_measure}_{d}',
#                 numerator=sentinel_measure,
#                 denominator="population",
#                 group_by=["age_band", d, "practice"]
#             )
        
#         measures.append(m)
