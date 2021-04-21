import re
from pathlib import Path

import pandas

INPUT_FILE_REGEX = re.compile(r"input_(?P<date>\d{4}-\d{2}-\d{2})\.csv")
DATE_FORMAT = "%Y-%m-%d"
OUTPUT_DIR = Path("output")

MEASURE_COL = "hba1c"
MEASURE_EVENT_CODE_COL = "hba1c_event_code"
VALUE_COLS = [MEASURE_COL, MEASURE_EVENT_CODE_COL]
INDEX_COLS = ["patient_id", "date"]


def read_file(f_path):
    date_str = re.match(INPUT_FILE_REGEX, f_path.name).group("date")
    date_timestamp = pandas.to_datetime(date_str, format=DATE_FORMAT)
    return pandas.read_csv(f_path).assign(date=date_timestamp)


def get_records():
    return (
        pandas.concat(
            (
                read_file(x)
                for x in OUTPUT_DIR.iterdir()
                if re.match(INPUT_FILE_REGEX, x.name) is not None
            ),
            ignore_index=True,
        )
        .set_index(INDEX_COLS)
        .loc[:, VALUE_COLS]
    )


def get_counts(records):
    return records.loc[:, MEASURE_COL].groupby(INDEX_COLS).count()


def write_summary(counts):
    counts.describe().to_csv(OUTPUT_DIR / f"{MEASURE_COL}_event_summary.csv")


if __name__ == "__main__":
    records = get_records()
    counts = get_counts(records)
    write_summary(counts)
