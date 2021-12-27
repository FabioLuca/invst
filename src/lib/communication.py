from twilio.rest import Client
import logging
from src.lib import messages as M


class Whatsapp:

    def __init__(self, access_config: dict, access_userdata: dict, logger_name: str) -> None:

        self.access_config = access_config
        self.access_userdata = access_userdata

        self.account_sid = self.access_userdata["account_sid"]
        self.auth_token = self.access_userdata["auth_token"]
        self.from_phone = self.access_config["from_phone"]
        self.to_phone = self.access_config["to_phone"]

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".communication"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing communication.")

        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, body: str):

        message = self.client.messages.create(
            body=body,
            from_=self.from_phone,
            to=self.to_phone
        )

        if message.error_code == "null":

            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendMessage_Fail")

        else:
            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendMessage_Success")

        return message, flag, level, message

    def receive_messages(self, count_limit: int):
        """Get the current received messages (sent to the owner number). The
        result is a list of the last ``count_limit`` messages, each having the
        properties such as:

        1. ``sid``
        2. ``body``: content of the message.
        3. ``date_created``
        4. ``date_updated``

        They can be accessed for example: :code:`messages[0].body`.

        """
        messages = self.client.messages.list(
            limit=count_limit, to=self.from_phone)

        # flag, level, message = M.get_status(self.logger_name,
        #                                     "Comm_ReceiveMessage_Fail")

        flag, level, message = M.get_status(self.logger_name,
                                            "Comm_ReceiveMessage_Success")

        return messages, flag, level, message

    def receive_last_message(self):
        messages, flag, level, message = self.receive_messages(count_limit=1)

        return messages[0], flag, level, message
