# import logging
# import os
# import json
# from azure.communication.networktraversal import CommunicationRelayClient
# from azure.communication.identity import CommunicationIdentityClient

# import azure.functions as func

# connection_str = os.getenv("ICE_CONNECTION_STRING")

# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     identity_client = CommunicationIdentityClient.from_connection_string(connection_str)
#     relay_client = CommunicationRelayClient.from_connection_string(connection_str)

#     _ = identity_client.create_user()
#     relay_client.get_relay_configuration()

#     relay_configuration = relay_client.get_relay_configuration()

#     for iceServer in relay_configuration.ice_servers:
#         assert iceServer.username is not None
#         assert iceServer.credential is not None
#         assert iceServer.urls is not None
#         for url in iceServer.urls:
#             print('Url:' + url)

#         credentials = {
#             "username": iceServer.username,
#             "credential": iceServer.credential
#         }

#     return func.HttpResponse(
#             json.dumps(credentials),
#             status_code=200
#     )

import logging
import os
import json
from datetime import timedelta
from azure.communication.networktraversal import CommunicationRelayClient
from azure.communication.identity import CommunicationIdentityClient, CommunicationUserIdentifier
import azure.functions as func

connection_str = os.getenv("ICE_CONNECTION_STRING")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Instantiate clients
    identity_client = CommunicationIdentityClient.from_connection_string(connection_str)
    relay_client = CommunicationRelayClient.from_connection_string(connection_str)

    # Create an identity
    identity = identity_client.create_user()
    logging.info(f'Created an identity with ID: {identity.properties["id"]}')
    
    # Issue a 24-hour token for the identity
    token_result = identity_client.get_token(identity, ["voip"])
    logging.info(f"Issued a token that expires at {token_result.expires_on}: {token_result.token}")
    
    # Revoke the token if required
    # identity_client.revoke_tokens(identity)
    # logging.info(f"Revoked all tokens for identity ID: {identity.properties['id']}")

    # Example of issuing a token with a custom expiration time of 1 hour
    token_expires_in = timedelta(hours=1)
    short_lived_token = identity_client.get_token(identity, ["voip"], token_expires_in=token_expires_in)
    logging.info(f"Issued a short-lived token that expires at {short_lived_token.expires_on}: {short_lived_token.token}")

    # Get relay configuration for ICE server credentials
    relay_configuration = relay_client.get_relay_configuration()

    # Extract ICE server credentials
    ice_servers_info = []
    for iceServer in relay_configuration.ice_servers:
        ice_server_info = {
            "urls": iceServer.urls,
            "username": iceServer.username,
            "credential": iceServer.credential
        }
        ice_servers_info.append(ice_server_info)
        logging.info(f"ICE Server URL: {iceServer.urls}")

    # Prepare response data including identity, tokens, and ICE server credentials
    response_data = {
        "identity": identity.properties['id'],
        "token": token_result.token,
        "short_lived_token": short_lived_token.token,
        "ice_servers": ice_servers_info
    }

    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        mimetype="application/json"
    )

