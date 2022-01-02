from datetime import datetime
import json
import requests
import pandas as pd

from src.lib import messages as M


class Depots:

    def get_depots(self):
        """Returns the information for all the depots.
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
        url = self.access_config["url_depots"]

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
                "############# Depots #############")
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
                self.logger_name, "API_Trade_Depots_Success")
        else:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Depots_Error",
                (str(response.status_code),
                 response_body_json["messages"]["message"]))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Parse the content from the API into Pandas format
        # ----------------------------------------------------------------------
        list_depot_id = []
        list_depot_display_id = []
        list_depot_type = []
        list_depot_holder_name = []
        list_default_settlement_account_id = []
        list_client_id = []

        for depot_item in response_body_json["values"]:
            depot_id = depot_item["depotId"]
            depot_display_id = depot_item["depotDisplayId"]
            depot_type = depot_item["depotType"]
            depot_holder_name = depot_item["holderName"]
            default_settlement_account_id = depot_item["defaultSettlementAccountId"]
            client_id = depot_item["clientId"]

            list_depot_id.append(depot_id)
            list_depot_display_id.append(depot_display_id)
            list_depot_type.append(depot_type)
            list_depot_holder_name.append(depot_holder_name)
            list_default_settlement_account_id.append(
                default_settlement_account_id)
            list_client_id.append(client_id)

        zippedList = list(
            zip(
                list_depot_id,
                list_depot_display_id,
                list_depot_type,
                list_depot_holder_name,
                list_default_settlement_account_id,
                list_client_id,
            )
        )

        data_output = pd.DataFrame(
            zippedList,
            columns=[
                "Depot ID",
                "Depot Display ID",
                "Depot Type",
                "Holder Name",
                "Settlement account ID",
                "Client ID",
            ],
        )

        data_output["Date"] = today_string

        return data_output, flag, level, message

    def get_depot_position(self, depot_id):
        """Returns the position from a depot.
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
        url = self.access_config["url_depot_position"]
        url = url.replace("[DEPOT_ID]", depot_id)

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
                "############# Depot Position #############")
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
                self.logger_name, "API_Trade_Depots_Success")
        else:
            result = response
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_Depots_Error",
                (str(response.status_code),
                 response_body_json["messages"]["message"]))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Parse the content from the API into Pandas format
        # ----------------------------------------------------------------------
        list_depot_position_aggregated_depot_id = []
        list_depot_position_aggregated_purchase_value_value = []
        list_depot_position_aggregated_purchase_value_unit = []
        list_depot_position_aggregated_current_value_value = []
        list_depot_position_aggregated_current_value_unit = []
        list_depot_position_aggregated_profit_loss_purchase_absolute_value = []
        list_depot_position_aggregated_profit_loss_purchase_absolute_unit = []
        list_depot_position_aggregated_profit_loss_purchase_relative = []
        list_depot_position_aggregated_profit_loss_prevday_absolute_value = []
        list_depot_position_aggregated_profit_loss_prevday_absolute_unit = []
        list_depot_position_aggregated_profit_loss_prevday_relative = []

        depot_item = response_body_json["aggregated"]
        depot_position_aggregated_depot_id = depot_item["depot"]["depotId"]
        depot_position_aggregated_purchase_value_value = depot_item["purchaseValue"]["value"]
        depot_position_aggregated_purchase_value_unit = depot_item["purchaseValue"]["unit"]
        depot_position_aggregated_current_value_value = depot_item["currentValue"]["value"]
        depot_position_aggregated_current_value_unit = depot_item["currentValue"]["unit"]
        depot_position_aggregated_profit_loss_purchase_absolute_value = depot_item[
            "profitLossPurchaseAbs"]["value"]
        depot_position_aggregated_profit_loss_purchase_absolute_unit = depot_item[
            "profitLossPurchaseAbs"]["unit"]
        depot_position_aggregated_profit_loss_purchase_relative = depot_item[
            "profitLossPurchaseRel"]
        depot_position_aggregated_profit_loss_prevday_absolute_value = depot_item[
            "profitLossPrevDayAbs"]["value"]
        depot_position_aggregated_profit_loss_prevday_absolute_unit = depot_item[
            "profitLossPrevDayAbs"]["unit"]
        depot_position_aggregated_profit_loss_prevday_relative = depot_item[
            "profitLossPrevDayRel"]

        list_depot_position_aggregated_depot_id.append(
            depot_position_aggregated_depot_id)
        list_depot_position_aggregated_purchase_value_value.append(
            depot_position_aggregated_purchase_value_value)
        list_depot_position_aggregated_purchase_value_unit.append(
            depot_position_aggregated_purchase_value_unit)
        list_depot_position_aggregated_current_value_value.append(
            depot_position_aggregated_current_value_value)
        list_depot_position_aggregated_current_value_unit.append(
            depot_position_aggregated_current_value_unit)
        list_depot_position_aggregated_profit_loss_purchase_absolute_value.append(
            depot_position_aggregated_profit_loss_purchase_absolute_value)
        list_depot_position_aggregated_profit_loss_purchase_absolute_unit.append(
            depot_position_aggregated_profit_loss_purchase_absolute_unit)
        list_depot_position_aggregated_profit_loss_purchase_relative.append(
            depot_position_aggregated_profit_loss_purchase_relative)
        list_depot_position_aggregated_profit_loss_prevday_absolute_value.append(
            depot_position_aggregated_profit_loss_prevday_absolute_value)
        list_depot_position_aggregated_profit_loss_prevday_absolute_unit.append(
            depot_position_aggregated_profit_loss_prevday_absolute_unit)
        list_depot_position_aggregated_profit_loss_prevday_relative.append(
            depot_position_aggregated_profit_loss_prevday_relative)

        zippedList = list(
            zip(
                list_depot_position_aggregated_depot_id,
                list_depot_position_aggregated_purchase_value_value,
                list_depot_position_aggregated_purchase_value_unit,
                list_depot_position_aggregated_current_value_value,
                list_depot_position_aggregated_current_value_unit,
                list_depot_position_aggregated_profit_loss_purchase_absolute_value,
                list_depot_position_aggregated_profit_loss_purchase_absolute_unit,
                list_depot_position_aggregated_profit_loss_purchase_relative,
                list_depot_position_aggregated_profit_loss_prevday_absolute_value,
                list_depot_position_aggregated_profit_loss_prevday_absolute_unit,
                list_depot_position_aggregated_profit_loss_prevday_relative,
            )
        )

        data_output_aggregated = pd.DataFrame(
            zippedList,
            columns=[
                "Depot Aggregated ID",
                "Depot Aggregated Purchase Value",
                "Depot Aggregated Purchase Value Unit",
                "Depot Aggregated Current Value",
                "Depot Aggregated Current Value Unit",
                "Depot Aggregated Profit/Loss Purchase Absolute Value",
                "Depot Aggregated Profit/Loss Purchase Absolute Unit",
                "Depot Aggregated Profit/Loss Purchase Relative",
                "Depot Aggregated Profit/Loss Previous Day Absolute Value",
                "Depot Aggregated Profit/Loss Previous Day Absolute Unit",
                "Depot Aggregated Profit/Loss Previous Day Relative",
            ],
        )

        data_output_aggregated["Date"] = today_string

        list_depot_position_wkn = []
        list_depot_position_depot_id = []
        list_depot_position_position_id = []
        list_depot_position_quantity = []
        list_depot_position_available_quantity = []
        list_depot_position_purchase_value_value = []
        list_depot_position_purchase_value_unit = []
        list_depot_position_purchase_price_value = []
        list_depot_position_purchase_price_unit = []
        list_depot_position_current_value_value = []
        list_depot_position_current_value_unit = []
        list_depot_position_current_price_value = []
        list_depot_position_current_price_unit = []
        list_depot_position_current_price_date = []
        list_depot_position_hedgeability = []
        list_depot_position_current_price_determinable = []
        list_depot_position_custody_type = []
        list_depot_position_profit_loss_purchase_absolute_value = []
        list_depot_position_profit_loss_purchase_absolute_unit = []
        list_depot_position_profit_loss_purchase_relative = []
        list_depot_position_profit_loss_prevday_absolute_value = []
        list_depot_position_profit_loss_prevday_absolute_unit = []
        list_depot_position_profit_loss_prevday_relative = []

        for depot_item in response_body_json["values"]:
            depot_position_wkn = depot_item["wkn"]
            depot_position_depot_id = depot_item["depotId"]
            depot_position_position_id = depot_item["positionId"]
            depot_position_quantity = depot_item["quantity"]["value"]
            depot_position_available_quantity = depot_item["availableQuantity"]["value"]
            depot_position_purchase_value_value = depot_item["purchaseValue"]["value"]
            depot_position_purchase_value_unit = depot_item["purchaseValue"]["unit"]
            depot_position_purchase_price_value = depot_item["purchasePrice"]["value"]
            depot_position_purchase_price_unit = depot_item["purchasePrice"]["unit"]
            depot_position_current_value_value = depot_item["currentValue"]["value"]
            depot_position_current_value_unit = depot_item["currentValue"]["unit"]
            depot_position_current_price_value = depot_item["currentPrice"]["price"]["value"]
            depot_position_current_price_unit = depot_item["currentPrice"]["price"]["unit"]
            depot_position_current_price_date = depot_item["currentPrice"]["priceDateTime"]
            depot_position_hedgeability = depot_item["hedgeability"]
            depot_position_current_price_determinable = depot_item["currentPriceDeterminable"]
            depot_position_custody_type = depot_item["custodyType"]
            depot_position_profit_loss_purchase_absolute_value = depot_item[
                "profitLossPurchaseAbs"]["value"]
            depot_position_profit_loss_purchase_absolute_unit = depot_item[
                "profitLossPurchaseAbs"]["unit"]
            depot_position_profit_loss_purchase_relative = depot_item["profitLossPurchaseRel"]
            depot_position_profit_loss_prevday_absolute_value = depot_item[
                "profitLossPrevDayAbs"]["value"]
            depot_position_profit_loss_prevday_absolute_unit = depot_item[
                "profitLossPrevDayAbs"]["unit"]
            depot_position_profit_loss_prevday_relative = depot_item["profitLossPrevDayRel"]

            list_depot_position_wkn.append(depot_position_wkn)
            list_depot_position_depot_id.append(depot_position_depot_id)
            list_depot_position_position_id.append(depot_position_position_id)
            list_depot_position_quantity.append(depot_position_quantity)
            list_depot_position_available_quantity.append(
                depot_position_available_quantity)
            list_depot_position_purchase_value_value.append(
                depot_position_purchase_value_value)
            list_depot_position_purchase_value_unit.append(
                depot_position_purchase_value_unit)
            list_depot_position_purchase_price_value.append(
                depot_position_purchase_price_value)
            list_depot_position_purchase_price_unit.append(
                depot_position_purchase_price_unit)
            list_depot_position_current_value_value.append(
                depot_position_current_value_value)
            list_depot_position_current_value_unit.append(
                depot_position_current_value_unit)
            list_depot_position_current_price_value.append(
                depot_position_current_price_value)
            list_depot_position_current_price_unit.append(
                depot_position_current_price_unit)
            list_depot_position_current_price_date.append(
                depot_position_current_price_date)
            list_depot_position_hedgeability.append(
                depot_position_hedgeability)
            list_depot_position_current_price_determinable.append(
                depot_position_current_price_determinable)
            list_depot_position_custody_type.append(
                depot_position_custody_type)
            list_depot_position_profit_loss_purchase_absolute_value.append(
                depot_position_profit_loss_purchase_absolute_value)
            list_depot_position_profit_loss_purchase_absolute_unit.append(
                depot_position_profit_loss_purchase_absolute_unit)
            list_depot_position_profit_loss_purchase_relative.append(
                depot_position_profit_loss_purchase_relative)
            list_depot_position_profit_loss_prevday_absolute_value.append(
                depot_position_profit_loss_prevday_absolute_value)
            list_depot_position_profit_loss_prevday_absolute_unit.append(
                depot_position_profit_loss_prevday_absolute_unit)
            list_depot_position_profit_loss_prevday_relative.append(
                depot_position_profit_loss_prevday_relative)

        zippedList = list(
            zip(
                list_depot_position_wkn,
                list_depot_position_depot_id,
                list_depot_position_position_id,
                list_depot_position_quantity,
                list_depot_position_available_quantity,
                list_depot_position_purchase_value_value,
                list_depot_position_purchase_value_unit,
                list_depot_position_purchase_price_value,
                list_depot_position_purchase_price_unit,
                list_depot_position_current_value_value,
                list_depot_position_current_value_unit,
                list_depot_position_current_price_value,
                list_depot_position_current_price_unit,
                list_depot_position_current_price_date,
                list_depot_position_hedgeability,
                list_depot_position_current_price_determinable,
                list_depot_position_custody_type,
                list_depot_position_profit_loss_purchase_absolute_value,
                list_depot_position_profit_loss_purchase_absolute_unit,
                list_depot_position_profit_loss_purchase_relative,
                list_depot_position_profit_loss_prevday_absolute_value,
                list_depot_position_profit_loss_prevday_absolute_unit,
                list_depot_position_profit_loss_prevday_relative,
            )
        )

        data_output = pd.DataFrame(
            zippedList,
            columns=[
                "WKN",
                "Depot ID",
                "Position ID",
                "Quantity",
                "Available Quantity",
                "Purchase Value",
                "Purchase Value Unit",
                "Purchase Price",
                "Purchase Price Unit",
                "Current Value",
                "Current Value Unit",
                "Current Price",
                "Current Price Unit",
                "Current Price Date",
                "Hedgeability",
                "Current Price Determinable",
                "Custody Type",
                "Profit/Loss Purchase Absolute Value",
                "Profit/Loss Purchase Absolute Unit",
                "Profit/Loss Purchase Relative",
                "Profit/Loss Previous Day Absolute Value",
                "Profit/Loss Previous Day Absolute Unit",
                "Profit/Loss Previous Day Relative",
            ],
        )

        data_output["Date"] = today_string

        return (data_output_aggregated, data_output), flag, level, message
