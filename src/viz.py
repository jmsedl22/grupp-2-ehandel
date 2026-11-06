import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from .metrics import revenue_by_month

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
