"""Module for centralized management of messages to the user and logging.
"""

import pathlib
import logging
from src.lib import constants as C

MESSAGE = {
    "General_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "General error.",
    },
    "General_Initialization": {
        "Flag": C.NEUTRAL,
        "Level": C.DEBUG,
        "Message": "Method initialization.",
    },
    "API_401_Msg_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Unauthorized access to the server: 401",
    },
    "API_422_Msg_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "The server could understand the request, but was unable "
                   "to process it. Error 422. See content: %s"
    },
    "API_422_Msg_Err_NoFundsAvailable": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "The server could understand the request, but was unable "
                   "to process it due to unavailable enough funds. Error 422."
    },
    "API_422_Msg_Err_NoTradingValues": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "The chosen supplier didn't provide a value. Try again "
                   "later. Error 422."
    },
    "API_422_Msg_Err_UnsupportedOrderType": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "The Order Type is not supported by this supplier. "
                   "Error 422."
    },
    "API_500_Msg_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "General error from the server: 500",
    },
    "API_200_Msg_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Positive response but with Error Message. "
                   "Verify that the ticker and other parameters are valid.",
    },
    "API_200_Content_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Positive response but with improper content due to "
                   "the fast access to API."
    },
    "API_200_Premium_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Positive response but the request demands a premium "
                   "account from Alpha Vantage."
    },
    "API_Other_Errors": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Unknown error from the API request."
    },
    "API_200_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Positive response from API."
    },
    "API_Neg_Response": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Negative response for ticker %s from API. Code: %s. Text: %s"
    },
    "API_Error_EmptyResult": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Error due to empty dictionary from the API."
    },
    "API_Error_NotFoundSymbol": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "The symbol %s was not found."
    },
    "API_429_ToManyRequests": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Negative response for ticker %s from API. Limit of requests "
                   "already reached."
    },
    "API_ParamCheck_General": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "No configuration match for ticker %s."
    },
    "API_ParamCheck_TypeSeries": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Invalid input for 'type_series' for ticker %s."
    },
    "API_ParamCheck_Period": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Invalid input for 'period' for ticker %s."
    },
    "API_Trade_Initialization": {
        "Flag": C.NEUTRAL,
        "Level": C.DEBUG,
        "Message": "Initializing method."
    },
    "API_Trade_Oauth_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the authentication. Error code: %s. Message: %s"
    },
    "API_Trade_Oauth_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the authentication."
    },
    "API_Trade_Ident_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the identification step. Error code: %s. Message: %s"
    },
    "API_Trade_Ident_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the identification step."
    },
    "API_Trade_Validate_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the validation step. Error code: %s. Message: %s"
    },
    "Comdirec_Connect_Step1_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the first step of the connection."
    },
    "API_Trade_Validate_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the validation step."
    },
    "API_Trade_Activate_TAN_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the TAN activation step. Error code: %s. Message: %s"
    },
    "API_Trade_Activate_TAN_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the TAN activation step."
    },
    "API_Trade_Oauth_2Flow_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the Oauth Second Flow step. Error code: %s. Message: %s"
    },
    "API_Trade_Oauth_2Flow_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the Oauth Second Flow step."
    },
    "API_Trade_Authentication_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on the authentication."
    },
    "API_Trade_Authentication_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on the authentication."
    },
    "API_Trade_Account_Balance_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on getting the account balance. Error code: %s. Message: %s"
    },
    "API_Trade_Account_Balance_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on getting the account balance."
    },
    "API_Trade_Depots_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure on getting the depots. Error code: %s. Message: %s"
    },
    "API_Trade_Depots_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success on getting the depots."
    },
    "API_Trade_No_Active_Session": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "There are no active and valid session."
    },
    "No_Quotation_Available": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "There are no available quotations for the order to be "
                   "based on. This means all the tried possible suppliers "
                   "didn't respond with a value. This could be due to not an "
                   "open market situation."
    },
    "Convertion_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Data for AlphaVantage converted from DICT "
                   "to Pandas DataFrame."
    },
    "Fetch_Convert_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Successful fetch of dataframe from the API "
                   "for ticker %s."
    },
    "Config_Load_Config": {
        "Flag": C.NEUTRAL,
        "Level": C.INFO,
        "Message": "Loading the configuration from %s."
    },
    "Config_Load_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Successful loading the configuration from %s."
    },
    "Config_Load_Fail_Find": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure loading the configuration from %s. This file does "
                   "not exist."
    },
    "Config_Load_Fail": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure loading the configuration from %s. This file is "
                   "not supported."
    },
    "Config_Load_Fail_Key": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure loading the configuration. The key %s is not "
                   "available."
    },
    "Config_Error_No_Source_Fetching": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "No source of data was define for fetching %s."
    },
    "Config_Error_No_Source_Trading": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "No source of data was define for trading %s."
    },
    "Comm_SendMessage_Fail": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure to send message."
    },
    "Comm_SendMessage_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to send message."
    },
    "Comm_ReceiveMessage_Fail": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure to receive message."
    },
    "Comm_ReceiveMessage_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to receive message."
    },
    "Comm_SendEmail_Fail": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure to send email."
    },
    "Comm_SendEmail_API_Fail": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Failure to send email while acessing the API."
    },
    "Comm_SendEmail_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to send email."
    },
    "Storage_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to save the file %s"
    },
    "Storage_LoadSuccess": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to load the file %s"
    },
    "Storage_Success_Dropbox": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Success to save the file on Dropbox at %s"
    },
    "Storage_Error_BadExtension": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Error saving file due to the invalid extension."
    },
    "Storage_Error_BadListSizes": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Error saving data in Excel due to invalid data lengths."
    },
    "Storage_LoadError_BadExtension": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Error loading file due to the invalid extension."
    },
}


