# import sys
# import pathlib

# source_path = pathlib.Path.cwd().resolve().parents[0] / "src"
# print(str(source_path))
# sys.path.append(source_path)
import logging
from lib.config import Config

# import data_access
from data_access import DataAccess


if __name__ == '__main__':

    config = Config(filename="../cfg/api-cfg.json")
    
    logging.basicConfig(
        #filename=self.config.path_logger,
        filemode="a",
        datefmt="%Y.%m.%d %I:%M:%S %p",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    #logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('invst')


    #print(config.json_data)

    data_access = DataAccess(ticker="BTC",
                             source=config.data_source,
                             access_config=config.access_data,
                             logger_name="invst")