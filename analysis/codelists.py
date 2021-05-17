from cohortextractor import (
    codelist,
    codelist_from_csv,
    combine_codelists
)


asthma_codelist = codelist_from_csv("codelists/opensafely-asthma-annual-review-qof.csv",
                                 system="snomed",
                                 column="code",)

copd_codelist = codelist_from_csv("codelists/opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
                                 system="snomed",
                                 column="code",)

qrisk_codelist = codelist_from_csv("codelists/opensafely-cvd-risk-assessment-score-qof.csv",
                                 system="snomed",
                                 column="code",)

tsh_codelist = codelist_from_csv("codelists/opensafely-thyroid-stimulating-hormone-tsh-testing.csv",
                                 system="snomed",
                                 column="code",)

alt_codelist = codelist_from_csv("codelists/opensafely-alanine-aminotransferase-alt-tests.csv",
                                 system="snomed",
                                 column="code",)

cholesterol_codelist = codelist_from_csv("codelists/opensafely-cholesterol-tests.csv",
                                 system="snomed",
                                 column="code",)

hba1c_codelist = codelist_from_csv("codelists/opensafely-glycated-haemoglobin-hba1c-tests.csv",
                                 system="snomed",
                                 column="code",)

rbc_codelist = codelist_from_csv("codelists/opensafely-red-blood-cell-rbc-tests.csv",
                                 system="snomed",
                                 column="code",)

sodium_codelist = codelist_from_csv("codelists/opensafely-sodium-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

systolic_bp_codelist = codelist_from_csv("codelists/opensafely-systolic-blood-pressure-qof.csv",
                                 system="snomed",
                                 column="code",)

medication_review_1 = codelist_from_csv("codelists/opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
    system="snomed",
    column="code",)

medication_review_2 = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-medrvw_cod.csv",
    system="snomed",
    column="code",)

medication_review_codelist = combine_codelists(
    medication_review_1, 
    medication_review_2
)