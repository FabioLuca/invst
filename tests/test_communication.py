
import pytest
import time
from pathlib import Path
from src.lib.config import Config
from src.lib.invst_const import constants as C
from src.lib import messages as M
from src.data_access import DataAccess

from src.lib.communication import Whatsapp

LOGGER_NAME = "invst.test_communication"

# @pytest.fixture(autouse=True)
# def slow_down_tests():
#     """Fixture to add a waiting time before each test, to avoid
#     overloading the API and having wrong responses."""
#     yield
#     time.sleep(15)


def config_preparation():

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
        "cfg" / "api-cfg-access.json"

    config = Config(logger_name=LOGGER_NAME)
    config_dictionary = config.load_config(filename=config_access_file)
    config_access_userdata = config.load_config(
        filename=config_access_userdata_file)

    # --------------------------------------------------------------------------
    #   ACT
    # --------------------------------------------------------------------------
    test_whatsapp = Whatsapp(
        access_config=config.data_source_comm_access_data,
        access_userdata=config.data_source_comm_user_data,
        logger_name=LOGGER_NAME
    )

    return test_whatsapp


def test_send_message():
    body = "Test connection ..."
    test_instance = config_preparation()
    result, flag, level, message = test_instance.send_message(body)
    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_SendMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected)


def test_receive_messages():
    message_count = 10
    test_instance = config_preparation()
    result, flag, level, message = \
        test_instance.receive_messages(count_limit=message_count)
    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_ReceiveMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected and
           isinstance(result, list) and len(result) <= message_count)


def test_receive_last_message():
    test_instance = config_preparation()
    result, flag, level, message = test_instance.receive_last_message()
    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_ReceiveMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected)
