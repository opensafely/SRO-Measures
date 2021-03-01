from cohortextractor import (
    codelist,
    codelist_from_csv,
)




asthma_codelist = codelist_from_csv("codelists/user-richard-croker-asthma-annual-review-qof.csv",
                                 system="snomed",
                                 column="code",)

cpod_codelist = codelist_from_csv("codelists/user-richard-croker-chronic-obstructive-pulmonary-disease-qof.csv",
                                 system="snomed",
                                 column="code",)

qrisk_codelist = codelist_from_csv("codelists/user-richard-croker-cvd-risk-assessment-score-qof.csv",
                                 system="snomed",
                                 column="code",)