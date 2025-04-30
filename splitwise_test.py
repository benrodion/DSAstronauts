import pytest
from splitwise import OptimalSplit

#tests if the algorithm handles unexpected inputs correctly
def exception_test():
    
    with pytest.raises(ValueError): # case: balances don't add up to 0
        OptimalSplit.minTransfers([["Angela", "Olaf", 10], []])


# tests if the algorithm returns the correct results if provided with adequate inputs 
def functional_test():
    ...