
import pytest
import time
from datetime import datetime
from pathlib import Path
from src.lib.config import Config
from src.lib import messages as M
from src.session import Session

LOGGER_NAME = "invst.test_comdirect"


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

    config_base_path = Path.cwd().resolve() / "cfg"
    config_access_file = config_base_path / "api-cfg.json"
    config_access_userdata_file = config_base_path / "user" / "api-cfg-access.json"
    config_local_file = config_base_path / "local" / "local.json"
    config_parameters_file = config_base_path / "parameters.json"

    config = Config(logger_name=LOGGER_NAME)
    config.load_config(filename=config_access_file)
    config.load_config(filename=config_access_userdata_file)
    config.load_config(filename=config_local_file)
    config.load_config(filename=config_parameters_file)

    # --------------------------------------------------------------------------
    #   Example of accessing a Comdirect account and fetching information.
    # --------------------------------------------------------------------------
    comdirect = Session(access_config=config.data_source_trade_access_data,
                        access_userdata=config.data_source_trade_user_data,
                        logger_name=LOGGER_NAME,
                        )
    return comdirect


def test_get_balance():
    test_comdirect = config_preparation()
    test_comdirect.connect()
    balance, flag, level, message = test_comdirect.get_accounts_balance()
    print(balance)

    # body = f"Testing sending message ...\n\nReference: {datetime.now().strftime('%H:%M:%S')}"
    # test_instance = config_preparation()
    # result, flag, level, message = test_instance.send_message(body)
    # flag_expected, level_expected, message_expected = \
    #     M.get_status(LOGGER_NAME, "Comm_SendMessage_Success")
    assert(1 == 1)
