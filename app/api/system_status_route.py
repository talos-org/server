from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.monitor.system_status_controller import SystemStatusController
from app.models.permission.permission_controller import PermissionController
from app.models.exception.multichain_error import MultiChainError
import json

mod = Blueprint("systemstatus", __name__)


BLOCKCHAIN_NAME_FIELD_NAME = "blockchainName"
CONNECTABLE_NODES_FIELD_NAME = "connectableNodes"
verbose = False
addresses = "*"
permissions = ["connect"]

"""
Returns information relating to all the peers of the node making the request
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""


@mod.route("/get_peer_info", methods=["GET"])
def get_peer_info():
    try:
        request_args = request.args

        if not request_args:
            raise ValueError("No parameters were passed!")

        blockchain_name = request_args.get("blockchainName")

        if blockchain_name is None:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " parameter was not found in the request!"
            )

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        peer_info = SystemStatusController.get_peer_info(blockchain_name)


        return jsonify(peer_info), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Returns the wallet address of the node making the request
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""


@mod.route("/get_wallet_address", methods=["GET"])
def get_wallet_address():
    try:
        request_args = request.args

        if not request_args:
            raise ValueError("No parameters were passed!")

        blockchain_name = request_args.get(BLOCKCHAIN_NAME_FIELD_NAME)

        if blockchain_name is None:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " parameter was not found in the request!"
            )

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()
        wallet_address = SystemStatusController.get_wallet_address(blockchain_name)
        return jsonify({"walletAddress: ": wallet_address}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)


"""
Returns all nodes the current node cannot connect to
The following data is expected in the body of the request:
    "blockchainName": blockchain name
"""


@mod.route("/get_inactive_nodes", methods=["POST"])
def get_inactive_nodes():
    try:
        json_request = request.get_json()

        if not json_request:
            raise ValueError("The request body is empty!")

        if not BLOCKCHAIN_NAME_FIELD_NAME in json_request:
            raise ValueError(
                "The "
                + BLOCKCHAIN_NAME_FIELD_NAME
                + " field was not found in the request!"
            )

        blockchain_name = json_request["blockchainName"]

        nodes_with_connect_permission = PermissionController.get_permissions(
            blockchain_name, permissions, addresses, verbose
        )

        nodes_json = json.dumps(nodes_with_connect_permission)
        nodes_json = json.loads(nodes_json)

        if not blockchain_name or not blockchain_name.strip():
            raise ValueError("The blockchain name can't be empty!")

        blockchain_name = blockchain_name.strip()

        inactive_nodes = SystemStatusController.get_inactive_nodes(
            blockchain_name, nodes_json
        )


        return jsonify(list(inactive_nodes)), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except (ValueError, Exception) as ex:
        return (jsonify({"error": {"message": str(ex)}}), status.HTTP_400_BAD_REQUEST)
