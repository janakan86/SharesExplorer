# This is a sample Python script.
import pandas as pd
# import pandas_datareader.data as web

from datetime import datetime
from datetime import date
from datetime import timezone
import numpy as np

import yfinance as yf


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

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


class CalculationHelper:
    @staticmethod
    def get_todays_price(code):
        # very slow. Consider downloading and storing prices per day
        ticker = yf.Ticker(str(code) + ".ax").info
        return float(ticker['regularMarketPreviousClose'])

    @staticmethod
    def years_in_between(date_latest, date_earlier):
        dt_object_earliest = CalculationHelper.to_datetime(date_earlier)
        dt_object_latest = CalculationHelper.to_datetime(date_latest)

        gap = dt_object_latest.date() - dt_object_earliest.date()
        gap_in_seconds = gap.total_seconds()
        gap_in_years = gap_in_seconds / 31536000
        return gap_in_years

    @staticmethod
    def years_from_today(date_str):
        today = date.today()
        dt_object = CalculationHelper.to_datetime(date_str)
        gap = today - dt_object.date()

        # if bought today consider it bought a day before to avoid division by zero
        if gap.total_seconds() == 0.0:
            gap_in_seconds = 86400
        else:
            gap_in_seconds = gap.total_seconds()

        gap_in_years = gap_in_seconds / 31536000
        return gap_in_years

    # https://gist.github.com/blaylockbk/1677b446bc741ee2db3e943ab7e4cabd?permalink_comment_id=3775327
    @staticmethod
    def to_datetime(date):
        """
        Converts a numpy datetime64 object to a python datetime object
        Input:
          date - a np.datetime64 object
        Output:
          DATE - a python datetime object
        """
        timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                     / np.timedelta64(1, 's'))
        return datetime.fromtimestamp(timestamp, timezone.utc)

    @staticmethod
    def write_to_excel(data_frame, sheet_name):
        with pd.ExcelWriter(
                "/Users/kanaganayagamjanakan/Documents/cagr.xlsx"
        ) as writer:
            data_frame.to_excel(writer, sheet_name=sheet_name)


