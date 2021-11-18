import pytest
from pathlib import Path

# import src.lib.constants as C
import src.constants as C
from src.config import Config

from src.data_access import DataAccess

import pandas
import os


LOGGER_NAME = None

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


@pytest.fixture
def data_access():
    return DataAccess()


def test_invalid_ticker():
    # assert DataAccess
    assert (
        DataAccess(
            ticker="INVALID",
            source=config.data_source_name,
            access_config=config.data_source_access_data,
            access_userdata=config.data_source_user_data,
            logger_name=LOGGER_NAME,
        )
        == C.SUCCESS
    )


# btc_values = google.update_values(type_series="TIMESERIES", period="DAILY")


# def test_buy(data_access):
#     assert data_access.buy(ticker="BTC", value=10) == "Buy"


# def test_sell(data_access):
#     assert data_access.sell(ticker="BTC", value=10) == "Sell"
