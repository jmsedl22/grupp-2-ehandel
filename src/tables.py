from math import isfinite
from typing import Any

import pandas as pd

MISSING = "—"
MONTHS = (
    "januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti",
    "september", "oktober", "november", "december"
)


def _format_number(value: Any, decimals: int) -> str:
    if pd.isna(value) or not isfinite(value):
        return MISSING

    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def format_count(value: Any) -> str:
    return _format_number(value, 0)


def format_amount(value: Any) -> str:
    return _format_number(value, 2)


def format_percentage(value: Any) -> str:
    formatted = format_amount(value)
    return MISSING if formatted == MISSING else f"{formatted} %"


def format_date(value: Any) -> str:
    if pd.isna(value):
        return MISSING

    return pd.Timestamp(value).strftime("%Y-%m-%d")


def format_month(value: Any) -> str:
    if pd.isna(value):
        return MISSING

    date = pd.Timestamp(value)
    return f"{MONTHS[date.month - 1]} {date.year}"


def format_label(value: Any) -> str:
    return "Ej angivet" if pd.isna(value) else str(value)
