from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.configuration.configuration_controller import ConfigurationController
from app.models.exception.multichain_error import MultiChainError


mod = Blueprint("configuration", __name__)

cc = ConfigurationController()

"""
Creates the blockchain with the provided name
The name is expected in the body of the post request using the tag "name"
"""


@mod.route("/create_chain/", methods=["POST"])
def create_chain():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request["blockchainName"]

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
The name is expected in the body of the post request using the tag "name"
The parameters are expected in the body, nested under the tag "params"
The parameter tags are expected as follows:
    "param blockchainName":
    "param description":
    "param maxBlockSize": 
    "param targetBlockTime":
    "param miningTurnover":
"""


@mod.route("/config_parameters/", methods=["POST"])
def config_params():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request["blockchainName"]
        parameters = json_request["params"]

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
The blockchain name is expected in the body using the "blockchainName" tag
"""


@mod.route("/deploy_chain/", methods=["GET"])
def deploy_chain():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request["blockchainName"]
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
The blockchain name is expected in the body using the "blockchainName" tag
"""


@mod.route("/get_node_address/", methods=["GET"])
def get_node_address():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT,
            )

        blockchain_name = json_request["blockchainName"]
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
