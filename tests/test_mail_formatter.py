
import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.lib.config import Config
from src.lib.invst_const import constants as C
from src.lib import messages as M

from src.communication import Communication

LOGGER_NAME = "invst.test_mail_formatter"


def create_test_df():

    testfile = "tests/assets/example_summary.xlsx"
    df_results = pd.read_excel(testfile)
    print(df_results)
    return df_results


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
    # ---------------------------------------------------------------------------
    test_communication = Communication(
        access_config=config.data_source_comm_access_data,
        access_userdata=config.data_source_comm_user_data,
        logger_name=LOGGER_NAME
    )

    return test_communication


def test_format_agenda():

    test_communication = config_preparation()
    df_results = create_test_df()

    list_events, list_days = test_communication.create_agenda(
        dataframe=df_results)

    print(list_events)
    print(list_days)

    email_subject, email_body = test_communication.format_email_success(
        results=df_results)

    assert(email_subject == "AA")
