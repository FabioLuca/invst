"""Script for getting the current values from Comdirect and storing into Excel
files, to be used as a tracker.

"""
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import json
from src.lib.config import Config
from src.session import Session
from src.communication import Communication
from src.lib import constants as C
from src.storage import Storage

LOGGER_NAME = "invst.comdirect_status_update"


def run_update(mode: int = 0, wait_time: int = 0):
    """

    Parameters
    ----------
    mode: int
        Defines the mode of execution of the routine of authentication for
        Comdirect. The possible values are:
        * ``0``: Runs the authentication routine based on waiting for user
          input to console (local operation).
        * ``1``: Runs the authentication routine based on 2 steps. Runs the
          first part of the authentication.
        * ``2``: Runs the authentication routine based on 2 steps. Runs the
          second part of the authentication.
        * ``3``: Runs the authentication routine based on a waiting time.
    wait_time: int
        Only valid mode set to ``0``. Defines the time in seconds to waiting
        before executing the second part of the authentcation for Comdirect.

    """

    # --------------------------------------------------------------------------
    #   Defines the logger configuration and start the logger. Add a few
    #   message to mark the start of the execution.
    # --------------------------------------------------------------------------
    logs_folder = Path.cwd().resolve() / "logs"
    logs_folder.mkdir(parents=True, exist_ok=True)
    if not (logs_folder / "logs.log").exists():
        with open((logs_folder / "logs.log"), 'w') as filelog:
            pass

    logging.basicConfig(
        filename=(logs_folder / "logs.log"),
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
    config_base_path = Path.cwd().resolve() / "cfg"
    config_access_file = config_base_path / "api-cfg.json"
    config_access_userdata_file = config_base_path / "user" / "api-cfg-access.json"
    config_local_file = config_base_path / "local" / "local.json"
    config_parameters_file = config_base_path / "parameters.json"

    config = Config(logger_name=LOGGER_NAME)
    re_load_config = config.load_config(filename=config_access_file)
    re_load_user = config.load_config(filename=config_access_userdata_file)
    re_load_local = config.load_config(filename=config_local_file)
    re_load_param = config.load_config(filename=config_parameters_file)

    if (re_load_config[1] != C.SUCCESS or
            re_load_user[1] != C.SUCCESS or
            re_load_local[1] != C.SUCCESS or
            re_load_param[1] != C.SUCCESS):
        return "Error loading files"

    # --------------------------------------------------------------------------
    #   Starts the communication and send a message to notify.
    # --------------------------------------------------------------------------
    communication = Communication(
        access_config=config.data_source_comm_access_data,
        access_userdata=config.data_source_comm_user_data,
        logger_name=LOGGER_NAME
    )

    communication.send_message(
        body=f"Starting data update from Comdirect.\nReference: {datetime.now().strftime('%H:%M:%S')}")

    # --------------------------------------------------------------------------
    #   Example of accessing a Comdirect account and fetching information.
    # --------------------------------------------------------------------------
    if mode == 0 or mode == 1 or mode == 3:
        comdirect = Session(access_config=config.data_source_trade_access_data,
                            access_userdata=config.data_source_trade_user_data,
                            logger_name=LOGGER_NAME,
                            )
        connection, flag, level, message = comdirect.connect(mode=mode,
                                                             wait_time=wait_time)

        if mode == 1:
            temp_connection = Path.cwd().resolve() / "temp.json"
            with open(temp_connection, 'w', encoding='utf-8') as f:
                json.dump(connection, f, ensure_ascii=False, indent=4)
            return "First part complete"

    elif mode == 2:
        temp_connection = Path.cwd().resolve() / "temp.json"
        with open(temp_connection) as json_file:
            session_info = json.load(json_file)
        temp_connection.unlink()

        comdirect = Session(access_config=config.data_source_trade_access_data,
                            access_userdata=config.data_source_trade_user_data,
                            logger_name=LOGGER_NAME,
                            session_info=session_info
                            )
        connection, flag, level, message = comdirect.connect(mode=mode,
                                                             wait_time=wait_time)

    if mode == 0 or mode == 2 or mode == 3:
        balance, flag, level, message = comdirect.get_accounts_balance()
        depots, flag, level, message = comdirect.get_depots()
        if flag == C.SUCCESS:
            for index, row in depots.iterrows():
                depot_position, flag, level, message = comdirect.get_depot_position(
                    row["Depot ID"])
        orders, flag, level, message = comdirect.get_orders()
        logger.info(orders.T)
        # (results, a, b), flag, level, message = comdirect.make_order(wkn="A0RGCS",
        #                                                              type_order="LIMIT",
        #                                                              side_order="BUY",
        #                                                              quantity=4,
        #                                                              value_limit=85.00)
        # orders_after, flag, level, message = comdirect.get_orders()
        # print(orders_after.T)
        # logger.info(orders_after.T)
        comdirect.revoke_token()

        # --------------------------------------------------------------------------
        #   Store the results into an Excel files.
        # --------------------------------------------------------------------------
        today_string = datetime.today().strftime('%Y-%m-%d')
        file_export_trade = f"Export_Comdirect_{today_string}.xlsx"
        folder = Path(config.local_config["paths"]["data_storage"])
        file_export_trade = folder / file_export_trade

        storage = Storage(config=config, logger_name=LOGGER_NAME)
        storage.save_pandas_as_excel(
            dataframes=[balance,
                        depots,
                        depot_position[0],
                        depot_position[1],
                        orders
                        ],
            sheetsnames=['Balance',
                         'Depots',
                         'Depot Positions Aggregated',
                         'Depot Positions',
                         'Orders'],
            filename=file_export_trade
        )

    return "Finalized update!"


if __name__ == "__main__":
    run_update(wait_time=0)
