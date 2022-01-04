import pandas as pd
import numpy as np
from datetime import datetime
#from ..lib.invst_const import constants as C


class Arbitration:

    def recommend_threshold_cross(self,
                                  source_column: str,
                                  threshold_upper: float,
                                  threshold_lower: float,
                                  mode: str = "abs",
                                  hysteresis: bool = True,
                                  values_upper_mid_lower: tuple = (
                                      "BUY", "HOLD", "SELL"),
                                  result_column: str = ""):
        """Calculate a recommendation to buy or sell based on a threshold crossing.
        Strategy methods: Functions which will return a final recommendation
        about a ticker. The returned value is a value between -1 and 1
        indicating possible buy or sell actions.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe which contains the
                series to be analyzed or based of the calculation.
            threshold_upper: float
                Upper threshold for the crossing. When different from the lower
                threshold it will automatically introduce an histeresys in the
                method.
                Depending on the parameter `mode` this value represents an
                absolute value or a relative (to the peak in the total series).
            threshold_lower: float
                Upper threshold for the crossing. When different from the upper
                threshold it will automatically introduce an histeresys in the
                method.
                Depending on the parameter `mode` this value represents an
                absolute value or a relative (to the peak in the total series).
            mode: string, optional
                Mode of calculation, 2 inputs are possible:

                #. "abs": The threshold are used absolute values.
                #. "norm": The threshold are used as relative values to the
                   peaks (normalization).

        """

        if result_column == "":
            result_column = f"Recommendation {source_column} {threshold_upper} {threshold_lower}"

        # --------------------------------------------------------------------------
        #   Populate the default value as HOLD
        # --------------------------------------------------------------------------
        value_default = values_upper_mid_lower[1]
        value_high = values_upper_mid_lower[0]
        value_low = values_upper_mid_lower[2]

        if mode == "norm":
            threshold_upper = self.ohlc_dataset[source_column].max(
            ) * threshold_upper
            threshold_lower = self.ohlc_dataset[source_column].min(
            ) * threshold_lower

        # ----------------------------------------------------------------------
        #   Fill in the default value and calculate the crossing of the thrshold
        #   applying histeresys.
        # ----------------------------------------------------------------------
        self.ohlc_dataset.loc[:, result_column] = value_default

        i = 0
        for index, row in self.ohlc_dataset.iterrows():

            if i > 1:

                if self.ohlc_dataset.iloc[i][source_column] > threshold_upper:
                    value = value_high
                elif self.ohlc_dataset.iloc[i][source_column] < threshold_lower:
                    value = value_low
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_high and hysteresis:
                    value = value_high
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_low and hysteresis:
                    value = value_low
                else:
                    value = value_default

                self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                    result_column)] = value

            i = i + 1

    def recommend_threshold_curve(self, source_column: str, reference_column_upper: str,  reference_column_lower: str, hysteresis: bool = True, values_upper_mid_lower: tuple = ("BUY", "HOLD", "SELL"),  result_column: str = "", result_dataframe: pd.DataFrame = None):

        if result_column == "":
            result_column = f"Recommendation {source_column} {reference_column_upper} {reference_column_lower}"

        value_default = values_upper_mid_lower[1]
        value_high = values_upper_mid_lower[0]
        value_low = values_upper_mid_lower[2]

        self.ohlc_dataset.loc[:, result_column] = value_default

        i = 0
        for index, row in self.ohlc_dataset.iterrows():

            if i > 1:

                threshold_upper = self.ohlc_dataset.iloc[i][reference_column_upper]
                threshold_lower = self.ohlc_dataset.iloc[i][reference_column_lower]

                if self.ohlc_dataset.iloc[i][source_column] > threshold_upper:
                    value = value_high
                elif self.ohlc_dataset.iloc[i][source_column] < threshold_lower:
                    value = value_low
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_high and hysteresis:
                    value = value_high
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_low and hysteresis:
                    value = value_low
                else:
                    value = value_default

                self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                    result_column)] = value

            i = i + 1

    def define_actions(self, source_column: str, result_column: str = "", result_dataframe: pd.DataFrame = None):

        if result_column == "":
            result_column = f"Recommended Events {source_column}"

        self.ohlc_dataset.loc[:, result_column] = "HOLD"

        i = 0
        for index, row in self.ohlc_dataset.iterrows():

            current_value = self.ohlc_dataset.iloc[i][source_column]
            previous_value = self.ohlc_dataset.iloc[i - 1][source_column]

            if (current_value == "BUY" and previous_value != "BUY"):
                event = "BUY"
            elif (current_value == "SELL" and previous_value != "SELL"):
                event = "SELL"
            else:
                event = "HOLD"

            self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                result_column)] = event

            i = i + 1

    def arbitrate(self):
        """Calculate the arbitration (combined strategy) which is a complex
        logic using other previous methods (e.g. MACD, RSI) or different sources
        (e.g. Machine Learning).

        The higher priority trigger in the overall logic is for crash
        protection. So if a stock value drops more than 10% in a single day
        a sell order will take the priority over all the other analysis. This
        trigger is only valid from the most recent entry.

        The first observation using data from many symbols is that the MACD
        by itself can produce relative positive performance (comparing to a
        buy-hold) strategy, if the stock is not on a strong upward (bullish)
        movement. To calculate the overall state of the stock, the average gains
        and average loses over the data period is calculated and produce a
        ratio:

        .. math::

            Ratio = \\frac{AverageGain}{AverageLoss}

        Where the Average for both the Gain and Loss is done by sum of positive
        deltas (between days) or negative deltas (in absolute value).

        A `Ratio` below 1.1 or 1.2, by empirical observation, seems the limit
        for produce better results with pure MACD.

        """

        self.logger.info("Performing Combined analysis for %s", self.symbol)

        result = "HOLD"

        real_dataframe = self.ohlc_dataset[self.ohlc_dataset['Data Type']
                                           == "Real data"]
        prediction_dataframe = self.ohlc_dataset[self.ohlc_dataset['Data Type']
                                                 == "Prediction data"]

        last_entry_datetime = datetime.strptime(
            str(real_dataframe.index[-1]), '%Y-%m-%d %H:%M:%S')
        last_entry_datetime = last_entry_datetime.date()

        if self.analysis_results["MACD"]["Day Next Event"] == "No change":
            next_event_datetime = last_entry_datetime
        else:
            next_event_datetime = datetime.strptime(
                self.analysis_results["MACD"]["Day Next Event"], '%Y-%m-%d')
            next_event_datetime = next_event_datetime.date()

        MACD_next_status_spam = (next_event_datetime -
                                 last_entry_datetime).days

        MACD_previous_status = self.analysis_results["MACD"]["Previous Day Event"]
        MACD_new_status = self.analysis_results["MACD"]["Last Day Event"]
        MACD_next_status = self.analysis_results["MACD"]["Next Event"]

        ###### CRASH ###########################################################
        if self.ohlc_dataset["Crash Recommendation"].iloc[-1] == "SELL":
            result = "SELL"
        ###### LOWER OSCILATION ################################################
        elif self.ratio_up_down < 1.2:
            print("Lower oscillation")
            if MACD_previous_status == "HOLD" and MACD_new_status != "HOLD" and MACD_next_status_spam > 10:
                print("MACD based")
                result = MACD_new_status
        ###### OTHERS ##########################################################
        else:
            if MACD_previous_status == "HOLD" and MACD_new_status != "HOLD" and MACD_next_status_spam > 10:
                result = MACD_new_status

        return result

        self.ohlc_dataset.loc[:, "Combined Recommendation"] = "HOLD"

        for index in range(self.ohlc_dataset.shape[0]):
            ###### CRASH #######################################################
            if index == self.ohlc_dataset.shape[0]:
                if self.ohlc_dataset["Crash Recommendation"].iloc[index] == "SELL":
                    self.ohlc_dataset["Combined Recommendation"].iloc[index] = "SELL"
            ###### LOWER OSCILATION ############################################
            elif self.ratio_up_down < 1.2:
                self.ohlc_dataset["Combined Recommendation"].iloc[index] = self.ohlc_dataset["MACD Recommendation"].iloc[index]
            ###### OTHERS ######################################################
            else:
                self.ohlc_dataset["Combined Recommendation"].iloc[index] = self.ohlc_dataset["BBANDS Recommendation"].iloc[index]

        self.define_actions(source_column="Combined Recommendation",
                            result_column="Combined Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="Combined Recommendation",
                                  source_column_events="Combined Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost=self.operation_cost,
                                  tax_percentage=self.tax_percentage,
                                  result_column="Combined Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=self.initial_value,
                                 result_column="Combined Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="Combined")
