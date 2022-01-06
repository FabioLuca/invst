"""Example for the use of the project. The following steps are taken:

#. **Create a logger**, so all the steps during the execution are presented,
   either to have information of the current status to the user, or to support
   debugging. By default, the display to the user is done with `info` level,
   whilst the storrage in the log files are done with `debug` level.
#. **Load the configurations**, since the project depends on configuration
   input for the access of the API's, the `.json` files are loaded and the
   content stored in dictionaries to be used by the next steps.
#. **Fetch ticker data** from AlphaVantage API. For example purpose, two cases
   are done, first trying to fetch from an invalid ticker (`GOOG2`) and then
   in sequence trying to fetch for a list of valid symbols.
#. **Perform analysis** per symbol, producing a result for each one. See the
   documentation for the strategy analysis for more details.
#. **Display** on the console an overview of the results. 
#. **Fetch depot status** from Comdirect account, where for each available
   element in the depot account, its values (e.g. current price, purchase price)
   are returned to be used for performance tracking.
#. **Store the results** in Microsoft Excel files, saving a different file per
   day (current date is used in the filename), and each data having a separate
   sheet in the `.xlsx` file.

Other files in the automation folder can be used as examples.

"""
import logging
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.lib.config import Config
from src.data_access import DataAccess
from src.analysis import Analysis
from src.session import Session

from src.lib import print_table as pt
from src.lib import constants as C

LOGGER_NAME = "invst"

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    #   Defines the logger configuration and start the logger. Add a few
    #   message to mark the start of the execution.
    # --------------------------------------------------------------------------
    logging.basicConfig(
        filename=Path.cwd().resolve() / "logs" / "logs.log",
        filemode="a",
        datefmt="%Y.%m.%d %I:%M:%S %p",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    logformat = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y.%m.%d %I:%M:%S %p",)

    logger_console = logging.StreamHandler()
    logger_console.setLevel(logging.INFO)
    logger_console.setFormatter(logformat)

    logging.getLogger(LOGGER_NAME).addHandler(logger_console)

    logger = logging.getLogger(LOGGER_NAME)

    logger.info("")
    logger.info("========================== NEW RUN ==========================")

    # --------------------------------------------------------------------------
    #   Defines the location of the files with configurations and load them.
    # --------------------------------------------------------------------------
    config_access_file = Path.cwd().resolve() / "cfg" / "api-cfg.json"
    config_access_userdata_file = Path.cwd().resolve() / "cfg" / \
        "api-cfg-access.json"
    config_local_file = Path.cwd().resolve() / "cfg" / "local.json"

    config = Config(logger_name=LOGGER_NAME)
    config.load_config(filename=config_access_file)
    config.load_config(filename=config_access_userdata_file)
    config.load_config(filename=config_local_file)

    # --------------------------------------------------------------------------
    #   Examples of a wrong call, for GOOG2 which doesn't exists. Followed by
    #   and a request for a group of sysmbols.
    # --------------------------------------------------------------------------
    goog2 = DataAccess(
        ticker="GOOG2",
        source=config.data_source_fetch_name,
        access_config=config.data_source_fetch_access_data,
        access_userdata=config.data_source_fetch_user_data,
        logger_name=LOGGER_NAME,
    )

    goog2_values, flag, level, message = goog2.update_values(
        type_series="TIMESERIES", period="DAILY"
    )

    goog = DataAccess(
        ticker="GOOG",
        source=config.data_source_fetch_name,
        access_config=config.data_source_fetch_access_data,
        access_userdata=config.data_source_fetch_user_data,
        logger_name=LOGGER_NAME,
    )

    goog_values, flag, level, message = goog.update_values(
        type_series="TIMESERIES", period="DAILY"
    )

    # --------------------------------------------------------------------------
    #   Perform analysis of the data.
    # --------------------------------------------------------------------------
    analysis = Analysis(symbol="GOOG",
                        ohlc_data=goog_values,
                        analysis_length=250,
                        initial_value=10000,
                        stopgain=1.4,
                        stoploss=0.85,
                        operation_cost=5,
                        tax_percentage=0.1,
                        logger_name=LOGGER_NAME,
                        display_analysis=False,
                        save_analysis=True)
    decision = analysis.analyze()

    # --------------------------------------------------------------------------
    #   Example of accessing a Comdirect account and fetching information.
    # --------------------------------------------------------------------------
    comdirect = Session(access_config=config.data_source_trade_access_data,
                        access_userdata=config.data_source_trade_user_data,
                        logger_name=LOGGER_NAME,
                        )
    comdirect.connect()
    balance, flag, level, message = comdirect.get_accounts_balance()
    depots, flag, level, message = comdirect.get_depots()
    if flag == C.SUCCESS:
        for index, row in depots.iterrows():
            depot_position, flag, level, message = comdirect.get_depot_position(
                row["Depot ID"])
    comdirect.revoke_token()

    # --------------------------------------------------------------------------
    #   Store the results into an Excel files.
    # --------------------------------------------------------------------------
    today_string = datetime.today().strftime('%Y-%m-%d')
    file_export_trade = f"Export_Comdirect_{today_string}.xlsx"
    folder = Path(config.local_config["paths"]["data_storage"])
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    file_export_trade = folder / file_export_trade
    writer_trade = pd.ExcelWriter(file_export_trade, engine='xlsxwriter')
    balance.to_excel(writer_trade, sheet_name='Balance')
    depots.to_excel(writer_trade, sheet_name='Depots')
    depot_position[0].to_excel(
        writer_trade, sheet_name='Depot Positions Aggregated')
    depot_position[1].to_excel(writer_trade, sheet_name='Depot Positions')
    writer_trade.save()
