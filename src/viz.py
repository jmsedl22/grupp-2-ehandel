from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from itertools import pairwise
from math import isfinite
from textwrap import fill
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure

MONTHS = (
    "januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti",
    "september", "oktober", "november", "december"
)


@contextmanager
def _chart(
    settings: Mapping[str, Any],
    **subplot_kwargs: Any,
) -> Generator[tuple[Figure, Any], None, None]:
    with (
        plt.rc_context(rc={
            "figure.figsize": settings["figure_size"],
            "figure.facecolor": settings["background_color"],
            "figure.constrained_layout.use": True,
            "axes.facecolor": settings["background_color"],
            "axes.edgecolor": settings["grid_color"],
            "axes.labelcolor": settings["text_color"],
            "axes.labelsize": settings["font_size"],
            "axes.titlesize": settings["title_size"],
            "axes.titleweight": "bold",
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": settings["font_family"],
            "font.size": settings["font_size"],
            "text.color": settings["text_color"],
            "xtick.color": settings["text_color"],
            "ytick.color": settings["text_color"],
            "xtick.labelsize": settings["font_size"],
            "ytick.labelsize": settings["font_size"],
            "legend.fontsize": settings["font_size"],
            "grid.color": settings["grid_color"],
            "grid.linewidth": 0.6,
        }),
        plt.ioff(),
    ):
        fig, axes = plt.subplots(**subplot_kwargs)
        try:
            yield fig, axes
        finally:
            plt.close(fig)


def _format_number(value: Any, decimals: int = 2) -> str:
    if pd.isna(value):
        return "—"

    if isinstance(value, str):
        value = pd.to_numeric(value, errors="raise")

    if not isfinite(value):
        return "—"

    return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")


def _format_date(value: Any) -> str:
    if pd.isna(value):
        return "—"

    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _format_month(value: Any) -> str:
    if pd.isna(value):
        return "—"

    date = pd.Timestamp(value)
    return f"{MONTHS[date.month - 1]} {date.year}"


def _format_percentage(value: Any) -> str:
    formatted = _format_number(value)
    return "—" if formatted == "—" else f"{formatted} %"


def _empty_chart(ax: Axes) -> None:
    ax.text(
        0.5, 0.5, "Inga data",
        transform=ax.transAxes,
        ha="center",
        va="center",
    )
    ax.set_axis_off()


def _revenue_labels(summary: pd.DataFrame, column: str) -> list[str]:
    return [
        fill("Ej angivet" if pd.isna(value) else str(value), width=24)
        for value in summary[column]
    ]


def _draw_revenue_bars(
    ax: Axes,
    summary: pd.DataFrame,
    column: str,
    settings: Mapping[str, Any],
    annotate: bool = False,
) -> None:
    if summary.empty:
        _empty_chart(ax)
        return

    positions = range(len(summary))
    bars = ax.barh(
        positions,
        summary["revenue"],
        color=settings["main_color"],
    )
    ax.set_yticks(positions, labels=_revenue_labels(summary, column))

    if annotate:
        annotations = [
            f"{_format_number(revenue)} SEK "
            f"({_format_percentage(share)})"
            for revenue, share in zip(
                summary["revenue"], summary["share_pct"], strict=True,
            )
        ]
        ax.bar_label(bars, labels=annotations, padding=5)
        ax.margins(x=0.4)

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda value, _position: _format_number(value)
        )
    )
    ax.grid(True, axis="x")
    ax.invert_yaxis()


def plot_revenue_category(
    category_revenue: pd.DataFrame,
    settings: Mapping[str, Any],
    date_min: Any,
    date_max: Any,
) -> Figure:
    """Plot prepared category revenue and shares for the dataset period."""
    labels = _revenue_labels(category_revenue, "category")
    width, height = settings["figure_size"]
    line_count = sum(label.count("\n") + 1 for label in labels)
    height = max(height, 1.8 + 0.4 * line_count)

    with _chart(settings, figsize=(width, height)) as (fig, ax):
        ax.set_title(
            "Intäkt per kategori\n"
            f"{_format_date(date_min)} – {_format_date(date_max)}"
        )
        ax.set_xlabel("Intäkt")
        ax.set_ylabel("Kategori")
        _draw_revenue_bars(
            ax, category_revenue, "category", settings, annotate=True,
        )
        return fig


