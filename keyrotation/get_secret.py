# author = "Anton Fernando"
# email = "afernando@outlook.com.au"
# copyright = ""
# version = "1.0"

import base64
import logging

# Import the Secret Manager client library.
from google.cloud import secretmanager

# Get logger
logger = logging.getLogger(__name__)


class SecretsVersionError(Exception):
    """Create new exception type to capture secret version access errors"""

    pass


class SecretsIdError(Exception):
    """Create new exception type to capture secrets access errors"""

    pass


def get_secret_id(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
                        event. The `@type` field maps to
                         `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
                        The `data` field maps to the PubsubMessage data
                        in a base64-encoded string. The `attributes` field maps
                        to the PubsubMessage attributes if any is present.
         context (google.cloud.functions.Context): Metadata of triggering event
                        including `event_id` which maps to the PubsubMessage
                        messageId, `timestamp` which maps to the PubsubMessage
                        publishTime, `event_type` which maps to
                        `google.pubsub.topic.publish`, and `resource` which is
                        a dictionary that describes the service API endpoint
                        pubsub.googleapis.com, the triggering topic's name, and
                        the triggering event type
                        `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None. The output is written to Cloud Logging.
    """

    logger.info(
        "This function was triggered by messageId %s published at %s to %s",
        context.event_id,
        context.timestamp,
        context.resource["name"],
    )
    try:
        if "data" in event:
            name = base64.b64decode(event["data"]).decode("utf-8")
        else:
            raise SecretsIdError("Failed to data from the event")
        if "attributes" in event:
            secret_id = event["attributes"]["secretId"]
        else:
            raise SecretsIdError("Failed to read attributes from the event")
        logger.info("Secret ID received %s", secret_id)
        return secret_id

    except SecretsIdError as err:
        logger.error("Request to secrets api returned an error: %s", err)
        raise Exception("Request to secrets api returned an error", err) from err

    except Exception as exc:
        logger.error("Failed to retrieve the secret ID")
        logger.error(exc)
        raise Exception("Power BI key rotation failed", exc) from exc


def access_secret_version(secret_id):
    # Create a client
    client = secretmanager.SecretManagerServiceClient()

    # Initialize request argument(s)
    request = secretmanager.AccessSecretVersionRequest(
        name=f"{secret_id}/versions/latest",
    )

    # Make the request
    response = client.access_secret_version(request=request)
    payload = response.payload.data.decode("UTF-8")

    # Return the response
    return payload
