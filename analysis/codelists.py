from cohortextractor import (
    codelist,
    codelist_from_csv,
)


crd_codelist = codelist_from_csv("codelists/opensafely-chronic-respiratory-disease.csv",
                                 system="ctv3",
                                 column="CTV3ID",)
