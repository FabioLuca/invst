from datetime import datetime
import json
import requests
import pandas as pd

from src.lib import messages as M
from src.lib import constants as C


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
        (result, response_body_json, response_headers_json), flag, level, message = self.basic_request(
            type_req="GET",
            url=self.access_config["url_accounts_balance"],
            payload={},
            header_type="Standard",
            request_name="Account Balance",
            url_replacements=None)

        if flag != C.SUCCESS:
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
