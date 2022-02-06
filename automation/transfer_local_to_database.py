"""Automation script to copy from files to remote database.

"""
from datetime import datetime
from pathlib import Path
from src.storage import Storage
from typing import Union
import pandas as pd
import numpy as np
from src.lib.config import Config
from typing import Union

LOGGER_NAME = "invst.transfer_local_database"

if __name__ == "__main__":

    today_string = datetime.today().strftime('%Y-%m-%d')

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

    folder_local = Path(config.local_config["paths"]["data_storage"])
    folder_dropbox = config.data_source_storage_access_data["path_export"]
    load_source = config.local_config["storage"]["load"]

    storage = Storage(config=config, logger_name=LOGGER_NAME)
    database_name = "invst_db"

    # --------------------------------------------------------------------------
    #   ADDS THE HISTORY FILES
    # --------------------------------------------------------------------------
    files = storage.list_files_folder(folderpath=folder_local,
                                      criteria="History_Aggregated",
                                      force_local=True)
    blocks = ["History Aggregated"]

    for file in files[0]:
        for sheet in blocks:

            print("-----------------------------------------------------------")
            print(f"   Loading {file}")

            # ------------------------------------------------------------------
            #   Loads the data from the file
            # ------------------------------------------------------------------
            df_file, flag, level, message = storage.load_pandas(
                file, sheetname=sheet,
                force_local=True)

            print(f"   Storing in database {database_name} on table {sheet}")

            if df_file is not None:

                storage.store_pandas(
                    dataframe=df_file, database_name=database_name, table_name=sheet,
                    ignores={"local": True, "dropbox": True},
                    forces={"google_cloud_mysql": True})

            print("")

    # --------------------------------------------------------------------------
    #   ADDS THE EXPORT_COMDIRECT FILES
    # --------------------------------------------------------------------------
    files = storage.list_files_folder(folderpath=folder_local,
                                      criteria="Export_Comdirect_",
                                      force_local=True)

    blocks = ["Depot Positions Aggregated",
              "Depots",
              "Balance",
              "Depot Positions",
              "Orders"]

    for file in files[0]:
        for sheet in blocks:

            print("-----------------------------------------------------------")
            print(f"   Loading {sheet} from {file}")

            # ------------------------------------------------------------------
            #   Loads the data from the file
            # ------------------------------------------------------------------
            df_file, flag, level, message = storage.load_pandas(
                file, sheetname=sheet,
                force_local=True)

            print(f"   Storing in database {database_name} on table {sheet}")

            if df_file is not None:

                storage.store_pandas(
                    dataframe=df_file, database_name=database_name, table_name=sheet,
                    ignores={"local": True, "dropbox": True},
                    forces={"google_cloud_mysql": True})

            print("")
