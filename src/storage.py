import logging
import pandas as pd
from pathlib import Path
from src.lib import messages as M
from src.lib.config import Config
from src.lib.storage.dropbox import DropboxAPI as Dropbox
from src.lib.storage.googlecloud_mysql import GoogleCloudMySQL
from typing import Union


class Storage(Dropbox, GoogleCloudMySQL):

    def __init__(self, config: Config, logger_name: str) -> None:

        self.cnxn = None
        self.cursor = None
        self.config_db = None

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        self.config = config

        self.store_local = self.config.local_config.get(
            'storage', {}).get('store', {}).get('local', False)
        self.store_dropbox = self.config.local_config.get(
            'storage', {}).get('store', {}).get('dropbox', False)
        self.store_google_cloud_mysql = self.config.local_config.get(
            'storage', {}).get('store', {}).get('google_cloud_mysql', False)
        self.load = self.config.local_config.get(
            'storage', {}).get('load')
        self.data_storage = self.config.local_config.get(
            "data_storage", None)
        if self.data_storage is not None:
            self.data_storage = Path(self.data_storage).resolve()
        self.temp_folder = self.config.local_config.get(
            'paths', {}).get("temp_storage", None)
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

    def list_files_folder(self, folderpath: Union[Path, str], criteria: str):
        if self.load == "dropbox":
            files = self.list_files(folderpath=folderpath, criteria=criteria)
        elif self.load == "local":
            files = list(
                filter(Path.is_file, folderpath.glob(f"**/{criteria}*")))
            if len(files) < 1:
                return None, None, None, None
        return files, None, None, None

    def store_pandas(self,
                     dataframe: Union[pd.DataFrame, list[pd.DataFrame]],
                     sheetname: Union[str, list[str]] = None,
                     filename: Path = None,
                     database_name: str = None,
                     table_name: str = None):

        self.logger.info("Storing dataframe")

        # ----------------------------------------------------------------------
        #   LOCAL FOLDER
        # ----------------------------------------------------------------------
        if self.store_local and not self.store_dropbox:
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
        if self.store_local and self.store_dropbox:
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
        if self.store_google_cloud_mysql:
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

    def save_pandas_as_excel(self,
                             dataframe: Union[pd.DataFrame, list[pd.DataFrame]],
                             sheetname: Union[str, list[str]],
                             filename: Path,
                             copy_dropbox: bool = False):
        """
        """
        # ----------------------------------------------------------------------
        #   Verifies that the necessary information for execution is valid.
        # ----------------------------------------------------------------------
        if filename.suffix != ".xlsx":
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_Error_BadExtension")
            return result, flag, level, message

        if isinstance(dataframe, pd.DataFrame):
            dataframe = [dataframe]

        if isinstance(sheetname, str):
            sheetname = [sheetname]

        if len(dataframe) != len(sheetname):
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_Error_BadListSizes")
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Creates the path if necessary and stores the content from Pandas
        #   as Excel.
        # ----------------------------------------------------------------------
        folder = filename.parents[0]
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)

        excel_writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        for dataframe_item, sheetname_item in zip(dataframe, sheetname):
            dataframe_item.to_excel(excel_writer, sheet_name=sheetname_item)

        excel_writer.save()

        # ----------------------------------------------------------------------
        #   Saves a copy of the file into Dropbox. The operation is done by
        #   copying the local content to the remote one.
        # ----------------------------------------------------------------------
        if copy_dropbox:
            destination_dropbox = self.dropbox_path
            copy_resp = self.upload_file(filename, destination_dropbox)
            if copy_resp is not None:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name, "Storage_Success_Dropbox", destination_dropbox)

        # ----------------------------------------------------------------------
        #   Return the results
        # ----------------------------------------------------------------------
        result = None
        flag, level, message = M.get_status(
            self.logger_name, "Storage_Success", filename)
        return result, flag, level, message

    def load_pandas_from_csv(self,
                             relative_path: Union[Path, str]):
        """
        """
        # ----------------------------------------------------------------------
        #   Defines the source of the file depending on the configuration from
        #   the user.
        # ----------------------------------------------------------------------
        if self.load == "dropbox":
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path
        elif self.load == "local":
            filename = relative_path

        # ----------------------------------------------------------------------
        #   Verifies that the necessary information for execution is valid.
        # ----------------------------------------------------------------------
        if filename.suffix != ".csv":
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_LoadError_BadExtension")
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Loads the
        # ----------------------------------------------------------------------
        dataframe = pd.read_csv(filename,
                                header=0,
                                quotechar='"',
                                skipinitialspace=True,
                                decimal=",",
                                delimiter=';',
                                thousands='.',
                                parse_dates=[1],
                                )

        flag, level, message = M.get_status(
            self.logger_name, "Storage_LoadSuccess", filename)

        return dataframe, flag, level, message

    def load_pandas_from_excel(self,
                               relative_path: Union[Path, str],
                               sheetname: str):
        """
        """
        # ----------------------------------------------------------------------
        #   Defines the source of the file depending on the configuration from
        #   the user.
        # ----------------------------------------------------------------------
        if self.load == "dropbox":
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path
        elif self.load == "local":
            filename = relative_path

        # ----------------------------------------------------------------------
        #   Verifies that the necessary information for execution is valid.
        # ----------------------------------------------------------------------
        if filename.suffix != ".xlsx":
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_LoadError_BadExtension")
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Loads the
        # ----------------------------------------------------------------------
        dataframe = pd.read_excel(
            filename, sheet_name=sheetname)

        flag, level, message = M.get_status(
            self.logger_name, "Storage_LoadSuccess", filename)

        return dataframe, flag, level, message

    def load_file(self, filepath: Path):

        self.download_file()
