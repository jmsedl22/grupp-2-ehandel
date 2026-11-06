import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from .metrics import revenue_by_month, calculate_order_ranges

def plot_revenue_category_city(result_1, result_2):
    """
    Creates bar charts for total revenue by product category and city
    """

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    x1 = result_1["revenue"]
    y1 = result_1["category"]

    x2 = result_2["revenue"]
    y2 = result_2["city"]

    ax1.barh(y1, x1 ,color="turquoise")
    ax1.set_title("Intäkt per kategori", fontsize=16, fontweight= "bold", pad=20)
    ax1.set_ylabel("Kategori", fontsize=14)
    ax1.grid(True, axis="x", linewidth=0.3)
    ax1.invert_yaxis()
    ax1.set_axisbelow(True)

    ax2.barh(y2, x2, color="lightgreen")
    ax2.set_title("Intäkt per stad", fontsize=16, fontweight= "bold", pad=20)
    ax2.set_xlabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax2.set_ylabel("Stad", fontsize=14)
    ax2.xaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax2.grid(True, axis="x", linewidth=0.3)
    ax2.invert_yaxis()
    ax2.set_axisbelow(True)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)

    plt.show()


def plot_monthly_revenue(df: pd.DataFrame) -> None:
    """
    Creates a multi-line chart for monthly revenue by category
    """

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

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
    ax.legend(title="Kategori")
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


