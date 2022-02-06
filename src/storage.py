import logging
import pandas as pd
from pathlib import Path
from src.lib import messages as M
from src.lib.config import Config
from src.lib.storage.dropbox import DropboxAPI as Dropbox
from src.lib.storage.googlecloud_mysql import GoogleCloudMySQL
from src.lib.storage.pandas_operations import PandasOperations
from typing import Union


class Storage(Dropbox, GoogleCloudMySQL, PandasOperations):

    def __init__(self, config: Config, logger_name: str) -> None:

        self.cnxn = None
        self.cursor = None
        self.config_db = None

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        self.config = config

        self.store_local = self.config.get_key(
            "local", ["storage", "store", "local"], False)
        self.store_dropbox = self.config.get_key(
            "local", ["storage", "store", "dropbox"], False)
        self.store_google_cloud_mysql = self.config.get_key(
            "local", ["storage", "store", "google_cloud_mysql"], False)
        self.load = self.config.get_key(
            "local", ["storage", "load"], "local")
        self.data_storage = self.config.get_key(
            "local", ["paths", "data_storage"], None)
        if self.data_storage is not None:
            self.data_storage = Path(self.data_storage).resolve()
        self.temp_folder = self.config.get_key(
            "local", ["paths", "temp_storage"], None)
        if self.temp_folder is not None:
            self.temp_folder = Path(self.temp_folder).resolve()

        self.dropbox_path = self.config.data_source_storage_access_data.get(
            "path_export", None)

        self.access_token = self.config.data_source_storage_user_data["TOKEN"]
        self.app_key = self.config.data_source_storage_user_data["APPKEY"]
        self.app_secret = self.config.data_source_storage_user_data["SECRET"]

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".storage"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing storage.")

    def list_files_folder(self, folderpath: Union[Path, str], criteria: str, force_local: bool = False):
        if self.load == "dropbox":
            files = self.list_files(folderpath=folderpath, criteria=criteria)
        elif self.load == "local" or force_local:
            files = list(
                filter(Path.is_file, folderpath.glob(f"**/{criteria}*")))
            if len(files) < 1:
                return None, None, None, None
        elif self.load == "google_cloud_mysql":
            files = None
        return files, None, None, None

    def load_pandas(self,
                    relative_path: Union[Path, str] = None,
                    sheetname: str = None,
                    database_name: str = None,
                    table_name: str = None,
                    force_local: bool = False):

        self.logger.info("Loading dataframe")

        # ----------------------------------------------------------------------
        #   LOCAL FOLDER
        # ----------------------------------------------------------------------
        if self.load == "local" or force_local:
            if isinstance(relative_path, Path) and relative_path is not None:
                if relative_path.suffix == ".xlsx":
                    if sheetname is not None:
                        dataframe, flag, level, message = self.load_pandas_from_excel(relative_path=relative_path,
                                                                                      sheetname=sheetname,
                                                                                      load_dropbox=False)
                    else:
                        self.logger.error(
                            "Missing parameters for loading local Excel file")
                elif relative_path.suffix == ".csv":
                    dataframe, flag, level, message = self.load_pandas_from_csv(relative_path=relative_path,
                                                                                load_dropbox=False)
            else:
                self.logger.error("Missing parameters for loading local file")

        # ----------------------------------------------------------------------
        #   DROPBOX
        # ----------------------------------------------------------------------
        elif self.load == "dropbox":
            if isinstance(relative_path, str) and relative_path is not None:
                if relative_path[-5:] == ".xlsx":
                    if sheetname is not None:
                        dataframe, flag, level, message = self.load_pandas_from_excel(relative_path=relative_path,
                                                                                      sheetname=sheetname,
                                                                                      load_dropbox=True)
                    else:
                        self.logger.error(
                            "Missing parameters for loading local Excel file")
                elif relative_path[-4:] == ".csv":
                    dataframe, flag, level, message = self.load_pandas_from_csv(relative_path=relative_path,
                                                                                load_dropbox=True)
            else:
                self.logger.error(
                    "Missing parameters for loading Dropbox file")

        # ----------------------------------------------------------------------
        #   GOOGLE CLOUD MYSQL
        # ----------------------------------------------------------------------
        elif self.load == "google_cloud_mysql":
            self.logger.info("Loading dataframe from Google Cloud MySQL")
            if database_name is not None and table_name is not None:

                dataframe, flag, level, message = self.load_pandas_from_db(database_name=database_name,
                                                                           table_name=table_name)
            else:
                dataframe = None
                flag, level, message = M.get_status(
                    self.logger_name, "Storage_Load_Error_Database_Parameters")

        # ----------------------------------------------------------------------
        #   Unwrap the result in case of a single dataframe.
        # ----------------------------------------------------------------------
        if isinstance(dataframe, list) and len(dataframe) == 1:
            dataframe = dataframe[0]

        return dataframe, flag, level, message

    def store_pandas(self,
                     dataframe: Union[pd.DataFrame, list[pd.DataFrame]],
                     sheetname: Union[str, list[str]] = None,
                     filename: Path = None,
                     database_name: str = None,
                     table_name: str = None,
                     ignores: dict = {},
                     forces: dict = {}):

        self.logger.info("Storing dataframe")

        # ----------------------------------------------------------------------
        #   LOCAL FOLDER
        # ----------------------------------------------------------------------
        if (self.store_local and not self.store_dropbox and not ignores.get("local", False)) or forces.get("local", False):
            self.logger.info("Saving dataframe in Local")
            if sheetname is not None and filename is not None:
                self.save_pandas_as_excel(dataframe=dataframe,
                                          sheetname=sheetname,
                                          filename=filename)
            else:
                self.logger.error("Missing parameters for local storage")

        # ----------------------------------------------------------------------
        #   DROPBOX
        #   Saving to Dropbox alone is not possible, since it needs a file to
        #   be copied to the service, so this must always have the Local
        #   storage as enabled.
        # ----------------------------------------------------------------------
        if (self.store_local and self.store_dropbox and not ignores.get("dropbox", False)) or forces.get("dropbox", False):
            self.logger.info("Saving dataframe in Local and Dropbox")
            if sheetname is not None and filename is not None:
                self.save_pandas_as_excel(dataframe=dataframe,
                                          sheetname=sheetname,
                                          filename=filename,
                                          copy_dropbox=True)
            else:
                self.logger.error("Missing parameters for Dropbox storage")

        # ----------------------------------------------------------------------
        #   GOOGLE CLOUD MYSQL
        # ----------------------------------------------------------------------
        if (self.store_google_cloud_mysql and not ignores.get("google_cloud_mysql", False)) or forces.get("google_cloud_mysql", False):
            self.logger.info("Saving dataframe in Google Cloud MySQL")
            if database_name is not None and table_name is not None:
                self.save_pandas_as_db(database_name=database_name,
                                       table_name=table_name,
                                       dataframe=dataframe)
            else:
                self.logger.error("Missing parameters for database storage")

    def save_file(self, filepath: Path, save_dropbox: bool):

        if save_dropbox:
            destination = self.dropbox_path
            copy_resp = self.upload_file(filepath, destination)
            if copy_resp is not None:
                self.logger.info("File copied to Dropbox!")
