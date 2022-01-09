"""Data analysis and decision taking module.
"""

import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.lib.config import Config
from src.lib.analysis.preprocessing import PreProcessing
from src.lib.analysis.methods.crash import Crash
from src.lib.analysis.methods.macd import MACD
from src.lib.analysis.methods.rsi_sma import RSI_SMA
from src.lib.analysis.methods.rsi_ema import RSI_EMA
from src.lib.analysis.methods.bollinger_band import BOLLINGER_BANDS
from src.lib.analysis.methods.combined import CombinedStrategy

LOGGER_NAME = "invst.analysis"


class Analysis(Crash, MACD, RSI_SMA, RSI_EMA, BOLLINGER_BANDS, CombinedStrategy, PreProcessing):
    """Data analysis class.

    Attributes
    ----------
        symbol: `string`
            A string with the acronym of the symbol / ticker to be used.
        ohlc_data: `Pandas dataframe`
            A Pandas dataframe with the OHLC data to be used on the analysis.
        decision: `int`
            An integere which holds the **final outcome** of the analysis. The
            value is enumerated as:

            * ``BUY`` = 1
            * ``SELL`` = -1
            * ``HOLD`` = 0

        analysis_length_pre: `int`
            Number of samples to be used for the analysis. This number is the
            one applied on the initial steps of the analysis, when truncating
            the dataset. Afterwards the truncated dataset is immediatelly used
            for the methods and predictions. For the methods themselves, this
            number shouldn't be too high, since using older data doesn't
            bring performance improvement to them. However, for the neural
            netoworks, a higher value can bring benefits since it means a larger
            dataset for learning. The downside on using al the available data
            is that it may take a considerable time to adjust the neural network
            if ``analysis_length_pre`` is too high.
        analysis_length_post: `int`
            Number of samples to be used for simulation and comparison. The
            analysis themselves use the ``analysis_length_pre`` parameter. This
            parameter is applies for final comparison.

        sequence_length: `int`
            Number of samples to be used as sequence for input to the RNN /
            LSTM.
        prediction_length: `int`
            Number of samples to be used as sequence for output in the RNN /
            LSTM.

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
                 logger_name: str):

        # ----------------------------------------------------------------------
        #   Results and data management related attributes.
        # ----------------------------------------------------------------------
        self.symbol: str = symbol
        self.ohlc_dataset = ohlc_data
        self.ohlc_dataset_prediction = None
        self.analysis_results = {}
        self.decision = None

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        config_base_path = Path.cwd().resolve() / "cfg"
        config_local_file = config_base_path / "local" / "local.json"
        config_parameters_file = config_base_path / "parameters.json"

        self.config = Config(logger_name=LOGGER_NAME)
        self.config.load_config(filename=config_local_file)
        self.config.load_config(filename=config_parameters_file)

        # ----------------------------------------------------------------------
        #   Analysis related attributes.
        # ----------------------------------------------------------------------
        self.analysis_length_pre = self.config.analysis_length_pre
        self.analysis_length_post = self.config.analysis_length_post
        self.data_length = 0
        self.up_movement = 0
        self.down_movement = 0
        self.ratio_up_down = 0

        # ----------------------------------------------------------------------
        #   RNN related attributes.
        # ----------------------------------------------------------------------
        self.sequence_length = self.config.lstm_sequence_length
        self.prediction_length = self.config.lstm_prediction_length

        # ----------------------------------------------------------------------
        #   Simulation related attributes.
        # ----------------------------------------------------------------------
        self.initial_value = self.config.initial_value
        self.stopgain = self.config.stopgain
        self.stoploss = self.config.stoploss
        self.operation_cost_fix = self.config.operation_cost_fix
        self.operation_cost_proportional = self.config.operation_cost_proportional
        self.operation_cost_min = self.config.operation_cost_min
        self.operation_cost_max = self.config.operation_cost_max
        self.tax_percentage = self.config.tax_percentage

        # ----------------------------------------------------------------------
        #   General configurations.
        # ----------------------------------------------------------------------
        self.display_analysis = self.config.display_analysis
        self.save_analysis = self.config.save_analysis

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".analysis"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing analysis.")

    def analyze(self):
        """Performs the complete analysis of the data for a determined symbol / 
        ticker.

        The basic operation of this method is:

        1. **Pre-Process**: Execute operations for adequating the data for
           analysis.
        2. **Parameters calculation**: Calculate basic parameters from the
           signals which are necessary for follow-up methods and strategies.
        3. **Apply Strategies**: Run the strategies defined. Each one is run
           individually from each other. The strategy themselves have inclusive
           prediction techniques.
        4. **Arbitrate**: Combined the results from all the different strategies
           into a final outcome.

        Parameters
        ----------
            None
                This method will use attributes from them class ``Analysis``
                and no parameter is explicitly passed to it.

        Returns
        -------
            analysis_results: `dictionary`
                Summary from the results from the ticker.
            ohlc_dataset: `Pandas Dataframe`
                Complete dataframe from the analysis from ticker.

        """

        # ----------------------------------------------------------------------
        #   Data adequation
        # ----------------------------------------------------------------------
        self.define_past_time()
        self.truncate_range(length=self.analysis_length_pre)
        self.define_closure()

        # ----------------------------------------------------------------------
        #   Parameters calculations
        # ----------------------------------------------------------------------
        self.calc_parameters()

        # ----------------------------------------------------------------------
        #   Creates a new dataframe time range to future dates
        # ----------------------------------------------------------------------
        self.extend_time_range(length=self.prediction_length)

        # ----------------------------------------------------------------------
        #   Individual strategies calculations
        # ----------------------------------------------------------------------
        self.calc_Crash()
        self.calc_MACD()
        self.calc_RSI_SMA()
        self.calc_RSI_EMA()
        self.calc_BBANDS()

        # ----------------------------------------------------------------------
        #   Final decision based on the previous BSH (Buy-Sell-Hold)
        # ----------------------------------------------------------------------
        self.decision = self.arbitrate()

        # ----------------------------------------------------------------------
        #   Export the dataframe for storage in an Excel file.
        # ----------------------------------------------------------------------
        if self.save_analysis:
            today_string = datetime.today().strftime('%Y-%m-%d')
            folder = Path(self.config.local_config["paths"]["data_storage"])
            file_export = f"Analysis data_{today_string}.xlsx"
            file_export = folder / "analysis" / today_string / file_export
            self.ohlc_dataset.to_excel(file_export)

        return (self.decision, self.analysis_results, self.ohlc_dataset)

    def calc_parameters(self):
        """Calculates basic parameters from the time series. The focus of this
        method are general parameters which can be used to support defining the
        better strategy when combining results.

        Parameters calculated:

        .. list-table:: Parameters
            :widths: 25 50
            :header-rows: 1

            * - Parameter
              - Description
            * - Up movement
              - Sum of all the positive changes in consecutive entries in the
                dataframe for the defined column.
            * - Down movement
              - Sum of all the negative changes in consecutive entries in the
                dataframe for the defined column. The final value is absolute.
            * - Ratio up/down
              - Ratio between `Up movement` and `Down movement`.

        """

        self.calc_change(dataframe=self.ohlc_dataset,
                         source_column="Close Final",
                         shift=1,
                         result_column="Close Final Change")

        self.up_movement = self.ohlc_dataset["Close Final Change"].clip(
            lower=0).sum() / self.data_length
        self.down_movement = self.ohlc_dataset["Close Final Change"].clip(
            upper=0).abs().sum() / self.data_length

        self.ratio_up_down = self.up_movement / self.down_movement
