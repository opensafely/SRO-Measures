from cohortextractor import (
    codelist,
    codelist_from_csv,
)


asthma_codelist = codelist_from_csv("codelists/user-richard-croker-asthma-annual-review-qof.csv",
                                 system="snomed",
                                 column="code",)

copd_codelist = codelist_from_csv("codelists/user-richard-croker-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
                                 system="snomed",
                                 column="code",)

qrisk_codelist = codelist_from_csv("codelists/user-richard-croker-cvd-risk-assessment-score-qof.csv",
                                 system="snomed",
                                 column="code",)

tsh_codelist = codelist_from_csv("codelists/user-richard-croker-thyroid-stimulating-hormone-tsh-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

alt_codelist = codelist_from_csv("codelists/user-richard-croker-alanine-aminotransferase-alt-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

cholesterol_codelist = codelist_from_csv("codelists/user-richard-croker-cholesterol-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

hba1c_codelist = codelist_from_csv("codelists/user-richard-croker-glycated-haemoglobin-hba1c-tests.csv",
                                 system="snomed",
                                 column="code",)

rbc_codelist = codelist_from_csv("codelists/user-richard-croker-red-blood-cell-rbc-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

sodium_codelist = codelist_from_csv("codelists/user-richard-croker-sodium-tests-numerical-value.csv",
                                 system="snomed",
                                 column="code",)

systolic_bp_codelist = codelist_from_csv("codelists/user-richard-croker-systolic-blood-pressure-qof.csv",
                                 system="snomed",
                                 column="code",)

ethnicity_codes = codelist_from_csv(
        "codelists/opensafely-ethnicity.csv",
        system="ctv3",
        column="Code",
        category_column="Grouping_6",
    )