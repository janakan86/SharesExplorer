import pandas as pd
import CalculationData
import CalculationHelper
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

        calculated_cagrs_df = pd.DataFrame(
            columns=['code', 'total Units purchased', 'Total Purchase value', 'total units sold', 'total sales value',
                     'current value', 'total dividends', 'total value', 'current profit', 'cagr'])

        calculated_key_numbers_df = pd.DataFrame(columns=['key stats'])
        codes_df = self.calculation_data.purchasesDF['code'].unique()

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