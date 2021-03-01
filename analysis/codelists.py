from cohortextractor import (
    codelist,
    codelist_from_csv,
)


crd_codelist = codelist_from_csv("codelists/opensafely-chronic-respiratory-disease.csv",
                                 system="ctv3",
                                 column="CTV3ID",)

asthma_codelist = codelist_from_csv("codelists/user-richard-croker-asthma-annual-review-qof.csv",
                                 system="snomed",
                                 column="code",)

copd_codelist = codelist_from_csv("codelists/user-richard-croker-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
                                 system="snomed",
                                 column="code",)

qrisk_codelist = codelist_from_csv("codelists/user-richard-croker-cvd-risk-assessment-score-qof.csv",
                                 system="snomed",
                                 column="code",)