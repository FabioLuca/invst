import logging
import pandas as pd
from pathlib import Path
from src.lib import messages as M
from src.lib.config import Config
from src.lib.storage.dropbox import DropboxAPI


class Storage(DropboxAPI):

    def __init__(self, config: Config, logger_name: str) -> None:

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        self.config = config

        # config_base_path = Path.cwd().resolve() / "cfg"
        # config_access_file = config_base_path / "api-cfg.json"
        # config_access_userdata_file = config_base_path / "user" / "api-cfg-access.json"
        # config_local_file = config_base_path / "local" / "local.json"
        # config_parameters_file = config_base_path / "parameters.json"

        # self.config = Config(logger_name=logger_name)
        # self.config.load_config(filename=config_access_file)
        # self.config.load_config(filename=config_access_userdata_file)
        # self.config.load_config(filename=config_local_file)
        # self.config.load_config(filename=config_parameters_file)

        self.save_dropbox = self.config.local_config.get(
            'storage', {}).get('save_dropbox')
        # self.save_dropbox = self.config.local_config["storage"]["save_dropbox"]

        print(self.save_dropbox)

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

    def save_file(self, filepath: Path, save_dropbox: bool):

        if save_dropbox:
            destination = self.config.data_source_storage_access_data["path_balance"]
            copy_resp = self.upload_file(filepath, destination)
            if copy_resp is not None:
                self.logger.info("File copied to Dropbox!")

    def save_pandas_as_excel(self,
                             dataframes: list[pd.DataFrame],
                             sheetsnames: list[str],
                             filename: Path):
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

        if len(dataframes) != len(sheetsnames):
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

        for dataframe, sheetname in zip(dataframes, sheetsnames):
            dataframe.to_excel(excel_writer, sheet_name=sheetname)

        excel_writer.save()

        # ----------------------------------------------------------------------
        #   Saves a copy of the file into Dropbox. The operation is done by
        #   copying the local content to the remote one.
        # ----------------------------------------------------------------------
        if self.save_dropbox:
            destination_dropbox = self.config.data_source_storage_access_data["path_balance"]
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

    def load_file(self, filepath: Path):

        self.download_file()
