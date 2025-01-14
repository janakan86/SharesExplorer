# This is a sample Python script.
import pandas as pd
# import pandas_datareader.data as web

from datetime import datetime
from datetime import date
from datetime import timezone
import numpy as np

import yfinance as yf

import CalculationHelper
import CalculationData
import Calculations


sc = Calculations.ShareCalculations(CalculationData.CalculationData())
sc.calculateTotalGain() #prints calculated value


sales_profit = sc.calculate_sales_profit_for_code("VHY")
print(str(sales_profit))
# print(str(sales_profit))

print('weighted CAGR for all codes')
sc.calculate_weighted_CAGR_for_all_codes()

print('weighted CAGR for code VTS')
sc.calculate_weighted_CAGR('VHY')

# to do
# -> add variable for printing and print only if set (similar to logging on off)

