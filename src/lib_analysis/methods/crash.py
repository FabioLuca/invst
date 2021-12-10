import pandas as pd
from src.lib_analysis.basic import Basic
from src.lib_analysis.arbitration import Arbitration
from src.lib_analysis.report_analysis import ReportAnalysis
from src.lib_analysis.performance_simulation import PerformanceSimulation
from src.lib_analysis.summary import Summary


class Crash (Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_Crash(self):
        """Simple sell indication for large drops of stock.

        """

        self.logger.info("Performing Crash analysis for %s", self.symbol)

        current_value = self.ohlc_dataset["Close Final Change"].iloc[-1]
        previous_value = self.ohlc_dataset["Close Final Change"].iloc[-2]

        percentual_drop = (current_value - previous_value) / previous_value

        if percentual_drop < -0.1:
            self.ohlc_dataset.loc[:, "Crash Recommendation"] = "SELL"

        else:
            self.ohlc_dataset.loc[:, "Crash Recommendation"] = "HOLD"

        self.define_actions(source_column="Crash Recommendation",
                            result_column="Crash Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="Crash Recommendation",
                                  source_column_events="Crash Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost=self.operation_cost,
                                  tax_percentage=self.tax_percentage,
                                  result_column="Crash Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=10000,
                                 result_column="Crash Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="Crash")
