import logging
import pandas as pd
from pathlib import Path
from src.lib import messages as M
from typing import Union


class PandasOperations:

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
                             relative_path: Union[Path, str],
                             load_dropbox: bool = False):
        """
        """
        # ----------------------------------------------------------------------
        #   Defines the source of the file depending on the configuration from
        #   the user.
        # ----------------------------------------------------------------------
        filename = relative_path

        if load_dropbox:
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path

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
                               sheetname: str,
                               load_dropbox: bool = False):
        """
        """
        # ----------------------------------------------------------------------
        #   Defines the source of the file depending on the configuration from
        #   the user.
        # ----------------------------------------------------------------------
        filename = relative_path

        if load_dropbox:
            destination_folder = Path.cwd().resolve() / self.temp_folder
            self.download_file(file=relative_path,
                               destination_folder=destination_folder)
            dropbox_path_rel = self.dropbox_path
            if dropbox_path_rel[0] == "/" or dropbox_path_rel[0] == "\\":
                dropbox_path_rel = dropbox_path_rel[1:]
            filename = destination_folder / dropbox_path_rel / relative_path

        # ----------------------------------------------------------------------
        #   Verifies that the necessary information for execution is valid.
        # ----------------------------------------------------------------------
        if filename.suffix != ".xlsx":
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_LoadError_BadExtension")
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Loads the data. Checks first if the sheet is available, otherwise
        #   returns an error.
        # ----------------------------------------------------------------------
        tabs = pd.ExcelFile(filename).sheet_names
        if sheetname in tabs:
            dataframe = pd.read_excel(
                filename, sheet_name=sheetname)
        else:
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Storage_LoadError_MissingSheet")
            return result, flag, level, message

        flag, level, message = M.get_status(
            self.logger_name, "Storage_LoadSuccess", filename)

        return dataframe, flag, level, message
