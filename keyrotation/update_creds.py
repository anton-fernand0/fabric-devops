# author = "Anton Fernando"
# email = "afernando@outlook.com.au"
# copyright = ""
# version = "1.0"

import json
import logging

from models.credentialsdetails import CredentialsDetails
from models.credentialsdetailsrequest import CredentialsDetailsRequest
from services.aadservice import AadService
from services.addcredentialsservice import AddCredentialsService
from services.asymmetrickeyencryptor import AsymmetricKeyEncryptor
from services.datavalidationservice import DataValidationService
from services.getdatasource import GetDatasourceService
from services.updatecredentialsservice import UpdateCredentialsService

# Get logger
logger = logging.getLogger(__name__)


class AccessTokenError(Exception):
    """Create new exception type to capture errors with retrieving the access token"""

    pass


class CredentialUpdateError(Exception):
    """Create new exception type to capture errors with updating data source credentials"""

    pass


def rotate_creds(username, password, datasource, gateway):
    # Get logger
    logger = logging.getLogger(__name__)

    request = {
        "data": {
            "credType": "Basic",
            "credentialsArray": [username, password],
            "privacyLevel": "Organizational",
            "datasourceId": datasource,
            "gatewayId": gateway,
        }
    }
    request_data = request["data"]
    gateway_id = request_data["gatewayId"]
    datasource_id = request_data["datasourceId"]
    gateway = {
        "id": gateway_id,
        "publicKey": None,
    }
    logger.info("Updating datasource %s", datasource_id)
    try:
        access_token = AadService.get_access_token()
        logger.info("access token retrieved successfully")
    except AccessTokenError as err:
        logger.error("Failed to retrieve the access token: %s", err)
        raise Exception(
            "Failed to retrieve the access token. Check the service principal client ID and secret.",
            err,
        ) from err

    # Validate the credentials data by the user
    data_validation_service = DataValidationService()
    data_validation_service.validate_creds(request_data)

    data_source_service = GetDatasourceService()
    gateway_api_response = data_source_service.get_gateway(access_token, gateway_id)

    if not gateway_api_response.ok:
        if not gateway_api_response.reason == "Not Found":
            return (
                json.dumps(
                    {
                        "errorMsg": str(
                            f'Error {gateway_api_response.status_code} {gateway_api_response.reason}\\nRequest Id:\t{gateway_api_response.headers.get("RequestId")}'
                        )
                    }
                ),
                gateway_api_response.status_code,
            )
    else:
        gateway = gateway_api_response.json()
        logger.info("Gateway info retrieved successfully")

    try:
        update_creds_service = UpdateCredentialsService()
        api_response = update_creds_service.update_datasource(
            access_token,
            request_data["credType"],
            request_data["privacyLevel"],
            request_data["credentialsArray"],
            gateway,
            request_data["datasourceId"],
        )
        logger.info(api_response)
        logger.info("Finished updating datasource %s", datasource_id)

    except CredentialUpdateError as err:
        logger.error("Failed to update data source credentials: %s", err)
        raise Exception(
            "Failed to rupdate data source credentials.",
            err,
        ) from err
