import pandas as pd
from src.lib_analysis.basic import Basic
from src.lib_analysis.arbitration import Arbitration
from src.lib_analysis.report_analysis import ReportAnalysis
from src.lib_analysis.performance_simulation import PerformanceSimulation


class MACD (Basic, Arbitration, PerformanceSimulation, ReportAnalysis):

    def calc_MACD(self):
        """Calculate de MACD indicator. The MACD is based on the following
        steps:

        #. [MACD Line] = 12-period EMA - 26-period EMA
        #. [MACD Signal] = 9-period EMA of [MACD Line]
        #. [MACD Histogram] = [MACD Line] - [MACD Signal]

        The interpretation of the indicator (histogram) is that positive values
        indicate a buy recommendation, while negative indicate a sell position.

        """

        self.logger.info("Performing MACD analysis")

        self.calc_EMA(source_column="Close Final",
                      length=12,
                      result_column="MACD EMA 12")

        self.calc_EMA(source_column="Close Final",
                      length=26,
                      result_column="MACD EMA 26")

        self.calc_difference(minuend_column="MACD EMA 12",
                             subtrahend_column="MACD EMA 26",
                             result_column="MACD Line")

        self.calc_EMA(source_column="MACD Line",
                      length=9,
                      result_column="MACD Signal")

        self.calc_difference(minuend_column="MACD Line",
                             subtrahend_column="MACD Signal",
                             result_column="MACD Histogram")

        self.recommend_threshold_cross(source_column="MACD Histogram",
                                       threshold_upper=0.15,
                                       threshold_lower=0.15,
                                       mode="norm",
                                       result_column="MACD Recommendation")

        self.define_actions(source_column="MACD Recommendation",
                            result_column="MACD Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="MACD Recommendation",
                                  source_column_events="MACD Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost=self.operation_cost,
                                  tax_percentage=self.tax_percentage,
                                  result_column="MACD Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=10000,
                                 result_column="MACD Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()
