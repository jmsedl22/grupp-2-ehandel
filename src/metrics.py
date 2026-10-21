
# calculate the average order value (AOV)

def calculate_aov(total_revenue: float, count_orders: int) -> float:
    
    if count_orders == 0:                              # avoid division by zero
        return 0.0
    
    aov = total_revenue/count_orders 

    return aov

