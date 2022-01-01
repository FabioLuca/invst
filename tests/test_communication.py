
import pytest
import time
from datetime import datetime
from pathlib import Path
from src.lib.config import Config
from src.lib.invst_const import constants as C
from src.lib import messages as M
from src.data_access import DataAccess

from src.lib.communication import Whatsapp

LOGGER_NAME = "invst.test_communication"


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
    body = f"Testing sending message ...\n\nReference: {datetime.now().strftime('%H:%M:%S')}"
    test_instance = config_preparation()
    result, flag, level, message = test_instance.send_message(body)
    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_SendMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected)


def test_receive_messages():
    message_count = 30
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


def test_get_response__inlist():
    case_sensitive = False
    maximum_time = 10
    maximum_positions = 10
    possible_responses = ["yes", "no"]

    test_instance = config_preparation()

    body = f"Testing getting response ...\n\nRespond with 'yes'.\n\nReference: {datetime.now().strftime('%H:%M:%S')}"
    result, flag, level, message = test_instance.send_message(body)

    result, flag, level, message = \
        test_instance.get_response(initial_message=result,
                                   maximum_time=maximum_time,
                                   maximum_positions=maximum_positions,
                                   possible_responses=possible_responses,
                                   case_sensitive=case_sensitive)

    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_ReceiveMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected and
           result.body.lower() == "yes")


def test_get_response__any():
    case_sensitive = False
    maximum_time = 10
    maximum_positions = 10
    possible_responses = []

    test_instance = config_preparation()

    body = f"Testing getting response ...\n\nAny response is valid.\n\nReference: {datetime.now().strftime('%H:%M:%S')}"
    result, flag, level, message = test_instance.send_message(body)

    result, flag, level, message = \
        test_instance.get_response(initial_message=result,
                                   maximum_time=maximum_time,
                                   maximum_positions=maximum_positions,
                                   possible_responses=possible_responses,
                                   case_sensitive=case_sensitive)

    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_ReceiveMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected and
           result.body != "")


def test_inquiry__case_insensitive():
    case_sensitive = False
    maximum_time = 10
    maximum_positions = 10
    possible_responses = ["yes", "no"]

    test_instance = config_preparation()

    question = f"Would you like some ice-cream?\n\nAnswer: 'yes' or 'no'.\n\nReference: {datetime.now().strftime('%H:%M:%S')}"

    result, flag, level, message = \
        test_instance.inquiry(question=question,
                              maximum_time=maximum_time,
                              maximum_positions=maximum_positions,
                              possible_responses=possible_responses,
                              case_sensitive=case_sensitive)

    flag_expected, level_expected, message_expected = \
        M.get_status(LOGGER_NAME, "Comm_ReceiveMessage_Success")
    assert(flag == flag_expected and level ==
           level_expected and message == message_expected and
           result.body.lower() == "yes")
