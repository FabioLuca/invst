import pandas as pd
from src.lib_analysis.basic import Basic
from src.lib_analysis.arbitration import Arbitration
from src.lib_analysis.report_analysis import ReportAnalysis
from src.lib_analysis.performance_simulation import PerformanceSimulation
from src.lib_analysis.summary import Summary


class BOLLINGER_BANDS (Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_BBANDS(self):
        """Calculate de MACD indicator. The MACD is based on the following
        steps:

        # . [MACD Line] = 12-period EMA - 26-period EMA
        # . [MACD Signal] = 9-period EMA of [MACD Line]
        # . [MACD Histogram] = [MACD Line] - [MACD Signal]

        The interpretation of the indicator (histogram) is that positive values
        indicate a buy recommendation, while negative indicate a sell position.

        """

        self.logger.info(
            "Performing Bollinger Bands analysis for %s", self.symbol)

        self.calc_SMA(source_column="Close Final",
                      length=20,
                      result_column="BBANDS SMA 20")

        self.calc_MovingStdDev(source_column="Close Final",
                               length=20,
                               result_column="BBANDS StdDev 20")

        self.ohlc_dataset.loc[:,
                              "BBANDS Upper"] = self.ohlc_dataset["BBANDS SMA 20"] + (2 * self.ohlc_dataset["BBANDS StdDev 20"])

        self.ohlc_dataset.loc[:,
                              "BBANDS Lower"] = self.ohlc_dataset["BBANDS SMA 20"] - (2 * self.ohlc_dataset["BBANDS StdDev 20"])

        self.recommend_threshold_curve(source_column="Close Final",
                                       reference_column_upper="BBANDS Upper",
                                       reference_column_lower="BBANDS Lower",
                                       values_upper_mid_lower=(
                                           "BUY", "HOLD", "SELL"),
                                       result_column="BBANDS Recommendation")

        self.define_actions(source_column="BBANDS Recommendation",
                            result_column="BBANDS Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="BBANDS Recommendation",
                                  source_column_events="BBANDS Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost=self.operation_cost,
                                  tax_percentage=self.tax_percentage,
                                  result_column="BBANDS Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=10000,
                                 result_column="BBANDS Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="BBANDS")
