from datetime import datetime
import json
import requests
import pandas as pd

from src.lib import messages as M


class Accounts:

    def get_accounts_balance(self):
        """Returns the balance for all the accounts.
        """

        today_string = datetime.today().strftime('%Y-%m-%d')

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
        url = self.access_config["url_accounts_balance"]

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'x-http-request-info': (f'{{"clientRequestId":'
                                    f'{{"sessionId":"{self.session_id}",'
                                    f'"requestId":"{self.request_id}"}}}}'),
            'Content-Type': 'application/json',
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        if response.status_code in [500]:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_500_Msg_Err")
            return result, flag, level, message

        if response.text == "":
            response_body_json = {}
        else:
            response_body_json = json.loads(response.text)
        response_headers_json = dict(response.headers)

        if self.logger is not None:
            self.logger.debug(
                "############# Account Balance #############")
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
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Account_Balance_Success")
        else:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Account_Balance_Error",
                (str(response.status_code),
                 response_body_json["messages"]["message"]))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Parse the content from the API into Pandas format
        # ----------------------------------------------------------------------
        list_account_id = []
        list_account_display_id = []
        list_account_iban = []
        list_account_currency = []
        list_account_available_cash_value = []
        list_account_available_cash_unit = []
        list_account_available_cash_euro_value = []
        list_account_available_cash_euro_unit = []
        list_account_balance_value = []
        list_account_balance_unit = []
        list_account_balance_euro_value = []
        list_account_balance_euro_unit = []

        for account_item in response_body_json["values"]:
            account_id = account_item["account"]["accountId"]
            account_display_id = account_item["account"]["accountDisplayId"]
            account_currency = account_item["account"]["currency"]
            account_iban = account_item["account"]["iban"]
            account_available_cash_value = account_item["availableCashAmount"]["value"]
            account_available_cash_unit = account_item["availableCashAmount"]["unit"]
            account_available_cash_euro_value = account_item["availableCashAmountEUR"]["value"]
            account_available_cash_euro_unit = account_item["availableCashAmountEUR"]["unit"]
            account_balance_value = account_item["balance"]["value"]
            account_balance_unit = account_item["balance"]["unit"]
            account_balance_euro_value = account_item["balanceEUR"]["value"]
            account_balance_euro_unit = account_item["balanceEUR"]["unit"]

            list_account_id.append(account_id)
            list_account_display_id.append(account_display_id)
            list_account_currency.append(account_currency)
            list_account_iban.append(account_iban)
            list_account_available_cash_value.append(
                account_available_cash_value)
            list_account_available_cash_unit.append(
                account_available_cash_unit)
            list_account_available_cash_euro_value.append(
                account_available_cash_euro_value)
            list_account_available_cash_euro_unit.append(
                account_available_cash_euro_unit)
            list_account_balance_value.append(account_balance_value)
            list_account_balance_unit.append(account_balance_unit)
            list_account_balance_euro_value.append(account_balance_euro_value)
            list_account_balance_euro_unit.append(account_balance_euro_unit)

        zippedList = list(
            zip(
                list_account_id,
                list_account_display_id,
                list_account_currency,
                list_account_iban,
                list_account_available_cash_value,
                list_account_available_cash_unit,
                list_account_available_cash_euro_value,
                list_account_available_cash_euro_unit,
                list_account_balance_value,
                list_account_balance_unit,
                list_account_balance_euro_value,
                list_account_balance_euro_unit,
            )
        )

        data_output = pd.DataFrame(
            zippedList,
            columns=[
                "Account ID",
                "Account Display ID",
                "Account Currency",
                "IBAN",
                "Available Cash Value",
                "Available Cash Unit",
                "Available Cash Euro Value",
                "Available Cash Euro Unit",
                "Balance Value",
                "Balance Unit",
                "Balance Euro Value",
                "Balance Euro Unit",
            ],
        )

        data_output["Date"] = today_string

        return data_output, flag, level, message
