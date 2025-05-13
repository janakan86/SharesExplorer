import pandas as pd
import CalculationHelper
class CalculationData:
    def __init__(self):
        self.purchasesDF = pd.read_excel(
            CalculationHelper.construct_path(CalculationHelper.get_property("sharepurchases.filepath")),
            sheet_name=CalculationHelper.get_property("sharepurchases.sheetname"))

        self.salesDF = pd.read_excel(
            CalculationHelper.construct_path(CalculationHelper.get_property("sharesales.filepath")),
            sheet_name=CalculationHelper.get_property("sharesales.sheetname"))

        self.dividendsDF = pd.read_excel(
            CalculationHelper.construct_path(CalculationHelper.get_property("dividends.filepath")),
            sheet_name=CalculationHelper.get_property("dividends.sheetname"))

        self.latest_closing_price_df = self.load_latest_closing_price()

    def load_latest_closing_price(self):
        todays_prices_df = {}
        codes_df = self.purchasesDF['code'].unique()

        for code in codes_df:
            todays_prices_df[str(code)] = CalculationHelper.get_todays_price(str(code))

        return todays_prices_df