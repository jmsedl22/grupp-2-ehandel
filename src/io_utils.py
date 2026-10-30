from pathlib import Path
import pandas as pd

REQUIRED = [
    "order_id", "date", "city", "category",
    "price", "units", "revenue"
]

def load_data(path: str) -> pd.DataFrame:
    """
    Loads CSV
    """

    # Reads the CSV file and reports common errors.
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Data file not found: {path}"
        ) from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            f"Data file is empty: {path}"
        ) from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Malformed CSV file: {path}"
        ) from exc

    # Checks that all required columns exist before processing the data.
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(
            f"Invalid CSV file '{path}'. Missing columns: {missing}"
        )

    # Converts the date column and raises ValueError for invalid dates.
    try:
        df["date"] = pd.to_datetime(df["date"], errors="raise")
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(
            f"Invalid date values in '{path}': {exc}"
        ) from exc

    # Converts the price, units, and revenue columns to numerical values.
    df = coerce_numeric(df)

    return df


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Convert each required numeric column, raising an error if conversion fails.
    for c in ["price", "units", "revenue"]:
        try:
            out[c] = pd.to_numeric(out[c], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid numeric values in column '{c}'"
            ) from exc

    return out
