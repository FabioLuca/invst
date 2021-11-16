# import lib.constants as Const
# import lib.json_manager as JsonMgr

# import lib.log_manager as LogMgr
# import lib.config as Config
# import lib.timestamp as TimeStamp
import requests
import json
# import quandl as Quandl
# import pandas_datareader as PandasDataReader
import datetime
import logging


"""============================================================================
    Função: request_data
    Pedido e recebimento do JSON com os dados
============================================================================"""

class DataAccess:

    def __init__(self, ticker, source, access_config, access_userdata, logger_name=None):
        """
        """

        """----------------------------------------------------------
            Defines the parameters of the class
        ----------------------------------------------------------"""
        self.ticker = ticker
        self.ticker_name = ""
        self.source = source
        self.access_config = access_config
        self.__access_userdata = access_userdata
        
        """----------------------------------------------------------
            Defines the logger to output the information and also
            add an entry for the start of the class
        ----------------------------------------------------------"""
        self.__logger_name = logger_name
        self.__logger = None
        if self.__logger_name is not None:
            self.__logger = logging.getLogger(str(self.__logger_name) + '.data_access')

        if self.__logger is not None:
            self.__logger.info("Initializing ticker %s from %s", self.ticker, self.source)
        
        """----------------------------------------------------------
            Makes the access
        ----------------------------------------------------------"""
        if self.source == "AlphaVantage":
            self.__access_alphavantage(access_config=self.access_config
                                       access_userdata=self.__access_userdata)


    def __access_alphavantage(self, access_config, access_userdata, period="", start="", end="", config=None):

        url = access_config["URL_TIMESERIES_DAILY"]
        r = requests.get(url)
        response = json.loads(r.text)

        if r.status_code == 200:

            """---------------------------------------------------------------------
                The API for AlphaVantage has a limit os accesses for a given time.
                If it is to fast, the response is positive, but with an error
                message: "{'Note': 'Thank you for using Alpha Vantage! Our 
                standard API call frequency is 5 calls per minute and 500 
                calls per day. ...". So to identify if an message was returned,
                just check the first value.
            ---------------------------------------------------------------------"""
            if str(response)[0:8] == "{'Note':":
                result = response
                flag = 1 #Const.FAIL
                level = 1 #Const.ERROR
                message = (
                    "Positive response but with improper content due to the fast access to API: "
                    + str(self.ticker)
                )
                if self.__logger is not None:
                    self.__logger.info(message)
                return result, flag, level, message
            else:
                result = response
                flag = 1 #Const.SUCCESS
                level = 1 #Const.INFO
                message = "Positive response for ticker from AlphaVantage: " + str(
                    self.ticker
                )
                if self.__logger is not None:
                    self.__logger.info(message)
                return result, flag, level, message

        else:
            result = json.loads(r.text)
            flag = 1 #Const.FAIL
            level = 1 #Const.ERROR
            message = "Negative response for ticker from AlphaVantage: " + str(
                self.ticker
            )
            if self.__logger is not None:
                self.__logger.info(message)
            return result, flag, level, message


    def get_ticker_data(self, period="", start="", end="", logger=None, config=None):

        if self.source == "AlphaVantage":
            if period == "Daily":
                url = self.access_data["AlphaVantage"]["access_data"][
                    "URL_TIMESERIES_DAILY"
                ]
                url = url.replace(
                    "[APIKEY]",
                    self.access_data["AlphaVantage"]["access_data"]["APIKEY"],
                )
                url = url.replace("[STOCK]", self.ticker)
                # url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + stock + '&apikey=' + APIKey

            logger.add_log_info(
                message="Request information for AlphaVantage: " + str(url),
            )

            r = requests.get(url)
            response = json.loads(r.text)

            

        elif self.source == "YahooFinance":

            if start == "":
                start = datetime.datetime.today() - datetime.timedelta(days=30)

            if end == "":
                end = datetime.datetime.today()

            result = PandasDataReader.get_data_yahoo(self.ticker, start=start, end=end)
            flag = Const.SUCCESS
            level = Const.INFO
            message = "Positive response for ticker from Yahoo Finance: " + str(
                self.ticker
            )
            if config.log_results and logger is not None:
                logger.add_log_event(flag, level, message)
            return result, flag, level, message

        elif self.source == "Quandl":

            result = Quandl.get(self.ticker, start_date=start, end_date=end)
            flag = Const.SUCCESS
            level = Const.INFO
            message = "Positive response for ticker from Quandl: " + str(self.ticker)
            if config.log_results and logger is not None:
                logger.add_log_event(flag, level, message)
            return result, flag, level, message

    """============================================================================
        Função: buy_ticker
        Sends a order for buying a ticker
    ============================================================================"""

    def buy_ticker(
        self, ticker, quantity, logger=None, config=None,
    ):

        """----------------------------------------------------------
            Get the result of the purchase
        ----------------------------------------------------------"""
        if config.simulation_mode:
            quantity = quantity
            value = 15.0
            time = TimeStamp.get_now_timestamp()
        else:
            quantity = quantity
            value = 15.1
            time = TimeStamp.get_now_timestamp()

        """----------------------------------------------------------
            Register operation
        ----------------------------------------------------------"""
        result, flag, level, message = JsonMgr.add_operation_regitry(
            type_operation="BUY",
            ticker=ticker,
            quantity=quantity,
            value=value,
            time=time,
            str_file_json="",
            logger=logger,
            config=config,
        )

        """----------------------------------------------------------
            Update wallet status
        ----------------------------------------------------------"""
        result, flag, level, message = JsonMgr.update_wallet(
            value=-value, time=time, str_file_json="", logger=logger, config=config,
        )

        """----------------------------------------------------------
            Update wallet status
        ----------------------------------------------------------"""
        result, flag, level, message = JsonMgr.update_wallet_ticker(
            ticker=ticker,
            quantity=quantity,
            time=time,
            str_file_json="",
            logger=logger,
            config=config,
        )

        if not simulation:
            # REAL BUY
            print("Not simulation")

        result = ticker, quantity, value
        flag = Const.SUCCESS
        level = Const.INFO
        message = "Ticker " + str(ticker) + " bought. Quantity: " + str(quantity)
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message

    def sell_ticker(
        self, ticker, quantity, logger=None, config=None,
    ):

        """----------------------------------------------------------
            Get the result of the purchase
        ----------------------------------------------------------"""
        if config.simulation_mode:
            quantity = quantity
            value = 15.0
            time = TimeStamp.get_now_timestamp()
        else:
            quantity = quantity
            value = 15.1
            time = TimeStamp.get_now_timestamp()

        """----------------------------------------------------------
            Register operation
        ----------------------------------------------------------"""
        result, flag, level, message = JsonMgr.add_operation_registry(
            type_operation="SELL",
            ticker=ticker,
            quantity=quantity,
            value=value,
            time=time,
            str_file_json="",
            logger=logger,
            config=config,
        )

        """----------------------------------------------------------
            Update wallet status
        ----------------------------------------------------------"""
        result, flag, level, message = JsonMgr.update_wallet(
            value=value, time=time, str_file_json="", logger=logger, config=config
        )

        # ----------------------------------------------------------------------
        #   Update wallet status
        # ----------------------------------------------------------------------
        result, flag, level, message = JsonMgr.update_wallet_ticker(
            ticker=ticker,
            quantity=-quantity,
            time=time,
            str_file_json="",
            logger=logger,
            config=config,
        )

        if not config.simulation_mode:
            # REAL BUY
            print("Not simulation")

        result = ticker, quantity, value
        flag = Const.SUCCESS
        level = Const.INFO
        message = "Ticker " + str(ticker) + " sold. Quantity: " + str(quantity)
        if config.log_results and logger is not None:
            logger.add_log_event(flag, level, message)
        return result, flag, level, message
