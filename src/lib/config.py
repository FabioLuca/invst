"""-----------------------------------------------------------------------------
    MODULE CONFIG
-----------------------------------------------------------------------------"""
import json
import logging
import inspect
import src.lib.invst_const.constants as C


class Config:
    """Loads the designated configuration file and parses the content into
    blocks of information (sub-dictionaries)"""

    def __init__(self, logger_name=None):

        self.filename = None
        self.__json_file = None
        self.json_data = None

        self.data = None
        self.data_source_name = None
        self.data_source_access_data = None
        self.data_source_user_data = None

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.__logger_name = logger_name
        self.__logger = None
        if self.__logger_name is not None:
            self.__logger = logging.getLogger(str(self.__logger_name) + ".config")

        if self.__logger is not None:
            self.__logger.info("Initializing configuration")

    def load_config(self, filename):

        if self.__logger is not None:
            self.__logger.info("Loading the configuration from %s", filename)

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

            # ----------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ----------------------------------------------------------------------
            self.data_source_name = self.json_data["data_source"]["name"]
            self.data_source_access_data = self.json_data["data_source"][
                self.data_source_name
            ]["access_data"]

        elif filename.stem == "api-cfg-access":

            if self.data_source_name is None:
                result = None
                flag = C.FAIL
                level = C.ERROR
                message = "No source of data was define for %s" % (
                    inspect.currentframe().f_code.co_name
                )
                if self.__logger is not None:
                    self.__logger.error(message)
                return result, flag, level, message

            # ----------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ----------------------------------------------------------------------
            self.data_source_user_data = self.json_data["data_source"][
                self.data_source_name
            ]["user_data"]

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
