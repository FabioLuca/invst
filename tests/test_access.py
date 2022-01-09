
import pytest
import time
from pathlib import Path
from src.lib.config import Config
from src.lib import constants as C
from src.lib import messages as M
from src.data_access import DataAccess

LOGGER_NAME = "invst.test_access"


@pytest.fixture(autouse=True)
def slow_down_tests():
    """Fixture to add a waiting time before each test, to avoid
    overloading the API and having wrong responses."""
    yield
    time.sleep(15)


def data_access_preparation(ticker):

    # --------------------------------------------------------------------------
    #   ARRANGE
    #   Defines the location of the files with configurations to be loaded, and
    #   load up the parameters afterwards.
    # --------------------------------------------------------------------------
    current_folder = Path.cwd().resolve().name

    if current_folder in ["tests"]:
        config_access_file = Path.cwd().resolve().parents[0]
        config_access_userdata_file = Path.cwd().resolve().parents[0]
    else:
        config_access_file = Path.cwd().resolve()
        config_access_userdata_file = Path.cwd().resolve()

    config_access_file = config_access_file / "cfg" / "api-cfg.json"
    config_access_userdata_file = config_access_userdata_file / \
        "cfg" / "user" / "api-cfg-access.json"

    config = Config(logger_name=LOGGER_NAME)
    config_dictionary = config.load_config(filename=config_access_file)
    config_access_userdata = config.load_config(
        filename=config_access_userdata_file)

    # --------------------------------------------------------------------------
    #   ACT
    # --------------------------------------------------------------------------
    test_instance = DataAccess(
        ticker=ticker,
        source=config.data_source_fetch_name,
        # config_dictionary, #config.data_source_access_data,
        access_config=config.data_source_fetch_access_data,
        # config_access_userdata, #config.data_source_user_data,
        access_userdata=config.data_source_fetch_user_data,
        logger_name=LOGGER_NAME)

    return test_instance


def test_valid_ticker():
    ticker = "GOOG"
    test_instance = data_access_preparation(ticker)
    result, flag, level, message = test_instance.update_values()
    flag_expected, level_expected, message_expected = M.get_status(
        logger_name=LOGGER_NAME,
        message_id="Fetch_Convert_Success",
        param=(ticker))
    assert (flag == flag_expected and level ==
            level_expected and message == message_expected)


def test_invalid_ticker():
    ticker = "GOOG#"
    test_instance = data_access_preparation(ticker)
    result, flag, level, message = test_instance.update_values()
    flag_expected, level_expected, message_expected = M.get_status(
        logger_name=LOGGER_NAME,
        message_id="API_200_Msg_Err")
    assert (flag == flag_expected and level ==
            level_expected and message == message_expected)


def test_invalid_type_series_parameter():
    ticker = "GOOG"
    test_instance = data_access_preparation(ticker)
    result, flag, level, message = test_instance.update_values(
        type_series="TIME")
    flag_expected, level_expected, message_expected = M.get_status(
        logger_name=LOGGER_NAME,
        message_id="API_ParamCheck_TypeSeries",
        param=(ticker))
    assert (flag == flag_expected and level ==
            level_expected and message == message_expected)


def test_invalid_period_parameter():
    ticker = "GOOG"
    test_instance = data_access_preparation(ticker)
    result, flag, level, message = test_instance.update_values(period="DAY")
    flag_expected, level_expected, message_expected = M.get_status(
        logger_name=LOGGER_NAME,
        message_id="API_ParamCheck_Period",
        param=(ticker))
    assert (flag == flag_expected and level ==
            level_expected and message == message_expected)

# def test_valid_ticker():
#     """Verifies the case of proper confgiuration"""

#     # --------------------------------------------------------------------------
#     #   Defines the location of the files with configurations
#     # --------------------------------------------------------------------------
#     current_folder = Path.cwd().resolve().name

#     if current_folder in ["tests"]:
#         config_access_file = Path.cwd().resolve().parents[0]
#         config_access_userdata_file = Path.cwd().resolve().parents[0]
#     else:
#         config_access_file = Path.cwd().resolve()
#         config_access_userdata_file = Path.cwd().resolve()

