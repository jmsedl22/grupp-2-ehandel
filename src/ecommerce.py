from pathlib import Path
from typing import TypedDict

from pandas import DataFrame

from io_utils import load_data
import metrics

from metrics import (
    calculate_total_revenue,
    calculate_total_units,
    count_orders,
    calculate_aov,
)

# Return type of the Summery() function as a typed dictionary
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


    def __init__(self, file_path: str | Path) -> None:
        self.file_path = file_path
        self.dataframe = load_data(self.file_path)

    def summary(self) -> SummaryData:
        return {
            "total_revenue": calculate_total_revenue(self.dataframe),
            "total_units": calculate_total_units(self.dataframe),
            "order_count": count_orders(self.dataframe),
            "aov": calculate_aov(self.dataframe),
        }

    def revenue_by_category(self) -> DataFrame:
        return metrics.revenue_by_category(self.dataframe)


    def revenue_by_month(self) -> DataFrame:  
        return metrics.revenue_by_month(self.dataframe)


    def revenue_top_3_categories(self) -> DataFrame:  
        return metrics.revenue_top_3_categories(self.dataframe)


    def order_value_distribution(self) -> dict[str, float]:
        result = metrics.calculate_order_value_distribution(self.dataframe)

        return {key: float(value) for key, value in result.items()}

    def revenue_by_city(self) -> DataFrame: 
        return metrics.revenue_by_city(self.dataframe)