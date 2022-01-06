"""Script for sequence analysis of a list of symbols / tickers and providing
a report of the overall results for performance evaluation.

"""
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from src.communication import Communication
from src.lib.config import Config
from src.lib import constants as C
from src.data_access import DataAccess
from src.analysis import Analysis
from src.lib import print_table as pt

LOGGER_NAME = "invst.run_analysis"


def run_analysis():

    # --------------------------------------------------------------------------
    #   Defines the logger configuration and start the logger. Add a few
    #   message to mark the start of the execution.
    # --------------------------------------------------------------------------
    logging.basicConfig(
        filename=Path.cwd().resolve() / "logs" / "logs.log",
        filemode="a",
        datefmt="%Y.%m.%d %I:%M:%S %p",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    logformat = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y.%m.%d %I:%M:%S %p",)

    logger_console = logging.StreamHandler()
    logger_console.setLevel(logging.INFO)
    logger_console.setFormatter(logformat)

    logging.getLogger(LOGGER_NAME).addHandler(logger_console)

    logger = logging.getLogger(LOGGER_NAME)

    logger.info("")
    logger.info("========================== NEW RUN ==========================")

    # --------------------------------------------------------------------------
    #   Defines the location of the files with configurations and load them.
    # --------------------------------------------------------------------------
    config_base_path = Path.cwd().resolve() / "cfg"
    config_access_file = config_base_path / "api-cfg.json"
    config_access_userdata_file = config_base_path / "api-cfg-access.json"
    config_local_file = config_base_path / "local.json"
    config_parameters_file = config_base_path / "parameters.json"

    config = Config(logger_name=LOGGER_NAME)
    config.load_config(filename=config_access_file)
    config.load_config(filename=config_access_userdata_file)
    config.load_config(filename=config_local_file)
    config.load_config(filename=config_parameters_file)

    # --------------------------------------------------------------------------
    #   Collects data about the execution.
    # --------------------------------------------------------------------------
    execution_data = {}
    execution_data["parameters"] = config.parameters
    execution_data["execution"] = {}
    execution_data["execution"]["Time start"] = datetime.now().strftime(
        '%Y.%m.%d %H:%M:%S')

    # --------------------------------------------------------------------------
    #   Starts the communication and send a message to notify.
    # --------------------------------------------------------------------------
    communication = Communication(
        access_config=config.data_source_comm_access_data,
        access_userdata=config.data_source_comm_user_data,
        logger_name=LOGGER_NAME
    )

    communication.send_message(
        body=f"Starting analysis of tickers.\nReference: {datetime.now().strftime('%H:%M:%S')}")

    # --------------------------------------------------------------------------
    #   List of tickers and sequence analysis.
    # --------------------------------------------------------------------------
    symbols = [
        {"name": "Daimler AG", "symbol": "DAI.DE"},
        {"name": "Siemens AG", "symbol": "SIE.DE"},
        {"name": "Coca-Cola Co.", "symbol": "KO"},
        {"name": "Alphabet Inc.", "symbol": "GOOG"},
        {"name": "Tesla, Inc.", "symbol": "TSLA"},
        {"name": "Boeing Co.", "symbol": "BA"},
        {"name": "Apple", "symbol": "AAPL"},
        {"name": "Amazon", "symbol": "AMZN"},
        {"name": "Bristol-Meyers Squibb", "symbol": "BMY"},
        {"name": "General Motors", "symbol": "GM"},
        {"name": "AbbVie Inc.", "symbol": "ABBV"},
        {"name": "American Express CO.", "symbol": "AXP"},
        {"name": "3M CO.", "symbol": "MMM"},
        {"name": "CISCO INC.", "symbol": "CSCO"},
        {"name": "IBM CORP.", "symbol": "IBM"},
        {"name": "The Walt Disney Co.", "symbol": "DIS"},
        {"name": "Johnson & Johnson", "symbol": "JNJ"},
        {"name": "IDEX", "symbol": "IEX"},
        {"name": "Akamai Technologies, Inc.", "symbol": "AKAM"},
        {"name": "Telefonaktiebolaget LM Ericsson", "symbol": "ERIC"},
        {"name": "Thermo Fisher Scientific Inc.", "symbol": "TMO"},
        {"name": "Zscaler, Inc.", "symbol": "ZS"},
        {"name": "Meta", "symbol": "FB"},
    ]
    execution_data["execution"]["Symbols"] = symbols
    execution_data["execution"]["Symbols count"] = len(symbols)

    results_data = []
    results_analysis = []
    results_summary = []

    i = 1
    for symbol in symbols:

        logger.info(f"---------- Analysis {i} from {len(symbols)} ----------")
        i = i + 1

        # Short pause between requests to avoid over-request to AlphaVantage
        time.sleep(config.parameters["execution"]["time_sleep"]["value"])

        ticker = symbol["symbol"]

        result = DataAccess(ticker=ticker,
                            source=config.data_source_fetch_name,
                            access_config=config.data_source_fetch_access_data,
                            access_userdata=config.data_source_fetch_user_data,
                            logger_name=LOGGER_NAME,
                            )

        result_values, flag, level, message = result.update_values(
            type_series="TIMESERIES", period="DAILY"
        )

        if flag == C.SUCCESS:

            results_data.append(result)

            # ------------------------------------------------------------------
            #   Perform analysis of the data.
            # ------------------------------------------------------------------
            analysis = Analysis(symbol=ticker,
                                ohlc_data=result_values,
                                logger_name=LOGGER_NAME)
            decision = analysis.analyze()

            results_analysis.append(analysis)
            results_summary.append({ticker: analysis.analysis_results})

            analysis = None
            result = None

    # --------------------------------------------------------------------------
    #   Terminate the execution since there were only empty results. This is an
    #   error to be catched.
    # --------------------------------------------------------------------------
    if len(results_summary) == 0 or len(results_summary) == 0:
        execution_data["execution"]["Time end"] = datetime.now().strftime(
            '%Y.%m.%d %H:%M:%S')
        email_subject, email_body = communication.format_email_fail_empty()
        communication.send_email(subject=email_subject, body_html=email_body)
        logger.info(
            "======================= COMPLETED RUN =======================")
        sys.exit()

    # --------------------------------------------------------------------------
    #   Builds up the final response to be presented to the user. Storing the
    #   results in Microsoft Excel file and also preparing an
    # --------------------------------------------------------------------------
    today_string = datetime.today().strftime('%Y-%m-%d')
    file_export_summary = f"Export_Summary_{today_string}.xlsx"
    folder = Path(config.local_config["paths"]["data_storage"])
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    file_export_summary = folder / file_export_summary
    df_results_summary = pt.summary_table(
        results_summary, file_export_summary)

    print(df_results_summary.columns)
    print(df_results_summary["Last Day Event"])

    execution_data["execution"]["Time end"] = datetime.now().strftime(
        '%Y.%m.%d %H:%M:%S')
    execution_data["execution"]["Duration"] = (
        datetime.strptime(execution_data["execution"]["Time end"], '%Y.%m.%d %H:%M:%S') -
        datetime.strptime(execution_data["execution"]["Time start"], '%Y.%m.%d %H:%M:%S')).seconds / 60.0

    email_subject, email_body = communication.format_email_success(
        results=df_results_summary, execution_stat=execution_data)
    communication.send_email(subject=email_subject,
                             body_html=email_body,
                             attachment=file_export_summary)

    logger.info(
        "======================= COMPLETED RUN =======================")

    return "Completed run"


if __name__ == "__main__":
    run_analysis()
