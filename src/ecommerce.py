from pathlib import Path
from typing import TypedDict

from pandas import DataFrame

from . import io_utils, metrics, viz


# Return type of the Summary() function as a typed dictionary
class SummaryData(TypedDict):
    total_revenue: float
    total_units: int
    order_count: int
    aov: float


# Return type of the order_value_distribution() function as a typed dictionary.
class OrderValueDistributionData(TypedDict):
    min_revenue: float
    median_revenue: float
    max_revenue: float


# Class CommerceAnalyzer
# Functions as an interface between the notebook and util functions
class CommerceAnalyzer:
    file_path: str | Path
    dataframe: DataFrame

    def __init__(
        self,
        file_path: str | Path | None = None
    ) -> None:
        if file_path is None:
            file_path = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "ecommerce_sales.csv"
            )

        self.file_path = file_path
        self.dataframe = io_utils.load_data(self.file_path)

        self.settings = {
            "background_color": "#FFFFFF",
            "text_color": "#243239",
            "grid_color": "#D9E2E3",
            "main_color": "#246B75",
            "histogram_color": "#72A9AB",
            "aov_color": "#B85B31",
            "median_color": "#20434B",
            "font_family": "DejaVu Sans",
            "font_size": 10,
            "title_size": 14,
            "figure_size": (9.0, 4.3),
        }

    def summary(self) -> SummaryData:
        return {
            "total_revenue": metrics.calculate_total_revenue(self.dataframe),
            "total_units": metrics.calculate_total_units(self.dataframe),
            "order_count": metrics.count_orders(self.dataframe),
            "aov": metrics.calculate_aov(self.dataframe),
        }

    def revenue_by_category(self) -> DataFrame:
        return metrics.revenue_by_category(self.dataframe)

    def revenue_by_month(self) -> DataFrame:
        return metrics.revenue_by_month(self.dataframe)

    def revenue_top_3_categories(self) -> DataFrame:
        return metrics.revenue_top_3_categories(self.dataframe)

    def order_value_distribution(self) -> OrderValueDistributionData:
        result = metrics.calculate_order_value_distribution(self.dataframe)
        return {
            "min_revenue": result["min_revenue"],
            "median_revenue": result["median_revenue"],
            "max_revenue": result["max_revenue"]
        }

    def order_ranges(self) -> DataFrame:
        return metrics.calculate_order_ranges(self.dataframe)

    def revenue_by_city(self) -> DataFrame:
        return metrics.revenue_by_city(self.dataframe)

    def plot_revenue_category(self) -> None:
        category_revenue = self.revenue_by_category()
        viz.plot_revenue_category(category_revenue)

    def plot_revenue_city(self) -> None:
        city_revenue = self.revenue_by_city()
        viz.plot_revenue_city(city_revenue)

    def plot_monthly_revenue(self) -> None:
        viz.plot_monthly_revenue(self.dataframe)

    def plot_order_value_distribution(self) -> None:
        order_ranges_df = self.order_ranges()
        viz.plot_order_value_distribution(order_ranges_df)

    def plot_revenue_distribution_city(self) -> None:
        viz.plot_revenue_distribution_city(self.dataframe)

    def plot_revenue_distribution_category(self) -> None:
        viz.plot_revenue_distribution_category(self.dataframe)
