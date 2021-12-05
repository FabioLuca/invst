
import logging
import pandas as pd
from .lib_analysis.preprocessing import PreProcessing
# from .lib_analysis.basic import Basic
# from .lib_analysis.arbitration import Arbitration

from .lib_analysis.methods.macd import MACD
from .lib_analysis.methods.macd_advanced import MACDAdvanced
from .lib_analysis.methods.arima import ARIMA


class Analysis(MACD, MACDAdvanced, ARIMA, PreProcessing):
    """Data analysis class.

    Attributes
    ----------
        symbol: `string`
            A string with the acronym of the symbol / ticker to be used.
        ohlc_data: `Pandas dataframe`
            A Pandas dataframe with the OHLC data to be used on the analysis.
        decision: `int`
            An integere which holds the final outcome of the analysis. The value
            is enumerated as:

            * **BUY** = 1
            * **SELL** = -1
            * **HOLD** = 0

        logger_name: `string`
            Name of the logger.
        display_analysis: `bool`
            Boolean indicating if after the analysis a chart with the results
            should be displayed or not. The chart will be display for `true`.
        save_analysis: `bool`
            Boolean indicating if after displaying the chart with the results,
            it should be saved or not. The chart will be saved for `true`.
    """

    def __init__(self,
                 symbol: str,
                 ohlc_data: pd.DataFrame,
                 initial_value: float,
                 stopgain: float,
                 stoploss: float,
                 operation_cost: float,
                 tax_percentage: float,
                 logger_name: str,
                 display_analysis: bool = False,
                 save_analysis: bool = False):

        self.symbol: str = symbol
        #self.initial_value = None
        self.ohlc_dataset = ohlc_data
        self.decision = None

        self.initial_value = initial_value
        self.stopgain = stopgain
        self.stoploss = stoploss
        self.operation_cost = operation_cost
        self.tax_percentage = tax_percentage

        self.display_analysis = display_analysis
        self.save_analysis = save_analysis

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".analysis"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing analysis.")

    def analyze(self):
        """Performs the complete analysis of the data.

        The basic operation of this method is:

        #. **Pre-Process**: Execute operations for adequating the data for
           analysis.
        #. **Apply Strategies**: Run the strategies defined. Each one is run
           individually from each other.
        #. **Arbitrate**: Combined the results from all the different strategies
           into a final outcome.

        """

        # ----------------------------------------------------------------------
        #   Data adequation
        # ----------------------------------------------------------------------
        self.truncate_range(length=250)  # aprox. 250-working days / year
        self.define_closure()

        # ----------------------------------------------------------------------
        #   Strategies calculations
        # ----------------------------------------------------------------------
        self.calc_MACD()
        self.calc_MACD_Advanced()
        self.calc_ARIMA()

        # ----------------------------------------------------------------------
        #   Final decision based on the previous BSH (Buy-Sell-Hold)
        # ----------------------------------------------------------------------
        self.decision = self.arbitrate(["MACD Recommendation",
                                        "ARIMA Recommendation"])

        return (self.decision, self.ohlc_dataset)
