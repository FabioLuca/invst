import pandas as pd
import numpy as np
from src.lib_analysis.basic import Basic
from src.lib_analysis.arbitration import Arbitration
from src.lib_analysis.report_analysis import ReportAnalysis
from src.lib_analysis.performance_simulation import PerformanceSimulation
from src.lib_analysis.summary import Summary


class RSI_SMA (Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_RSI_SMA(self):
        """Calculate de RSI (Relative Strength Index) indicator. The RSI is
        based on the following steps:

        .. math::

            RSI = 100 - \\frac{100}{1 + RS}

        where:

        .. math::

            RS = \\frac{Average Gain}{Average Loss}

        The Gain and Loss are taken as the diffeenrce day-by-day from the
        Closing value. For example:

        .. math::

            Gain = CloseValue_N - CloseValue_{N-1}

        where `N` is the value for any day, and `N-1` for the previous ones.

        This result is averaged over the last 14 entries (e.g. days), where both
        Exponential or Simple moving averages can be used. For this application
        the Simple Moving Average is used.

        The result from the RSI is to be interpreted as:

        * RSI > 70 means overbought, so an indication for selling.
        * RSI < 30 measn oversold, so an indication for buying.

        However the RSI needs a more careful analysis, as informed by
        `Investopedia <https://www.investopedia.com/terms/r/rsi.asp>`_:

            During trends, the RSI readings may fall into a band or range.
            During an uptrend, the RSI tends to stay above 30 and should
            frequently hit 70. During a downtrend, it is rare to see the RSI
            exceed 70, and the indicator frequently hits 30 or below. These
            guidelines can help determine trend strength and spot potential
            reversals. For example, if the RSI can’t reach 70 on a number of
            consecutive price swings during an uptrend, but then drops below
            30, the trend has weakened and could be reversing lower.

            The opposite is true for a downtrend. If the downtrend is unable to
            reach 30 or below and then rallies above 70, that downtrend has
            weakened and could be reversing to the upside. Trend lines and
            moving averages are helpful tools to include when using the RSI
            in this way.

        This analysis could be improved by the application of the histeresis in
        the method.

        """

        self.logger.info("Performing RSI SMA analysis for %s", self.symbol)

        N = 14

        # self.calc_change(source_column="Close Final",
        #                  shift=1,
        #                  result_column="RSI SMA Close Final Difference")

        self.calc_threshold(dataframe=self.ohlc_dataset,
                            source_column="Close Final Change",
                            threshold=0,
                            comparison="<",
                            replace_value=0,
                            result_column="RSI SMA Gain")

        self.calc_threshold(dataframe=self.ohlc_dataset,
                            source_column="Close Final Change",
                            threshold=0,
                            comparison=">",
                            replace_value=0,
                            result_column="RSI SMA Loss")

        self.calc_absolute(dataframe=self.ohlc_dataset,
                           source_column="RSI SMA Loss",
                           result_column="RSI SMA Loss Absolute")

        # self.calc_SMA(source_column="RSI SMA Gain",
        #               length=N,
        #               minimum_length=N,
        #               result_column="RSI SMA Gain Average")

        # self.calc_SMA(source_column="RSI SMA Loss Positive",
        #               length=N,
        #               minimum_length=N,
        #               result_column="RSI SMA Loss Average")

        # Get initial Averages
        self.ohlc_dataset['RSI SMA Gain Average'] = self.ohlc_dataset['RSI SMA Gain'].rolling(
            window=N, min_periods=N).mean()[:N+1]
        self.ohlc_dataset['RSI SMA Loss Average'] = self.ohlc_dataset['RSI SMA Loss Absolute'].rolling(
            window=N, min_periods=N).mean()[:N+1]

        for i, row in enumerate(self.ohlc_dataset['RSI SMA Gain Average'].iloc[N+1:]):
            self.ohlc_dataset['RSI SMA Gain Average'].iloc[i + N + 1] =\
                (self.ohlc_dataset['RSI SMA Gain Average'].iloc[i + N] *
                 (N - 1) +
                 self.ohlc_dataset['RSI SMA Gain'].iloc[i + N + 1])\
                / N
        # Average Losses
        for i, row in enumerate(self.ohlc_dataset['RSI SMA Loss Average'].iloc[N+1:]):
            self.ohlc_dataset['RSI SMA Loss Average'].iloc[i + N + 1] =\
                (self.ohlc_dataset['RSI SMA Loss Average'].iloc[i + N] *
                 (N - 1) +
                 self.ohlc_dataset['RSI SMA Loss Absolute'].iloc[i + N + 1])\
                / N

        self.calc_division(dataframe=self.ohlc_dataset,
                           dividend_column="RSI SMA Gain Average",
                           divisor_column="RSI SMA Loss Average",
                           result_column="RSI SMA RS")

        self.ohlc_dataset.loc[:, "RSI SMA RSI"] = 100 - \
            (100 / (1 + self.ohlc_dataset["RSI SMA RS"]))

        # print(self.ohlc_dataset[["Close Final", "RSI SMA Close Final Difference", "RSI SMA Gain", "RSI SMA Loss Absolute",
        #       "RSI SMA RS", "RSI SMA RSI"]].tail(50))

        self.recommend_threshold_cross(source_column="RSI SMA RSI",
                                       threshold_upper=70,
                                       threshold_lower=30,
                                       mode="abs",
                                       hysteresis=False,
                                       values_upper_mid_lower=(
                                           # C.SELL, C.HOLD, C.BUY),
                                           "SELL", "HOLD", "BUY"),
                                       result_column="RSI SMA Recommendation Pure")

        self.recommend_threshold_cross(source_column="RSI SMA RSI",
                                       threshold_upper=70,
                                       threshold_lower=30,
                                       mode="abs",
                                       hysteresis=True,
                                       values_upper_mid_lower=(
                                           # C.SELL, C.HOLD, C.BUY),
                                           "SELL", "HOLD", "BUY"),
                                       result_column="RSI SMA Recommendation")

        self.define_actions(source_column="RSI SMA Recommendation",
                            result_column="RSI SMA Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="RSI SMA Recommendation",
                                  source_column_events="RSI SMA Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost=self.operation_cost,
                                  tax_percentage=self.tax_percentage,
                                  result_column="RSI SMA Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=10000,
                                 result_column="RSI SMA Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="RSI SMA")
