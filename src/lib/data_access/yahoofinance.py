from datetime import datetime
import json
import requests
import pandas as pd
from src.lib import messages as M


class YahooFinance:

    def access_yahoofinance(self):
        """Fetches Json data from the Yahoo Finance API.

        The data is requested with daily interval for 10 years long. Requesting
        for the `max` long will return the data not in day-interval, but
        3-months interval.

        """

        # ----------------------------------------------------------------------
        #   Builds up the API path
        # ----------------------------------------------------------------------
        if (self.type_series == "INFORMATION"):
            url = self.access_config["BASE_URL"] + \
                self.access_config["URL_QUOTE"]
            querystring = {"symbols": f"{self.ticker}"}

        elif (self.type_series == "TIMESERIES" and self.period == "DAILY" and self.adjusted):
            url = self.access_config["BASE_URL"] + \
                self.access_config["URL_CHART"] + f"/{self.ticker}"
            querystring = {"range": "10y",
                           "region": "US",
                           "interval": "1d",
                           "lang": "en",
                           "events": "div,split",
                           }

        apikey = self.access_userdata["APIKEY"]

        headers = {'x-api-key': f"{apikey}"}

        # ----------------------------------------------------------------------
        #   Gets the access
        # ----------------------------------------------------------------------
        r = requests.request("GET", url, headers=headers, params=querystring)
        self.logger.info(f"Response from request: {r.status_code}")

        # ----------------------------------------------------------------------
        #   Treats the response for errors.
        # ----------------------------------------------------------------------
        if r.status_code == 429:
            result = r.text
            flag, level, message = M.get_status(
                self.logger_name, "API_429_ToManyRequests", self.ticker)

            return result, flag, level, message

        elif r.status_code == 200:

            response = json.loads(r.text)

            if (self.type_series == "INFORMATION" and response["quoteResponse"]["error"] is None) or \
                    (self.type_series == "TIMESERIES" and response["chart"]["error"] is None):
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Success")

            elif str(response)[0:17] == "{'Error Message':":
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Msg_Err")

            else:
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Success")

            return result, flag, level, message

        else:
            result = json.loads(r.text)
            flag, level, message = M.get_status(self.logger_name,
                                                "API_Neg_Response",
                                                (self.ticker, r.status_code, r.text))
            return result, flag, level, message

    def dict_to_pandas_yahoofinance(self):
        """Converts Json data returned from the Yahoo Finance API into a Pandas
        dataframe object with the following structure of columns:

        1. ``Date``
        2. ``Open``
        3. ``High``
        4. ``Low``
        5. ``Close``
        6. ``Close Final``: Meaning the adjusted close value.
        7. ``Volume``
        8. ``Dividend Amount``
        9. ``Split Coefficient``

        """

        # ----------------------------------------------------------------------
        #   Reorganize the disctionaries and split them.
        #   Data sample will take the first element of the dicture, just to
        #   try to identify the structure of the information to be parsed.
        # ----------------------------------------------------------------------
        data_output = self.data_json

        if data_output is None:
            result = None
            flag, level, message = M.get_status(
                self.logger_name, "API_Error_EmptyResult")
            return result, flag, level, message

        if data_output.get("chart", {}).get("error", {}) is not None:
            if data_output.get("chart", {}).get("error", {}).get("code", None) == "Not Found":
                result = None
                flag, level, message = M.get_status(
                    self.logger_name, "API_Error_NotFoundSymbol", (self.ticker))
                return result, flag, level, message

        lista_tempo_number = data_output["chart"]["result"][0]["timestamp"]
        lista_tempo_time = [datetime.fromtimestamp(
            x) for x in lista_tempo_number]
        lista_tempo_str = [str(x) for x in lista_tempo_time]

        if "events" in data_output["chart"]["result"][0]:
            if "dividends" in data_output["chart"]["result"][0]["events"]:
                # --------------------------------------------------------------
                #   TO-DO: For now the dividends are populated as None only.
                #   Missing the implementation yet.
                # --------------------------------------------------------------
                # lista_dividend_amount = data_output["chart"]["result"][0]["events"]["dividends"]
                lista_dividend_amount = [None] * len(lista_tempo_number)
            else:
                lista_dividend_amount = [None] * len(lista_tempo_number)

            if "splits" in data_output["chart"]["result"][0]["events"]:
                # --------------------------------------------------------------
                #   TO-DO: For now the splits are populated as None only.
                #   Missing the implementation yet.
                # --------------------------------------------------------------
                # lista_split_coefficient = data_output["chart"]["result"][0]["events"]["splits"]
                lista_split_coefficient = [None] * len(lista_tempo_number)
            else:
                lista_split_coefficient = [None] * len(lista_tempo_number)
        else:
            lista_dividend_amount = [None] * len(lista_tempo_number)
            lista_split_coefficient = [None] * len(lista_tempo_number)

        ohlc_data = data_output["chart"]["result"][0]["indicators"]["quote"][0]
        lista_maximo = ohlc_data["high"]
        lista_volume = ohlc_data["volume"]
        lista_abertura = ohlc_data["open"]
        lista_minimo = ohlc_data["low"]
        lista_fechamento = ohlc_data["close"]

        adjusted_ohlc_data = data_output["chart"]["result"][0]["indicators"]["adjclose"][0]
        lista_fechamento_final = adjusted_ohlc_data["adjclose"]

        # ----------------------------------------------------------------------
        #   Converte dados no formato pro Pandas / Finta (OHLC)
        # ----------------------------------------------------------------------
        zippedList = list(
            zip(
                lista_tempo_str,
                lista_abertura,
                lista_maximo,
                lista_minimo,
                lista_fechamento,
                lista_fechamento_final,
                lista_volume,
                lista_dividend_amount,
                lista_split_coefficient,
            )
        )

        data_output = pd.DataFrame(
            zippedList,
            columns=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Close Final",
                "Volume",
                "Dividend Amount",
                "Split Coefficient",
            ],
        )

        data_output.index = pd.to_datetime(data_output["Date"])
        data_output = data_output.drop(columns=["Date"])

        # ----------------------------------------------------------------------
        #   Return
        # ----------------------------------------------------------------------
        result = data_output
        flag, level, message = M.get_status(
            self.logger_name, "Convertion_Success")

        return result, flag, level, message
