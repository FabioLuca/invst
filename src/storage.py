import logging
import pandas as pd
from pathlib import Path
from src.lib import messages as M
from src.lib.config import Config
from src.lib.storage.dropbox import DropboxAPI
from typing import Union


class Storage(DropboxAPI):

    def __init__(self, config: Config, logger_name: str) -> None:

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        self.config = config

        self.save_dropbox = self.config.local_config.get(
            'storage', {}).get('save_dropbox')
        self.load_dropbox = self.config.local_config.get(
            'storage', {}).get('load_dropbox')
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

    def list_files_folder(self, folderpath: Union[Path, str], regex: str):
        if self.load_dropbox:
            files = self.list_files(folderpath=folderpath, regex=regex)
        else:
            files = list(
                filter(Path.is_file, folderpath.glob(f"**/{regex}*")))
            if len(files) < 1:
                return None, None, None, None
        return files, None, None, None

    def save_file(self, filepath: Path, save_dropbox: bool):

        if save_dropbox:
            destination = self.dropbox_path
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
        if self.load_dropbox:
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path
        else:
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
        if self.load_dropbox:
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path
        else:
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
