import logging
import json
import uuid
import time
from src.lib.comdirect.access import Access
from src.lib.comdirect.accounts import Accounts
from src.lib.comdirect.depots import Depots
from src.lib.comdirect.orders import Orders


class Session (Access, Accounts, Depots, Orders):

    def __init__(self, access_config, access_userdata, logger_name) -> None:

        self.session_connected = False

        self.client_id = access_userdata["client_id"]
        self.client_secret = access_userdata["client_secret"]
        self.username = access_userdata["account_number"]
        self.pin = access_userdata["pin"]

        self.access_token = None
        self.refresh_token = None
        self.session_id = None
        self.request_id = None
        self.identifier = None
        self.authentication_info = None
        self.challenge_id = None
        self.challenge_type = None

        self.access_config = access_config

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".session"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing access session.")

    def get_session_id(self):
        return uuid.uuid4()

    def get_request_id(self):
        time_miliseconds = int(round(time.time() * 1000))
        time_string = str(time_miliseconds)[-9:]
        return time_string

    def get_challenge_info(self, info):
        authentication_info = json.loads(info)
        challenge_id = authentication_info["id"]
        challenge_type = authentication_info["typ"]

        return challenge_id, challenge_type, authentication_info
