import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from . metrics import (revenue_by_month, calculate_order_ranges, calculate_aov, calculate_order_value_distribution, calculate_total_units, count_orders,)

def plot_revenue_category(category_revenue) -> None:
    """
    Creates a bar chart for total revenue by product category
    """
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    ax.barh(category_revenue["category"], category_revenue["revenue"] ,color="turquoise")
    ax.set_title("Intäkt per kategori", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax.xaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax.set_ylabel("Kategori", fontsize=14)
    ax.grid(True, axis="x", linewidth=0.3)
    ax.invert_yaxis()
    ax.set_axisbelow(True)

    plt.show()


def plot_revenue_city(city_revenue) -> None:
    """
    Creates a bar chart for total revenue by city
    """
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    ax.barh(city_revenue["city"], city_revenue["revenue"], color="lightgreen")
    ax.set_title("Intäkt per stad", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax.xaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax.set_ylabel("Stad", fontsize=14)
    ax.grid(True, axis="x", linewidth=0.3)
    ax.invert_yaxis()
    ax.set_axisbelow(True)

    plt.show()


def plot_monthly_revenue(df: pd.DataFrame) -> None:
    """
    Creates a multi-line chart for monthly revenue by category
    """
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    for category in df["category"].unique():
        category_data = df[df["category"] == category]
        monthly_data = revenue_by_month(category_data)

        ax.plot(
            monthly_data["date"],
            monthly_data["revenue"],
            marker="o",
            linewidth=2,
            markersize=8,
            label=category
        )

    ax.yaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax.set_title("Intäkt per månad och kategori", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Månad", fontsize=14, labelpad=20)
    ax.set_ylabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax.legend(title="Kategori", loc="upper right", ncol=3)
    ax.grid(True, axis="y", linewidth=0.3)

    plt.show()


def plot_order_value_distribution(df: pd.DataFrame) -> None:
    """
    Creates a bar chart for order value distribution
    """
    number_of_orders = df["number of orders"].to_list()
    percentages = df["percentages"].to_list()
    labels = df.index.to_list()

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
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
    ax.set_ylim(0, max(number_of_orders) * 1.2)
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

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    bp = ax.boxplot(revenue_by_city, tick_labels=cities, vert=False, patch_artist=True)
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
    """
    Creates a box plot for revenue distribution by category
    """
    revenue_groups = df.groupby("category")["revenue"]
    categories = revenue_groups.median().sort_values(ascending=True).index
    revenue_by_category = [
        revenue_groups.get_group(category)
        for category in categories
    ]

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    bp = ax.boxplot(revenue_by_category, tick_labels=categories, vert=False, patch_artist=True)
    colors = ["thistle", "plum", "mediumorchid", "blueviolet", "indigo"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    for cap in bp['caps']:
        cap.set(linewidth = 2)
    for median in bp['medians']:
        median.set(linewidth = 3)
    for flier in bp['fliers']:
        flier.set(alpha = 0.5)

    ax.set_title("Intäktsfördelning per kategori", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Orderintäkt [SEK]", fontsize=14, labelpad=20)
    ax.set_ylabel("Kategori", fontsize=14, labelpad=20)
    ax.grid(True, axis="x", linewidth=0.3)
    
    plt.show()


def plot_typical_order(df: pd.DataFrame, unit_counts: pd.DataFrame) -> None:
    """Visualize the value and size of a typical order."""

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Order value distribution
    counts, bins, patches = axes[0].hist(
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

    fig.suptitle(
        "HUR SER EN TYPISK ORDER UT?",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.show()

