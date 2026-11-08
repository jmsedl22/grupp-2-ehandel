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
COLUMN_LABELS = {
    "category": "Kategori",
    "city": "Stad",
    "revenue": "Intäkter",
    "share_pct": "Andel av totala intäkter",
}


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
    """Helper function that keeps a consistent style to all tables."""
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
    ], columns=["Mätning", "Värde"])

    return _style_table(df, settings, "Nyckeltal", numeric_columns=["Värde"])


def _revenue_table(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
    group_column: str,
    caption: str,
) -> Styler:
    group_heading = COLUMN_LABELS[group_column]
    numerics = {
        COLUMN_LABELS["revenue"]: format_amount,
        COLUMN_LABELS["share_pct"]: format_percentage,
    }

    df = summary[[group_column, "revenue", "share_pct"]].rename(
        columns=COLUMN_LABELS
    )

    return _style_table(
        df,
        settings,
        caption,
        numeric_columns=list(numerics)
    ).format({
        group_heading: format_label,
        **numerics
    }, escape="html")


def category_table(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Styler:
    return _revenue_table(
        summary, settings,
        "category", "Intäkter per kategori",
    )


def city_table(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Styler:
    return _revenue_table(
        summary, settings,
        "city", "Intäkter per stad",
    )


def top_categories_table(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Styler:
    return _revenue_table(
        summary, settings,
        "category", "Topp 3 kategorier",
    )


def data_overview_table(
    overview: Mapping[str, Any],
    settings: Mapping[str, Any],
) -> Styler:
    count_labels = {
        "row_count": "Antal rader",
        "order_count": "Unika order",
        "missing_values_total": "Saknade värden totalt",
        "duplicate_row_count": "Exakta dubblettrader",
        "negative_numeric_row_count": "Rader med negativa numeriska värden",
        "price_units_discrepancy_count": (
            "Avvikelser mellan pris × antal och intäkt"
        ),
    }

    rows = [
        ("Första datum", format_date(overview["date_min"])),
        ("Sista datum", format_date(overview["date_max"])),
    ]

    rows.extend(
        (label, format_count(overview[key]))
        for key, label in count_labels.items()
    )

    rows.extend(
        (f"Saknade värden: {column}", format_count(count))
        for column, count in overview["missing_values_by_column"].items()
    )

    missing_dates = ", ".join(
        format_date(date)
        for date in overview["dates_without_observations"]
    )
    rows.append(("Datum utan observationer", missing_dates or "Inga"))

    df = pd.DataFrame(rows, columns=["Mätning", "Värde"])

    return _style_table(
        df,
        settings,
        "Dataöversikt",
        numeric_columns=["Värde"],
    )


def order_summary_table(
    summary: Mapping[str, Any],
    settings: Mapping[str, Any],
) -> Styler:
    labels = {
        "aov": "Genomsnittligt ordervärde",
        "median_revenue": "Median",
        "min_revenue": "Minimum",
        "max_revenue": "Maximum",
        "q1": "Första kvartilen (Q1)",
        "q3": "Tredje kvartilen (Q3)",
        "iqr": "Kvartilavstånd (IQR)",
    }

    rows = [
        (label, format_amount(summary[key]))
        for key, label in labels.items()
    ]
    df = pd.DataFrame(rows, columns=["Mätning", "Värde"])

    return _style_table(
        df,
        settings,
        "Orderstatistik",
        numeric_columns=["Värde"],
    )


def anomaly_summary_table(
    summary: Mapping[str, Any],
    settings: Mapping[str, Any],
) -> Styler:
    rows = [
        ("Övre IQR-gräns", format_amount(summary["threshold"])),
        ("Antal stora order", format_count(summary["order_count"])),
        (
            "Andel av alla order",
            format_percentage(summary["order_share_pct"]),
        ),
        ("Intäkter från stora order", format_amount(summary["revenue"])),
        (
            "Andel av totala intäkter",
            format_percentage(summary["revenue_share_pct"]),
        ),
    ]
    df = pd.DataFrame(rows, columns=["Mätning", "Värde"])

    return _style_table(
        df,
        settings,
        "Stora order över övre IQR-gränsen (Q3 + 1,5 × IQR)",
        numeric_columns=["Värde"],
    )
