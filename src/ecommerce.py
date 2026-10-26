from pathlib import Path
from typing import TypedDict

import pandas

from io_utils import load_data


# Return type of the Summery() function, as a typed dictionary
class SummaryData(TypedDict):
    total_revenue: float
    total_units: int
    order_count: int
    aov: float


# Class CommerceAnalyzer
# Functions as an interface between the notebook and util functions
class CommerceAnalyzer:
    file_path: str | Path
    dataframe: pandas.DataFrame


    def __init__(self, file_path: str | Path) -> None:
        self.file_path = file_path
        self.dataframe = load_data(self.file_path)


    def summary(self) -> SummaryData:  # type: ignore
        pass
