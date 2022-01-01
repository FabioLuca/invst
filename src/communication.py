"""Module for managing the communication to the user."""
import logging
from src.lib_communication.mail import Mail
from src.lib_communication.whatsapp import Whatsapp


class Communication (Whatsapp, Mail):

    def __init__(self, access_config: dict, access_userdata: dict, logger_name: str) -> None:

        self.access_config = access_config
        self.access_userdata = access_userdata

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
