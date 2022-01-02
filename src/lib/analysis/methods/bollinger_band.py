"""Calculates the recommendation for buy/sell based on the Bollinger Bands
strategy.
"""
from src.lib.analysis.basic import Basic
from src.lib.analysis.arbitration import Arbitration
from src.lib.analysis.report_analysis import ReportAnalysis
from src.lib.analysis.performance_simulation import PerformanceSimulation
from src.lib.analysis.summary import Summary


class BOLLINGER_BANDS (Basic, Arbitration, PerformanceSimulation, ReportAnalysis, Summary):

    def calc_BBANDS(self):
        """Calculate de Bollinger Bands indicator, which is based on first
        taking the closure value and calculating the 20 last entries moving
        average (simple):

        .. math::

            SMA_{VC}^{(N=20)}(k) = \\frac{1}{N} \\sum_{i=k-N+1}^{k} VC_{i}

        where `VC` represenst the closing value for the entry, and `N` the
        length in samples to be taken. For this case, :math:`N=20`. For the
        closing value, the adjusted one is the one applied.

        Similarly, the moving standard deviation is calculated for the same
        length:

        .. math::

            StdDev_{VC}^{(N=20)}(k) = \\sqrt{\\frac{1}{N-1} \\sum_{i=k-N+1}^{k} \\left( VC_{i} - \\overline{VC_{i}}\\right)^{2}}

        From the 2 values calculated above, 2 bands will be defined, where:

        .. math::

            UB = SMA_{VC} + 2 StdDev_{VC}

            LB = SMA_{VC} - 2 StdDev_{VC}

        on which `UB` and `LB` means upper band and lower band respectively.

        The analysis or recommandation are based on the rules:

        #. When `VC` is above the `UB`, this indicates an overbought situation,
           and thus a sell indication.
        #. When `VC` is above the `LB`, this indicates an oversold situation,
           and thus a buy indication.

        Parameters
        ----------
            None
                The input for the calculation is based on the Pandas dataframe
                data which is already available. The expected column for
                this operation is:

                #. `Close Final`

        Returns
        -------
            None
                The outcome from the calculation is not explicitly returned, but
                added to the Pandas dataframe as new columns. The new columns
                are:

                #. `BBANDS SMA 20`: Result from the simple moving average of the
                   last 20 samples.
                #. `BBANDS StdDev 20`: Result from the moving sample standard
                   deviation of the last 20 samples.
                #. `BBANDS Upper`: Resulting upper band.
                #. `BBANDS Lower`: Resulting lower band.
                #. `BBANDS Recommendation`: Resulting recommendation for the
                   strategy.
                #. `BBANDS Recommendation Events`: Resulting recommendation
                   events for the strategy.
                #. `BBANDS Simulation`: Resulted simulation based on the
                   previous strategy recommendation.
                #. `BBANDS Simulation Reference`: Resulted simulation from the
                   buy-hold strategy to be used as reference for the current
                   strategy simulation.

        """

        self.logger.info(
            "Performing Bollinger Bands analysis for %s", self.symbol)

        self.calc_SMA(dataframe=self.ohlc_dataset,
                      source_column="Close Final",
                      length=20,
                      result_column="BBANDS SMA 20")

        self.calc_MovingStdDev(dataframe=self.ohlc_dataset,
                               source_column="Close Final",
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
