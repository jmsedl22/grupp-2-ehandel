import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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


# Create a chart showing monthly revenue

# Function for creating a line chart showing monthly revenue
def plot_monthly_revenue(result):

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    # Set the data for x- and y-axis
    x = result["date"]
    y = result["revenue"]

    # Create a line chart
    ax.plot(x, y, marker="o", color="seagreen", linewidth=2, markeredgecolor="white", markersize=8)

    # Format y-axis
    ax.yaxis.set_major_formatter(ticker.EngFormatter(unit=""))
    ax.set_ylim(450_000, 700_000)
    ax.get_yticklabels()[0].set_visible(False)

    # Add a title and axis labels and format them
    ax.set_title("Intäkt per månad", fontsize=16, fontweight= "bold", pad=20)
    ax.set_xlabel("Månad", fontsize=14, labelpad=20)
    ax.set_ylabel("Intäkt [SEK]", fontsize=14, labelpad=20)

    # Add horizontal gridlines
    ax.grid(True, axis="y", linewidth=0.3)

    # Show the graph
    plt.show()


# Create a chart showing order value distribution

# Function for creating a bar chart for order value distribution
def plot_order_value_distribution(result):

    # Select data for the chart
    number_of_orders = result["number of orders"].to_list()
    percentages = result["percentages"].to_list()
    labels = result.index.to_list()

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
