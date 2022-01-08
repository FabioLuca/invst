import logging
import json
import uuid
import time
import requests
from src.lib import messages as M
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

        self.order_challenge_id = None
        self.order_challenge_type = None
        self.order_authentication_info = None

        self.depot_id = None

        self.access_config = access_config

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".session"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing access session.")

    def basic_request(self,
                      type_req: str,
                      url: str,
                      payload: dict,
                      header_type: str,
                      request_name: str,
                      url_replacements: dict = None):

        self.logger.info(f"Executing request {request_name}.")

        if url_replacements is not None:
            for item in url_replacements:
                url = url.replace(f"[{item}]", url_replacements[item])

        if header_type == "Standard":
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'x-http-request-info': (f'{{"clientRequestId":'
                                        f'{{"sessionId":"{self.session_id}",'
                                        f'"requestId":"{self.request_id}"}}}}'),
                'Content-Type': 'application/json',
            }
        elif header_type == "TAN_Order":
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
                'x-http-request-info': (f'{{"clientRequestId":'
                                        f'{{"sessionId":"{self.session_id}",'
                                        f'"requestId":"{self.request_id}"}}}}'),
                'Content-Type': 'application/json',
                # 'x-once-authentication': 'TAN_FREI',
                'x-once-authentication-info': f'{{"id":"{self.order_challenge_id}"}}',
                'x-once-authentication': 'TAN_FREI',
            }

        response = requests.request(
            type_req, url, headers=headers, data=payload)

        # ----------------------------------------------------------------------
        #   Catch all the negative responses.
        # ----------------------------------------------------------------------
        if response.status_code in [500]:
            result = (response, None, None)
            flag, level, message = M.get_status(
                self.logger_name, "API_500_Msg_Err")

        elif response.status_code in [401]:
            result = (response, None, None)
            flag, level, message = M.get_status(
                self.logger_name, "API_401_Msg_Err")

        elif response.status_code in [422]:
            result = (response, None, None)

            if response.text == "":
                response_body_json = {}
            else:
                response_body_json = json.loads(response.text)

            if response_body_json["messages"][0]["key"] == "fehler-ausmachender-betrag-ist-hoeher-als-verf-betrag":
                flag, level, message = M.get_status(
                    self.logger_name, "API_422_Msg_Err_NoFundsAvailable")
            elif response_body_json["messages"][0]["key"] == "fehler-keine-handelswerte-ermittelbar":
                flag, level, message = M.get_status(
                    self.logger_name, "API_422_Msg_Err_NoTradingValues")
            elif response_body_json["messages"][0]["key"] == "fehler_unsupported_ordertyp":
                flag, level, message = M.get_status(
                    self.logger_name, "API_422_Msg_Err_UnsupportedOrderType")
            else:
                flag, level, message = M.get_status(
                    self.logger_name, "API_422_Msg_Err", (response.text))

        # ----------------------------------------------------------------------
        #   Threats the positive response.
        # ----------------------------------------------------------------------
        elif response.status_code in [200, 201, 204]:

            if response.text == "":
                response_body_json = {}
            else:
                response_body_json = json.loads(response.text)
            response_headers_json = dict(response.headers)

            if self.logger is not None:
                self.logger.debug(
                    f"############# {request_name} #############")
                self.logger.debug("URL: %s", url)
                self.logger.debug("Payload: %s", json.dumps(
                    payload, indent=4, sort_keys=True))
                self.logger.debug("Headers: %s", json.dumps(
                    headers, indent=4, sort_keys=True))
                self.logger.debug("Status code: %s", response.status_code)
                self.logger.debug("Response body: %s", json.dumps(
                    response_body_json, indent=4, sort_keys=True))
                self.logger.debug("Response headers: %s", json.dumps(
                    response_headers_json, indent=4, sort_keys=True))

            result = (response, response_body_json, response_headers_json)
            flag, level, message = M.get_status(
                self.logger_name, "API_200_Success")

        # ----------------------------------------------------------------------
        #   Unknown error.
        # ----------------------------------------------------------------------
        else:
            result = (response, None, None)
            flag, level, message = M.get_status(
                self.logger_name, "API_Other_Errors")

        return result, flag, level, message

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
