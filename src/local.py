"""
Module for access of
"""
import logging
from pathlib import Path
from lib.config import Config
from data_access import DataAccess

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
    #   Instantiate a ticker
    # --------------------------------------------------------------------------
    google = DataAccess(
        ticker="GOOG",
        source=config.data_source_name,
        access_config=config.data_source_access_data,
        access_userdata=config.data_source_user_data,
        logger_name=LOGGER_NAME,
    )

    btc_values = google.update_values(type_series="TIMESERIES", period="DAILY")