#     config_access_file = config_access_file / "cfg" / "api-cfg.json"
#     config_access_userdata_file = config_access_userdata_file / "cfg" / "api-cfg-access.json"


#     # --------------------------------------------------------------------------
#     #   Load the configuration
#     # --------------------------------------------------------------------------
#     config = Config(logger_name=LOGGER_NAME)
#     config_dictionary = config.load_config(filename=config_access_file)
#     config_access_userdata = config.load_config(filename=config_access_userdata_file)

#     test_instance = DataAccess(
#                         ticker="GOOG",
#                         source=config.data_source_name,
#                         access_config=config.data_source_access_data,
#                         access_userdata=config.data_source_user_data,
#                         logger_name=LOGGER_NAME,
#             )


#     # --------------------------------------------------------------------------
#     #   ARRANGE
#     #   Defines the location of the files with configurations to be loaded, and
#     #   load up the parameters afterwards.
#     # --------------------------------------------------------------------------
#     # current_folder = Path.cwd().resolve().name

#     # if current_folder in ["tests"]:
#     #     config_access_file = Path.cwd().resolve().parents[0]
#     #     config_access_userdata_file = Path.cwd().resolve().parents[0]
#     # else:
#     #     config_access_file = Path.cwd().resolve()
#     #     config_access_userdata_file = Path.cwd().resolve()

#     # config_access_file = config_access_file / "cfg" / "api-cfg.json"
#     # config_access_userdata_file = config_access_userdata_file / "cfg" / "api-cfg-access.json"

#     # config = Config(logger_name=LOGGER_NAME)
#     # config_dictionary = config.load_config(filename=config_access_file)
#     # config_access_userdata = config.load_config(filename=config_access_userdata_file)

#     # # --------------------------------------------------------------------------
#     # #   ACT
#     # # --------------------------------------------------------------------------
#     # test_instance = DataAccess(
#     #                     ticker="GOOG",
#     #                     source=config.data_source_name,
#     #                     access_config=config_dictionary, #config.data_source_access_data,
#     #                     access_userdata=config_access_userdata, #config.data_source_user_data,
#     #                     logger_name=LOGGER_NAME)


#     ########################

#     #test_instance = data_access_preparation("GOOG")
#     result, flag, level, message = test_instance.update_values()
#     flag_expected, level_expected, message_expected = M.get_status("Fetch_Convert_Success", "GOOG")
#     assert (flag == flag_expected and level == level_expected and message == message_expected)

# def test_invalid_ticker():
#     """Verifies the case of proper confgiuration"""

#     # --------------------------------------------------------------------------
#     #   Defines the location of the files with configurations
#     # --------------------------------------------------------------------------
#     current_folder = Path.cwd().resolve().name #.parents[0]
#     print("Pasta atual %s" % ( current_folder))
#     if current_folder in ["tests"]:
#         config_access_file = Path.cwd().resolve().parents[0]
#         config_access_userdata_file = Path.cwd().resolve().parents[0]
#     else:
#         config_access_file = Path.cwd().resolve()
#         config_access_userdata_file = Path.cwd().resolve()

#     config_access_file = config_access_file / "cfg" / "api-cfg.json"
#     config_access_userdata_file = config_access_userdata_file / "cfg" / "api-cfg-access.json"


#     # --------------------------------------------------------------------------
#     #   Load the configuration
#     # --------------------------------------------------------------------------
#     config = Config(logger_name=LOGGER_NAME)
#     config_dictionary = config.load_config(filename=config_access_file)
#     config_access_userdata = config.load_config(filename=config_access_userdata_file)


#     test_instance = DataAccess(
#                         ticker="GOOG@",
#                         source=config.data_source_name,
#                         access_config=config.data_source_access_data,
#                         access_userdata=config.data_source_user_data,
#                         logger_name=LOGGER_NAME,
#             )
#     result, flag, level, message = test_instance.update_values()
#     assert (flag == C.FAIL and level == C.ERROR)

# # btc_values = google.update_values(type_series="TIMESERIES", period="DAILY")


# # def test_buy(data_access):
# #     assert data_access.buy(ticker="BTC", value=10) == "Buy"


# # def test_sell(data_access):
# #     assert data_access.sell(ticker="BTC", value=10) == "Sell"
