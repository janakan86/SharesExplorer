import pandas as pd
import CalculationHelper
class CalculationData:
    def __init__(self):
        self.dividendsDF = pd.read_excel(
            "/<path to excel file with dividends details>.xlsx",
            sheet_name="<sheet name>")
        self.purchasesDF = pd.read_excel(
            "//<path to excel file with purchases details>.xlsx",
            sheet_name="<sheet name>")

        self.salesDF = pd.read_excel(
            "/<path to excel file with dividends sales details>.xlsx",
            sheet_name="<sheet name>")

        self.latest_closing_price_df = self.load_latest_closing_price()

    def load_latest_closing_price(self):
        todays_prices_df = {}
        codes_df = self.purchasesDF['code'].unique()

        for code in codes_df:
            todays_prices_df[str(code)] = CalculationHelper.get_todays_price(str(code))

        return todays_prices_df