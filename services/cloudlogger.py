import json
import logging
import logging.config
import logging.handlers
import pathlib

import google.cloud.logging


class CloudLogger:

    @classmethod
    def initiate_logger(cls):
        log_client = google.cloud.logging.Client()
        log_handler = log_client.get_default_handler()

        config_file = pathlib.Path("logging_config.json")
        with open(config_file) as f_in:
            config = json.load(f_in)

        logging.config.dictConfig(config)

        logger = logging.getLogger(__name__)

        return logger


CloudLogger.initiate_logger()
