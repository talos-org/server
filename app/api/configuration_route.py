from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.configuration.configuration_controller import ConfigurationController
from app.models.exception.multichain_error import MultiChainError

BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
PARAMETERS_FIELD_NAME = "params"


mod = Blueprint("configuration", __name__)

cc = ConfigurationController()

"""
Creates the blockchain with the provided name
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""


@mod.route("/create_chain", methods=["POST"])
def create_chain():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {"error": "The blockchainName field was not found in the request!"}
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = blockchain_name.strip()
        cc.create_chain(blockchain_name)
        return jsonify({"Status": blockchain_name + " created!"}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Configures the parameters in the param.dat using the blockchain name provided
The following data is expected in the body of the request:
    "blockchainName":
    "params" : [
        "description" : 
        "maxBlockSize" :
        "targetBlockTime" :
        "miningTurnover" :
    ]
"""


@mod.route("/config_parameters", methods=["POST"])
def config_params():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not PARAMETERS_FIELD_NAME in json_request:
            return (
                jsonify(
                    {
                        "error": "The "
                        + PARAMETERS_FIELD_NAME
                        + " field was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        parameters = json_request[PARAMETERS_FIELD_NAME]

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not parameters:
            return jsonify(
                {
                    "error": "No parameters were supplied, please provide the required parameters!"
                }
            )

        blockchain_name = blockchain_name.strip()
        required_parameters = [
            "description",
            "maxblocksize",
            "targetblocktime",
            "miningturnover",
        ]

        original_number_of_keys = len(parameters)
        parameters = {
            key: value
            for key, value in parameters.items()
            if key.lower() in required_parameters
        }
        new_number_of_keys = len(parameters)

        if new_number_of_keys < original_number_of_keys:
            return jsonify(
                {
                    "error": "Some of The required parameters are missing. Expecting: "
                    + str(len(required_parameters))
                    + " parameters, receieved: "
                    + str(new_number_of_keys)
                    + " parameters."
                }
            )

        cc.config_params(blockchain_name, parameters)
        return jsonify({"Status": "Configurations Changed!"}), status.HTTP_200_OK
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Deploys the created chain
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""
@mod.route("/deploy_chain", methods=["POST"])
def deploy_chain():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {"error": "The blockchainName field was not found in the request!"}
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]
        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = blockchain_name.strip()
        if cc.deploy_blockchain(blockchain_name):
            return (
                jsonify({"Status": blockchain_name + " Deployed"}),
                status.HTTP_200_OK,
            )

    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
Returns the node address of the provided blockchain name
The following data is expected to be passed in as query parameters:
    "blockchainName": blockchain name
"""

@mod.route("/get_node_address", methods=["GET"])
def get_node_address():
    try:
        request_args = request.args

        if not request_args:
            return (
                jsonify({"error": "No parameters were passed!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)

        if blockchain_name is None:
            return (
                jsonify(
                    {
                        "error": "The "
                        + BLOCKCHAIN_NAME_FIELD_NAME
                        + " parameter was not found in the request!"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        if not blockchain_name or not blockchain_name.strip():
            return (
                jsonify({"error": "The blockchain name can't be empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = blockchain_name.strip()

        return (
            jsonify({"nodeAddress": cc.get_node_address(blockchain_name)}),
            status.HTTP_200_OK,
        )

    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST

    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST



"""
Checks if the passed in blockchain name already exists
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""
@mod.route("/check_blockchain_name", methods=["POST"])
def check_blockchain_name():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            return (
                jsonify(
                    {"error": "The blockchainName field was not found in the request!"}
                ),
                status.HTTP_400_BAD_REQUEST,
            )

        blockchain_name = json_request[BLOCKCHAIN_NAME_FIELD_NAME]

        existing_blockchains=cc.get_blockchains()

        if blockchain_name in existing_blockchains:
            return jsonify({"status": "Blockchain name already exists!"}), status.HTTP_400_BAD_REQUEST

        else:
            return jsonify({"status": "Valid blockchain name"}), status.HTTP_200_OK

    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST




"""
Returns all the existing blockchains on the requesting node
No parameters needed
"""
@mod.route("/get_blockchains", methods=["GET"])
def get_blockchains():
    try:

        existing_blockchains=cc.get_blockchains()

        return (
            jsonify({"Existing Blockchains": existing_blockchains}),
            status.HTTP_200_OK
        )

    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST
