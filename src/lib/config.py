"""Module for managing configurations which are stored in Json files.
"""

import json
import logging
import inspect
# import glob
from pathlib import Path
from src.lib import messages as M
# from src.lib import constants as C


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

    def __init__(self, logger_name):

        self.filename = None
        self.json_file = None
        self.json_data = None

        self.data = None

        self.api_data = None
        self.user_data = None

        self.data_source_fetch_name = None
        self.data_source_fetch_access_data = None
        self.data_source_fetch_user_data = None

        self.data_source_trade_name = None
        self.data_source_trade_access_data = None
        self.data_source_trade_user_data = None

        self.data_source_wapp_name = None
        self.data_source_wapp_access_data = None
        self.data_source_wapp_user_data = None

        self.data_source_mail_name = None
        self.data_source_mail_access_data = None
        self.data_source_mail_user_data = None

        self.data_source_comm_access_data = None
        self.data_source_comm_user_data = None

        self.data_source_storage_name = None
        self.data_source_storage_access_data = None
        self.data_source_storage_user_data = None

        self.local_config = None

        self.parameters = None

        # ----------------------------------------------------------------------
        #   Shortened name for the variables, so the code looks more clean than
        #   refering to a dictionary. At this point it is done only the
        #   variables initialization.
        # ----------------------------------------------------------------------

        # ---------------- Execution Block -------------------------------------
        self.time_sleep = None
        self.lstm_model_age = None
        self.display_analysis = None
        self.save_analysis = None

        # ---------------- Analysis Block --------------------------------------
        self.analysis_length_pre = None
        self.lstm_sequence_length = None
        self.lstm_prediction_length = None
        self.lstm_number_blocks = None
        self.lstm_number_features = None
        self.lstm_hidden_neurons = None
        self.lstm_epochs = None
        self.lstm_normalization_lower = None
        self.lstm_normalization_upper = None

        # ---------------- Simulation Block ------------------------------------
        self.analysis_length_post = None
        self.initial_value = None
        self.stopgain = None
        self.stoploss = None
        self.operation_cost_fix = None
        self.operation_cost_proportional = None
        self.operation_cost_min = None
        self.operation_cost_max = None
        self.tax_percentage = None

        # ---------------- Report Block ----------------------------------------
        self.filter_in_analysis = None

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".config"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing configuration.")

    def assert_filename(self, filename: Path):
        """Verifies if the file passed for the configuration exists. In case it
        doesn't exist, the application will search for a file with the same name
        and extension, starting from 1 folder above (not more). This is intended
        to support with some operations from the project, where the starting
        folder is different from the main application, for example, creating
        docs in Sphinx.
        """
        foundfiles = None
        if not filename.exists():
            self.logger.info(
                f"File {filename} not found in the expected location! Searching for similar ones.")
            for path in Path('..').rglob(filename.name):
                foundfiles = path
                break
            if foundfiles is None:
                self.logger.info(f"File {filename} is not available!")
            return foundfiles
        self.logger.info(f"Found {filename} in expected location.")
        return filename

    def load_config(self, filename: Path):
        """Loads the content from the configuration file. The 
        """

        filename_original = filename
        filename = self.assert_filename(filename=filename)

        if filename is None:
            flag, level, message = M.get_status(
                self.logger_name, "Config_Load_Fail_Find", filename_original)
            return None, flag, level, message

        flag, level, message = M.get_status(
            self.logger_name, "Config_Load_Config", filename)

        self.filename = filename
        self.json_file = None
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
            try:
                self.api_data = self.json_data["api"]

                self.data_source_fetch_name = self.json_data[
                    "api"]["fetching"]["selection"]
                self.data_source_fetch_access_data = self.json_data[
                    "api"]["fetching"][self.data_source_fetch_name]["access_data"]

                self.data_source_trade_name = self.json_data[
                    "api"]["trading"]["selection"]
                self.data_source_trade_access_data = self.json_data[
                    "api"]["trading"][self.data_source_trade_name]["access_data"]

                self.data_source_wapp_name = self.json_data[
                    "api"]["communicating"]["whatsapp"]["selection"]
                self.data_source_wapp_access_data = self.json_data[
                    "api"]["communicating"]["whatsapp"][self.data_source_wapp_name]["access_data"]

                self.data_source_mail_name = self.json_data[
                    "api"]["communicating"]["email"]["selection"]
                self.data_source_mail_access_data = self.json_data[
                    "api"]["communicating"]["email"][self.data_source_mail_name]["access_data"]

                self.data_source_storage_name = self.json_data[
                    "api"]["storage"]["selection"]
                self.data_source_storage_access_data = self.json_data[
                    "api"]["storage"][self.data_source_storage_name]["access_data"]

                self.data_source_comm_access_data = {
                    "whatsapp": self.data_source_wapp_access_data,
                    "email": self.data_source_mail_access_data
                }

            except KeyError as dictkey:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name, "Config_Load_Fail_Key", str(dictkey))
                return result, flag, level, message

        elif filename.stem == "api-cfg-access":

            if self.data_source_fetch_name is None:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name,
                    "Config_Error_No_Source_Fetching",
                    inspect.currentframe().f_code.co_name)
                return result, flag, level, message

            if self.data_source_trade_name is None:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name,
                    "Config_Error_No_Source_Trading",
                    inspect.currentframe().f_code.co_name)
                return result, flag, level, message

            # ------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ------------------------------------------------------------------
            try:
                self.user_data = self.json_data["api"]

                self.data_source_fetch_user_data = self.json_data[
                    "api"]["fetching"][self.data_source_fetch_name]["user_data"]
                self.data_source_trade_user_data = self.json_data[
                    "api"]["trading"][self.data_source_trade_name]["user_data"]
                self.data_source_wapp_user_data = self.json_data[
                    "api"]["communicating"]["whatsapp"][self.data_source_wapp_name]["user_data"]
                self.data_source_mail_user_data = self.json_data[
                    "api"]["communicating"]["email"][self.data_source_mail_name]["user_data"]
                self.data_source_storage_user_data = self.json_data[
                    "api"]["storage"][self.data_source_storage_name]["user_data"]

                self.data_source_comm_user_data = {
                    "whatsapp": self.data_source_wapp_user_data,
                    "email": self.data_source_mail_user_data
                }

            except KeyError as dictkey:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name, "Config_Load_Fail_Key", str(dictkey))
                return result, flag, level, message

        elif filename.stem == "local":
            # ------------------------------------------------------------------
            #   Configuration related to local parameters.
            # ------------------------------------------------------------------
            self.local_config = self.json_data

        elif filename.stem == "parameters":
            # ------------------------------------------------------------------
            #   Configuration related to calculation parameters.
            # ------------------------------------------------------------------
            self.parameters = self.json_data

            # ------------------------------------------------------------------
            #   Shortened name for the variables, so the code looks more clean
            #   than refering to a dictionary. At this point it is done only the
            #   variables initialization.
            # ------------------------------------------------------------------

            # ---------------- Execution Block ---------------------------------
            self.time_sleep = self.parameters["execution"]["time_sleep"]["value"]
            self.lstm_model_age = self.parameters["execution"]["lstm_model_age"]["value"]
            self.display_analysis = self.parameters["execution"]["display_analysis"]["value"]
            self.save_analysis = self.parameters["execution"]["save_analysis"]["value"]

            # ---------------- Analysis Block ----------------------------------
            self.analysis_length_pre = self.parameters["analysis"]["length_analysis"]["value"]
            self.lstm_sequence_length = self.parameters["analysis"]["lstm_sequence_length"]["value"]
            self.lstm_prediction_length = self.parameters["analysis"]["lstm_prediction_length"]["value"]
            self.lstm_number_blocks = self.parameters["analysis"]["lstm_number_blocks"]["value"]
            self.lstm_number_features = self.parameters["analysis"]["lstm_number_features"]["value"]
            self.lstm_hidden_neurons = self.parameters["analysis"]["lstm_hidden_neurons"]["value"]
            self.lstm_epochs = self.parameters["analysis"]["lstm_epochs"]["value"]
            self.lstm_normalization_lower = self.parameters[
                "analysis"]["lstm_normalization_lower"]["value"]
            self.lstm_normalization_upper = self.parameters[
                "analysis"]["lstm_normalization_upper"]["value"]

            # ---------------- Simulation Block --------------------------------
            self.analysis_length_post = self.parameters["simulation"]["length_analysis"]["value"]
            self.initial_value = self.parameters["simulation"]["starting_value"]["value"]
            self.stopgain = self.parameters["simulation"]["stopgain"]["value"]
            self.stoploss = self.parameters["simulation"]["stoploss"]["value"]
            self.operation_cost_fix = self.parameters["simulation"]["operation_cost_fix"]["value"]
            self.operation_cost_proportional = self.parameters[
                "simulation"]["operation_cost_proportional"]["value"]
            self.operation_cost_min = self.parameters["simulation"]["operation_cost_min"]["value"]
            self.operation_cost_max = self.parameters["simulation"]["operation_cost_max"]["value"]
            self.tax_percentage = self.parameters["simulation"]["tax_percentage"]["value"]

            # ---------------- Report Block ------------------------------------
            self.filter_in_analysis = self.parameters["report"]["filter_in_analysis"]["value"]

        else:
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "Config_Load_Fail", filename)
            return result, flag, level, message

        result = None
        flag, level, message = M.get_status(
            self.logger_name, "Config_Load_Success", filename)
        return result, flag, level, message

    def get_dictionary(self):
        """Returns the complete dictionary of configuration"""
        return self.json_data

    def load_config_file(self):
        """Loads the Json file where the configuration is stored and returns
        the content in a dictionary format"""
        with open(self.filename, encoding="utf-8") as self.json_file:
            self.json_data = json.load(self.json_file)

    def get_key(self, file, levels, backup):

        if file == "local":
            temp = self.local_config
        elif file == "user":
            temp = self.user_data
        elif file == "parameters":
            temp = self.parameters
        elif file == "api-cfg":
            temp = self.api_data
        else:
            return backup

        for i in range(len(levels)):
            if i == len(levels):
                temp = temp.get(levels[i], backup)
            else:
                temp = temp.get(levels[i], {})

        return temp
