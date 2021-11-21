"""Module for centralized management of messages to the user or for logging.
"""

import pathlib
from .invst_const import constants as C

MESSAGE = {
    "General_Error": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "General error.",
    },
    "API_200_Msg_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Positive response but with Error Message. "
                   "Verify that the ticker and other parameters are valid.""",
    },
    "API_200_Content_Err": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Positive response but with improper content due to "
                   "the fast access to API."
    },
    "API_200_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Positive response for ticker from AlphaVantage."
    },
    "API_Neg_Response": {
        "Flag": C.FAIL,
        "Level": C.ERROR,
        "Message": "Negative response for ticker %s from AlphaVantage."
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
    "Convertion_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Data for AlphaVantage converted from DICT "
                   "to Pandas DataFrame."
    },
    "Fetch_Convert_Success": {
        "Flag": C.SUCCESS,
        "Level": C.INFO,
        "Message": "Successful fetch of dataframe from AlphaVantage "
                   "for ticker %s."
    },
    "Config_Load_Config": {
        "Flag": C.NEUTRAL,
        "Level": C.INFO,
        "Message": "Loading the configuration from %s."
    },



}


def get_status(message_id, param=None):
    """Gets the content (flag, level and message) for a given ID.

    Note
    ----
    There are 3 elements as general abstraction, described below:

    *  **flag**: status of success, neutral or fail. Neutral is intended
       only for cases where a clear definition of success or fail
       is not possible.
    *  **level**:
    *  **message**: text to be displayed or logged for supporting user.

    Parameters
    ----------
        message_id: string
            Identifies which message from the dictionary to be returned, along
            with the flag and level information.
        param: tuple of strings, optional
            For messages which have parameters to be set (using %s), this
            parameter will be used in the order passed. In case this
            parameter is passed as a single string, it will be automatically
            converted into a tuple (of 1 entry).

    """

    message = MESSAGE[message_id]["Message"]

    if isinstance(param, str) or isinstance(param, pathlib.Path):
        param = (str(param),)

    if param is None and message.count('%s') == 0:
        message = MESSAGE[message_id]["Message"]
    elif len(param) == message.count('%s'):
        message = MESSAGE[message_id]["Message"] % (param)
    else:
        message = "!!!!!ERROR PARSING!!!!!"
    return MESSAGE[message_id]["Flag"], MESSAGE[message_id]["Level"], message
