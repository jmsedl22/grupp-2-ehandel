# Calculate total revenue and total number of units sold

def calculate_total_revenue_units(df):

    total_revenue = sum(df["revenue"])   # Sum all values in the column "revenue"
    total_units = sum(df["units"])       # Sum all values in the column "units"

    return total_revenue, total_units    # Returas both calculated totals


