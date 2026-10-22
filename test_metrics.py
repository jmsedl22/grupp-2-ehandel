
import pandas as pd

from src.metrics import calculate_aov


 # test AOV when there are no orders 
def test_calculate_aov_zero():
    result = calculate_aov(1000, 0)

    # chech if the results are correct
    assert result == 0.0                                        


# test AOV calculation
def test_calculate_aov():
    result = calculate_aov(1000, 4)

    # chech if the results are correct
    assert result == 250.0                                      