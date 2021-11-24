from .lib import messages as M
import requests
import logging
import json
import uuid
import datetime


class Session:

    def __init__(self, source, access_config, access_userdata, logger_name=None) -> None:

        self.__client_id = access_userdata["client_id"]
        self.__client_secret = access_userdata["client_secret"]
        self.__username = access_userdata["account_number"]
        self.__pin = access_userdata["pin"]

        self.__access_token = None
        self.__refresh_token = None
        self.__session_id = None
        self.__request_id = None
        self.__identifier = None

        #self.__source = source
        self.__access_config = access_config

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.__logger_name = logger_name
        self.__logger = None
        if self.__logger_name is not None:
            self.__logger = logging.getLogger(
                str(self.__logger_name) + ".session")

        if self.__logger is not None:
            self.__logger.info("Initializing access session.")

    def connect(self):

        # ----------------------------------------------------------------------
        #   First step: Post the user information
        # ----------------------------------------------------------------------
        url = self.__access_config["url_oauth_token"]
        payload = f"client_id={self.__client_id}&client_secret={self.__client_secret}&grant_type=password&username={self.__username}&password={self.__pin}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = json.loads(response.text)

        #print("---- 1 --------------------------------------")
        #print(json.dumps(response_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            self.__access_token = response_json["access_token"]
            self.__refresh_token = response_json["refresh_token"]

            result = response_json
            flag, level, message = M.get_status("API_Trade_Oauth_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response.text
            flag, level, message = M.get_status("API_Trade_Oauth_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Second step
        # ----------------------------------------------------------------------
        url = self.__access_config["url_session"]

        self.__session_id = self.__get_session_id()
        self.__request_id = self.__get_request_id()

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__access_token}',
            'x-http-request-info': f'{{"clientRequestId":{{"sessionId":"{self.__session_id}","requestId":"{self.__request_id}"}}}}',
            'Content-Type': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_json = json.loads(response.text)

        # print("---- 2 --------------------------------------")
        # print(response.text)
        # print(response.status_code)

        # print(json.dumps(response_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            self.__identifier = response_json["identifier"]

            result = response_json
            flag, level, message = M.get_status("API_Trade_Ident_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response.text
            flag, level, message = M.get_status("API_Trade_Ident_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Third step - Validate session
        # ----------------------------------------------------------------------
        url = self.__access_config["url_session_validate"]
        #url = "https://api.comdirect.de/api/session/clients/user/v1/sessions/F6D3F5F6BF4E4A758063E75135C120A6/validate"
        url = url.replace("[IDENTIFIER]", self.__identifier)

        payload = json.dumps({
            "identifier": f"{self.__identifier}",
            "sessionTanActive": True,
            "activated2FA": True
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__access_token}',
            'x-http-request-info': f'{{"clientRequestId":{{"sessionId":"{self.__session_id}","requestId":"{self.__request_id}"}}}}',
            # 'x-http-request-info': '{"clientRequestId":{"sessionId":"34d0a0ba-3115-bcb0-3501-82619c482730","requestId":"691878198"}}',
            'Content-Type': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = json.loads(response.text)

        print("---- 3 --------------------------------------")

        print(json.dumps(response_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            self.__identifier = response_json["identifier"]

            result = response_json
            flag, level, message = M.get_status("API_Trade_Validate_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response.text
            flag, level, message = M.get_status("API_Trade_Validate_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        return response_json

    def get_session_id(self):
        self.__session_id = uuid.uuid4()

    def get_request_id(self):
        self.__request_id = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")
