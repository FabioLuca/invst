import math
import numpy as np
from IPython.display import display
from datetime import datetime
from benedict import benedict
import itertools
import matplotlib.dates as mdates
import pandas as PD
import talib
import lib.constants as Const
import lib.calibration as Cal

from ..lib import messages as M


class PreProcessing:

    def set_time_range(self, length):
        """Limit the data to a proper length, always keeping the latest data
        available.
        """
        self.ohlc_dataset = self.ohlc_dataset.tail(length)

    def define_closure(self):
        """Define the column for closure. This is necessary since depending on
        the source of data or on the configuration, there might be different
        columns for it. The new column is named "Close Final".
        """
        headers = self.ohlc_dataset.columns

        if "Adj Close" in headers and "Close Final" not in headers:
            self.ohlc_dataset.columns["Close Final"] = self.ohlc_dataset.columns["Adj Close"]
        elif "Close" in headers and "Close Final" not in headers:
            self.ohlc_dataset.columns["Close Final"] = self.ohlc_dataset.columns["Close"]


################################################################################
#
#   FUNCTIONS FOR PATTERN IDENTIFICATION
#
################################################################################


def calculate_upper_shadow(
    data_input, output_name, logger=None, config=None, **specific_parameters


):
    """-------------------------------------------------------------------------
        FUNCTION calculate_upper_shadow

        Calculate the Upper Shadow for the Candlestick, which is the absolute
        value of the maximum value minus the closest from opening or closing
        value. The result is added to the original Pandas DataFrame.
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column_open = input_parameters.get("source_column_open", "")
    column_close = input_parameters.get("source_column_close", "")
    column_high = input_parameters.get("source_column_high", "")
    if column_open == "" or column_close == "" or column_high == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the add delta method"

    # --------------------------------------------------------------------------
    #   Calculate
    # --------------------------------------------------------------------------
    data_input[output_name] = (
        data_input[column_high]
        - data_input[[column_open, column_close]].max(axis=1, skipna=True)
    ).abs()

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the size of the upper shadows of the candlestick."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_lower_shadow(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_lower_shadow

        Calculate the Lower Shadow for the Candlestick, which is the absolute
        value of the minimum value minus the closest from opening or closing
        value. The result is added to the original Pandas DataFrame.
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checks the specific parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column_open = input_parameters.get("source_column_open", "")
    column_close = input_parameters.get("source_column_close", "")
    column_low = input_parameters.get("source_column_low", "")
    if column_open == "" or column_close == "" or column_low == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the add delta method"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Process calculation
    # --------------------------------------------------------------------------
    data_input[output_name] = (
        data_input[column_low]
        - data_input[[column_open, column_close]].min(axis=1, skipna=True)
    ).abs()

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the size of the lower shadows of the candlestick."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_real_body(data_input, logger=None, config=None):

    data_input["Real Body"] = (
        data_input["Open"] - data_input["Close Final"]).abs()

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Added the column for the Real Body"
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def identify_pattern(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION identify_patterns

        Uses TA-lib library to identify patterns in the data
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checks the specific parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    pattern = input_parameters.get("pattern", "")
    column_open = input_parameters.get("source_column_open", "")
    column_high = input_parameters.get("source_column_high", "")
    column_low = input_parameters.get("source_column_low", "")
    column_close = input_parameters.get("source_column_close", "")
    if (
        pattern == ""
        or column_open == ""
        or column_high == ""
        or column_close == ""
        or column_low == ""
    ):
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Identify Pattern method"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Identify the pattern using TA Library
    # --------------------------------------------------------------------------
    method = getattr(talib, pattern)

    data_input[output_name] = method(
        data_input[column_open],
        data_input[column_high],
        data_input[column_low],
        data_input[column_close],
    )

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Calculated pattern " + str(pattern)
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def write_pattern_string(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION write_pattern_string

        Add a new column to the DataFrame in a String format, listing all the
        patterns identified by the function: identify_patterns
    -------------------------------------------------------------------------"""

    data_input[output_name] = ""

    for column in data_input:
        if column[:7] == "Pattern":
            for index, row in data_input.iterrows():  # data_input[column]:

                type_move = ""
                aux = ""

                if row[column] > 0:
                    type_move = ": Bear"
                elif row[column] < 0:
                    type_move = ": Bull"

                if row[column] != 0:
                    aux = data_input.loc[index, output_name]
                    # (aux)
                    if aux == "":
                        aux = column[8:] + type_move
                    else:
                        aux = aux + " / " + column[8:] + type_move
                    data_input.loc[index, output_name] = aux

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Added the pattern name"
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


################################################################################
#
#   FUNCTIONS FOR DATA PROCESSING
#
################################################################################


