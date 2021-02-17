from cohortextractor import (
    codelist,
    codelist_from_csv,
)


holder_codelist = codelist_from_csv("codelists/opensafely-structured-medication-review-nhs-england.csv",
                  system="snomed",
                  column="code",)

crd_codelist = codelist_from_csv("codelists/opensafely-chronic-respiratory-disease.csv",
                                 system="ctv3",
                                 column="CTV3ID",)
