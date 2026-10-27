



from pathlib import Path

import pandas as pd


def load_data(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file from a string path or pathlib.Path object."""
    df = pd.read_csv(file_path, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"])
    return df