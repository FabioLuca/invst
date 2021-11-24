"""Module for managing configurations which are stored in Json files.
"""

import json
import logging
import inspect
from . import messages as M
from .invst_const import constants as C


class Config:
    """Loads the designated configuration file and parses the content into
    blocks of information (sub-dictionaries).

    Parameters
    ----------
        logger_name: string
            The name for the logger object. The recommendation is to keep a
            single name across the application, so pass here the same used in
            other parts of the application.

    Attributes
    ----------
        filename: `pathlib path`
            File path with the .json file where the configuration is stored. At
            initialization its content is `None`, and the value is updated
            after the call of the method `load_config`.
        json_file: `file object`
            File object where the configuration is stored. At initialization
            its content is `None`, and the value is updated after the call of
            the method `load_config`.
        json_data: `dictionary`
            Configuration dictionary. At initialization its content is `None`,
            and the value is updated after the call of the method `load_config`.

    """

    def __init__(self, logger_name=None):

        self.filename = None
        self.__json_file = None
        self.json_data = None

        self.data = None

        self.data_source_fetch_name = None
        self.data_source_fetch_access_data = None
        self.data_source_fetch_user_data = None

        self.data_source_trade_name = None
        self.data_source_trade_access_data = None
        self.data_source_trade_user_data = None

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.__logger_name = logger_name
        self.__logger = None
        if self.__logger_name is not None:
            self.__logger = logging.getLogger(
                str(self.__logger_name) + ".config")

        if self.__logger is not None:
            self.__logger.info("Initializing configuration")

    def load_config(self, filename):

        flag, level, message = M.get_status("Config_Load_Config", filename)
        if self.__logger is not None:
            self.__logger.info(message)

        self.filename = filename
        self.__json_file = None
        self.json_data = None

        self.load_config_file()

        if filename.stem == "api-cfg":

            # # ----------------------------------------------------------------------
            # #   Configuration for logging parameters. All the parameters defined
            # #   in "logging" on the first level will added with the same name.
            # # ----------------------------------------------------------------------
            # for parameter in self.json_data["logging"]:
            #     vars(self)[parameter] = self.json_data["logging"][parameter]

            # # ----------------------------------------------------------------------
            # #   Configuration related to file paths
            # # ----------------------------------------------------------------------
            # for parameter in self.json_data["paths"]:
            #     vars(self)[parameter] = self.json_data["paths"][parameter]

            # ------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ------------------------------------------------------------------
            self.data_source_fetch_name = self.json_data[
                "api"]["fetching"]["selection"]
            self.data_source_fetch_access_data = self.json_data[
                "api"]["fetching"][self.data_source_fetch_name]["access_data"]
            self.data_source_trade_name = self.json_data[
                "api"]["trading"]["selection"]
            self.data_source_trade_access_data = self.json_data[
                "api"]["trading"][self.data_source_trade_name]["access_data"]

        elif filename.stem == "api-cfg-access":

            if self.data_source_fetch_name is None:
                result = None
                flag = C.FAIL
                level = C.ERROR
                message = "No source of data was define for fetching %s" % (
                    inspect.currentframe().f_code.co_name
                )
                if self.__logger is not None:
                    self.__logger.error(message)
                return result, flag, level, message

            if self.data_source_trade_name is None:
                result = None
                flag = C.FAIL
                level = C.ERROR
                message = "No source of data was define for trading %s" % (
                    inspect.currentframe().f_code.co_name
                )
                if self.__logger is not None:
                    self.__logger.error(message)
                return result, flag, level, message

            # ----------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ----------------------------------------------------------------------
            self.data_source_fetch_user_data = self.json_data[
                "api"]["fetching"][self.data_source_fetch_name]["user_data"]
            self.data_source_trade_user_data = self.json_data[
                "api"]["trading"][self.data_source_trade_name]["user_data"]

        result = None
        flag = C.SUCCESS
        level = C.INFO
        message = "Successful loading of the file %s" % (filename)
        if self.__logger is not None:
            self.__logger.info(message)
        return result, flag, level, message

    def get_dictonary(self):
        """Returns the complete dictionary of configuration"""
        return self.json_data

    def load_config_file(self):
        """Loads the Json file where the configuration is stored and returns
        the content in a dictionary format"""
        with open(self.filename) as self.__json_file:
            self.json_data = json.load(self.__json_file)
