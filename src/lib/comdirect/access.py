import json
import requests
from src.lib import messages as M


class Access:

    def connect(self):

        flag, level, message = M.get_status(
            self.logger_name, "API_Trade_Initialization")

        # ----------------------------------------------------------------------
        #   2.1 OAuth2 Resource Owner Password Credentials Flow
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.access_config["url_oauth_token"]
        payload = (f"client_id={self.client_id}&"
                   f"client_secret={self.client_secret}&"
                   f"grant_type=password&username={self.username}&"
                   f"password={self.pin}")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        self.logger.debug("############# 2.1 #############")
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

        if response.status_code in [200, 201]:
            self.access_token = response_body_json["access_token"]
            self.refresh_token = response_body_json["refresh_token"]

            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Oauth_Success")

        else:
            result = response
            flag, level, message = M.get_status(self.logger_name, "API_Trade_Oauth_Error", (str(
                response.status_code), response_body_json["messages"]["message"]))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.2 Session-Status
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.access_config["url_session"]

        self.session_id = self.get_session_id()
        self.request_id = self.get_request_id()

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'x-http-request-info': (f'{{"clientRequestId":'
                                    f'{{"sessionId":"{self.session_id}",'
                                    f'"requestId":"{self.request_id}"}}}}'),
            'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        response_body_json = json.loads(response.text)
        response_body_json = response_body_json[0]
        response_headers_json = dict(response.headers)

        self.logger.debug("############# 2.2 #############")
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

        if response.status_code in [200, 201]:
            self.identifier = response_body_json["identifier"]

            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Ident_Success")
        else:
            result = response
            flag, level, message = M.get_status(self.logger_name, "API_Trade_Ident_Error", (str(
                response.status_code), response_body_json["messages"]["message"]))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.3 System validation of session TAN
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.access_config["url_session_validate"]
        url = url.replace("[IDENTIFIER]", self.identifier)

        #self.request_id = self.get_request_id()

        payload = json.dumps({
            "identifier": f"{self.identifier}",
            "sessionTanActive": True,
            "activated2FA": True
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'x-http-request-info': (f'{{"clientRequestId":'
                                    f'{{"sessionId":"{self.session_id}",'
                                    f'"requestId":"{self.request_id}"}}}}'),
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        self.logger.debug("############# 2.3 #############")
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

        if response.status_code in [200, 201]:
            info = response_headers_json["x-once-authentication-info"]
            (self.challenge_id,
             self.challenge_type,
             self.authentication_info) = self.get_challenge_info(info)

            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Validate_Success")

        else:
            result = response
            flag, level, message = M.get_status(self.logger_name, "API_Trade_Validate_Error", (str(
                response.status_code), response_body_json["messages"]["message"]))
            return result, flag, level, message

        sec = input('Tap enter after the TAN approval.\n')

        # ----------------------------------------------------------------------
        #   2.4 Activation of a session TAN
        # ----------------------------------------------------------------------
        response_body_json = None
        response_headers_json = None

        url = self.access_config["url_session_tan"]
        url = url.replace("[IDENTIFIER]", self.identifier)

        #self.request_id = self.get_request_id()

        payload = json.dumps({
            "identifier": f"{self.identifier}",
            "sessionTanActive": True,
            "activated2FA": True
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'x-http-request-info': (f'{{"clientRequestId":'
                                    f'{{"sessionId":"{self.session_id}",'
                                    f'"requestId":"{self.request_id}"}}}}'),
            'Content-Type': 'application/json',
            'x-once-authentication-info': f'{{"id":"{self.challenge_id}"}}',
            'x-once-authentication': '',
        }

        response = requests.request(
            "PATCH", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        self.logger.debug("############# 2.4 #############")
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

        # print("---- 2.4 --------------------------------------")
        # print(json.dumps(response_body_json, indent=4, sort_keys=True))
        # print(json.dumps(response_headers_json, indent=4, sort_keys=True))

        if response.status_code in [200, 201]:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Activate_TAN_Success")
        else:
            result = response
            flag, level, message = M.get_status(
                self.logger_name,
                "API_Trade_Activate_TAN_Error",
                (str(response.status_code),
                 str(
                    response_body_json["messages"]["message"])
                 ))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   2.5 OAuth2 CD Secondary-Flow
        # ----------------------------------------------------------------------
        url = self.access_config["url_oauth_token"]
        payload = (f"client_id={self.client_id}&"
                   f"client_secret={self.client_secret}&"
                   f"grant_type=cd_secondary&token={self.access_token}")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        self.logger.debug("############# 2.5 #############")
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

        if response.status_code in [200, 201]:
            self.access_token = response_body_json["access_token"]
            self.refresh_token = response_body_json["refresh_token"]

            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Oauth_2Flow_Success")

        else:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Oauth_2Flow_Error", (str(
                    response.status_code), response_body_json["messages"]["message"]))
            return result, flag, level, message

        flag, level, message = M.get_status(
            self.logger_name, "API_Trade_Authentication_Success")

        self.session_connected = True

        return result, flag, level, message

    def revoke_token(self):
        """Revoke the current token (session).
        """

        # ----------------------------------------------------------------------
        #   Verifies first if there is a valid session. If not, then leaves the
        #   execution.
        # ----------------------------------------------------------------------
        if not self.session_connected:
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_No_Active_Session")
            return None, flag, level, message

        # ----------------------------------------------------------------------
        #   Executes the command to the API.
        # ----------------------------------------------------------------------
        url = self.access_config["url_session_revoke"]

        payload = ""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.request(
            "DELETE", url, headers=headers, data=payload)

        if response.text == "":
            response_body_json = {}
        else:
            response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        self.logger.debug(
            "############# Revoke Token #############")
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