class ShareCalculations:
    def __init__(self, calculation_data):
        self.calculation_data = calculation_data

    # the gap between the money earned - money spent
    def calculateTotalGain(self):
        # currentValue of shares + total dividends = total value
        # total purchases - dividends = total money spent

        total_purchase = self.calculation_data.purchasesDF[
                             "total"].sum() / 2  # dividing by 2 to prevent the total row getting added
        total_dividends = self.calculation_data.dividendsDF[
                              "amount"].sum() / 2  # dividing by 2 to prevent the total row getting added
        total_sales = self.calculation_data.salesDF[
                          "total"].sum() / 2  # dividing by 2 to prevent the total row getting added

        current_Value = 0

        codes_df = self.calculation_data.purchasesDF['code'].unique()

        for code in codes_df:
            if isinstance(code, str):
                purchases_of_code_df = self.calculation_data.purchasesDF.loc[
                    self.calculation_data.purchasesDF['code'] == code]
                units_of_purchase = purchases_of_code_df['units'].sum()

                sales_of_code_df = self.calculation_data.salesDF.loc[self.calculation_data.salesDF['code'] == code]
                units_of_sales = sales_of_code_df['units'].sum()

                current_Value = current_Value + (
                        (units_of_purchase - units_of_sales) * self.calculation_data.latest_closing_price_df[str(code)])

        print("current market Value " + str(current_Value))
        money_spent = total_purchase - total_dividends - total_sales
        print("total money_spent " + str(money_spent))

        print("total dividends received " + str(total_dividends))
        print("gain  " + str(current_Value - money_spent))
        pt_gain = ((current_Value - money_spent) / money_spent) * 100
        print("percentage of gain on money spent", str(pt_gain))

    def calculate_sales_profit_for_code(self, code, purchases_of_code_df=None, sales_of_code_df=None):

        # TODO -  code clean up. use the parameters instead of filtering the df again
        purchases_of_code_df = self.calculation_data.purchasesDF.loc[self.calculation_data.purchasesDF['code'] == code]
        sales_of_code_df = self.calculation_data.salesDF.loc[self.calculation_data.salesDF['code']== code]
        sales_profit = 0
        for index, row_purchases in purchases_of_code_df.iterrows():
            # consider all units are unsold to begin with
            units_not_sold_for_this_purchase = row_purchases['units']

            purchase_brokerage = row_purchases['brokerage']

            # loop the dataframe of purchases
            # treat each purchase of the particular code as a separate investment and calculate cagr
            for index_sales, row_sales in sales_of_code_df.iterrows():
                if row_sales['units'] > 0 and row_sales['units'] <= row_purchases['units']:
                    # calculate the cagr for sold shares
                    units_sold = row_sales['units']

                    sales_brokerage = row_sales['brokerage']
                    purchase_brokerage_apportioned = purchase_brokerage * units_sold / row_purchases['units']

                    sales_profit = sales_profit + (units_sold * float(row_sales['price'])) - sales_brokerage - (
                                units_sold * row_purchases['price']) - purchase_brokerage_apportioned

                    # calculate the units to calculate the cagr for shares not sold
                    units_not_sold_for_this_purchase = row_purchases['units'] - row_sales['units']

                    # update the sales figure so that it is not considered when processing the next purchase
                    sales_of_code_df.at[index_sales, 'units'] = 0

                if row_sales['units'] > 0 and row_sales['units'] > row_purchases['units']:
                    # calculate cagr for sold shares separately
                    units_sold = row_purchases['units']

                    sales_brokerage_apportioned = row_sales['brokerage'] * units_sold / row_sales['units']

                    sales_profit = sales_profit + (units_sold * row_sales['price']) - sales_brokerage_apportioned - (
                                units_sold * row_purchases['price']) - purchase_brokerage

                    # calculate the units to calculate the cagr for shares not sold
                    units_not_sold_for_this_purchase = 0

                    # update the sales figure so that it is not considered when processing the next purchase
                    sales_of_code_df.at[index_sales, 'units'] = row_sales['units'] - row_purchases['units']
                    sales_of_code_df.at[index_sales, 'brokerage'] = row_sales['brokerage'] - sales_brokerage_apportioned

        return sales_profit

    def calculate_weighted_CAGR_for_all_codes(self):

        self.purchasesDF = pd.read_excel(
            "/Users/kanaganayagamjanakan/Library/CloudStorage/OneDrive-Personal/SharePurchases.xlsx",
            sheet_name="purchases")

        calculated_cagrs_df = pd.DataFrame(
            columns=['code', 'total Units purchased', 'Total Purchase value', 'total units sold', 'total sales value',
                     'current value', 'total dividends', 'total value', 'current profit', 'cagr'])

        calculated_key_numbers_df = pd.DataFrame(columns=['key stats'])
        codes_df = self.purchasesDF['code'].unique()

        numerator = 0
        denominator = 0
        for code in codes_df:
            if isinstance(code, str):

                sales_of_code_df = self.calculation_data.salesDF.loc[self.calculation_data.salesDF['code'] == code]
                dividends_of_code_sf = self.calculation_data.dividendsDF.loc[
                    self.calculation_data.dividendsDF['code'] == code]

                purchases_of_code_df = self.calculation_data.purchasesDF.loc[
                    self.calculation_data.purchasesDF['code'] == code]
                purchase_total = purchases_of_code_df['total'].sum()
                current_value = ((purchases_of_code_df['units'].sum() - sales_of_code_df['units'].sum()) *
                                 self.calculation_data.latest_closing_price_df[code])
                total_value = sales_of_code_df['total'].sum() + dividends_of_code_sf['amount'].sum() + current_value
                weighted_cagr_for_code = self.calculate_weighted_CAGR(code)
                calculated_cagrs_df.loc[len(calculated_cagrs_df.index)] = [
                    code,
                    purchases_of_code_df['units'].sum(),
                    purchase_total,
                    sales_of_code_df['units'].sum(),
                    sales_of_code_df['total'].sum(),
                    current_value,
                    dividends_of_code_sf['amount'].sum(),
                    total_value,
                    total_value - purchase_total,
                    weighted_cagr_for_code * 100
                ]

                numerator = numerator + (weighted_cagr_for_code * purchase_total)
                denominator = denominator + purchase_total

        weighter_cagr_for_all_codes = numerator / denominator
        print("weighted cagr for all codes " + str(weighter_cagr_for_all_codes))

        calculated_key_numbers_df.loc[len(calculated_key_numbers_df.index)] = [
            "cagr for all codes " + str(weighter_cagr_for_all_codes)]
        calculated_key_numbers_df.loc[len(calculated_key_numbers_df.index)] = [
            "total purchases " + str(self.calculation_data.purchasesDF["total"].sum() / 2)]
        calculated_key_numbers_df.loc[len(calculated_key_numbers_df.index)] = [
            "total dividends" + str(self.calculate_total_dividend_pt())]
        # calculated_key_numbers_df.loc[len(calculated_key_numbers_df.index)] = ["total money spent " + str(self.money_spent())]
        calculated_key_numbers_df.loc[len(calculated_key_numbers_df.index)] = [
            "total sales" + str(self.calculation_data.salesDF["total"].sum() / 2)]

        CalculationHelper.write_to_excel(calculated_key_numbers_df, "sheet 1")
        #  self.writeToExcel(calculated_cagrs_df,"sheet 2")

        return weighter_cagr_for_all_codes

    # calculate cagr separately for each time money was invested and then calculate the weighted CAGR for the code
    def calculate_weighted_CAGR(self, code):
        print(code)
        # store all the calculate cagrs. This will be used to calculate weighted cagr
        calculated_cagr_df = pd.DataFrame(columns=['units', 'purchasePrice', 'beginning_value', 'cagr', 'comments'])

        purchases_of_code_df = self.calculation_data.purchasesDF.loc[self.calculation_data.purchasesDF['code'] == code]
        sales_of_code_df = self.calculation_data.salesDF.loc[self.calculation_data.salesDF['code'] == code]
        total_dividend_of_cod_df = self.calculation_data.dividendsDF.loc[
            self.calculation_data.dividendsDF['code'] == code]

        total_units_purchased_for_code = purchases_of_code_df['units'].sum()
        total_units_sold_for_code = sales_of_code_df['units'].sum()
        available_units = total_units_purchased_for_code - total_units_sold_for_code

        total_dividends_for_code = total_dividend_of_cod_df['amount'].sum()
        # total_dividends_for_code = 0
        print("total_dividends " + str(total_dividends_for_code))
        print("total_purchases " + str(total_units_purchased_for_code) + " units totalling " + str(
            purchases_of_code_df['total'].sum()))
        # loop the dataframe of purchases
        # treat each purchase of the particular code as a separate investment and calculate cagr
        for index, row_purchases in purchases_of_code_df.iterrows():

            # consider all units are unsold to begin with
            units_not_sold_for_this_purchase = row_purchases['units']

            purchase_brokerage = row_purchases['brokerage']

            for index_sales, row_sales in sales_of_code_df.iterrows():
                if row_sales['units'] > 0 and row_sales['units'] <= row_purchases['units']:
                    # calculate the cagr for sold shares
                    units_sold = row_sales['units']

                    sales_brokerage = row_sales['brokerage']
                    purchase_brokerage_apportioned = purchase_brokerage * units_sold / row_purchases['units']
                    # print ("units sold" + str(units_sold))
                    # print("rowsales price" + str(row_sales['price']))
                    calculated_cagr = self.calculate_CAGR(units_sold * row_sales['price'] - sales_brokerage,
                                                          units_sold * row_purchases[
                                                              'price'] + purchase_brokerage_apportioned,
                                                          CalculationHelper.years_from_today(row_purchases['date']))

                    # the cagr for sold shares will continue to go down with time if there are no
                    # shares left on that code. so this calculation gives a good indication of what the cagr was when it was sold
                    # todo find a way to incorporate this stat
                    calculated_cagr_on_sold_day = self.calculate_CAGR(units_sold * row_sales['price'] - sales_brokerage,
                                                                      units_sold * row_purchases[
                                                                          'price'] + purchase_brokerage_apportioned,
                                                                      CalculationHelper.years_in_between(
                                                                          row_sales['date'],
                                                                          row_purchases['date']))

                    calculated_cagr_df.loc[len(calculated_cagr_df.index)] = [units_sold, row_purchases['price'],
                                                                             units_sold * row_purchases['price'],
                                                                             calculated_cagr, "sold shares calculation"]

                    # calculate the units to calculate the cagr for shares not sold
                    units_not_sold_for_this_purchase = row_purchases['units'] - row_sales['units']

                    # update the sales figure so that it is not considered when processing the next purchase
                    sales_of_code_df.at[index_sales, 'units'] = 0

                if row_sales['units'] > 0 and row_sales['units'] > row_purchases['units']:
                    # calculate cagr for sold shares separately
                    units_sold = row_purchases['units']

                    sales_brokerage_apportioned = row_sales['brokerage'] * units_sold / row_sales['units']

                    calculated_cagr = self.calculate_CAGR(units_sold * row_sales['price'] - sales_brokerage_apportioned,
                                                          units_sold * row_purchases['price'] + purchase_brokerage,
                                                          CalculationHelper.years_from_today(row_purchases['date']))

                    # the cagr for sold shares will continue to go down with time if there are no
                    # shares left on that code. so this calculation gives a good indication of what the cagr was when it was sold
                    # todo find a way to incorporate this stat
                    calculated_cagr_on_sold_day = self.calculate_CAGR(
                        units_sold * row_sales['price'] - sales_brokerage_apportioned,
                        units_sold * row_purchases['price'] + purchase_brokerage,
                        CalculationHelper.years_in_between(row_sales['date'],
                                                           row_purchases['date']))

                    calculated_cagr_df.loc[len(calculated_cagr_df.index)] = [units_sold, row_purchases['price'],
                                                                             units_sold * row_purchases['price'],
                                                                             calculated_cagr, "sold shares calculation"]

                    # calculate the units to calculate the cagr for shares not sold
                    units_not_sold_for_this_purchase = 0

                    # update the sales figure so that it is not considered when processing the next purchase
                    sales_of_code_df.at[index_sales, 'units'] = row_sales['units'] - row_purchases['units']
                    sales_of_code_df.at[index_sales, 'brokerage'] = row_sales['brokerage'] - sales_brokerage_apportioned

            # apportion the dividends to the unsold shares
            if units_not_sold_for_this_purchase == 0 or available_units == 0:
                apportioned_dividends = 0
            else:
                apportioned_dividends = total_dividends_for_code * units_not_sold_for_this_purchase / available_units

                beginning_value = units_not_sold_for_this_purchase * row_purchases['price']
                ending_value = units_not_sold_for_this_purchase * self.calculation_data.latest_closing_price_df[
                    str(code)] + apportioned_dividends

                print(str(code))
                calculated_cagr = self.calculate_CAGR(ending_value, beginning_value,
                                                      CalculationHelper.years_from_today(row_purchases['date']))
                calculated_cagr_df.loc[len(calculated_cagr_df.index)] = [units_not_sold_for_this_purchase,
                                                                         row_purchases['price'], beginning_value,
                                                                         calculated_cagr, "unsold shares calculation"]

        # self.writeToExcel(calculated_cagr_df)
        # iterate the calculated cagrs and calculate the weighted cagr
        numerator = 0
        denominator = 0

        for index_cagr, row_cagr in calculated_cagr_df.iterrows():
            numerator = numerator + row_cagr['cagr'] * row_cagr['beginning_value']
            denominator = denominator + row_cagr['beginning_value']

        weighted_cagr = numerator / denominator
        print("weighted cagr " + str(weighted_cagr))

        return weighted_cagr

    def calculate_CAGR(self, ending_value, beginning_value, n):

        no_of_years = n

        # if no of years is very small, even though it is mathematically correct, it gives a impractical high value.
        # we are making it to at least one tenth of a year to make the number more realistic
        if no_of_years < 0.1:
            no_of_years = 0.1

        power = 1 / no_of_years
        CAGR = pow((ending_value / beginning_value), power) - 1
        print("calculating cagr " + "  beginning Value " + str(beginning_value) + "  ending value " + str(
            ending_value) + "  n " + str(n) + " power " + str(power) + " CAGr=> " + str(CAGR))
        return CAGR

    def calculate_total_dividend_pt(self):
        total_purchase = self.calculation_data.purchasesDF[
                             "total"].sum() / 2  # dividing by 2 to prevent the total row getting added
        total_dividend = self.calculation_data.dividendsDF[
                             "amount"].sum() / 2  # dividing by 2 to prevent the total row getting added

        return (total_dividend / total_purchase) * 100


sc = ShareCalculations(CalculationData())
sc.calculateTotalGain() #prints calculated value


sales_profit = sc.calculate_sales_profit_for_code("VHY")
print(str(sales_profit))
# print(str(sales_profit))

print('weighted CAGR for all codes')
sc.calculate_weighted_CAGR_for_all_codes()

print('weighted CAGR for code VTS')
sc.calculate_weighted_CAGR('VHY')

#  -> append sheet 1 and 2 to the same excel
#  -> refactor code - move utility methods to new class
#  -> fix issues in the sheet 2 figures - cagr numbers
#  -> fix bugs in cagr calculation
#  -> how to handle if the n value is very small
# -> add variable for printing and print only if set (similar to logging on off)


# requirement
