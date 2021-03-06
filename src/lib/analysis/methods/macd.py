from src.lib.analysis.basic import Basic
from src.lib.analysis.arbitration import Arbitration
from src.lib.analysis.report_analysis import ReportAnalysis
from src.lib.analysis.performance_simulation import PerformanceSimulation
from src.lib.analysis.summary import Summary
from src.lib.analysis.methods.lstm import LSTM


class MACD (LSTM, Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_MACD(self):
        """Calculate de MACD indicator. The MACD is based on the following
        steps:

        .. math::

            \\text{MACD Line} = EMA_{VC}^{(N=12)} - EMA_{VC}^{(N=26)}

        where `VC` refers to the closing value of the stock, and where the
        exponential moving average is defined for a magnitude `X` (in the
        current application, :math:`X=VC`) and length `N` by the self-recurring
        formular as follows:

        .. math::

            EMA_{X}^{(N)}(k) =
            \\begin{cases}
                EMA_{X}(0) = X(0) \\\\
                EMA_{X}(k) = \\alpha.X(k) + (1 - \\alpha).EMA_{X}(k-1)
            \\end{cases}

        where:

        .. math::

            \\alpha = \\frac{2}{1 + N}

        the result from :math:`\\text{MACD Line}` is used to calculate the
        :math:`\\text{MACD Signal}`, determined by:

        .. math::

            \\text{MACD Signal} = EMA_{\\text{MACD Line}}^{(N=9)}

        and finally:

        .. math::

            \\text{MACD Histogram} = \\text{MACD Line} - \\text{MACD Signal}

        The interpretation of the indicator (`MACD Histogram`) is that positive
        values indicate a buy recommendation, while negative indicate a sell
        position.

        """

        self.logger.info("Performing MACD analysis for %s", self.symbol)

        self.calc_EMA(dataframe=self.ohlc_dataset,
                      source_column="Close Final",
                      length=12,
                      result_column="MACD EMA 12")

        self.calc_EMA(dataframe=self.ohlc_dataset,
                      source_column="Close Final",
                      length=26,
                      result_column="MACD EMA 26")

        self.calc_difference(dataframe=self.ohlc_dataset,
                             minuend_column="MACD EMA 12",
                             subtrahend_column="MACD EMA 26",
                             result_column="MACD Line")

        self.calc_EMA(dataframe=self.ohlc_dataset,
                      source_column="MACD Line",
                      length=9,
                      result_column="MACD Signal")

        self.calc_difference(dataframe=self.ohlc_dataset,
                             minuend_column="MACD Line",
                             subtrahend_column="MACD Signal",
                             result_column="MACD Histogram")

        self.calc_LSTM(dataframe=self.ohlc_dataset,
                       source_column="MACD Histogram",
                       sequence_length=self.sequence_length,
                       prediction_length=self.prediction_length,
                       extend_original_data=True,
                       result_column="MACD Histogram Fit")

        self.recommend_threshold_cross(
            source_column="MACD Histogram",
            threshold_upper=0.0,  # 0.15
            threshold_lower=0.0,  # 0.15
            mode="norm",
            values_upper_mid_lower=(
                "BUY", "HOLD", "SELL"),
            result_column="MACD Recommendation")

        self.define_actions(source_column="MACD Recommendation",
                            result_column="MACD Recommended Events")

        self.simulate_performance(source_column_close="Close Final",
                                  source_column_decision="MACD Recommendation",
                                  source_column_events="MACD Recommended Events",
                                  initial_value=self.initial_value,
                                  stopgain=self.stopgain,
                                  stoploss=self.stoploss,
                                  operation_cost_fix=self.operation_cost_fix,
                                  operation_cost_proportional=self.operation_cost_proportional,
                                  operation_cost_min=self.operation_cost_min,
                                  operation_cost_max=self.operation_cost_max,
                                  tax_percentage=self.tax_percentage,
                                  result_column="MACD Simulation")
        self.calculate_reference(source_column_close="Close Final",
                                 initial_value=10000,
                                 result_column="MACD Simulation Reference")

        if self.display_analysis or self.save_analysis:
            self.present_analysis()

        self.get_summary(method_name="MACD")
