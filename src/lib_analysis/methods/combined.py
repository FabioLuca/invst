import pandas as pd
from src.lib_analysis.basic import Basic
from src.lib_analysis.arbitration import Arbitration
from src.lib_analysis.report_analysis import ReportAnalysis
from src.lib_analysis.performance_simulation import PerformanceSimulation
from src.lib_analysis.summary import Summary


class CombinedStrategy (Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_CombinedStrategy(self):
        """Calculate the combined strategy which is a complex logic using other
        previous methods (e.g. MACD, RSI) or different sources (e.g. Machine
        Learning).

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

        if self.ratio_up_down < 1.2:

            self.ohlc_dataset.loc[:,
                                  "Combined Recommendation"] = \
                self.ohlc_dataset["MACD Recommendation"]
        else:
            self.ohlc_dataset.loc[:,
                                  "Combined Recommendation"] = \
                self.ohlc_dataset["BBANDS Recommendation"]

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
                                 initial_value=10000,
                                 result_column="Combined Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="Combined")
