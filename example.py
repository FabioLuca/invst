"""Example for the use of the invst project.
"""
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.lib.config import Config
from src.session import Session
from src.data_access import DataAccess


LOGGER_NAME = "invst"

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    #   Defines the logger configuration
    # --------------------------------------------------------------------------
    logging.basicConfig(
        #filename=Path.cwd().resolve() / "logs" / "logs.log",
        filemode="a",
        datefmt="%Y.%m.%d %I:%M:%S %p",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # --------------------------------------------------------------------------
    #   Start the logger and add a few message to mark the start of the
    #   execution
    # --------------------------------------------------------------------------
    logger = logging.getLogger(LOGGER_NAME)

    logger_file = logging.FileHandler(
        Path.cwd().resolve() / "logs" / "logs.log",)
    logger.addHandler(logger_file)

    logger_file.setLevel(logging.DEBUG)
    fileformat = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger_file.setFormatter(fileformat)

    logger.info("")
    logger.info("========================== NEW RUN ==========================")

    # --------------------------------------------------------------------------
    #   Defines the location of the files with configurations
    # --------------------------------------------------------------------------
    config_access_file = Path.cwd().resolve() / "cfg" / "api-cfg.json"
    config_access_userdata_file = Path.cwd().resolve() / "cfg" / \
        "api-cfg-access.json"

    # --------------------------------------------------------------------------
    #   Load the configuration
    # --------------------------------------------------------------------------
    config = Config(logger_name=LOGGER_NAME)
    config_dictionary = config.load_config(filename=config_access_file)

    config_access_userdata = config.load_config(
        filename=config_access_userdata_file)

    # --------------------------------------------------------------------------
    #   Examples of a wrong call, for GOOG2 which doesn't exists and for GOOG
    #   for Google.
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
    #   Example of accessing a Comdirect account
    # --------------------------------------------------------------------------
    comdirect = Session(source=config.data_source_trade_name,
                        access_config=config.data_source_trade_access_data,
                        access_userdata=config.data_source_trade_user_data,
                        logger_name=LOGGER_NAME,
                        )
    comdirect.connect()
    balance, flag, level, message = comdirect.get_accounts_balance()
    depots, flag, level, message = comdirect.get_depots()
    for index, row in depots.iterrows():
        depot_position, flag, level, message = comdirect.get_depot_position(
            row["Depot ID"])
    comdirect.revoke_token()

    # --------------------------------------------------------------------------
    #   Store the results into an Excel file
    # --------------------------------------------------------------------------
    today_string = datetime.today().strftime('%Y-%m-%d')
    file_export = f"Export {today_string}.xlsx"
    writer = pd.ExcelWriter(file_export, engine='xlsxwriter')
    goog_values.to_excel(writer, sheet_name='GOOG')
    balance.to_excel(writer, sheet_name='Balance')
    depots.to_excel(writer, sheet_name='Depots')
    depot_position.to_excel(writer, sheet_name='Depot Positions')
    writer.save()
