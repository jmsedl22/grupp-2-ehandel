
# calculate the average order value (AOV)
def calculate_aov(total_revenue: float, count_orders: int) -> float:
     # avoid division by zero
    if count_orders == 0:                              
        return 0.0

    # calculate AOV
    aov = total_revenue/count_orders 

    return aov

