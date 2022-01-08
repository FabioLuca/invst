"""Module for the Section 7 from the Comdirect API documentation: ORDER
"""
from datetime import datetime
import json
import requests
import pandas as pd
from src.lib import messages as M
from src.lib import constants as C


class Quotes:

    def get_quote(self, wkn: str, venue_id: str):

        # ----------------------------------------------------------------------
        #   Verifies first if there is a valid session. If not, then leaves the
        #   execution.
        # ----------------------------------------------------------------------
        if not self.session_connected:
            flag, level, message = M.get_status(
                self.logger_name, "API_Trade_No_Active_Session")
            return None, flag, level, message

        # ----------------------------------------------------------------------
        #   8.1.1
        #   This step is aimed to find the lowest price available in the market.
        # ----------------------------------------------------------------------
        payload = json.dumps({

            "depotId": f"{self.depot_id}",
            "orderType": "QUOTE",
            "side": "BUY",
            "instrumentId": f"{wkn}",
            "quantity": {"value": "1", "unit": "XXX"},
            "venueId": f"{venue_id}",
        })

        (result, response_body_json, response_headers_json), flag, level, message = \
            self.basic_request(
                type_req="POST",
                url=self.access_config["url_quoteticket"],
                payload=payload,
                header_type="Standard",
                request_name="8.1.1 - Quote validation",
                url_replacements=None)

        if flag != C.SUCCESS:
            value = None
            return (result, value), flag, level

        (result, response_body_json, response_headers_json), flag, level, message = \
            self.basic_request(
                type_req="POST",
                url=self.access_config["url_quotes"],
                payload=payload,
                header_type="Standard",
                request_name="8.1.3 - Quote request",
                url_replacements=None)

        if flag != C.SUCCESS:
            value = None
            return (result, value), flag, level, message

        value = 1

        return (result, value), flag, level, message
