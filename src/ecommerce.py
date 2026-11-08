from pathlib import Path
from typing import TypedDict

from matplotlib.figure import Figure
from pandas import DataFrame
from pandas.io.formats.style import Styler

from . import io_utils, metrics, tables, viz


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

    def summary_table(self) -> Styler:
        return tables.summary_table(self.summary(), self.settings)

    def category_table(self) -> Styler:
        result = metrics.category_summary(self.dataframe)
        return tables.category_table(result, self.settings)

    def city_table(self) -> Styler:
        result = metrics.city_summary(self.dataframe)
        return tables.city_table(result, self.settings)

    def top_categories_table(self) -> Styler:
        result = metrics.top_categories_summary(self.dataframe, n=3)
        return tables.top_categories_table(result, self.settings)

    def data_overview_table(self) -> Styler:
        result = metrics.data_overview(self.dataframe)
        return tables.data_overview_table(result, self.settings)

    def order_summary_table(self) -> Styler:
        result = metrics.order_summary(self.dataframe)
        return tables.order_summary_table(result, self.settings)

    def anomaly_summary_table(self) -> Styler:
        result = metrics.large_order_summary(self.dataframe)
        return tables.anomaly_summary_table(result, self.settings)

    def monthly_table(self) -> Styler:
        result = metrics.monthly_summary(self.dataframe)
        return tables.monthly_table(result, self.settings)

    def largest_orders_table(self, limit: int = 5) -> Styler:
        if isinstance(limit, bool):
            raise TypeError("limit must be a positive integer")

        result = metrics.largest_orders(self.dataframe, n=limit)
        return tables.largest_orders_table(result["rows"], self.settings)

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

    def plot_revenue_by_category(self) -> Figure:
        category_revenue = metrics.category_summary(self.dataframe)
        overview = metrics.data_overview(self.dataframe)

        return viz.plot_revenue_category(
            category_revenue,
            self.settings,
            overview["date_min"],
            overview["date_max"],
        )

    def plot_revenue_category(self) -> Figure:
        return self.plot_revenue_by_category()

    def plot_revenue_city(self) -> Figure:
        city_revenue = metrics.city_summary(self.dataframe)
        return viz.plot_revenue_city(city_revenue, self.settings)

    def plot_revenue_category_city(self) -> Figure:
        category_revenue = metrics.category_summary(self.dataframe)
        city_revenue = metrics.city_summary(self.dataframe)
        return viz.plot_revenue_category_city(
            category_revenue, city_revenue, self.settings,
        )

    def plot_monthly_revenue(self) -> Figure:
        summary = metrics.monthly_summary(self.dataframe)
        return viz.plot_monthly_revenue(summary, self.settings)

    def plot_order_value_distribution(self) -> Figure:
        histogram = metrics.order_histogram(self.dataframe)
        summary = metrics.order_summary(self.dataframe)

        return viz.plot_order_value_distribution(
            histogram,
            summary,
            self.settings,
        )

    def plot_typical_order(self) -> Figure:
        orders, unit_counts = metrics.calculate_typical_order_data(self.dataframe)
        histogram = metrics.order_histogram(self.dataframe)
        return viz.plot_typical_order(
            orders, unit_counts, histogram, self.settings,
        )

    def plot_revenue_distribution_city(self) -> Figure:
        summary = metrics.revenue_boxplot_summary(self.dataframe, "city")
        return viz.plot_revenue_distribution_city(summary, self.settings)

    def plot_revenue_distribution_category(self) -> Figure:
        summary = metrics.revenue_boxplot_summary(self.dataframe, "category")
        return viz.plot_revenue_distribution_category(summary, self.settings)
