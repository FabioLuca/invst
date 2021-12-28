"""Module for managing the communication to the user."""
import logging
import time
import re
from twilio.rest import Client
from src.lib.invst_const import constants as C
from src.lib import messages as M


class Whatsapp:

    def __init__(self, access_config: dict, access_userdata: dict, logger_name: str) -> None:

        self.access_config = access_config
        self.access_userdata = access_userdata

        self.account_sid = self.access_userdata["account_sid"]
        self.auth_token = self.access_userdata["auth_token"]
        self.from_phone = self.access_config["from_phone"]
        self.to_phone = self.access_config["to_phone"]

        self.count_messages = self.access_config["count_messages"]
        self.tries = self.access_config["request_tries"]
        self.pause = self.access_config["pause_between_tries"]

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".communication"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing communication.")

        self.client = Client(self.account_sid, self.auth_token)

    def clear_string(self, input_string: str, keep_spaces: bool = False, keep_special: bool = False):

        regex_template = '[^a-zA-Z]'
        if keep_spaces:
            regex_template = regex_template + " "
        if keep_special:
            regex_template = regex_template + ":"

        regex = re.compile(regex_template)
        output_string = regex.sub('', input_string)

        return output_string

    def send_message(self, body: str):

        msg_content = self.client.messages.create(
            body=body,
            from_=self.from_phone,
            to=self.to_phone
        )

        if msg_content.error_code == "null":

            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendMessage_Fail")

        else:
            flag, level, message = M.get_status(self.logger_name,
                                                "Comm_SendMessage_Success")

        return msg_content, flag, level, message

    def receive_messages(self, count_limit: int, direction: str = "both"):
        """Get the current received messages (sent to the owner number). The
        result is a list of the last ``count_limit`` messages, each having the
        properties such as:

        1. ``sid``
        2. ``body``: content of the message.
        3. ``date_created``
        4. ``date_updated``
        5. ``to``: phone number which the message was sent to.
        6. ``from_``: phone number which the message was sent from. Note the
           underscore (`_`) symbol at the end.
        7. ``status``
        8. ``num_media``
        9. ``direction``

        They can be accessed for example: :code:`messages[0].body`.

        """
        if direction == "both":
            to_list = None
        elif direction == "received_only":
            to_list = self.from_phone
        elif direction == "sent_only":
            to_list = self.to_phone

        messages = self.client.messages.list(
            limit=count_limit, to=to_list)

        # flag, level, message = M.get_status(self.logger_name,
        #                                     "Comm_ReceiveMessage_Fail")

        flag, level, message = M.get_status(self.logger_name,
                                            "Comm_ReceiveMessage_Success")

        return messages, flag, level, message

    def receive_last_message(self):
        messages, flag, level, message = self.receive_messages(count_limit=1)

        return messages[0], flag, level, message

    def get_response(self, initial_message,
                     maximum_time: float,
                     maximum_positions: int = 10,
                     possible_responses: list = [],
                     case_sensitive: bool = False,
                     clear_response: bool = True,
                     send_feedback: bool = True,
                     verbose: bool = False):

        # ----------------------------------------------------------------------
        #   Prepare the possible expected responses. In case case insensitive
        #   is enabled, then all content will be converted to lower case.
        # ----------------------------------------------------------------------
        if not case_sensitive:
            possible_responses = [each_string.lower()
                                  for each_string in possible_responses]

        message_status = {}

        for j in range(self.tries):

            messages, flag, level, message = self.receive_messages(
                count_limit=self.count_messages, direction="both")

            # print("")
            # print(message_status)
            # for k in range(len(messages)):
            #     print(
            #         f"   {k}   {self.clear_string(input_string=messages[k].body, leave_spaces=False, leave_special=False)[:40]}")

            i_initial = -1
            found_initial_message = False
            response = None

            for i in range(len(messages)-1, -1, -1):

                if messages[i].sid == initial_message.sid:
                    found_initial_message = True
                    i_initial = i
                    initial_message_time = messages[i].date_created
                    if verbose:
                        self.send_message(
                            body=f"I found the question at position: {i_initial}")
                    continue

                if found_initial_message:
                    if i < i_initial:

                        # ------------------------------------------------------
                        #   Get all the necessary info from the message under
                        #   analysis.
                        # ------------------------------------------------------
                        msg_sid = messages[i].sid
                        msg_direction = messages[i].direction
                        msg_response = messages[i].body
                        if clear_response:
                            msg_response = self.clear_string(msg_response)
                        if not case_sensitive:
                            msg_response = msg_response.lower()
                        msg_time = messages[i].date_created
                        time_difference = (
                            msg_time - initial_message_time).total_seconds() / 60

                        if msg_sid not in message_status and msg_direction == "inbound":
                            message_status[msg_sid] = {}
                            message_status[msg_sid]["value"] = msg_response
                            message_status[msg_sid]["status"] = "NEW"

                        if msg_direction == "inbound" and message_status[msg_sid]["status"] == "NEW":

                            if time_difference <= maximum_time:

                                if len(possible_responses) == 0 or msg_response in possible_responses:
                                    message_status[msg_sid]["status"] = "VALID RESPONSE"
                                    if send_feedback:
                                        self.send_message(
                                            body=f"I understood this valid response: '{msg_response}'")
                                    response = messages[i]
                                    break
                                elif send_feedback:
                                    message_status[msg_sid]["status"] = "UNEXPECTED VALUE"
                                    self.send_message(
                                        body=f"Your response was not undestood: '{msg_response}'. I can only understand: {possible_responses}")

                            else:
                                if verbose:
                                    self.send_message(
                                        body=f"Your response was too late.")
                                message_status[msg_sid]["status"] = "TOO LATE"

                if found_initial_message and i < i_initial - maximum_positions:
                    break

            if not found_initial_message and j > 3:
                if send_feedback:
                    self.send_message(
                        body="An error occured. I lost the question ...")
                return None, flag, level, message

            if response is not None:
                break

            if verbose:
                self.send_message(
                    f"Tried to get response: {j+1} / {self.tries}")

            time.sleep(self.pause)

        return response, flag, level, message

    def inquiry(self, question: str,
                maximum_time: float = 10,
                maximum_positions: int = 1,
                possible_responses: list = ["yes", "no"],
                case_sensitive: bool = False,
                clear_response: bool = True,
                send_feedback: bool = True,
                verbose: bool = False):

        question_message, flag, level, message = self.send_message(
            body=question)

        if flag != C.SUCCESS:
            return question_message, flag, level, message

        response, flag, level, message = self.get_response(initial_message=question_message,
                                                           maximum_time=maximum_time,
                                                           maximum_positions=maximum_positions,
                                                           possible_responses=possible_responses,
                                                           case_sensitive=case_sensitive,
                                                           clear_response=clear_response,
                                                           send_feedback=send_feedback,
                                                           verbose=verbose)

        return response, flag, level, message
