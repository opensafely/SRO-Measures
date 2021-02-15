from cohortextractor import (
    codelist,
    codelist_from_csv,
)


holder_codelist = codelist_from_csv("codelists/opensafely-structured-medication-review-nhs-england.csv",
                  system="snomed",
                  column="code",)
