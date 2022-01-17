"""Module for the Section 7 from the Comdirect API documentation: ORDER
"""
from datetime import datetime
import json
import requests
import pandas as pd
from src.lib import messages as M
from src.lib import constants as C

from src.lib.comdirect.quotes import Quotes


class Orders (Quotes):

    def get_orders(self):

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
        #   7.1.2
        # ----------------------------------------------------------------------
        (result, response_body_json, response_headers_json), flag, level, message = \
            self.basic_request(
                type_req="GET",
                url=self.access_config["url_orderbook"],
                payload={},
                header_type="Standard",
                request_name="7.1.2 - Order book (list)",
                url_replacements={"DEPOT_ID": self.depot_id})

        if flag != C.SUCCESS:
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Parse the content from the API into Pandas format
        # ----------------------------------------------------------------------
        list_order_id = []
        list_instrument_id = []
        list_venue_id = []
        list_order_status = []
        list_order_type = []
        list_order_side = []
        list_validity_type = []
        list_quantity = []
        list_limit = []
        list_limit_unit = []

        for order_item in response_body_json["values"]:

            order_type = order_item["orderType"]

            if order_type == "ONE_CANCELS_OTHER":

                for suborder in order_item.get("subOrders", 0):

                    suborder_type = suborder["orderType"]

                    if suborder_type == "STOP_MARKET":

                        order_id = suborder.get("orderId")
                        instrument_id = suborder.get("instrumentId")
                        venue_id = suborder.get("venueId")
                        order_status = suborder["orderStatus"]
                        order_side = suborder["side"]
                        validity_type = suborder["validityType"]
                        quantity = suborder["quantity"]["value"]
                        limit = suborder["triggerLimit"]["value"]
                        limit_unit = suborder["triggerLimit"]["unit"]

                        list_order_id.append(order_id)
                        list_instrument_id.append(instrument_id)
                        list_venue_id.append(venue_id)
                        list_order_status.append(order_status)
                        list_order_type.append(order_type)
                        list_order_side.append(order_side)
                        list_validity_type.append(validity_type)
                        list_quantity.append(quantity)
                        list_limit.append(limit)
                        list_limit_unit.append(limit_unit)

                    elif suborder_type == "LIMIT":

                        order_id = suborder.get("orderId")
                        instrument_id = suborder.get("instrumentId")
                        venue_id = suborder.get("venueId")
                        order_status = suborder["orderStatus"]
                        order_side = suborder["side"]
                        validity_type = suborder["validityType"]
                        quantity = suborder["quantity"]["value"]
                        limit = suborder["limit"]["value"]
                        limit_unit = suborder["limit"]["unit"]

                        list_order_id.append(order_id)
                        list_instrument_id.append(instrument_id)
                        list_venue_id.append(venue_id)
                        list_order_status.append(order_status)
                        list_order_type.append(order_type)
                        list_order_side.append(order_side)
                        list_validity_type.append(validity_type)
                        list_quantity.append(quantity)
                        list_limit.append(limit)
                        list_limit_unit.append(limit_unit)

            elif order_type == "LIMIT":

                order_id = order_item.get("orderId")
                instrument_id = order_item.get("instrumentId")
                venue_id = order_item["venueId"]
                order_status = order_item["orderStatus"]
                order_side = order_item["side"]
                validity_type = order_item["validityType"]
                quantity = order_item["quantity"]["value"]
                limit = order_item["limit"]["value"]
                limit_unit = order_item["limit"]["unit"]

                list_order_id.append(order_id)
                list_instrument_id.append(instrument_id)
                list_venue_id.append(venue_id)
                list_order_status.append(order_status)
                list_order_type.append(order_type)
                list_order_side.append(order_side)
                list_validity_type.append(validity_type)
                list_quantity.append(quantity)
                list_limit.append(limit)
                list_limit_unit.append(limit_unit)

        zippedList = list(
            zip(
                list_order_id,
                list_instrument_id,
                list_venue_id,
                list_order_status,
                list_order_type,
                list_order_side,
                list_validity_type,
                list_quantity,
                list_limit,
                list_limit_unit,
            )
        )

        data_output = pd.DataFrame(
            zippedList,
            columns=[
                "Order ID",
                "Instrument ID",
                "Venue ID",
                "Order Status",
                "Type",
                "Side",
                "Validity Type",
                "Quantity",
                "Limit Value",
                "Limit Unit",
            ],
        )

        data_output["Date"] = today_string

        return data_output, flag, level, message

    def make_order(self, wkn: str, type_order: str, side_order: str,
                   quantity: float, value_limit: float, validity_type: str = "GFD", validity: datetime = None):

        today_string = datetime.today().strftime('%Y-%m-%d')
        if validity is None:
            validity = datetime.today()

        # ----------------------------------------------------------------------
        #   Verifies first if there is a valid session. If not, then leaves the
        #   execution.
        # ----------------------------------------------------------------------
        if not self.session_connected:
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_No_Active_Session")
            return None, flag, level, message

        # ----------------------------------------------------------------------
        #   7.1.1
        # ----------------------------------------------------------------------
        (result, response_body_json, response_headers_json), flag, level, message = \
            self.basic_request(
                type_req="GET",
                url=self.access_config["url_orders_dimensions"],
                payload={},
                header_type="Standard",
                request_name="7.1.1 - Order Dimension",
                url_replacements={"WKN": wkn,
                                  "TYPE": type_order,
                                  "SIDE": side_order}
        )

        if flag != C.SUCCESS:
            return result, flag, level, message

        venues = response_body_json["values"][0]["venues"]
        lowest_quotation = None
        lowest_quotation_venue = ("", "")
        for venue in venues:

            if venue['name'] in self.access_config["possible_venues"] and validity_type in venue['validityTypes']:

                self.logger.info(f"Quoting value for {wkn} at {venue['name']}")

                # ----------------------------------------------------------------------
                #   8.1.1
                #   This step is aimed to find the lowest price available in the market.
                # ----------------------------------------------------------------------
                (result, quotation), flag, level, message = self.get_quote(
                    wkn=wkn, venue_id=venue["venueId"])

                if quotation is not None:
                    self.logger.info(
                        f"Value quoted for {wkn} at {venue['name']}: {quotation}")
                else:
                    self.logger.info(
                        f"Value quoted for {wkn} at {venue['name']}: --")

                if quotation is not None:
                    if lowest_quotation == None:
                        lowest_quotation = quotation
                        lowest_quotation_venue = (
                            venue["name"], venue["venueId"])
                    if quotation < lowest_quotation:
                        lowest_quotation = quotation
                        lowest_quotation_venue = (
                            venue["name"], venue["venueId"])

        if lowest_quotation is None:
            result = (result, response_body_json, response_headers_json)
            flag, level, message = M.get_status(
                self.logger_name, "No_Quotation_Available")
            return result, flag, level, message
        else:
            self.logger.info(
                f"Lowest value provided by {lowest_quotation_venue(0)} [ID={lowest_quotation_venue(1)} for {lowest_quotation:.2f}")

        # ----------------------------------------------------------------------
        #   7.1.5
        # ----------------------------------------------------------------------
        payload = json.dumps({
            "depotId": f"{self.depot_id}",
            "side": f"{side_order}",
            "instrumentId": f"{wkn}",
            "orderType": f"{type_order}",
            "quantity": {
                "value": f"{quantity}",
                "unit": "XXX"
            },
            "venueId": f"{lowest_quotation_venue(1)}",
            "limit": {
                "value": f"{lowest_quotation:.2f}",
                "unit": "EUR"
            }
        })

        if validity_type == "GFD":
            payload["validityType"] = "GFD"
        elif validity_type == "GTD":
            payload["validityType"] = "GTD"
            payload["validity"] = f"{validity.strftime('%Y-%m-%d')}"

        (result, response_body_json, response_headers_json), flag, level, message = self.basic_request(
            type_req="POST",
            url=self.access_config["url_orders_validation"],
            payload=payload,
            header_type="Standard",
            request_name="7.1.5 - Order Validation",
            url_replacements=None)

        if flag != C.SUCCESS:
            return result, flag, level, message

        info = response_headers_json["x-once-authentication-info"]
        self.order_challenge_id, self.order_challenge_type, self.order_authentication_info = \
            self.get_challenge_info(info)

        # ----------------------------------------------------------------------
        #   7.1.6
        # ----------------------------------------------------------------------
        (result, response_body_json, response_headers_json), flag, level, message = self.basic_request(
            type_req="POST",
            url=self.access_config["url_orders_costindicationexante"],
            payload=payload,
            header_type="Standard",
            request_name="7.1.6 - Order Validation",
            url_replacements=None)

        if flag != C.SUCCESS:
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   7.1.7
        # ----------------------------------------------------------------------
        (result, response_body_json, response_headers_json), flag, level, message = self.basic_request(
            type_req="POST",
            url=self.access_config["url_orders"],
            payload=payload,
            header_type="TAN_Order",
            request_name="7.1.7 - Order Placement",
            url_replacements=None)

        if flag != C.SUCCESS:
            return result, flag, level, message

        return result, response_body_json