def get_status(logger_name, message_id, param=None):
    """Gets the content (flag, level and message) for a given ID and adds an
    entry to the logger, according to the level of the content. The logger
    must be passed to the method.

    Note
    ----
    There are 3 elements as general abstraction, described below:

    *  **flag**: status of success, neutral or fail. Neutral is intended
       only for cases where a clear definition of success or fail
       is not possible.
    *  **level**: level for the logging: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
       By default (proposal from `example.py`) the console will display up to
       `INFO` level, while the log file will store up to `DEBUG` level.
    *  **message**: text to be displayed or logged for supporting user.

    Parameters
    ----------
        logger_name: string
            Logger name for handling the content. This follows the `logging`
            library for Python.
        message_id: string
            Identifies which message from the dictionary to be returned, along
            with the flag and level information.
        param: tuple of strings, optional
            For messages which have parameters to be set (using %s), this
            parameter will be used in the order passed. In case this
            parameter is passed as a single string, it will be automatically
            converted into a tuple (of 1 entry).

    """

    logger = logging.getLogger(logger_name)

    message = MESSAGE[message_id]["Message"]

    if isinstance(param, str) or isinstance(param, pathlib.Path):
        param = (str(param),)

    if param is None and message.count('%s') == 0:
        message = MESSAGE[message_id]["Message"]
    elif len(param) == message.count('%s'):
        message = MESSAGE[message_id]["Message"] % (param)
    else:
        message = "!!!!!ERROR PARSING!!!!!"

    if MESSAGE[message_id]["Level"] == C.DEBUG:
        logger.debug(message)
    elif MESSAGE[message_id]["Level"] == C.INFO:
        logger.info(message)
    elif MESSAGE[message_id]["Level"] == C.WARNING:
        logger.warning(message)
    elif MESSAGE[message_id]["Level"] == C.ERROR:
        logger.error(message)

    return MESSAGE[message_id]["Flag"], MESSAGE[message_id]["Level"], message
