"""Module for managing the communication to the user."""
import logging
from pathlib import Path
from src.lib.config import Config
from src.lib.communication.mail import Mail
from src.lib.communication.mail_formatter import MailFormatter
from src.lib.communication.whatsapp import Whatsapp


class Communication (Whatsapp, Mail, MailFormatter):

    def __init__(self, access_config: dict, access_userdata: dict, logger_name: str) -> None:

        self.access_config = access_config
        self.access_userdata = access_userdata

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        config_base_path = Path.cwd().resolve() / "cfg"
        config_local_file = config_base_path / "local" / "local.json"
        config_parameters_file = config_base_path / "parameters.json"

        self.config = Config(logger_name=logger_name)
        self.config.load_config(filename=config_local_file)
        self.config.load_config(filename=config_parameters_file)

        self.wapp_account_sid = self.access_userdata["whatsapp"]["account_sid"]
        self.wapp_auth_token = self.access_userdata["whatsapp"]["auth_token"]
        self.wapp_from_phone = self.access_userdata["whatsapp"]["from_phone"]
        self.wapp_to_phone = self.access_userdata["whatsapp"]["to_phone"]
        self.wapp_count_messages = self.access_config["whatsapp"]["count_messages"]
        self.wapp_tries = self.access_config["whatsapp"]["request_tries"]
        self.wapp_pause = self.access_config["whatsapp"]["pause_between_tries"]

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".communication"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing communication.")

        self.wapp_initialize()
