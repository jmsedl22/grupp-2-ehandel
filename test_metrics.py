
import pandas as pd

from src.metrics import calculate_aov


 #TEST AOV whene there are no orders
 
def test_calculate_aov_zero():
    result = calculate_aov(1000, 0)

    assert result == 0.0                                        # chech if the results are correct

def test_calculate_aov():
    result = calculate_aov(1000, 4)
    
    assert result == 250.0                                      # chech if the results are correct