import logging
from pathlib import Path
from src.lib.config import Config
from src.lib.storage.dropbox import Dropbox


class Storage(Dropbox):

    def __init__(self, logger_name: str) -> None:

        # ----------------------------------------------------------------------
        #   Defines the location of the files with configurations and load them.
        # ----------------------------------------------------------------------
        config_base_path = Path.cwd().resolve() / "cfg"
        config_access_file = config_base_path / "api-cfg.json"
        config_access_userdata_file = config_base_path / "user" / "api-cfg-access.json"
        config_local_file = config_base_path / "local" / "local.json"
        config_parameters_file = config_base_path / "parameters.json"

        self.config = Config(logger_name=logger_name)
        self.config.load_config(filename=config_access_file)
        self.config.load_config(filename=config_access_userdata_file)
        self.config.load_config(filename=config_local_file)
        self.config.load_config(filename=config_parameters_file)

        self.access_token = self.config.data_source_storage_user_data["TOKEN"]

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".storage"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing storage.")