def plot_revenue_city(
    city_revenue: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Create a revenue chart from the prepared city summary."""
    labels = _revenue_labels(city_revenue, "city")
    width, height = settings["figure_size"]
    line_count = sum(label.count("\n") + 1 for label in labels)
    height = max(height, 1.8 + 0.4 * line_count)

    with _chart(settings, figsize=(width, height)) as (fig, ax):
        ax.set_title("Intäkt per stad")
        ax.set_xlabel("Intäkt [SEK]")
        ax.set_ylabel("Stad")
        _draw_revenue_bars(ax, city_revenue, "city", settings)
        return fig


def plot_revenue_category_city(
    category_revenue: pd.DataFrame,
    city_revenue: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Draw prepared category and city revenues in a shared figure."""
    panels = [
        (category_revenue, "category", "Intäkt per kategori", "Kategori"),
        (city_revenue, "city", "Intäkt per stad", "Stad"),
    ]
    width, height = settings["figure_size"]
    heights = [
        max(
            height,
            1.8 + 0.4 * sum(
                label.count("\n") + 1
                for label in _revenue_labels(summary, column)
            ),
        )
        for summary, column, _, _ in panels
    ]

    with _chart(
        settings,
        nrows=2,
        figsize=(width, sum(heights)),
        height_ratios=heights,
        sharex=True,
    ) as (fig, axes):
        for ax, (summary, column, title, group_label) in zip(
            axes, panels, strict=True,
        ):
            ax.set_title(title)
            ax.set_xlabel("Intäkt [SEK]")
            ax.set_ylabel(group_label)
            _draw_revenue_bars(
                ax, summary, column, settings, annotate=(column == "category"),
            )
            ax.margins(x=0.4)
            ax.tick_params(axis="x", labelbottom=True)

        return fig


def plot_monthly_revenue(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Plot observed monthly revenue, preserving gaps in observations."""
    width, height = settings["figure_size"]
    width = max(width, 1.5 + 0.9 * len(summary))

    with _chart(settings, figsize=(width, height)) as (fig, ax):
        ax.set_title("Observerade intäkter per månad")
        ax.set_xlabel(
            "Månad\nLuckor i linjen: månader utan observationer."
        )
        ax.set_ylabel("Observerade intäkter [SEK]")

        if summary.empty:
            _empty_chart(ax)
            return fig

        months = summary["month"]
        ax.plot(
            months,
            summary["revenue"],
            color=settings["main_color"],
            marker="o",
            linewidth=2,
            markersize=6,
        )
        ax.set_xticks(
            months,
            labels=[
                _format_month(month).replace(" ", "\n")
                for month in months
            ],
        )
        ax.set_xlim(
            months.iloc[0] - pd.Timedelta(days=15),
            months.iloc[-1] + pd.Timedelta(days=15),
        )
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: _format_number(value)
            )
        )
        ax.grid(True, axis="y")

        return fig


def plot_revenue_by_weekday(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Plot total observed weekday revenue in the prepared order."""
    weekdays = {
        "Monday": "Måndag", "Tuesday": "Tisdag", "Wednesday": "Onsdag",
        "Thursday": "Torsdag", "Friday": "Fredag", "Saturday": "Lördag",
        "Sunday": "Söndag",
    }

    with _chart(settings) as (fig, ax):
        ax.set_title("Observerade intäkter per veckodag")
        ax.set_xlabel("Veckodag")
        ax.set_ylabel("Intäkt [SEK]")

        if summary.empty:
            _empty_chart(ax)
            return fig

        positions = range(len(summary))
        ax.bar(positions, summary["revenue"], color=settings["main_color"])
        ax.set_xticks(
            positions,
            labels=[weekdays[day] for day in summary["weekday"]],
        )
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: _format_number(value)
            )
        )
        ax.grid(True, axis="y")

        return fig


def _draw_order_histogram(
    ax: Axes,
    histogram: Mapping[str, list[float] | list[int]],
    summary: Mapping[str, float],
    settings: Mapping[str, Any],
) -> None:
    ax.set_title("Fördelning av ordervärden")
    ax.set_xlabel("Ordervärde [SEK]")
    ax.set_ylabel("Antal order")

    counts = histogram["counts"]
    if not counts:
        _empty_chart(ax)
        return

    edges = histogram["bin_edges"]
    widths = [
        right - left
        for left, right in pairwise(edges)
    ]
    ax.bar(
        edges[:-1],
        counts,
        width=widths,
        align="edge",
        color=settings["histogram_color"],
        edgecolor=settings["background_color"],
    )

    aov = summary["aov"]
    median = summary["median_revenue"]
    ax.axvline(
        aov,
        color=settings["aov_color"],
        linestyle="--",
        linewidth=2,
        zorder=4,
        label=f"AOV: {_format_number(aov)} SEK",
    )
    ax.axvline(
        median,
        color=settings["median_color"],
        linestyle="-",
        linewidth=2,
        zorder=3,
        label=f"Median: {_format_number(median)} SEK",
    )

    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda value, _position: _format_number(value)
        )
    )
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda value, _position: _format_number(value, 0)
        )
    )
    ax.set_ylim(0, max(1.0, max(counts) * 1.2))
    ax.grid(True, axis="y")
    ax.legend()


