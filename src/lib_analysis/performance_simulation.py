import pandas as pd
from ..lib.invst_const import constants as C


class PerformanceSimulation:

    def simulate_performance(self,
                             source_column_close: str,
                             source_column_decision: str,
                             source_column_events: str,
                             initial_value: float,
                             stopgain: float,
                             stoploss: float,
                             operation_cost: float,
                             tax_percentage: float,
                             result_column: str = "",
                             result_dataframe: pd.DataFrame = None):
        """Perfoms the simulation of the results for a given strategy.
        """

        # ----------------------------------------------------------------------
        #   Start of a initial value and create the new column.
        # ----------------------------------------------------------------------
        self.ohlc_dataset[result_column] = initial_value

        # ----------------------------------------------------------------------
        #   Loop thru the moments the ticker was bought, so the results are
        #   calculated. For each new Buy event, a fixed amount is taken, to
        #   account for the cost of operation. At the end of an operation
        #   (sell), a percentage of the gain is removed, to account for taxes.
        # ----------------------------------------------------------------------
        i = 0
        pre_first_buy = True
        cycle_profit = 0
        cycle_balance = initial_value
        total_balance = initial_value
        tax_value = 0
        operation_cost_value = 0
        takegain_value = 0
        stoploss_value = 0

        for index, row in self.ohlc_dataset.iterrows():

            if i > 0:
                # --------------------------------------------------------------
                #   Get the values for calculation and also calculate the
                #   percentage factor.
                # --------------------------------------------------------------
                decision = self.ohlc_dataset.iloc[i][source_column_decision]
                event = self.ohlc_dataset.iloc[i][source_column_events]
                close_prev = self.ohlc_dataset.iloc[i - 1][source_column_close]
                close_today = self.ohlc_dataset.iloc[i][source_column_close]

                perc_day = 1 + ((close_today - close_prev) / close_prev)

                # --------------------------------------------------------------
                #   On the first SELL or HOLD, release the first buy flag. This
                #   is done so in case the strategy starts with a BUY situation,
                #   it won't be added in the calcualtion.
                # --------------------------------------------------------------
                if event == C.SELL or event == C.HOLD:
                    pre_first_buy = False

                # --------------------------------------------------------------
                #   Reduce the current position (balance) by a constant to
                #   account for the cost of operation. Also resets the cycle
                #   gain.
                # --------------------------------------------------------------
                if event == C.BUY and pre_first_buy == False:
                    operation_cost_value = operation_cost
                    cycle_balance = total_balance
                else:
                    operation_cost_value = 0

                # --------------------------------------------------------------
                #   Trigger the Stop loss and Gain loss
                # --------------------------------------------------------------
                if event == C.BUY and pre_first_buy == False and stoploss < 1:
                    if stoploss_value == 0:
                        stoploss_value = close_prev * stoploss

                if event == C.BUY and pre_first_buy == False and stopgain > 1:
                    if takegain_value == 0:
                        takegain_value = close_prev * stopgain

                # --------------------------------------------------------------
                #   Apply stoploss or takegain limits
                # --------------------------------------------------------------
                # stoploss_latch = False
                if stoploss_value > 0 and close_prev < stoploss_value and stoploss < 1:
                    # print("")
                    # print("STOPLOSS")
                    # print(stoploss)
                    # print(stoploss_value)
                    # print(close_prev)
                    print(close_today)
                    # stoploss_latch = True
                    takegain_value = 0
                    stoploss_value = 0

                    # if stoploss_latch:
                    # print("RRRRRRRR")
                    decision = C.SELL
                    event = C.SELL
                    # stoploss_latch = False

                # takegain_latch = False
                if takegain_value > 0 and close_prev > takegain_value and stopgain > 1:
                    # print("")
                    # print("TAKEGAIN")
                    # print(takegain)
                    # print(takegain_value)
                    # print(close_prev)
                    # print(close_today)
                    # takegain_latch = True
                    takegain_value = 0
                    stoploss_value = 0

                    # if takegain_latch:
                    # print("AQUI")
                    # print(row)
                    decision = C.SELL
                    event = C.SELL
                    # takegain_latch = False
                    # print(decision)

                # --------------------------------------------------------------
                #   De-Trigger the Stoploss and Takegain strategies in case of
                #   a sell action
                # --------------------------------------------------------------
                if event == C.SELL:
                    stoploss_value = 0
                    takegain_value = 0

                # --------------------------------------------------------------
                #   Calculate the tax
                # --------------------------------------------------------------
                if event == C.SELL:  # and cycle_profit > 0:
                    cycle_profit = total_balance - cycle_balance
                    # gainloss_latch = False
                    if cycle_profit < 0:
                        cycle_profit = 0
                    tax_value = cycle_profit * tax_percentage
                    # print(tax_total)
                else:
                    tax_value = 0

                # --------------------------------------------------------------
                #   Calculate the gain / balance
                # --------------------------------------------------------------
                if decision == C.BUY and pre_first_buy == False:
                    total_balance = total_balance * perc_day
                    # cycle_profit = cycle_profit + (close_today - close_prev) / close_prev

                # --------------------------------------------------------------
                #   Apply the tax and operation costs
                # --------------------------------------------------------------
                total_balance = total_balance - operation_cost_value - tax_value

                # --------------------------------------------------------------
                #   Doesn't let the value go below 0
                # --------------------------------------------------------------
                if total_balance <= 0:
                    total_balance = 0

                self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                    result_column)] = total_balance

            i = i + 1

    def calculate_reference(self,
                            source_column_close: str,
                            initial_value: float,
                            result_column: str = "",
                            result_dataframe: pd.DataFrame = None):
        """Perfoms the simulation of the results for a given strategy.
        """

        # ----------------------------------------------------------------------
        #   Start of a initial value and create the new column.
        # ----------------------------------------------------------------------
        self.ohlc_dataset[result_column] = initial_value

        # ----------------------------------------------------------------------
        #   Loop thru the moments the ticker was bought, so the results are
        #   calculated. For each new Buy event, a fixed amount is taken, to
        #   account for the cost of operation. At the end of an operation
        #   (sell), a percentage of the gain is removed, to account for taxes.
        # ----------------------------------------------------------------------
        i = 0
        total_balance = initial_value

        for index, row in self.ohlc_dataset.iterrows():

            if i > 0:
                # --------------------------------------------------------------
                #   Get the values for calculation and also calculate the
                #   percentage factor.
                # --------------------------------------------------------------
                # decision = data_input.iloc[i][input_column_decision]
                # event = data_input.iloc[i][input_column_decision_signal]
                close_prev = self.ohlc_dataset.iloc[i - 1][source_column_close]
                close_today = self.ohlc_dataset.iloc[i][source_column_close]

                perc_day = 1 + ((close_today - close_prev) / close_prev)

                # --------------------------------------------------------------
                #   Calculate the gain / balance
                # --------------------------------------------------------------
                total_balance = total_balance * perc_day

                # --------------------------------------------------------------
                #   Doesn't let the value go below 0
                # --------------------------------------------------------------
                if total_balance <= 0:
                    total_balance = 0

                self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                    result_column)] = total_balance

            i = i + 1
