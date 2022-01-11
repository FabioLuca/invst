"""Script for getting the current values from Comdirect and storing into Excel
files, to be used as a tracker.

"""
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.lib.config import Config
from src.session import Session
from src.communication import Communication
from src.lib import constants as C
from src.storage import Storage

LOGGER_NAME = "invst.comdirect_status_update"


def run_update(wait_time: int = 0):

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
    config.load_config(filename=config_access_file)
    config.load_config(filename=config_access_userdata_file)
    config.load_config(filename=config_local_file)
    config.load_config(filename=config_parameters_file)

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
    comdirect = Session(access_config=config.data_source_trade_access_data,
                        access_userdata=config.data_source_trade_user_data,
                        logger_name=LOGGER_NAME,
                        )
    comdirect.connect(wait_time=wait_time)
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
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    writer_trade = pd.ExcelWriter(file_export_trade, engine='xlsxwriter')
    balance.to_excel(writer_trade, sheet_name='Balance')
    depots.to_excel(writer_trade, sheet_name='Depots')
    depot_position[0].to_excel(
        writer_trade, sheet_name='Depot Positions Aggregated')
    depot_position[1].to_excel(writer_trade, sheet_name='Depot Positions')
    orders.to_excel(writer_trade, sheet_name='Orders')
    writer_trade.save()

    if config.data_source_storage_access_data["copy"]:
        destination = config.data_source_storage_access_data["path_balance"]
        storage = Storage(logger_name=LOGGER_NAME)
        copy_resp = storage.upload_file(file_export_trade, destination)
        if copy_resp is not None:
            logger.info("Copied file!")

    return "Finalized update!"


if __name__ == "__main__":
    run_update(wait_time=0)