def plot_order_value_distribution(
    histogram: Mapping[str, list[float] | list[int]],
    summary: Mapping[str, float],
    settings: Mapping[str, Any],
) -> Figure:
    """
    Creates a bar chart for order value distribution.
    """
    with _chart(settings) as (fig, ax):
        _draw_order_histogram(ax, histogram, summary, settings)
        return fig


def _revenue_boxplot(
    summary: Sequence[Mapping[str, Any]],
    settings: Mapping[str, Any],
    title: str,
    group_label: str,
) -> Figure:
    """Render revenue boxplots."""
    stats = [
        {
            **item,
            "label": fill(
                "Ej angivet" if pd.isna(item["label"]) else str(item["label"]),
                width=24,
            ),
        }
        for item in summary
    ]

    width, height = settings["figure_size"]
    line_count = sum(item["label"].count("\n") + 1 for item in stats)
    height = max(height, 1.8 + 0.4 * line_count)

    with _chart(settings, figsize=(width, height)) as (fig, ax):
        ax.set_title(title)
        ax.set_xlabel("Radintäkt [SEK]")
        ax.set_ylabel(group_label)

        if not stats:
            _empty_chart(ax)
            return fig

        bp = ax.bxp(
            stats,
            orientation="horizontal",
            patch_artist=True,
        )
        for box in bp["boxes"]:
            box.set_facecolor(settings["main_color"])
        for cap in bp["caps"]:
            cap.set(linewidth=2)
        for median in bp["medians"]:
            median.set(color=settings["median_color"], linewidth=3)
        for flier in bp["fliers"]:
            flier.set(alpha=0.5)

        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: _format_number(value)
            )
        )
        ax.grid(True, axis="x")

        return fig


def plot_revenue_distribution_city(
    summary: Sequence[Mapping[str, Any]],
    settings: Mapping[str, Any],
) -> Figure:
    """Render prepared city row-revenue distributions."""
    return _revenue_boxplot(
        summary, settings, "Intäktsfördelning per stad", "Stad",
    )


def plot_revenue_distribution_category(
    summary: Sequence[Mapping[str, Any]],
    settings: Mapping[str, Any],
) -> Figure:
    """Render prepared category row-revenue distributions."""
    return _revenue_boxplot(
        summary, settings, "Intäktsfördelning per kategori", "Kategori",
    )


def plot_typical_order(
    df: pd.DataFrame,
    unit_counts: pd.DataFrame,
    histogram: Mapping[str, list[float] | list[int]],
    settings: Mapping[str, Any],
) -> Figure:
    """Visualize prepared order values and units per order."""
    width, height = settings["figure_size"]

    with _chart(
        settings, ncols=2, figsize=(2 * width, height),
    ) as (fig, axes):
        fig.suptitle(
            "HUR SER EN TYPISK ORDER UT?",
            fontsize=settings["title_size"],
            fontweight="bold",
        )

        if df.empty:
            for ax in axes:
                _empty_chart(ax)
            return fig

        summary = {
            "aov": float(df["average_revenue"].iloc[0]),
            "median_revenue": float(df["median_revenue"].iloc[0]),
        }
        _draw_order_histogram(axes[0], histogram, summary, settings)
        axes[0].set_title("FÖRDELNING AV ORDERVÄRDE")

        ax = axes[1]
        ax.set_title("ANTAL PRODUKTER PER ORDER")
        ax.set_xlabel("Antal produkter")
        ax.set_ylabel("Antal order")

        if unit_counts.empty:
            _empty_chart(ax)
            return fig

        ax.bar(
            unit_counts["order_units"],
            unit_counts["order_count"],
            color=settings["main_color"],
            edgecolor=settings["background_color"],
        )

        median = df["median_units"].iloc[0]
        average = df["average_units"].iloc[0]
        ax.axvline(
            median,
            color=settings["median_color"],
            linestyle="-",
            linewidth=2,
            zorder=3,
            label=f"Median: {_format_number(median)}",
        )
        ax.axvline(
            average,
            color=settings["aov_color"],
            linestyle="--",
            linewidth=2,
            zorder=4,
            label=f"Medelvärde: {_format_number(average)}",
        )

        ax.set_xticks(unit_counts["order_units"])
        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: _format_number(value, 0)
            )
        )
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: _format_number(value, 0)
            )
        )
        ax.set_ylim(0, max(1.0, unit_counts["order_count"].max() * 1.2))
        ax.grid(True, axis="y")
        ax.legend()

        return fig
