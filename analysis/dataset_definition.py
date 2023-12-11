from datetime import datetime

from ehrql import Dataset, INTERVAL, Measures, case, months, when
from ehrql.codes import codelist_from_csv
from ehrql.tables.beta.core import patients, clinical_events
from ehrql.tables.beta.tpp import addresses, practice_registrations

codelists = {
    "asthma": codelist_from_csv(
        "codelists/opensafely-asthma-annual-review-qof.csv", column="code"
    ),
    "copd": codelist_from_csv(
        "codelists/opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
        column="code",
    ),
    "qrisk": codelist_from_csv(
        "codelists/opensafely-cvd-risk-assessment-score-qof.csv", column="code"
    ),
    "tsh": codelist_from_csv(
        "codelists/opensafely-thyroid-stimulating-hormone-tsh-testing.csv",
        column="code",
    ),
    "alt": codelist_from_csv(
        "codelists/opensafely-alanine-aminotransferase-alt-tests.csv", column="code"
    ),
    "cholesterol": codelist_from_csv(
        "codelists/opensafely-cholesterol-tests.csv", column="code"
    ),
    "hba1c": codelist_from_csv(
        "codelists/opensafely-glycated-haemoglobin-hba1c-tests.csv", column="code"
    ),
    "rbc": codelist_from_csv(
        "codelists/opensafely-red-blood-cell-rbc-tests.csv", column="code"
    ),
    "sodium": codelist_from_csv(
        "codelists/opensafely-sodium-tests-numerical-value.csv", column="code"
    ),
    "systolic_bp": codelist_from_csv(
        "codelists/opensafely-systolic-blood-pressure-qof.csv", column="code"
    ),
    "eth2001": codelist_from_csv(
        "codelists/primis-covid19-vacc-uptake-eth2001.csv",
        column="code",
        category_column="grouping_16_id",
    ),
    "medication_review_1": codelist_from_csv(
        "codelists/opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
        column="code",
    ),
    "medication_review_2": codelist_from_csv(
        "codelists/nhsd-primary-care-domain-refsets-medrvw_cod.csv", column="code"
    ),
}

dataset = Dataset()
age = patients.age_on(date=INTERVAL.start_date)
age_18_to_120 = (age >= 18) & (age < 120)

registered_practice = practice_registrations.for_patient_on(INTERVAL.start_date)
registered_practice_id = registered_practice.practice_pseudo_id

registered_at_start_of_interval = registered_practice.exists_for_patient()

sex = patients.sex

date_of_death = patients.date_of_death
has_died = date_of_death.is_not_null()

died_before_interval_start = has_died & date_of_death.is_before(INTERVAL.start_date)


key_measures = [
    "asthma",
    "copd",
    "qrisk",
    "tsh",
    "alt",
    "cholesterol",
    "hba1c",
    "rbc",
    "sodium",
    "systolic_bp",
    "medication_review",
]

measures_variables = {}

for m in key_measures:
    if m == "medication_review":
        measures_variables[m] = clinical_events.where(
            clinical_events.snomedct_code.is_in(
                codelists["medication_review_1"] + codelists["medication_review_2"]
            )
        ).where(
            clinical_events.date.is_on_or_between(
                INTERVAL.start_date, INTERVAL.end_date
            )
        )
    else:
        measures_variables[m] = clinical_events.where(
            clinical_events.snomedct_code.is_in(codelists[m])
        ).where(
            clinical_events.date.is_on_or_between(
                INTERVAL.start_date, INTERVAL.end_date
            )
        )
    measures_variables[m + "_binary_flag"] = measures_variables[m].exists_for_patient()
    measures_variables[m + "_code"] = (
        measures_variables[m]
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code
    )


denominator = (
    registered_at_start_of_interval
    & age_18_to_120
    & ~died_before_interval_start
    & sex.is_in(["male", "female"])
)

measures = Measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    denominator=denominator,
)


def calculate_num_intervals(start_date):
    """
    Calculate the number of intervals between the start date and the start of the latest full month
    Args:
        start_date: the start date of the study period
    Returns:
        num_intervals (int): the number of intervals between the start date and the start of the latest full month
    """
    now = datetime.now()
    start_of_latest_full_month = datetime(now.year, now.month, 1)

    num_intervals = (
        start_of_latest_full_month.year - datetime.strptime(start_date, "%Y-%m-%d").year
    ) * 12 + (
        start_of_latest_full_month.month
        - datetime.strptime(start_date, "%Y-%m-%d").month
    )

    return num_intervals


start_date = "2019-01-01"
num_intervals = calculate_num_intervals(start_date)


for m in key_measures:
    measures.define_measure(
        name=f"{m}_practice",
        numerator=measures_variables[m + "_binary_flag"],
        intervals=months(num_intervals).starting_on(start_date),
        group_by={
            "practice": registered_practice_id,
        },
    )

    measures.define_measure(
        name=f"{m}_code",
        numerator=measures_variables[m + "_binary_flag"],
        intervals=months(num_intervals).starting_on(start_date),
        group_by={m + "_code": measures_variables[m + "_code"]},
    )
