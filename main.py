# author = "Anton Fernando"
# email = "afernando@outlook.com.au"
# copyright = ""
# version = "1.0"

import os
import json
import logging
import sys

from app import App
from config import BaseConfig

import services.cloudlogger

from get_secret import access_secret_version, get_secret_id
from update_creds import rotate_creds

# Create a custom logger
logger = logging.getLogger(__name__)

# Initialize app object and load config
App.setup(BaseConfig)

gateway = os.environ["PBI_GATEWAY_ID"]
datasources = os.environ["PBI_DATASOURCE_IDS"]
datasources_list = datasources.split(",")


class KeyRotationError(Exception):
    """Create new exception type to capture errors with key rotation"""

    pass


def format_secret(secret: str):
    """This function formats the secret from the secret manager."""
    formatted_secret = secret.replace(r"\n", r"\\n").rstrip()
    return formatted_secret


def get_username(secret):
    """This function extracts the username from the secret."""
    secret_object = json.loads(secret)
    client_email = secret_object["client_email"]
    return client_email


def main(event, context):
    """Main functin for key rotation."""
    try:
        event_type = event["attributes"]["eventType"]
        version_id = event["attributes"]["versionId"]
        secret_id = event["attributes"]["secretId"]
        if event_type == "SECRET_DELETE":
            logger.error("SECRET %s is deleted.", secret_id)
            raise KeyRotationError(f"SECRET {secret_id} is deleted.")
        elif event_type == "SECRET_VERSION_DESTROY":
            logger.warning(
                "The secret version %s is destroyed.",
                version_id.rsplit("/", 1)[1],
            )
        elif event_type == "SECRET_VERSION_DISABLE":
            logger.info(
                "The secret version %s is disabled.", version_id.rsplit("/", 1)[1]
            )
        elif (
            event_type == "SECRET_UPDATE"
            or event_type == "SECRET_VERSION_ADD"
            or event_type == "SECRET_VERSION_ENABLE"
        ):
            logger.info(
                "Event %s was taken place for %s %s",
                event_type,
                secret_id,
                version_id,
            )
            secret_id = get_secret_id(event, context)
            latest_secret = access_secret_version(secret_id)
            password = format_secret(latest_secret)
            username = get_username(password)
            for datasource in datasources_list:
                rotate_creds(username, password, datasource, gateway)
    except KeyError:
        logger.info(
            "Key rotation attributes do not exist in the PubSub message. Not initiating key rotation"
        )
        sys.exit(100)
    except KeyRotationError as exc:
        logger.exception("Failed to update credentials: %s", exc)
        raise KeyRotationError(
            "Key rotation failed. Check event and context content.", exc
        ) from exc
    except Exception as exc:
        logger.exception("Failed to update data source credentials")
        logger.exception(exc)
        raise Exception("Power BI key rotation failed", exc) from exc
