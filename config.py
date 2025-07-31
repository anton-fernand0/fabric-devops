# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# Import the Secret Manager client library.
from google.cloud import secretmanager
import os

tenant_id = os.environ["PBI_TENANT_ID"]
client_id = os.environ["AZ_CLIENT_ID"]
client_secret_id = os.environ["AZ_CLIENT_SECRET_ID"]


class SecretsApiError(Exception):
    """Create new exception type to capture Secrets API errors"""

    pass


class BaseConfig(object):
    def access_secret_version(secret_id):
        """
        Purpose:
        Fetches a Secrets Manager Value

        Parameters:
            secret_id(str): Secret manager secret to fetch

        Return:
            secret_value(str): Decrypted secret manager value
        """

        try:
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

        except Exception as err:
            raise SecretsApiError(err)

    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = "ServicePrincipal"

    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = tenant_id

    # Client Id (Application Id) of the AAD app
    CLIENT_ID = client_id

    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = access_secret_version(client_secret_id)

    # Scope Base of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE_BASE = ["https://analysis.windows.net/powerbi/api/.default"]

    # URL used for initiating authorization request
    AUTHORITY_URL = "https://login.microsoftonline.com/organizations"

    # End point URL for Power BI API
    POWER_BI_API_URL = "https://api.powerbi.com/"

    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = ""

    # Master user password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = ""
