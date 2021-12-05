import pandas as pd
from ..lib.invst_const import constants as C


class Arbitration:

    def recommend_threshold_cross(self, source_column: str, threshold_upper: float,  threshold_lower: float, mode: str = "abs", result_column: str = "", result_dataframe: pd.DataFrame = None):
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
        #   Parse and checkks the specifica parameters
        # --------------------------------------------------------------------------
        # input_parameters = specific_parameters["specific_parameters"]
        # input_name = input_parameters.get("source_column_name", "")
        # value_default_string = input_parameters.get("value_default_string", "")
        # value_high_string = input_parameters.get("value_high_string", "")
        # value_low_string = input_parameters.get("value_low_string", "")
        # threshold_high = input_parameters.get(
        #     "threshold_high", Const.ERROR_BUY)
        # threshold_low = input_parameters.get("threshold_low", Const.ERROR_SELL)
        # if (
        #     input_name == ""
        #     or value_default_string == ""
        #     or value_high_string == ""
        #     or value_low_string == ""
        #     or threshold_high == Const.ERROR_BUY
        #     or threshold_low == Const.ERROR_SELL
        # ):
        #     result = data_input
        #     flag = Const.FAIL
        #     level = Const.ERROR
        #     message = "Invalid input for the Recommendation Threshold Cross method"
        # --------------------------------------------------------------------------
        #   Populate the default value as HOLD
        # --------------------------------------------------------------------------
        # value_default = getattr(Const, value_default_string)
        # value_high = getattr(Const, value_high_string)
        # value_low = getattr(Const, value_low_string)
        value_default = C.HOLD
        value_high = C.BUY
        value_low = C.SELL

        if mode == "norm":
            threshold_upper = self.ohlc_dataset[source_column].max(
            ) * threshold_upper
            threshold_lower = self.ohlc_dataset[source_column].min(
            ) * threshold_lower

        # ----------------------------------------------------------------------
        #   Fill in the default value and calculate the crossing of the thrshold
        #   applying histeresys.
        # ----------------------------------------------------------------------
        self.ohlc_dataset[result_column] = value_default

        i = 0
        for index, row in self.ohlc_dataset.iterrows():

            if i > 1:

                if self.ohlc_dataset.iloc[i][source_column] > threshold_upper:
                    value = value_high
                elif self.ohlc_dataset.iloc[i][source_column] < threshold_lower:
                    value = value_low
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_high:
                    value = value_high
                elif self.ohlc_dataset.iloc[i-1][result_column] == value_low:
                    value = value_low
                else:
                    value = value_default

                self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                    result_column)] = value

            i = i + 1

        # # --------------------------------------------------------------------------
        # #   Display results
        # # --------------------------------------------------------------------------
        # if config.disp_data:
        #     logger.display_data(data_input)

        # # --------------------------------------------------------------------------
        # #   Return the result
        # # --------------------------------------------------------------------------
        # result = data_input
        # flag = Const.SUCCESS
        # level = Const.INFO
        # message = (
        #     "Defined indicators from '"
        #     + str(input_name)
        #     + "' based on simple threshold cross."
        # )
        # if config.log_results and logger is not None:
        #     logger.add_log_event(flag, level, message)
        # return result, flag, level, message

    def define_actions(self, source_column: str, result_column: str = "", result_dataframe: pd.DataFrame = None):

        if result_column == "":
            result_column = f"Recommended Events {source_column}"

        self.ohlc_dataset[result_column] = C.HOLD

        i = 0
        for index, row in self.ohlc_dataset.iterrows():

            current_value = self.ohlc_dataset.iloc[i][source_column]
            previous_value = self.ohlc_dataset.iloc[i - 1][source_column]

            if (current_value == C.BUY and previous_value != C.BUY):
                event = C.BUY
            elif (current_value == C.SELL and previous_value != C.SELL):
                event = C.SELL
            else:
                event = C.HOLD

            self.ohlc_dataset.iloc[i, self.ohlc_dataset.columns.get_loc(
                result_column)] = event

            i = i + 1

    def arbitrate(self, values):

        decision = 1

        return decision
