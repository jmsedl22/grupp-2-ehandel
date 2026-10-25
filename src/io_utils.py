import pandas as pd

def load_data(file_path):
    df = pd.read_csv(file_path, encoding="utf-8")

    df["date"] = pd.to_datetime(df["date"])

    return df