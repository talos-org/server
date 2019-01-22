from flask import Flask, request, jsonify, Blueprint
from flask_api import status
from app.models.node.node_controller import NodeController
from app.models.exception.multichain_error import MultiChainError

mod = Blueprint("node", __name__)

NEW_NODE_ADDRESS_FIELD_NAME = "newNodeAddress"
ADMIN_NODE_ADDRESS_FIELD_NAME = "adminNodeAddress"


"""
Connects the current node to the admin node, and returns the wallet address.
The following data is expected in the body of the request:
    "adminNodeAddress": admin node address
"""
@mod.route("/connect_to_admin_node", methods=["POST"])
def connect_to_admin_node():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        if not ADMIN_NODE_ADDRESS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + ADMIN_NODE_ADDRESS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        admin_node_address = json_request[ADMIN_NODE_ADDRESS_FIELD_NAME]

        if not admin_node_address or not admin_node_address.strip():
            return (
                jsonify({"error": "The provided admin node address can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        admin_node_address = admin_node_address.strip()
        wallet_address = NodeController.connect_to_admin_node(admin_node_address)
        return jsonify({"Success, Wallet address: ": wallet_address}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST



"""
Adds the provided node to the blockchain network
The following data is expected in the body of the request:
    "newNodeAddress": node address of node that is being added
"""
@mod.route("/add_node", methods=["POST"])
def add_node():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )


        if not NEW_NODE_ADDRESS_FIELD_NAME in json_request:
            return (
                jsonify({"error": "The " + NEW_NODE_ADDRESS_FIELD_NAME + " field was not found in the request!"}),
                status.HTTP_400_BAD_REQUEST,
            )

        new_node_address = json_request[NEW_NODE_ADDRESS_FIELD_NAME]

        if not new_node_address or not new_node_address.strip():
            return (
                jsonify({"error": "The provided wallet address of the new node can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )
        new_node_wallet_address = new_node_address.strip()
        return jsonify({"Success, Wallet address: ": add_node(new_node_wallet_address)}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST


"""
WIP: remove node method is not yet complete in the controller
Removes the provided node to the blockchain network
The following data is expected in the body of the request:
    "newNodeAddress": node address of node that is being added
"""
@mod.route("/remove_node", methods=["POST"])
def remove_node():
    try:
        json_request = request.get_json()

        if not json_request:
            return (
                jsonify({"error": "The request body is empty!"}),
                status.HTTP_204_NO_CONTENT
            )

        new_node_address = json_request["newNodeAddress"]

        if not new_node_address or not new_node_address.strip():
            return (
                jsonify({"error": "The provided wallet address of the new node can't be empty!"}),
                status.HTTP_400_BAD_REQUEST
            )

        new_node_address = new_node_address.strip()
        return jsonify({"Success, Wallet address: ": NodeController.add_node(new_node_address)}), status.HTTP_200_OK
    except MultiChainError as ex:
        return jsonify(ex.get_info()), status.HTTP_400_BAD_REQUEST
    except Exception as ex:
        return jsonify({"error": str(ex)}), status.HTTP_400_BAD_REQUEST