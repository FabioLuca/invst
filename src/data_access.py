"""Ticker data fetch for AlphaVantage."""

from datetime import datetime
import json
import logging
import requests
import pandas as pd
import matplotlib.dates as mdates

# ------------------------------------------------------------------------------
#   Conflicts with the importing: For pytest, the be able to succesful import
#   the following files, they must be defined as reçatove paths:
#       from .lib.invst_const import constants as C
#       from .lib import messages as M
#   On the other hand, for Sphinx to be able to work with them, it must be
#   defined as aboslute paths:
#       from lib.invst_const import constants as C
#       from lib import messages as M
# ------------------------------------------------------------------------------

from .lib.invst_const import constants as C
from .lib import messages as M


class DataAccess:
    """Data Access class.

    Attributes
    ----------
        ticker: `string`
            A string with the acronym of the ticker to be fetched.
            This value must match to the API expectation.
        ticker_name: `string`
            A string with the full name of the ticker.
        source: `string`
            A string with the reference to the source of the data,
            for example, AlphaVantage.
        access_config: `dictionary`
            A dictionary with the configuration for access
            the API specified by `source`. See template below.
        access_userdata: `dictionary`
            A dictionary with the configuration for the
            user access the API specified by `source`, for example,
            the API key.
        type_series: None
        period: None
        adjusted: None
        start: None
        end: None
        data_json: `dictionary`
            A dictionary which stores the results of the fetch of the OHLC
            data for the given ticker.
        data_pandas: `Pandas data frame`
            A pandas dataframe which stores the results of the fetch of the
            OHLC data for the given ticker.

    Examples
    --------

    For the dictionary `access_config`:

    .. code-block:: json

        {
            "data_source": {
                "AlphaVantage": {
                    "user_data": {
                        "APIKEY": "<YOUR API KEY>"
                    }
                }
            }
        }

    For the dictionary `access_userdata`:

    .. code-block:: json

        {
            "data_source": {
                "AlphaVantage": {
                    "user_data": {
                        "APIKEY": "<YOUR API KEY>"
                    }
                }
            }
        }

    For acesing the data and class usage, the example below will fetch all
    the OHLC data for the Google ticker:

    .. code-block:: python

        google = DataAccess(ticker="GOOG",
                            source=config.data_source_name,
                            access_config=config.data_source_access_data,
                            access_userdata=config.data_source_user_data,
                            logger_name=LOGGER_NAME,
                           )
        google_data = google.update_values(type_series="TIMESERIES",
                                           period="DAILY",
                                           adjusted=True,
                                           start="",
                                           end=""
                                          )

    """

    def __init__(
        self, ticker, source, access_config, access_userdata, logger_name=None
    ):
        """metodo paa

        asasdfvr
        vfvfvfv
        """

        # ----------------------------------------------------------------------
        #   Defines the parameters of the class
        # ----------------------------------------------------------------------
        self.ticker = ticker
        self.ticker_name = ""
        self.source = source
        self.access_config = access_config
        self.__access_userdata = access_userdata

        self.type_series = None
        self.period = None
        self.adjusted = None
        self.start = None
        self.end = None
        self.data_json = None
        self.data_pandas = None

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.__logger_name = logger_name
        self.__logger = None
        if self.__logger_name is not None:
            self.__logger = logging.getLogger(
                str(self.__logger_name) + ".data_access")

        if self.__logger is not None:
            self.__logger.info(
                "Initializing ticker %s from %s", self.ticker, self.source
            )

    def update_values(
        self, type_series="TIMESERIES", period="DAILY", adjusted=True, start="", end=""
    ):
        """Updates the OHLC values for given ticker.

        Parameters
        ----------
            type_series: string, optional
                The first parameter.
            period: string, optional
                Time base of the data: daily, monthly, etc.
            adjusted: bool, optional
                For True it will return the adjusted closure value, otherwise
                it returns the regular closure.
            start: datetime, optional
                The second parameter.
            end: datetime, optional
                The end date for the time series to be fetched.

        Returns
        -------
            Pandas dataframe
                The returned dataframe is composed of the following
                items (headers):

                    # .  "Date"
                    # .  "Open"
                    # .  "High"
                    # .  "Low"
                    # .  "Close"
                    # .  "Close Final"
                    # .  "Volume"
                    # .  "Dividend Amount"
                    # .  "Split Coefficient"

        Examples
        --------
        An input example for using this method: To retrieve the complete time
        series (from first historical data, up to today) from AlphaVantage,
        where it entry in the series represents the OHLC data for a day, the
        inputs are:

        .. code-block:: python

            google_data = google.update_values(type_series="TIMESERIES",
                                               period="DAILY",
                                               adjusted=True,
                                               start="",
                                               end=""
                                              )


        """
        # ----------------------------------------------------------------------
        #   Verify the inputs, if they are valid, otherwise return an error
        # ----------------------------------------------------------------------
        result = None
        flag, level, message = M.get_status("General_Error")

        if type_series not in ["TIMESERIES"]:
            flag, level, message = M.get_status(
                "API_ParamCheck_TypeSeries", (self.ticker))
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        if period not in ["DAILY"]:
            flag, level, message = M.get_status(
                "API_ParamCheck_Period", (self.ticker))
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Setup the paramters for the data fetching
        # ----------------------------------------------------------------------
        self.type_series = type_series
        self.period = period
        self.adjusted = adjusted
        self.start = start
        self.end = end

        # ----------------------------------------------------------------------
        #   Access the webpage
        # ----------------------------------------------------------------------
        if self.source == "AlphaVantage":

            # ------------------------------------------------------------------
            #   Fetch the data (json dictionary)
            # ------------------------------------------------------------------
            self.data_json, flag, level, message = self.__access_alphavantage()

            if flag != C.SUCCESS:
                # if self.__logger is not None:
                #     self.__logger.error(message)
                return result, flag, level, message

            # ------------------------------------------------------------------
            #   Convert the json dict to pandas dataframe
            # ------------------------------------------------------------------
            (
                self.data_pandas,
                flag,
                level,
                message,
            ) = self.__dict_to_pandas_alphavantage()

            if flag != C.SUCCESS:
                if self.__logger is not None:
                    self.__logger.error(message)
                return result, flag, level, message

            elif flag == C.SUCCESS:
                result = self.data_pandas
                flag, level, message = M.get_status(
                    "Fetch_Convert_Success", (self.ticker,))
                if self.__logger is not None:
                    self.__logger.info(message)
                return result, flag, level, message

    def __access_alphavantage(self):
        """Access the API and verifies for the validity of the response."""

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
            flag, level, message = M.get_status(
                "API_ParamCheck_General", (self.ticker))
            if self.__logger is not None:
                self.__logger.error(message)
            return result, flag, level, message

        # ----------------------------------------------------------------------
        #   Replaces the keywords by final values
        # ----------------------------------------------------------------------
        url = url.replace(
            "[APIKEY]",
            self.__access_userdata["APIKEY"],
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
                flag, level, message = M.get_status("API_200_Msg_Err")
                if self.__logger is not None:
                    self.__logger.error(message)

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
                flag, level, message = M.get_status("API_200_Content_Err")
                if self.__logger is not None:
                    self.__logger.info(message)
            else:
                result = response
                flag, level, message = M.get_status("API_200_Success")
                if self.__logger is not None:
                    self.__logger.info(message)

            return result, flag, level, message

        else:
            result = json.loads(r.text)
            flag, level, message = M.get_status(
                "API_Neg_Response", (self.ticker))
            if self.__logger is not None:
                self.__logger.info(message)
            return result, flag, level, message

    def __dict_to_pandas_alphavantage(self):
        """Converts a json data returned from the API into a Pandas dataframe
        object."""

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
        flag, level, message = M.get_status("Convertion_Success")
        if self.__logger is not None:
            self.__logger.info(message)

        return result, flag, level, message
