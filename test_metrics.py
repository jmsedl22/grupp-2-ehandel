import pandas as pd
from src.metrics import calculate_total_revenue_units
df = pd.DataFrame(
    {"revenue":[200, 300, 700, 900], "units":[4,0,7,2]}
    )

print(calculate_total_revenue_units(df))