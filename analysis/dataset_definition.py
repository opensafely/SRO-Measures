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
        category_column="grouping_16_label",
    ),
    "medication_review_1": codelist_from_csv(
        "codelists/opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
        column="code",
    ),
    "medication_review_2": codelist_from_csv(
        "codelists/nhsd-primary-care-domain-refsets-medrvw_cod.csv", column="code"
    ),
}

start_date = "2019-01-01"
end_date = "2021-04-30"

dataset = Dataset()
age = patients.age_on(date=INTERVAL.start_date)
age_18_to_120 = (age >= 18) & (age < 120)
age_band = case(
    when((age >= 18) & (age < 20)).then("18-19"),
    when((age >= 20) & (age < 30)).then("20-29"),
    when((age >= 30) & (age < 40)).then("30-39"),
    when((age >= 40) & (age < 50)).then("40-49"),
    when((age >= 50) & (age < 60)).then("50-59"),
    when((age >= 60) & (age < 70)).then("60-69"),
    when((age >= 70) & (age < 80)).then("70-79"),
    when((age >= 80) & (age < 120)).then("80+"),
    default="missing",
)

registered_practice = practice_registrations.for_patient_on(INTERVAL.start_date)
registered_practice_id = registered_practice.practice_pseudo_id

registered_at_start_of_interval = registered_practice.exists_for_patient()

region = registered_practice.practice_nuts1_region_name

sex = patients.sex

date_of_death = patients.date_of_death
died_before_interval_start = date_of_death.is_before(INTERVAL.start_date)

imd = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
imd_quintile = case(
    when((imd >= 0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd < int(32844 * 2 / 5)).then("2"),
    when(imd < int(32844 * 3 / 5)).then("3"),
    when(imd < int(32844 * 4 / 5)).then("4"),
    when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
    default="unknown",
)

latest_ethnicity_start_of_period = (
    clinical_events.where(clinical_events.snomedct_code.is_in(codelists["eth2001"]))
    .where(clinical_events.date.is_on_or_before(INTERVAL.start_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)
latest_ethnicity_start_of_period_group = latest_ethnicity_start_of_period.to_category(
    codelists["eth2001"]
)

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


for m in key_measures:
    measures.define_measure(
        name=m,
        numerator=measures_variables[m + "_binary_flag"],
        denominator=denominator,
        intervals=months(42).starting_on("2019-01-01"),
        group_by={
            "practice": registered_practice_id,
        },
    )

demographics = {
    "age_band": age_band,
    "ethnicity": latest_ethnicity_start_of_period_group,
    "imd": imd_quintile,
    "region": region,
    "sex": sex,
}

for k, d in demographics.items():
    measures.define_measure(
        name=k,
        numerator=denominator,
        denominator=denominator,
        intervals=months(1).starting_on("2023-06-01"),
        group_by={
            k: d,
        },
    )
