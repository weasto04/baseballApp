import sqlite3
from pathlib import Path

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "baseball.db"

CSV_FILES = {
    "people": BASE_DIR / "people.csv",
    "teams": BASE_DIR / "teams.csv",
    "batting": BASE_DIR / "Batting.csv",
}


def quote_ident(identifier: str) -> str:
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


def sqlite_type_for_series(series: pd.Series) -> str:
    dtype = series.dtype

    if is_integer_dtype(dtype) or is_bool_dtype(dtype):
        return "INTEGER"
    if is_float_dtype(dtype):
        return "REAL"
    if is_datetime64_any_dtype(dtype):
        return "TEXT"
    if is_string_dtype(dtype):
        return "TEXT"

    # Fallback for mixed/object columns.
    return "TEXT"


def build_create_table_sql(table_name: str, df: pd.DataFrame) -> str:
    col_defs = [f"{quote_ident(col)} {sqlite_type_for_series(df[col])}" for col in df.columns]

    if table_name == "people":
        constraints = ["PRIMARY KEY (\"playerID\")"]
    elif table_name == "teams":
        constraints = ["PRIMARY KEY (\"teamID\", \"yearID\")"]
    elif table_name == "batting":
        constraints = [
            "PRIMARY KEY (\"playerID\", \"yearID\", \"stint\")",
            "FOREIGN KEY (\"playerID\") REFERENCES \"people\"(\"playerID\")",
            "FOREIGN KEY (\"teamID\", \"yearID\") REFERENCES \"teams\"(\"teamID\", \"yearID\")",
        ]
    else:
        constraints = []

    all_defs = col_defs + constraints
    return f"CREATE TABLE {quote_ident(table_name)} (\n  " + ",\n  ".join(all_defs) + "\n);"


def normalize_dataframe(path: Path) -> pd.DataFrame:
    # convert_dtypes keeps nullable integers as Int64 instead of upcasting to float.
    return pd.read_csv(path, low_memory=False).convert_dtypes()


def main() -> None:
    dataframes = {name: normalize_dataframe(path) for name, path in CSV_FILES.items()}

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")

        # Build schema first so PK/FK constraints are guaranteed.
        for table_name in ["people", "teams", "batting"]:
            create_sql = build_create_table_sql(table_name, dataframes[table_name])
            conn.execute(create_sql)

        # Insert parent tables before child table.
        for table_name in ["people", "teams", "batting"]:
            df = dataframes[table_name]
            # Convert pandas extension dtypes/NA to plain Python values for sqlite3.
            df = df.astype(object).where(pd.notna(df), None)
            placeholders = ", ".join(["?"] * len(df.columns))
            column_list = ", ".join(quote_ident(c) for c in df.columns)
            insert_sql = (
                f"INSERT INTO {quote_ident(table_name)} ({column_list}) VALUES ({placeholders})"
            )
            conn.executemany(insert_sql, df.itertuples(index=False, name=None))

        conn.commit()

        fk_issues = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_issues:
            raise RuntimeError(f"Foreign key validation failed: {fk_issues[:5]}")
    finally:
        conn.close()

    print(f"Created database: {DB_PATH}")


if __name__ == "__main__":
    main()
