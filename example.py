"""
Module for access of
"""
import logging
from pathlib import Path
from src.lib.config import Config
from src.data_access import DataAccess


LOGGER_NAME = "invst"

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    #   Defines the logger configuration
    # --------------------------------------------------------------------------
    logging.basicConfig(
        # filename=self.config.path_logger,
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
    logger.info("")
    logger.info("============================= NEW RUN =============================")

    # --------------------------------------------------------------------------
    #   Defines the location of the files with configurations
    # --------------------------------------------------------------------------
    config_access_file = Path.cwd().resolve() / "cfg" / "api-cfg.json"
    config_access_userdata_file = Path.cwd().resolve() / "cfg" / "api-cfg-access.json"

    # --------------------------------------------------------------------------
    #   Load the configuration
    # --------------------------------------------------------------------------
    config = Config(logger_name=LOGGER_NAME)
    config_dictionary = config.load_config(filename=config_access_file)

    config_access_userdata = config.load_config(filename=config_access_userdata_file)

    # --------------------------------------------------------------------------
    #   Examples of a wrong call, for GOOG2 which doesn't exists and for GOOG
    #   for Google.
    # --------------------------------------------------------------------------
    goog2 = DataAccess(
        ticker="GOOG2",
        source=config.data_source_name,
        access_config=config.data_source_access_data,
        access_userdata=config.data_source_user_data,
        logger_name=LOGGER_NAME,
    )

    goog2_values, flag, level, message = goog2.update_values(
        type_series="TIMESERIES", period="DAILY"
    )

    goog = DataAccess(
        ticker="GOOG",
        source=config.data_source_name,
        access_config=config.data_source_access_data,
        access_userdata=config.data_source_user_data,
        logger_name=LOGGER_NAME,
    )

    goog_values, flag, level, message = goog.update_values(
        type_series="TIMESERIES", period="DAILY"
    )

    print(goog_values)