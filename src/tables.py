from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

import pandas as pd
from pandas.io.formats.style import Styler

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


def _style_table(
    df: pd.DataFrame,
    settings: Mapping[str, Any],
    caption: str,
    numeric_columns: Sequence[str] = (),
) -> Styler:
    styles = {
        "": [("border-collapse", "collapse")],
        "caption, th, td": [
            ("background-color", settings["background_color"]),
            ("color", settings["text_color"]),
            ("font-family", f"{settings['font_family']}, sans-serif"),
            ("font-size", f"{settings['font_size']}pt"),
        ],
        "caption": [
            ("text-align", "left"),
            ("font-size", f"{settings['title_size']}pt"),
            ("font-weight", "bold"),
            ("padding", "0 0 0.5em"),
        ],
        "th, td": [
            ("padding", "0.4em 0.8em"),
            ("border-bottom", f"1px solid {settings['grid_color']}"),
        ],
        "th": [
            ("text-align", "left"),
            ("color", settings["main_color"]),
        ],
    }

    styler = (
        df.copy().style
        .hide(axis="index")
        .format(escape="html", na_rep=MISSING)
        .format_index(escape="html", axis="columns")
        .set_caption(caption)
        .set_table_styles([
            {"selector": selector, "props": props}
            for selector, props in styles.items()
        ])
        .set_properties(subset=None, **{"text-align": "left"})
    )

    if numeric_columns:
        styler.set_properties(
            subset=list(numeric_columns),
            **{"text-align": "right"},
        )

    return styler


def summary_table(
    summary: Mapping[str, Any],
    settings: Mapping[str, Any],
) -> Styler:
    df = pd.DataFrame([
        ("Totala intäkter", format_amount(summary["total_revenue"])),
        ("Sålda enheter", format_count(summary["total_units"])),
        ("Unika order", format_count(summary["order_count"])),
        ("Genomsnittligt ordervärde", format_amount(summary["aov"])),
    ], columns=["Antal", "Värde"])

    return _style_table(df, settings, "Nyckeltal", numeric_columns=["Värde"])
