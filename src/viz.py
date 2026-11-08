from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from math import isfinite
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure


@contextmanager
def _chart(
    settings: Mapping[str, Any],
    **subplot_kwargs: Any,
) -> Iterator[tuple[Figure, Any]]:
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


def _empty_chart(ax: Axes) -> None:
    ax.text(
        0.5, 0.5, "Inga data",
        transform=ax.transAxes,
        ha="center",
        va="center",
    )
    ax.set_axis_off()


def plot_revenue_category(category_revenue) -> None:
    """
    Creates a bar chart for total revenue by product category
    """
    _fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    ax.barh(category_revenue["category"], category_revenue["revenue"] ,color="turquoise")
    ax.set_title("Intäkt per kategori", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax.xaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax.set_ylabel("Kategori", fontsize=14)
    ax.grid(True, axis="x", linewidth=0.3)
    ax.invert_yaxis()
    ax.set_axisbelow(True)

    plt.show()


def plot_revenue_city(
    city_revenue: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Create a revenue chart from the prepared city summary."""
    with _chart(settings) as (fig, ax):
        ax.set_title("Intäkt per stad")
        ax.set_xlabel("Intäkt [SEK]")
        ax.set_ylabel("Stad")

        if city_revenue.empty:
            _empty_chart(ax)
        else:
            positions = range(len(city_revenue))
            labels = [
                "Ej angivet" if pd.isna(city) else str(city)
                for city in city_revenue["city"]
            ]

            ax.barh(
                positions,
                city_revenue["revenue"],
                color=settings["main_color"],
            )
            ax.set_yticks(positions, labels=labels)
            ax.xaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda value, _position: _format_number(value)
                )
            )
            ax.grid(True, axis="x")
            ax.invert_yaxis()

        return fig


def plot_monthly_revenue(
    summary: pd.DataFrame,
    settings: Mapping[str, Any],
) -> Figure:
    """Plot prepared monthly category revenues, retaining observation gaps."""
    with _chart(settings) as (fig, ax):
        ax.set_title("Intäkt per månad och kategori")
        ax.set_xlabel("Månad")
        ax.set_ylabel("Intäkt [SEK]")

        if summary.empty:
            _empty_chart(ax)
        else:
            for category, group in summary.groupby(
                "category",
                dropna=False,
                observed=True,
                sort=False,
            ):
                ax.plot(
                    group["month"],
                    group["revenue"],
                    marker="o",
                    linewidth=2,
                    markersize=6,
                    label="Ej angivet" if pd.isna(category) else str(category),
                )

            locator = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(
                mdates.ConciseDateFormatter(locator)
            )
            ax.yaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda value, _position: _format_number(value)
                )
            )
            ax.legend(title="Kategori")
            ax.grid(True, axis="y")

        return fig


def plot_order_value_distribution(df: pd.DataFrame) -> None:
    """
    Creates a bar chart for order value distribution
    """
    _fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    if df.empty:
        _empty_chart(ax)
        plt.show()
        return

    number_of_orders = df["number of orders"].to_list()
    percentages = df["percentages"].to_list()
    labels = df.index.to_list()
    bars = ax.bar(labels, number_of_orders, color="darkorange")

    for bar, percentage in zip(bars, percentages):
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()

        ax.annotate(
            f"{percentage:.2f}%",
            xy=(x, y),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom"
        )

    ax.set_title("Fördelning av ordervärden", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Orderintäkt intervall [SEK]", fontsize=14, labelpad=20)
    ax.set_ylabel("Antal beställningar", fontsize=14, labelpad=20)
    ax.tick_params(axis="x", rotation=15)
    ax.set_ylim(0, max(1.0, max(number_of_orders) * 1.2))
    ax.grid(True, axis="y", linewidth=0.3)
    ax.set_axisbelow(True)

    plt.show()


def plot_revenue_distribution_city(df: pd.DataFrame) -> None:
    """
    Creates a box plot for revenue distribution by city
    """
    revenue_groups = df.groupby("city")["revenue"]
    cities = revenue_groups.median().sort_values(ascending=True).index
    revenue_by_city = [
        revenue_groups.get_group(city)
        for city in cities
    ]

    _fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    bp = ax.boxplot(
        revenue_by_city,
        tick_labels=[str(city) for city in cities],
        orientation="horizontal",
        patch_artist=True,
    )
    colors = ["lightcyan", "lightblue", "dodgerblue", "steelblue", "darkblue"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    for cap in bp['caps']:
        cap.set(linewidth=2)
    for median in bp['medians']:
        median.set(linewidth=3)
    for flier in bp['fliers']:
        flier.set(alpha=0.5)

    ax.set_title("Intäktsfördelning per stad", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Orderintäkt [SEK]", fontsize=14, labelpad=20)
    ax.set_ylabel("Stad", fontsize=14, labelpad=20)
    ax.grid(True, axis="x", linewidth=0.3)

    plt.show()


def plot_revenue_distribution_category(df: pd.DataFrame) -> None:
    """Creates a box plot for revenue distribution by category."""
    revenue_groups = df.groupby("category")["revenue"]
    categories = revenue_groups.median().sort_values(ascending=True).index
    revenue_by_category = [
        revenue_groups.get_group(category)
        for category in categories
    ]

    _fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    bp = ax.boxplot(
        revenue_by_category,
        tick_labels=[str(category) for category in categories],
        orientation="horizontal",
        patch_artist=True,
    )
    colors = ["thistle", "plum", "mediumorchid", "blueviolet", "indigo"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    for cap in bp['caps']:
        cap.set(linewidth = 2)
    for median in bp['medians']:
        median.set(linewidth = 3)
    for flier in bp['fliers']:
        flier.set(alpha = 0.5)

    ax.set_title(
        "Intäktsfördelning per kategori",
        fontsize=16,
        fontweight="bold",
        pad=20
    )
    ax.set_xlabel("Orderintäkt [SEK]", fontsize=14, labelpad=20)
    ax.set_ylabel("Kategori", fontsize=14, labelpad=20)
    ax.grid(True, axis="x", linewidth=0.3)

    plt.show()


def plot_typical_order(df: pd.DataFrame, unit_counts: pd.DataFrame) -> None:
    """Visualize the value and size of a typical order."""
    if df.empty:
        return

    _fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Order value distribution
    _counts, bins, _patches = axes[0].hist(
        df["order_revenue"],
        bins=25,
        color="skyblue",
        edgecolor="white"
    )

    axes[0].axvline(
        df["median_revenue"].iloc[0],
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Median: {df["median_revenue"].iloc[0]:.2f} SEK"
    )

    axes[0].axvline(
        df["average_revenue"].iloc[0],
        color="purple",
        linestyle="--",
        linewidth=2,
        label=f"Medelvärde: {df["average_revenue"].iloc[0]:.2f} SEK"
    )
    axes[0].set_title("FÖRDELNING AV ORDERVÄRDE")
    axes[0].set_xlabel("Ordervärde [SEK]")
    axes[0].set_ylabel("Antal order")
    axes[0].legend()
    axes[0].set_xticks(bins[::2])
    axes[0].tick_params(axis="x")

    # Chart 2: Number of products per order
    axes[1].bar(
        unit_counts["order_units"],
        unit_counts["order_count"],
        color="lightgreen",
        edgecolor="white",
    )

    axes[1].axvline(
        df["median_units"].iloc[0],
        color="green",
        linestyle="-.",
        linewidth=2,
        label=f"Median: {df["median_units"].iloc[0]:.2f}"
    )

    axes[1].axvline(
        df["average_units"].iloc[0],
        color="purple",
        linestyle="-",
        alpha=0.5,
        linewidth=2,
        label=f"Medelvärde: {df["average_units"].iloc[0]:.2f}"
    )

    axes[1].set_title("ANTAL PRODUKTER PER ORDER")
    axes[1].set_xlabel("Antal produkter")
    axes[1].set_ylabel("Antal order")
    axes[1].legend()
    axes[1].set_xticks(unit_counts["order_units"])

    # Formatting
    for ax in axes:
        ax.grid(True, axis="y", linewidth=0.3)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", labelsize=8)

    _fig.suptitle(
        "HUR SER EN TYPISK ORDER UT?",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.show()
