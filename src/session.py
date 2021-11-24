from .lib import messages as M
import requests
import logging
import json
import uuid
import datetime
import time


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
        self.__authentication_info = None
        self.__challenge_id = None
        self.__challenge_type = None

        # self.__source = source
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
        #   2.1 OAuth2 Resource Owner Password Credentials Flow
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.__access_config["url_oauth_token"]
        payload = f"client_id={self.__client_id}&client_secret={self.__client_secret}&grant_type=password&username={self.__username}&password={self.__pin}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        print("---- 2.1 --------------------------------------")
        print(json.dumps(response_body_json, indent=4, sort_keys=True))
        print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            self.__access_token = response_body_json["access_token"]
            self.__refresh_token = response_body_json["refresh_token"]

            result = response
            flag, level, message = M.get_status("API_Trade_Oauth_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response
            flag, level, message = M.get_status("API_Trade_Oauth_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.2 Session-Status
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.__access_config["url_session"]

        self.__session_id = self.get_session_id()
        self.__request_id = self.get_request_id()

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__access_token}',
            'x-http-request-info': f'{{"clientRequestId":{{"sessionId":"{self.__session_id}","requestId":"{self.__request_id}"}}}}',
            'Content-Type': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        response_body_json = json.loads(response.text)
        response_body_json = response_body_json[0]
        response_headers_json = dict(response.headers)

        print("---- 2.2 --------------------------------------")
        print(json.dumps(response_body_json, indent=4, sort_keys=True))
        print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            self.__identifier = response_body_json["identifier"]

            result = response
            flag, level, message = M.get_status("API_Trade_Ident_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response
            flag, level, message = M.get_status("API_Trade_Ident_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.3 System validation of session TAN
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.__access_config["url_session_validate"]
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
            'Content-Type': 'application/json',
            # 'Cookie': 'qSession=22608551.eb2b00043f94633a8bb8b20'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        print("---- 2.3 --------------------------------------")
        print(json.dumps(response_body_json, indent=4, sort_keys=True))
        print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            info = response_headers_json["x-once-authentication-info"]
            (self.__challenge_id,
             self.__challenge_type,
             self.__authentication_info) = self.get_challenge_info(info)

            result = response
            flag, level, message = M.get_status("API_Trade_Validate_Success")
            if self.__logger is not None:
                self.__logger.info(message)
        else:
            result = response
            flag, level, message = M.get_status("API_Trade_Validate_Error")
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.4 Activation of a session TAN
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.__access_config["url_session_tan"]
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
            'Content-Type': 'application/json',
            'x-once-authentication-info': f'{{"id":"{self.__challenge_id}"}}',
            'x-once-authentication': '',
            # 'Cookie': 'qSession=22608551.ce1bae085773e7f8941cb9f'
        }

        response = requests.request(
            "PATCH", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        print("---- 2.4 --------------------------------------")
        print(json.dumps(response_body_json, indent=4, sort_keys=True))
        print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        time.sleep(8)

        # ----------------------------------------------------------------------
        #   2.5 OAuth2 CD Secondary-Flow
        # ----------------------------------------------------------------------
        url = self.__access_config["url_oauth_token"]

        payload = f"client_id={self.__client_id}&client_secret={self.__client_secret}&grant_type=cd_secondary&token={self.__access_token}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            # 'Cookie': 'qSession=22608551.ce1bae085773e7f8941cb9f'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        print("---- 2.5 --------------------------------------")
        print(json.dumps(response_body_json, indent=4, sort_keys=True))
        print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        return result, flag, level, message

    def get_session_id(self):
        return uuid.uuid4()

    def get_request_id(self):
        return datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")

    def get_challenge_info(self, info):
        authentication_info = json.loads(info)
        challenge_id = authentication_info["id"]
        challenge_type = authentication_info["typ"]

        return challenge_id, challenge_type, authentication_info