def rename_signal(data_input, column, new_name, logger=None, config=None):
    """-------------------------------------------------------------------------
        FUNCTION rename_signal

        Copy signals so they can be renamed
    -------------------------------------------------------------------------"""

    data_input[new_name] = data_input[column]

    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Copied and renamied signal " + \
        str(column) + " to " + str(new_name)
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_percentage_change(
    data_input, output_name="", logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_percentage_change

        Return the series of percentage difference for a DataFrame given the
        column. If a Name is supplied, then the result is added to the current
        DataFrame
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column = input_parameters.get("source_column_name", "")
    if column == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Percentual Change method"

    # --------------------------------------------------------------------------
    #   Calculate
    # --------------------------------------------------------------------------
    if output_name == "":
        percentage_change = data_input[column].pct_change()
    else:
        data_input[output_name] = data_input[column].pct_change()
        percentage_change = data_input

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = percentage_change
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Percentual change calculated for column " + str(column)
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_histogram(data_input, column, bins=50, logger=None, config=None):
    """-------------------------------------------------------------------------
        FUNCTION calculate_histogram
    -------------------------------------------------------------------------"""

    hist = data_input[column].hist(bins=bins)
    hist_data = data_input[column].describe()

    result = [hist, hist_data]
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Percentual change calculated for column " + str(column)
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_moving_average(
    data_input, output_name="", logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_moving_average

        Return the series of the moving average for a DataFrame given the column
        and the length of the window (in number of samples). If a Name is
        supplied, then the result is added to the current DataFrame
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column = input_parameters.get("source_column_name", "")
    length = input_parameters.get("length", -1)
    if length < 1 or column == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the moving average method"

    # --------------------------------------------------------------------------
    #   Calculate
    # --------------------------------------------------------------------------
    if output_name == "":
        moving_average = data_input[column].rolling(window=length).mean()
    else:
        data_input[output_name] = data_input[column].rolling(
            window=length).mean()
        moving_average = data_input

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = moving_average
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the Moving Average of "
        + str(column)
        + "' for "
        + str(length)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_exponencial_moving_average(
    data_input, output_name="", logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_moving_average

        Return the series of the moving average for a DataFrame given the column
        and the length of the window (in number of samples). If a Name is
        supplied, then the result is added to the current DataFrame
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column = input_parameters.get("source_column_name", "")
    length = input_parameters.get("length", -1)
    if length < 1 or column == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the exponential moving average method"

    # --------------------------------------------------------------------------
    #   Calculate
    # --------------------------------------------------------------------------
    if output_name == "":
        moving_average = (
            data_input[column]
            .ewm(span=length, min_periods=0, adjust=False, ignore_na=False)
            .mean()
        )
    else:
        data_input[output_name] = (
            data_input[column]
            .ewm(span=length, min_periods=0, adjust=False, ignore_na=False)
            .mean()
        )
        moving_average = data_input

    result = moving_average
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the Exponential Moving Average of '"
        + str(column)
        + "' for "
        + str(length)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_midpoint(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_midpoint

        Return the series of the moving average for a DataFrame given the column
        and the length of the window (in number of samples). If a Name is
        supplied, then the result is added to the current DataFrame
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column_max = input_parameters.get("source_max_column_name", "")
    column_min = input_parameters.get("source_min_column_name", "")
    length = input_parameters.get("length", -1)
    if length < 1 or column_max == "" or column_min == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Midpoint method"

    # --------------------------------------------------------------------------
    #   Calculate. Prepare the data
    # --------------------------------------------------------------------------
    if column_max is None:
        column_max = "High"

    if column_min is None:
        column_min = "Low"

    # --------------------------------------------------------------------------
    #   Prepare the data
    # --------------------------------------------------------------------------
    data_input[output_name] = np.nan

    # --------------------------------------------------------------------------
    #   Calculate the midpoint
    # --------------------------------------------------------------------------
    i = 0
    for index, row in data_input.iterrows():
        maxi = 0
        mini = 0
        if i >= length:
            for j in range(0, length):
                maxi = max(maxi, data_input.iloc[i - j][column_max])
                mini = max(mini, data_input.iloc[i - j][column_min])

            if i >= length:
                data_input.iloc[i, data_input.columns.get_loc(output_name)] = (
                    maxi + mini
                ) / 2

        else:
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = np.nan

        i = i + 1

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "': Midpoint from column '"
        + str(column_max)
        + "' and '"
        + str(column_min)
        + "' for "
        + str(output_name)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_difference(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_difference

        Return the series of the difference between 2 other columns
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column_minuend = input_parameters.get("source_column_minuend", "")
    column_subtrahend = input_parameters.get("source_column_subtrahend", "")
    if column_minuend == "" or column_subtrahend == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Calculate Difference method"

    # --------------------------------------------------------------------------
    #   Calculate the difference between the 2 columns
    # --------------------------------------------------------------------------
    data_input[output_name] = data_input[column_minuend] - \
        data_input[column_subtrahend]

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the difference between '"
        + str(column_minuend)
        + "' and '"
        + str(column_subtrahend)
        + "'."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_integration(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_integration

        Return the series of the integration (rolling sum) of series
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column = input_parameters.get("source_column_name", "")
    period = input_parameters.get("period", -1)
    if column == "" or period < 0:
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Calculate Integration method"

    # --------------------------------------------------------------------------
    #   Calculate the rolling sum (integration of the signal)
    # --------------------------------------------------------------------------
    if period == 0:
        data_input[output_name] = data_input[column].rolling.sum()
    else:
        data_input[output_name] = data_input[column].rolling(
            window=period).sum()

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the rolling integration (sum) of '"
        + str(column)
        + "' for "
        + str(period)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_minimum(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_minimum

        Return the series of the minimun from a rolling window
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column = input_parameters.get("source_column_name", "")
    period = input_parameters.get("period", -1)
    if column == "" or period < 0:
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Calculate Minimum method"

    # --------------------------------------------------------------------------
    #   Calculate the rolling minimum
    # --------------------------------------------------------------------------
    data_input[output_name] = data_input[column].rolling(window=period).min()

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the rolling minimum of '"
        + str(column)
        + "' for "
        + str(period)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_maximum(
    data_input, new_column, column, period, logger=None, config=None,
):
    # --------------------------------------------------------------------------
    #   Calculate the rolling sum (integration of the signal)
    # --------------------------------------------------------------------------
    data_input[new_column] = data_input[column].rolling(window=period).max()

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(new_column)
        + "' with the rolling maximum of '"
        + str(column)
        + "' for "
        + str(period)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_rsi(
    data_input, output_name, input_close, period, logger=None, config=None,
):

    # --------------------------------------------------------------------------
    #   Calculate the rolling sum (integration of the signal)
    # --------------------------------------------------------------------------
    data_input[output_name] = talib.RSI(data_input[input_close], period)

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the RSI (Relative Strength Index) from '"
        + str(input_close)
        + "' for "
        + str(period)
        + " samples."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_slow_stochastic(
    data_input,
    output_name_k,
    output_name_d,
    input_high,
    input_low,
    input_close,
    period_fast_k,
    period_slow_k,
    period_slow_d,
    logger=None,
    config=None,
):

    # --------------------------------------------------------------------------
    #   Calculate the rolling sum (integration of the signal)
    # --------------------------------------------------------------------------
    data_input[output_name_k], data_input[output_name_d] = talib.STOCH(
        high=data_input[input_high],
        low=data_input[input_low],
        close=data_input[input_close],
        fastk_period=period_fast_k,
        slowk_period=period_slow_k,
        slowk_matype=0,
        slowd_period=period_slow_d,
        slowd_matype=0,
    )

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name_k)
        + "' and '"
        + str(output_name_d)
        + "' with the Slow Stochastic from."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


################################################################################
#
#   FUNCTIONS FOR DATA ANYLISIS
#
################################################################################


def strategy_moving_average(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """Calculate a recommendation to buy or sell for the Moving Average
    analysis.
    Strategy methods: Functions which will return a final recommendation
    about a ticker. The returned value is a value between -1 and 1
    indicating possible buy or sell actions.
    """

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    column_fast = input_parameters.get("source_column_fast", "")
    column_slow = input_parameters.get("source_column_slow", "")
    cap = input_parameters.get("cap", True)
    if column_fast == "" or column_slow == "":
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Strategy Moving Average method"

    # --------------------------------------------------------------------------
    #   Populate the default value as HOLD
    # --------------------------------------------------------------------------
    data_input[output_name] = Const.HOLD

    # --------------------------------------------------------------------------
    #   Caclulate the differene of the 2 series. It's used here that the
    #   slower signal (e.g. Mov Avg) when higher than the fast signal (e.g.
    #   Close), the result will be negative. A change from the delta from
    #   positive to negative indicates a ...
    # --------------------------------------------------------------------------
    data_input[output_name] = data_input[column_slow] - data_input[column_fast]

    # --------------------------------------------------------------------------
    #   Applica uma sigmoid de -1 a 1 para saturar os valores
    # --------------------------------------------------------------------------
    if cap:
        data_input[output_name] = data_input[output_name].transform(
            lambda x: -(2 / (1 + math.exp(x)) - 1)
        )

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Calculated '" + \
        str(output_name) + "' with the Strategy Moving Average."
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


# def strategy_moving_average_crossover(data_input,  config=None):

#     strategy = "Strategy Moving Average Crossover"
#     strategy_aux = "Aux Strategy Moving Average Crossover"

#     data_input[strategy] = Const.HOLD

#     data_input[strategy_aux] = (
#         data_input["MA_Close_Short"] - data_input["MA_Close_Long"]
#     )
#     data_input.loc[data_input[strategy_aux] > 0, strategy_aux] = 1
#     data_input.loc[data_input[strategy_aux] < 0, strategy_aux] = -1

#     i = 0
#     for index, row in data_input.iterrows():
#         i = i + 1
#         if i == 1 or i == len(data_input[strategy]):
#             continue
#         if (
#             data_input.iloc[i - 1][strategy_aux] > 0
#             and data_input.iloc[i][strategy_aux] <= 0
#         ):
#             data_input.iloc[i, data_input.columns.get_loc(strategy)] = Const.SELL
#         elif (
#             data_input.iloc[i - 1][strategy_aux] < 0
#             and data_input.iloc[i][strategy_aux] >= 0
#         ):
#             data_input.iloc[i, data_input.columns.get_loc(strategy)] = Const.BUY

#     result = data_input
#     flag = Const.SUCCESS
#     level = Const.INFO
#     message = "Added the results for Strategy: for Moving Average Crossover"
#     if config.log_results:
#          logger.add_log(flag, level, message, disp_results)
#     return result, flag, level, message

# def strategy_MACD(
#     data_input,
#     new_column,
#     macd_histogram,
#     macd_integral,
#     macd_integral_min,
#     macd_integral_min_factor,
#
#     config=None,
#
# ):

#     data_input[new_column] = Const.HOLD

#     # data_input.loc[data_input[macd_histogram] > 0, new_column] = 1
#     # data_input.loc[data_input[macd_histogram] <= 0, new_column] = -1

#     i = 0
#     for index, row in data_input.iterrows():

#         if (
#             data_input.iloc[i][macd_histogram]
#             > Cal.STRATEGY_MACD_POSITIVE_THRESHOLD_HISTOGRAM_UP
#         ):
#             #     and data_input.iloc[i][macd_integral]
#             #     < data_input.iloc[i][macd_integral_min] * macd_integral_min_factor
#             # ):
#             data_input.iloc[i, data_input.columns.get_loc(new_column)] = Const.BUY
#         elif (
#             data_input.iloc[i][macd_histogram]
#             < Cal.STRATEGY_MACD_POSITIVE_THRESHOLD_HISTOGRAM_DOWN
#         ):
#             data_input.iloc[i, data_input.columns.get_loc(new_column)] = Const.SELL

#         i = i + 1

#     # --------------------------------------------------------------------------
#     #   Display results
#     # --------------------------------------------------------------------------
#     if config.disp_data:
#          logger.display_data(data_input)

#     # --------------------------------------------------------------------------
#     #   Return the result
#     # --------------------------------------------------------------------------
#     result = data_input
#     flag = Const.SUCCESS
#     level = Const.INFO
#     message = "Defined indicators from MACD strategy."
#     if config.log_results:
#          logger.add_log(flag, level, message, disp_results)
#     return result, flag, level, message


# def strategy_RSI(
#     data_input,
#     output_name,
#     input_rsi,
#
#     config=None,
#
# ):

#     data_input[output_name] = Const.HOLD

#     i = 0
#     for index, row in data_input.iterrows():

#         if data_input.iloc[i][input_rsi] > Cal.STRATEGY_RSI_THRESHOLD_UP:
#             data_input.iloc[i, data_input.columns.get_loc(output_name)] = Const.SELL
#         elif data_input.iloc[i][input_rsi] < Cal.STRATEGY_RSI_THRESHOLD_DOWN:
#             data_input.iloc[i, data_input.columns.get_loc(output_name)] = Const.BUY

#         i = i + 1

#     # --------------------------------------------------------------------------
#     #   Display results
#     # --------------------------------------------------------------------------
#     if config.disp_data:
#          logger.display_data(data_input)

#     # --------------------------------------------------------------------------
#     #   Return the result
#     # --------------------------------------------------------------------------
#     result = data_input
#     flag = Const.SUCCESS
#     level = Const.INFO
#     message = "Defined indicators from RSI strategy."
#     if config.log_results:
#          logger.add_log(flag, level, message, disp_results)
#     return result, flag, level, message


def recommendation_threshold_cross(
    #     data,
    #     output_name,
    #     input_name,
    #     value_default,
    #     value_high,
    #     value_low,
    #     threshold_high,
    #     threshold_low,
    #     logger=None,
    #     config=None,
    # ):
    data_input,
    output_name,
    logger=None,
    config=None,
    **specific_parameters
):
    """Calculate a recommendation to buy or sell for the Moving Average
    analysis.
    Strategy methods: Functions which will return a final recommendation
    about a ticker. The returned value is a value between -1 and 1
    indicating possible buy or sell actions.
    """

    # --------------------------------------------------------------------------
    #   Parse and checkks the specifica parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    input_name = input_parameters.get("source_column_name", "")
    value_default_string = input_parameters.get("value_default_string", "")
    value_high_string = input_parameters.get("value_high_string", "")
    value_low_string = input_parameters.get("value_low_string", "")
    threshold_high = input_parameters.get("threshold_high", Const.ERROR_BUY)
    threshold_low = input_parameters.get("threshold_low", Const.ERROR_SELL)
    if (
        input_name == ""
        or value_default_string == ""
        or value_high_string == ""
        or value_low_string == ""
        or threshold_high == Const.ERROR_BUY
        or threshold_low == Const.ERROR_SELL
    ):
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Recommendation Threshold Cross method"
    # --------------------------------------------------------------------------
    #   Populate the default value as HOLD
    # --------------------------------------------------------------------------
    value_default = getattr(Const, value_default_string)
    value_high = getattr(Const, value_high_string)
    value_low = getattr(Const, value_low_string)

    # --------------------------------------------------------------------------
    #   Fill in the default value
    # --------------------------------------------------------------------------
    data_input[output_name] = value_default

    # --------------------------------------------------------------------------
    #   Fill in the default value
    # --------------------------------------------------------------------------
    i = 0
    for index, row in data_input.iterrows():

        if data_input.iloc[i][input_name] > threshold_high:
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = value_high
        elif data_input.iloc[i][input_name] < threshold_low:
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = value_low

        i = i + 1

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Defined indicators from '"
        + str(input_name)
        + "' based on simple threshold cross."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def strategy_line_cross(
    data,
    output_name,
    input_name,
    reference_name_high,
    reference_name_low,
    value_default,
    value_high,
    value_low,
    logger=None,
    config=None,
):

    # --------------------------------------------------------------------------
    #   Fill in the default value
    # --------------------------------------------------------------------------
    data[output_name] = value_default

    # --------------------------------------------------------------------------
    #   Fill in the default value
    # --------------------------------------------------------------------------
    i = 0
    for index, row in data.iterrows():

        if data.iloc[i][input_name] > data.iloc[i][value_high]:
            data.iloc[i, data.columns.get_loc(output_name)] = value_high
        elif data.iloc[i][input_name] < data.iloc[i][reference_name_low]:
            data.iloc[i, data.columns.get_loc(output_name)] = value_low

        i = i + 1

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Defined indicators from '" +
        str(input_name) + "' based on line crossing."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def strategy_calculate_chances(
    data_input, new_column, columns, weights, logger=None, config=None,
):

    # --------------------------------------------------------------------------
    #   Define the efault value
    # --------------------------------------------------------------------------
    data_input[new_column] = Const.HOLD

    # --------------------------------------------------------------------------
    #   Apply the mathematical operation for all the strategies
    # --------------------------------------------------------------------------
    for column, weight in zip(columns, weights):
        norm = data_input[column].max()
        data_input[new_column] = data_input[new_column] + (
            data_input[column] * weight / norm
        )

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Added new column '"
        + str(new_column)
        + "' for the total chances of the strategies."
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def decide(data_input, output_name, logger=None, config=None, **specific_parameters):
    """-------------------------------------------------------------------------
        FUNCTION decide

        Decides the buy or sell action, based on previous calculated
        probability. The output will be the latched binary conclusion and
        a second set of data with only the event indication (buy, sell)
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checks the specific parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    input_name = input_parameters.get("source_column_name", "")
    decision_threshold_buy = input_parameters.get(
        "decision_threshold_buy", Const.ERROR_BUY
    )
    decision_threshold_sell = input_parameters.get(
        "decision_threshold_sell", Const.ERROR_SELL
    )
    if (
        input_name == ""
        or decision_threshold_buy == Const.ERROR_BUY
        or decision_threshold_sell == Const.ERROR_SELL
    ):
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Decide method"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Prepare the data from input into lists
    # --------------------------------------------------------------------------
    if isinstance(output_name, list):
        list_output_name = output_name
        output_name = list_output_name[0]
        output_name_signaling = list_output_name[1]

    # --------------------------------------------------------------------------
    #   Define the default value
    # --------------------------------------------------------------------------
    data_input[output_name] = Const.HOLD

    # --------------------------------------------------------------------------
    #   Apply a threshold to the decision
    # --------------------------------------------------------------------------
    data_input[output_name] = data_input[input_name].transform(
        lambda x: Const.BUY
        if x >= decision_threshold_buy
        else (Const.SELL if x <= decision_threshold_sell else Const.HOLD)
    )

    # --------------------------------------------------------------------------
    #   Calculate the latch. The use of the lambda function didn't work as
    #   expected, likely due it didn't apply sample by sample in the column
    #   so changed to a for loop. the latch intention is to removing the
    #   bouncing of buy / hold / sell
    # --------------------------------------------------------------------------
    i = 0
    for index, row in data_input.iterrows():
        # for a in data_input.index:

        if data_input.iloc[i][output_name] == Const.BUY or (
            data_input.iloc[i][output_name] == Const.HOLD
            and data_input.iloc[i - 1][output_name] == Const.BUY
        ):
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = Const.BUY
        elif data_input.iloc[i][output_name] == Const.SELL or (
            data_input.iloc[i][output_name] == Const.HOLD
            and data_input.iloc[i - 1][output_name] == Const.SELL
        ):
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = Const.SELL
        else:
            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = Const.HOLD

        i = i + 1

    # --------------------------------------------------------------------------
    #   Add a new column for the "events" from the decision. Intented to be used
    #   for signaling on the graph
    # --------------------------------------------------------------------------
    data_input[output_name_signaling] = Const.HOLD

    i = 0
    for index, row in data_input.iterrows():

        if (
            data_input.iloc[i][output_name] == Const.BUY
            and data_input.iloc[i - 1][output_name] != Const.BUY
        ):
            data_input.iloc[
                i, data_input.columns.get_loc(output_name_signaling)
            ] = Const.BUY
        elif (
            data_input.iloc[i][output_name] == Const.SELL
            and data_input.iloc[i - 1][output_name] != Const.SELL
        ):
            data_input.iloc[
                i, data_input.columns.get_loc(output_name_signaling)
            ] = Const.SELL
        else:
            data_input.iloc[
                i, data_input.columns.get_loc(output_name_signaling)
            ] = Const.HOLD

        i = i + 1

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = (
        "Calculated '"
        + str(output_name)
        + "' with the Decision for the strategy for '"
        + str(input_name)
    )
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


################################################################################
#
#    SIMULATION AND VERIFICATION
#
################################################################################


def calculate_performance(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_performance

        Perfoms the simulation of the results for a given strategy
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checks the specific parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    input_column_decision = input_parameters.get("source_column_name", "")
    input_column_decision_signal = input_parameters.get(
        "source_column_name_signaling", ""
    )
    input_column_close = input_parameters.get("source_column_close", "")
    initial_value = input_parameters.get("initial_value", -1)
    takegain = input_parameters.get("takegain_percentage", -1)
    stoploss = input_parameters.get("stoploss_percentage", -1)
    operation_cost = input_parameters.get("operation_cost", -1)
    tax_percentage = input_parameters.get("tax_percentage", -1)
    if (
        input_column_decision == ""
        or input_column_decision_signal == ""
        or input_column_close == ""
        or initial_value == -1
        or takegain == -1
        or stoploss == -1
        or operation_cost == -1
        or tax_percentage == -1
    ):
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Calculate Performance method"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Start of a initial value and create the new column
    # --------------------------------------------------------------------------
    data_input[output_name] = initial_value

    # --------------------------------------------------------------------------
    #   Loop thru the moments the ticker was bought, so the results are
    #   calculated. For each new Buy event, a fixed amount is taken, to
    #   account for the cost of operation. At the end of an operation (sell),
    #   a percentage of the gain is removed, to account for taxes.
    # --------------------------------------------------------------------------
    i = 0
    pre_first_buy = True
    cycle_profit = 0
    cycle_balance = initial_value
    total_balance = initial_value
    tax_value = 0
    operation_cost_value = 0
    takegain_value = 0
    stoploss_value = 0

    for index, row in data_input.iterrows():

        if i > 0:
            # ------------------------------------------------------------------
            #   Get the values for calculation and also calculate the percentage
            #   factor
            # ------------------------------------------------------------------
            decision = data_input.iloc[i][input_column_decision]
            event = data_input.iloc[i][input_column_decision_signal]
            close_prev = data_input.iloc[i - 1][input_column_close]
            close_today = data_input.iloc[i][input_column_close]

            perc_day = 1 + ((close_today - close_prev) / close_prev)

            # ------------------------------------------------------------------
            #   On the first SELL or HOLD, release the first buy flag. This
            #   is done so in case the strategy starts with a BUY situation, it
            #   won't be added in the calcualtion
            # ------------------------------------------------------------------
            if event == Const.SELL or event == Const.HOLD:
                pre_first_buy = False

            # --------------------------------------------------------------
            #   Reduce the current position (balance) by a constant to
            #   account for the cost of operation. Also resets the cycle
            #   gain
            # --------------------------------------------------------------
            if event == Const.BUY and pre_first_buy == False:
                operation_cost_value = operation_cost
                cycle_balance = total_balance
            else:
                operation_cost_value = 0

            # --------------------------------------------------------------
            #   Trigger the Stop loss and Gain loss
            # --------------------------------------------------------------
            if event == Const.BUY and pre_first_buy == False and stoploss < 1:
                if stoploss_value == 0:
                    stoploss_value = close_prev * stoploss
                    # print("")
                    # print("New Stop Loss: " + str(stoploss_value))

            if event == Const.BUY and pre_first_buy == False and takegain > 1:
                if takegain_value == 0:
                    takegain_value = close_prev * takegain
                    # print("New Take Gain: " + str(takegain_value))

            # ------------------------------------------------------------------
            #   Apply stoploss or takegain limits
            # ------------------------------------------------------------------
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
                decision = Const.SELL
                event = Const.SELL
                # stoploss_latch = False

            # takegain_latch = False
            if takegain_value > 0 and close_prev > takegain_value and takegain > 1:
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
                decision = Const.SELL
                event = Const.SELL
                # takegain_latch = False
                # print(decision)

            # --------------------------------------------------------------
            #   De-Trigger the Stoploss and Takegain strategies in case of
            #   a sell action
            # --------------------------------------------------------------
            if event == Const.SELL:
                stoploss_value = 0
                takegain_value = 0

            # --------------------------------------------------------------
            #   Calculate the tax
            # --------------------------------------------------------------
            if event == Const.SELL:  # and cycle_profit > 0:
                cycle_profit = total_balance - cycle_balance
                # gainloss_latch = False
                if cycle_profit < 0:
                    cycle_profit = 0
                tax_value = cycle_profit * tax_percentage
                # print(tax_total)
            else:
                tax_value = 0

            # ------------------------------------------------------------------
            #   Calculate the gain / balance
            # ------------------------------------------------------------------
            if decision == Const.BUY and pre_first_buy == False:
                total_balance = total_balance * perc_day
                # cycle_profit = cycle_profit + (close_today - close_prev) / close_prev

            # ------------------------------------------------------------------
            #   Apply the tax and operation costs
            # ------------------------------------------------------------------
            total_balance = total_balance - operation_cost_value - tax_value

            # ------------------------------------------------------------------
            #   Doesn't let the value go below 0
            # ------------------------------------------------------------------
            if total_balance <= 0:
                total_balance = 0

            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = total_balance

        i = i + 1

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Calculed the return of the strategy: '" + \
        str(output_name) + "'."
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


def calculate_performance_reference(
    data_input, output_name, logger=None, config=None, **specific_parameters
):
    """-------------------------------------------------------------------------
        FUNCTION calculate_performance

        Perfoms the simulation of the results for a given strategy
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Parse and checks the specific parameters
    # --------------------------------------------------------------------------
    input_parameters = specific_parameters["specific_parameters"]
    input_column_close = input_parameters.get("source_column_close", "")
    initial_value = input_parameters.get("initial_value", -1)
    if input_column_close == "" or initial_value == -1:
        result = data_input
        flag = Const.FAIL
        level = Const.ERROR
        message = "Invalid input for the Calculate Performance method"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Start of a initial value and create the new column
    # --------------------------------------------------------------------------
    data_input[output_name] = initial_value

    # --------------------------------------------------------------------------
    #   Loop thru the moments the ticker was bought, so the results are
    #   calculated. For each new Buy event, a fixed amount is taken, to
    #   account for the cost of operation. At the end of an operation (sell),
    #   a percentage of the gain is removed, to account for taxes.
    # --------------------------------------------------------------------------
    i = 0
    total_balance = initial_value

    for index, row in data_input.iterrows():

        if i > 0:
            # ------------------------------------------------------------------
            #   Get the values for calculation and also calculate the percentage
            #   factor
            # ------------------------------------------------------------------
            # decision = data_input.iloc[i][input_column_decision]
            # event = data_input.iloc[i][input_column_decision_signal]
            close_prev = data_input.iloc[i - 1][input_column_close]
            close_today = data_input.iloc[i][input_column_close]

            perc_day = 1 + ((close_today - close_prev) / close_prev)

            # ------------------------------------------------------------------
            #   Calculate the gain / balance
            # ------------------------------------------------------------------
            total_balance = total_balance * perc_day

            # ------------------------------------------------------------------
            #   Doesn't let the value go below 0
            # ------------------------------------------------------------------
            if total_balance <= 0:
                total_balance = 0

            data_input.iloc[i, data_input.columns.get_loc(
                output_name)] = total_balance

        i = i + 1

    # --------------------------------------------------------------------------
    #   Display results
    # --------------------------------------------------------------------------
    if config.disp_data:
        logger.display_data(data_input)

    # --------------------------------------------------------------------------
    #   Return the result
    # --------------------------------------------------------------------------
    result = data_input
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Calculed the return of the strategy: '" + \
        str(output_name) + "'."
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message


################################################################################
#
#   FUNCTIONS FOR DATA FORMATTING
#
################################################################################


def prepare_data(data_input, source, logger=None, config=None):
    """-------------------------------------------------------------------------
        FUNCTIONS prepare_data

        Convert and verify that the data supplies follows a Panda DataFrame time
        series
    -------------------------------------------------------------------------"""

    # --------------------------------------------------------------------------
    #   Check if a dict from AlphaVantage and convert it to Pandas
    #   DataFrame formate
    # --------------------------------------------------------------------------
    if isinstance(data_input, dict) and source == "AlphaVantage":
        data_input, flag, level, message = dict_to_pandas_alphavantage(
            data_input=data_input,
            path="Time Series (Daily)",
            logger=logger,
            config=config,
        )

    # --------------------------------------------------------------------------
    #   Display basic information from the data
    # --------------------------------------------------------------------------
    if isinstance(data_input, PD.DataFrame):

        # ----------------------------------------------------------------------
        #   Display results
        # ----------------------------------------------------------------------
        if config.disp_data:
            logger.display_data(data_input)
            logger.display_data_description(data_input)

        # ----------------------------------------------------------------------
        #   Return the result for success
        # ----------------------------------------------------------------------
        result = data_input
        flag = Const.SUCCESS
        level = Const.INFO
        message = "Data pre-processing successfully"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    # --------------------------------------------------------------------------
    #   Return the result for failure
    # --------------------------------------------------------------------------
    else:
        result = None
        flag = Const.FAIL
        level = Const.ERROR
        message = "Data type provided can't be used"
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message


"""===========================================================================
    FUNCTIONS pdict_to_pandas_alphavantagerepare_data

    Converts a dict into a Pandas Dataframe time series
==========================================================================="""


def dict_to_pandas_alphavantage(data_input, path, logger=None, config=None):

    # print(data_input)
    # print(data_input)

    # data_output = benedict(data_input)
    # if len(path) > 1:
    #     str_path = ".".join(path)
    # elif len(path) == 1:
    #     str_path = path

    # print(str_path)
    data_output = data_input[path]

    """--------------------------------------------------------------------
        Prepara os vetores (listas) de dados básicos
    --------------------------------------------------------------------"""
    lista_tempo_str = list()
    lista_tempo_time = list()
    lista_tempo_number = list()
    lista_abertura = list()
    lista_maximo = list()
    lista_minimo = list()
    lista_fechamento = list()
    lista_fechamento_final = list()
    lista_volume = list()

    lista_tempo_str.clear()
    lista_tempo_time.clear()
    lista_tempo_number.clear()
    lista_abertura.clear()
    lista_maximo.clear()
    lista_minimo.clear()
    lista_fechamento.clear()
    lista_fechamento_final.clear()
    lista_volume.clear()

    """--------------------------------------------------------------------
        Faz a quebra dos dados nos vetores
    --------------------------------------------------------------------"""
    data_test = data_output[str(list(data_output)[0])]

    if "5. volume" in data_test:
        for day in data_output:
            lista_tempo_str.append(day)
            lista_tempo_time.append(
                datetime(year=int(day[:4]), month=int(
                    day[5:7]), day=int(day[8:]))
            )
            lista_tempo_number.append(
                mdates.date2num(
                    datetime(year=int(day[:4]), month=int(
                        day[5:7]), day=int(day[8:]))
                )
            )

            lista_abertura.append(float(data_output[day]["1. open"]))
            lista_maximo.append(float(data_output[day]["2. high"]))
            lista_minimo.append(float(data_output[day]["3. low"]))
            lista_fechamento.append(float(data_output[day]["4. close"]))
            lista_fechamento_final.append(float(data_output[day]["4. close"]))
            lista_volume.append(float(data_output[day]["5. volume"]))

    elif "5. adjusted close" in data_test:
        for day in data_output:
            lista_tempo_str.append(day)
            lista_tempo_time.append(
                datetime(year=int(day[:4]), month=int(
                    day[5:7]), day=int(day[8:]))
            )
            lista_tempo_number.append(
                mdates.date2num(
                    datetime(year=int(day[:4]), month=int(
                        day[5:7]), day=int(day[8:]))
                )
            )

            lista_abertura.append(float(data_output[day]["1. open"]))
            lista_maximo.append(float(data_output[day]["2. high"]))
            lista_minimo.append(float(data_output[day]["3. low"]))
            lista_fechamento.append(float(data_output[day]["4. close"]))
            lista_fechamento_final.append(
                float(data_output[day]["5. adjusted close"]))
            lista_volume.append(float(data_output[day]["6. volume"]))

    """--------------------------------------------------------------------
        Inversão das listas para ordem correta
    --------------------------------------------------------------------"""
    lista_tempo_str.reverse()
    lista_tempo_time.reverse()
    lista_tempo_number.reverse()
    lista_abertura.reverse()
    lista_maximo.reverse()
    lista_minimo.reverse()
    lista_fechamento.reverse()
    lista_fechamento_final.reverse()
    lista_volume.reverse()

    """--------------------------------------------------------------------
        Converte dados no formato pro Pandas / Finta (OHLC)
    --------------------------------------------------------------------"""
    zippedList = list(
        zip(
            lista_tempo_str,
            lista_abertura,
            lista_maximo,
            lista_minimo,
            lista_fechamento,
            lista_fechamento_final,
            lista_volume,
        )
    )

    data_output = PD.DataFrame(
        zippedList,
        columns=["Date", "Open", "High", "Low",
                 "Close", "Close Final", "Volume"],
    )

    data_output.index = PD.to_datetime(data_output["Date"])
    data_output = data_output.drop(columns=["Date"])

    """--------------------------------------------------------------------
        Return
    --------------------------------------------------------------------"""
    result = data_output
    flag = Const.SUCCESS
    level = Const.INFO
    message = "Data for AlphaVantage converted from DICT to Pandas DataFrame"
    if config.log_results and logger is not None:
        logger.add_log_event(flag, level, message)
    return result, flag, level, message
