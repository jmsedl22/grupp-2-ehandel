import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from .metrics import revenue_by_month

# Create charts showing total revenue per category and city

# Function for creating bar charts showing total revenue by product category and city
def plot_revenue_category_city(result_1, result_2):

    # Create figure and axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    # Set the data for x- and y-axis
    x1 = result_1["revenue"]
    y1 = result_1["category"]

    x2 = result_2["revenue"]
    y2 = result_2["city"]

    # Create bar charts
    ax1.barh(y1, x1 ,color="turquoise")
    ax2.barh(y2, x2, color="lightgreen")

    # Format x-axis
    ax2.xaxis.set_major_formatter(ticker.EngFormatter(unit=""))

    # Add titles and axis labels and format them
    ax1.set_title("Intäkt per kategori", fontsize=16, fontweight= "bold", pad=20)
    ax2.set_title("Intäkt per stad", fontsize=16, fontweight= "bold", pad=20)
    ax2.set_xlabel("Intäkt [SEK]", fontsize=14, labelpad=20)
    ax1.set_ylabel("Kategori", fontsize=14)
    ax2.set_ylabel("Stad", fontsize=14)

    # Add vertical gridlines
    ax1.grid(True, axis="x", linewidth=0.3)
    ax2.grid(True, axis="x", linewidth=0.3)
    
    # Invert the order of y-axis values
    ax1.invert_yaxis()
    ax2.invert_yaxis()

    # Set gridlines behind the bars
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # Improve layout
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)

    # Show the graph
    plt.show()


# Create a chart showing monthly revenue by category

# Function for creating a multi-line chart showing monthly revenue by category
def plot_monthly_revenue(df: pd.DataFrame) -> None:

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    # Create a separate line for each category
    for category in df["category"].unique():

        # Filter data for the selected category
        category_data = df[df["category"] == category]

        # Calculate monthly revenue
        monthly_data = revenue_by_month(category_data)

        # Create a multi-line chart
        ax.plot(
            monthly_data["date"],
            monthly_data["revenue"],
            marker="o",
            linewidth=2,
            markersize=8,
            label=category
        )

    # Format y-axis
    ax.yaxis.set_major_formatter(ticker.EngFormatter(unit=""))

    # Add a title and axis labels and format them
    ax.set_title("Intäkt per månad och kategori", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Månad", fontsize=14, labelpad=20)
    ax.set_ylabel("Intäkt [SEK]", fontsize=14, labelpad=20)

    # Add legend
    ax.legend(title="Kategori")

    # Add horizontal gridlines
    ax.grid(True, axis="y", linewidth=0.3)

    # Show the graph
    plt.show()


# Create a chart showing order value distribution
from .metrics import calculate_order_ranges

# Function for creating a bar chart for order value distribution
def plot_order_value_distribution(df: pd.DataFrame) -> None:

    # Select data for the chart
    number_of_orders = df["number of orders"].to_list()
    percentages = df["percentages"].to_list()
    labels = df.index.to_list()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    # Create a bar chart
    bars = ax.bar(labels, number_of_orders, color="darkorange")

    # Add percentages above each bar
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

    # Add a title and axis labels and format them
    ax.set_title("Fördelning av ordervärden", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Orderintäkt intervall [SEK]", fontsize=14, labelpad=20)
    ax.set_ylabel("Antal beställningar", fontsize=14, labelpad=20)

    # Format x- and y-axis
    ax.tick_params(axis="x", rotation=15)
    ax.set_ylim(0, max(number_of_orders) * 1.2)

    # Add horizontal gridlines
    ax.grid(True, axis="y", linewidth=0.3)

    # Set gridlines behind the bars
    ax.set_axisbelow(True)

    # Show the graph
    plt.show()
