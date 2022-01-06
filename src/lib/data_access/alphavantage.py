from datetime import datetime
import json
import logging
import requests
import pandas as pd
import matplotlib.dates as mdates
from src.lib import constants as C
from src.lib import messages as M


class AlphaVantage:

    def access_alphavantage(self):
        """Fetches Json data from the Alpha Vantage API.
        """

        # ----------------------------------------------------------------------
        #   Builds up the API path
        # ----------------------------------------------------------------------
        if (self.type_series == "TIMESERIES" and self.period == "DAILY" and self.adjusted):
            url = self.access_config["URL_TIMESERIES_DAILY_ADJUSTED"]
        elif (
            self.type_series == "TIMESERIES"
            and self.period == "DAILY"
            and not self.adjusted
        ):
            url = self.access_config["URL_TIMESERIES_DAILY"]
        else:
            result = None
            flag, level, message = M.get_status(self.logger_name,
                                                "API_ParamCheck_General", (self.ticker))
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Replaces the keywords by final values
        # ----------------------------------------------------------------------
        url = url.replace(
            "[APIKEY]",
            self.access_userdata["APIKEY"],
        )
        url = url.replace("[TICKER]", self.ticker)

        # ----------------------------------------------------------------------
        #   Gets the access
        # ----------------------------------------------------------------------
        r = requests.get(url)
        response = json.loads(r.text)

        if r.status_code == 200:

            if str(response)[0:17] == "{'Error Message':":
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Msg_Err")

            # ------------------------------------------------------------------
            #   The API for AlphaVantage has a limit os accesses for a given
            #   time. If it is to fast, the response is positive, but with an
            #   error message: "{'Note': 'Thank you for using Alpha Vantage! Our
            #   standard API call frequency is 5 calls per minute and 500
            #   calls per day. ...". So to identify if an message was returned,
            #   just check the first value.
            # ------------------------------------------------------------------
            elif str(response)[0:8] == "{'Note':":
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Content_Err")
            elif str(response)[0:78] == "{'Information': 'Thank you for using Alpha Vantage! This is a premium endpoint":
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Premium_Err")
            else:
                result = response
                flag, level, message = M.get_status(
                    self.logger_name, "API_200_Success")

            return result, flag, level, message

        else:
            result = json.loads(r.text)
            flag, level, message = M.get_status(self.logger_name,
                                                "API_Neg_Response",
                                                (self.ticker))
            return result, flag, level, message

    def dict_to_pandas_alphavantage(self):
        """Converts Json data returned from the Alpha Vantage API into a Pandas
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
        data_metadata = data_output[str(list(data_output)[0])]
        data_content = data_output[str(list(data_output)[1])]
        data_sample = data_content[sorted(data_content)[0]]

        # ----------------------------------------------------------------------
        #   Prepare the lists of data
        # ----------------------------------------------------------------------
        lista_tempo_str = []
        lista_tempo_time = []
        lista_tempo_number = []
        lista_abertura = []
        lista_maximo = []
        lista_minimo = []
        lista_fechamento = []
        lista_fechamento_final = []
        lista_volume = []
        lista_dividend_amount = []
        lista_split_coefficient = []

        # ----------------------------------------------------------------------
        #   Loop thru all the data values and parse the entries
        # ----------------------------------------------------------------------
        if "5. volume" in data_sample:
            for day in data_content:
                lista_tempo_str.append(day)
                lista_tempo_time.append(
                    datetime(year=int(day[:4]), month=int(
                        day[5:7]), day=int(day[8:]))
                )
                lista_tempo_number.append(
                    mdates.date2num(
                        datetime(
                            year=int(day[:4]), month=int(day[5:7]), day=int(day[8:])
                        )
                    )
                )

                lista_abertura.append(float(data_content[day]["1. open"]))
                lista_maximo.append(float(data_content[day]["2. high"]))
                lista_minimo.append(float(data_content[day]["3. low"]))
                lista_fechamento.append(float(data_content[day]["4. close"]))
                lista_fechamento_final.append(
                    float(data_content[day]["4. close"]))
                lista_volume.append(float(data_content[day]["5. volume"]))
                lista_dividend_amount.append(
                    float(data_content[day]["6. dividend amount"])
                )
                lista_split_coefficient.append(
                    float(data_content[day]["7. split coefficient"])
                )

        elif "5. adjusted close" in data_sample:
            for day in data_content:
                lista_tempo_str.append(day)
                lista_tempo_time.append(
                    datetime(year=int(day[:4]), month=int(
                        day[5:7]), day=int(day[8:]))
                )
                lista_tempo_number.append(
                    mdates.date2num(
                        datetime(
                            year=int(day[:4]), month=int(day[5:7]), day=int(day[8:])
                        )
                    )
                )

                lista_abertura.append(float(data_content[day]["1. open"]))
                lista_maximo.append(float(data_content[day]["2. high"]))
                lista_minimo.append(float(data_content[day]["3. low"]))
                lista_fechamento.append(float(data_content[day]["4. close"]))
                lista_fechamento_final.append(
                    float(data_content[day]["5. adjusted close"])
                )
                lista_volume.append(float(data_content[day]["6. volume"]))
                lista_dividend_amount.append(
                    float(data_content[day]["7. dividend amount"])
                )
                lista_split_coefficient.append(
                    float(data_content[day]["8. split coefficient"])
                )

        # ----------------------------------------------------------------------
        #   Inversão das listas para ordem correta
        # ----------------------------------------------------------------------
        lista_tempo_str.reverse()
        lista_tempo_time.reverse()
        lista_tempo_number.reverse()
        lista_abertura.reverse()
        lista_maximo.reverse()
        lista_minimo.reverse()
        lista_fechamento.reverse()
        lista_fechamento_final.reverse()
        lista_volume.reverse()
        lista_dividend_amount.reverse()
        lista_split_coefficient.reverse()

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
